"""YAML Script Runner — DOM-aware script execution engine.

Loads YAML scripts and executes step-by-step actions (tap, swipe, wait,
wait_for, if/else) using the Screen DOM for element finding and condition
evaluation. Replaces the old verb-based quest_script system for v2.

Script format example::

    name: upgrade_barracks
    description: "升级兵营到下一级"
    steps:
      - action: tap
        pos: [540, 800]
        target: {type: button, text: "升级"}
        wait: 1.0
      - action: wait_for
        target: {type: text, value: "升级完成"}
        timeout: 60
      - action: if
        condition:
          exists: {type: text, value: "资源不足"}
        then:
          - action: tap
            pos: [680, 1000]
        else:
          - action: tap
            pos: [400, 1000]
"""

import glob
import logging
import math
import os
import time

import yaml

logger = logging.getLogger(__name__)


class ScriptAbortError(Exception):
    """Raised when a script encounters an unrecoverable failure."""
    pass


# ---------------------------------------------------------------------------
# Script loading
# ---------------------------------------------------------------------------

VALID_ACTIONS = {"tap", "swipe", "wait", "wait_for", "if"}
VALID_TARGET_TYPES = {"button", "text", "icon", "red_dot", "green_check", "finger"}
VALID_CONDITION_KEYS = {"exists", "not_exists", "scene", "all", "any"}


def _validate_script(data: dict) -> None:
    """Validate script schema. Raises ValueError on problems."""
    if not isinstance(data, dict):
        raise ValueError("Script must be a YAML mapping")
    if "name" not in data:
        raise ValueError("Script missing required 'name' field")
    if "steps" not in data or not isinstance(data["steps"], list):
        raise ValueError("Script missing required 'steps' list")
    if not data["steps"]:
        raise ValueError("Script 'steps' list is empty")
    for i, step in enumerate(data["steps"]):
        _validate_step(step, f"steps[{i}]")


def _validate_step(step: dict, path: str) -> None:
    """Validate a single step dict recursively."""
    if not isinstance(step, dict):
        raise ValueError(f"{path}: step must be a mapping")
    action = step.get("action")
    if action not in VALID_ACTIONS:
        raise ValueError(
            f"{path}: invalid action '{action}', "
            f"expected one of {sorted(VALID_ACTIONS)}"
        )

    if action == "tap":
        if "pos" not in step and "target" not in step:
            raise ValueError(f"{path}: tap requires 'pos' or 'target'")

    elif action == "swipe":
        if "from" not in step or "to" not in step:
            raise ValueError(f"{path}: swipe requires 'from' and 'to'")

    elif action == "wait":
        if "seconds" not in step:
            raise ValueError(f"{path}: wait requires 'seconds'")

    elif action == "wait_for":
        if "target" not in step:
            raise ValueError(f"{path}: wait_for requires 'target'")

    elif action == "if":
        if "condition" not in step:
            raise ValueError(f"{path}: if requires 'condition'")
        if "then" not in step:
            raise ValueError(f"{path}: if requires 'then'")
        cond = step["condition"]
        if not isinstance(cond, dict):
            raise ValueError(f"{path}.condition: must be a mapping")
        cond_keys = set(cond.keys())
        if not cond_keys.issubset(VALID_CONDITION_KEYS):
            bad = cond_keys - VALID_CONDITION_KEYS
            raise ValueError(
                f"{path}.condition: unknown keys {bad}"
            )
        # Validate then/else branches recursively
        for j, sub in enumerate(step["then"]):
            _validate_step(sub, f"{path}.then[{j}]")
        if "else" in step:
            for j, sub in enumerate(step["else"]):
                _validate_step(sub, f"{path}.else[{j}]")


def load_script(path: str) -> dict:
    """Load and validate a YAML script file.

    Returns:
        Parsed script dict.

    Raises:
        FileNotFoundError: if path doesn't exist.
        ValueError: if script is invalid.
    """
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    _validate_script(data)
    return data


def list_scripts(scripts_dir: str) -> list[str]:
    """List available script names (without extension) from a directory.

    Returns sorted list of script base names.
    """
    if not os.path.isdir(scripts_dir):
        return []
    pattern = os.path.join(scripts_dir, "*.yaml")
    paths = glob.glob(pattern)
    names = sorted(
        os.path.splitext(os.path.basename(p))[0] for p in paths
    )
    return names


# ---------------------------------------------------------------------------
# DOM element finding
# ---------------------------------------------------------------------------

def _flatten_elements(dom: dict) -> list[dict]:
    """Collect all elements from all DOM regions + popup children."""
    elements = []
    screen = dom.get("screen", {})

    # Spatial regions
    for region in ("top_bar", "center", "bottom_bar"):
        items = screen.get(region)
        if items:
            elements.extend(items)

    # Popup children
    popup = screen.get("popup")
    if popup and "children" in popup:
        elements.extend(popup["children"])

    return elements


def find_element(dom: dict, target: dict) -> dict | None:
    """Find a DOM element matching the target descriptor.

    Target format:
        {type: "button", text: "升级"}
        {type: "text", value: "升级完成"}
        {type: "icon", name: "search"}
        {type: "red_dot"}

    For multiple matches, picks closest to target["pos"] if provided,
    else first by y-coordinate.

    Returns:
        Matching element dict, or None.
    """
    elements = _flatten_elements(dom)
    target_type = target.get("type", "")

    matches = []
    for elem in elements:
        if elem.get("type") != target_type:
            continue

        if target_type == "button":
            search = target.get("text", "")
            elem_text = elem.get("text", "")
            if search.lower() not in elem_text.lower():
                continue

        elif target_type == "text":
            search = target.get("value", "")
            elem_value = elem.get("value", "")
            if search.lower() not in elem_value.lower():
                continue

        elif target_type == "icon":
            search = target.get("name", "")
            elem_name = elem.get("name", "")
            if search != elem_name:
                continue

        # red_dot, green_check, finger — type-only match
        matches.append(elem)

    if not matches:
        return None
    if len(matches) == 1:
        return matches[0]

    # Multiple matches — prefer closest to target pos hint
    hint_pos = target.get("pos")
    if hint_pos:
        hx, hy = hint_pos
        matches.sort(key=lambda e: math.hypot(
            e["pos"][0] - hx, e["pos"][1] - hy
        ))
    else:
        # First by y-coordinate (top to bottom)
        matches.sort(key=lambda e: e["pos"][1])

    return matches[0]


# ---------------------------------------------------------------------------
# Condition evaluation
# ---------------------------------------------------------------------------

def evaluate_condition(condition: dict, dom: dict) -> bool:
    """Evaluate a condition against the current DOM.

    Supported condition keys:
        exists: {type, text/value/name} — element found in DOM
        not_exists: {type, text/value/name} — element NOT found
        scene: "main_city" — screen.scene matches
        all: [cond, ...] — all sub-conditions true
        any: [cond, ...] — any sub-condition true
    """
    if "exists" in condition:
        return find_element(dom, condition["exists"]) is not None

    if "not_exists" in condition:
        return find_element(dom, condition["not_exists"]) is None

    if "scene" in condition:
        scene = dom.get("screen", {}).get("scene", "unknown")
        return scene == condition["scene"]

    if "all" in condition:
        return all(evaluate_condition(c, dom) for c in condition["all"])

    if "any" in condition:
        return any(evaluate_condition(c, dom) for c in condition["any"])

    logger.warning(f"Unknown condition keys: {list(condition.keys())}")
    return False


# ---------------------------------------------------------------------------
# Script Runner
# ---------------------------------------------------------------------------

class ScriptRunner:
    """Execute YAML scripts step-by-step using ADB and Screen DOM.

    Args:
        adb: ADBController for tap/swipe actions.
        dom_builder: ScreenDOMBuilder for building DOM from screenshots.
        screenshot_fn: Callable that returns a BGR numpy screenshot.
    """

    def __init__(self, adb, dom_builder, screenshot_fn) -> None:
        self.adb = adb
        self.dom_builder = dom_builder
        self.screenshot_fn = screenshot_fn

    def run(self, script: dict, dry_run: bool = False) -> bool:
        """Execute all steps in a script.

        Args:
            script: Parsed script dict (from load_script).
            dry_run: If True, print steps without executing.

        Returns:
            True if completed successfully, False if aborted.
        """
        name = script.get("name", "unnamed")
        steps = script["steps"]
        logger.info(f"Script '{name}': {len(steps)} steps (dry_run={dry_run})")

        try:
            for i, step in enumerate(steps):
                action = step["action"]
                if dry_run:
                    print(f"  [{i+1}/{len(steps)}] {action}: {_step_summary(step)}")
                    continue
                logger.info(f"Step {i+1}/{len(steps)}: {action}")
                self._execute_step(step)
        except ScriptAbortError as e:
            logger.error(f"Script '{name}' aborted: {e}")
            print(f"Script aborted: {e}")
            return False

        if not dry_run:
            logger.info(f"Script '{name}' completed successfully")
        return True

    def _execute_step(self, step: dict) -> None:
        """Dispatch step to the appropriate handler."""
        action = step["action"]
        handler = {
            "tap": self._execute_tap,
            "swipe": self._execute_swipe,
            "wait": self._execute_wait,
            "wait_for": self._execute_wait_for,
            "if": self._execute_if,
        }.get(action)

        if handler is None:
            logger.warning(f"Unknown action: {action}")
            return
        handler(step)

    def _execute_tap(self, step: dict) -> None:
        """Tap at pos, optionally verify target disappeared.

        Flow:
          1. Tap at pos → sleep wait
          2. If no target → done
          3. Screenshot → DOM → find_element
          4. If NOT found → tap succeeded
          5. If found → retry at element pos, up to 3 retries
        """
        pos = step.get("pos")
        target = step.get("target")
        wait = step.get("wait", 0.5)

        if pos:
            x, y = pos
        elif target:
            # No pos given — try to find element first
            screenshot = self.screenshot_fn()
            dom = self.dom_builder.build(screenshot)
            elem = find_element(dom, target)
            if elem:
                x, y = elem["pos"]
            else:
                logger.warning(f"tap: target not found and no pos given: {target}")
                return
        else:
            return

        self.adb.tap(x, y)
        logger.debug(f"Tapped ({x}, {y})")
        time.sleep(wait)

        # Verify target disappeared (if target specified)
        if not target:
            return

        for retry in range(3):
            screenshot = self.screenshot_fn()
            dom = self.dom_builder.build(screenshot)
            elem = find_element(dom, target)
            if elem is None:
                # Target gone — tap succeeded
                return
            # Target still present — retry at element's position
            ex, ey = elem["pos"]
            logger.info(
                f"tap retry {retry+1}/3: target still visible, "
                f"retapping at ({ex}, {ey})"
            )
            self.adb.tap(ex, ey)
            time.sleep(wait)

        logger.warning(f"tap: target still visible after 3 retries: {target}")

    def _execute_swipe(self, step: dict) -> None:
        """Execute a swipe action."""
        x1, y1 = step["from"]
        x2, y2 = step["to"]
        duration = step.get("duration_ms", 300)
        wait = step.get("wait", 0.5)

        self.adb.swipe(x1, y1, x2, y2, duration)
        logger.debug(f"Swiped ({x1},{y1}) → ({x2},{y2}) {duration}ms")
        time.sleep(wait)

    def _execute_wait(self, step: dict) -> None:
        """Sleep for a specified duration."""
        seconds = step["seconds"]
        logger.debug(f"Waiting {seconds}s")
        time.sleep(seconds)

    def _execute_wait_for(self, step: dict) -> None:
        """Poll DOM until target element appears or timeout.

        Raises ScriptAbortError on timeout.
        """
        target = step["target"]
        timeout = step.get("timeout", 30)
        poll_interval = step.get("poll_interval", 2)

        deadline = time.time() + timeout
        logger.info(
            f"wait_for: looking for {target} (timeout={timeout}s)"
        )

        while time.time() < deadline:
            screenshot = self.screenshot_fn()
            dom = self.dom_builder.build(screenshot)
            elem = find_element(dom, target)
            if elem is not None:
                logger.info(f"wait_for: found target at {elem['pos']}")
                return
            time.sleep(poll_interval)

        raise ScriptAbortError(
            f"wait_for timeout ({timeout}s): {target}"
        )

    def _execute_if(self, step: dict) -> None:
        """Evaluate condition and execute then/else branch."""
        condition = step["condition"]

        try:
            screenshot = self.screenshot_fn()
            dom = self.dom_builder.build(screenshot)
            result = evaluate_condition(condition, dom)
        except Exception as e:
            logger.warning(f"if: DOM build failed ({e}), treating as False")
            result = False

        branch_name = "then" if result else "else"
        branch = step.get(branch_name, [])

        if not branch:
            logger.debug(f"if: condition={result}, no '{branch_name}' branch")
            return

        logger.info(f"if: condition={result}, executing '{branch_name}' ({len(branch)} steps)")
        for sub_step in branch:
            self._execute_step(sub_step)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _step_summary(step: dict) -> str:
    """One-line summary of a step for dry-run output."""
    action = step["action"]
    if action == "tap":
        pos = step.get("pos", "?")
        target = step.get("target")
        if target:
            return f"pos={pos}, target={target}"
        return f"pos={pos}"
    if action == "swipe":
        return f"{step.get('from')} → {step.get('to')}"
    if action == "wait":
        return f"{step.get('seconds')}s"
    if action == "wait_for":
        return f"target={step.get('target')}, timeout={step.get('timeout', 30)}s"
    if action == "if":
        then_n = len(step.get("then", []))
        else_n = len(step.get("else", []))
        return f"condition={step.get('condition')}, then={then_n} steps, else={else_n} steps"
    return str(step)

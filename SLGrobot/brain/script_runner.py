"""YAML Script Runner — unified script execution engine.

Loads YAML scripts and executes step-by-step actions using a smart target
resolution strategy: text/icon targets call OCR/template-matching directly
(no DOM), while button/red_dot/etc. go through the Screen DOM.

Replaces both the old verb-based QuestScriptRunner and the v1 ScriptRunner.

Script format example::

    name: claim_quest_reward
    pattern: "领取任务奖励"
    description: "领取所有任务奖励"
    steps:
      - action: tap
        pos: [540, 800]
        wait: 1.0
      - action: tap
        target: {type: text, value: "领取", nth: -1}
        region: [0, 1350, 1080, 1500]
        wait: 1.5
        repeat: 10
        optional: true
      - action: ensure_main_city
        max_retries: 10
        wait: 1.5
      - action: find_building
        building: "兵营"
        scroll: true
        max_attempts: 3
        wait: 2.0
      - action: read_text
        region: [400, 900, 600, 960]
        var: "level"
      - action: eval
        var: "next_level"
        expr: "{level} + 1"
      - action: wait_for
        target: {type: text, value: "升级完成"}
        timeout: 60
      - action: if
        condition:
          exists: {type: text, value: "资源不足"}
        then:
          - action: tap
            pos: [680, 1000]
"""

import ast
import glob
import logging
import math
import operator
import os
import time

import numpy as np
import yaml

logger = logging.getLogger(__name__)


class ScriptAbortError(Exception):
    """Raised when a script encounters an unrecoverable failure."""
    pass


class StepNotReady(Exception):
    """Raised when a step's target is not found (retriable/skippable)."""
    pass


# ---------------------------------------------------------------------------
# Safe expression evaluator (ported from quest_script.py)
# ---------------------------------------------------------------------------

_SAFE_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
}

_SAFE_FUNCS = {"int": int, "str": str, "len": len, "abs": abs}


def _safe_eval(expression: str, variables: dict[str, str]) -> str:
    """Evaluate a simple arithmetic expression with variable substitution.

    Variables are referenced as ``{var_name}`` and substituted before parsing.
    Only arithmetic operators and whitelisted builtins are allowed.

    Returns the result as a string.
    """
    expr = expression
    for name, value in variables.items():
        expr = expr.replace(f"{{{name}}}", value)

    try:
        tree = ast.parse(expr, mode="eval")
    except SyntaxError as e:
        raise ValueError(f"Invalid expression: {expr!r}") from e

    def _eval_node(node):
        if isinstance(node, ast.Expression):
            return _eval_node(node.body)
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float, str)):
                return node.value
            raise ValueError(f"Unsupported constant type: {type(node.value)}")
        if isinstance(node, ast.BinOp):
            op_type = type(node.op)
            if op_type not in _SAFE_OPS:
                raise ValueError(f"Unsupported operator: {op_type.__name__}")
            left = _eval_node(node.left)
            right = _eval_node(node.right)
            return _SAFE_OPS[op_type](left, right)
        if isinstance(node, ast.UnaryOp):
            if isinstance(node.op, ast.USub):
                return -_eval_node(node.operand)
            raise ValueError(f"Unsupported unary op: {type(node.op).__name__}")
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in _SAFE_FUNCS:
                args = [_eval_node(a) for a in node.args]
                return _SAFE_FUNCS[node.func.id](*args)
            raise ValueError("Unsupported function call")
        if isinstance(node, ast.Name):
            if node.id in variables:
                try:
                    return int(variables[node.id])
                except ValueError:
                    return variables[node.id]
            raise ValueError(f"Unknown variable: {node.id}")
        raise ValueError(f"Unsupported AST node: {type(node).__name__}")

    result = _eval_node(tree)
    return str(result)


# ---------------------------------------------------------------------------
# Script loading
# ---------------------------------------------------------------------------

VALID_ACTIONS = {
    "tap", "swipe", "wait", "wait_for", "if",
    "ensure_main_city", "ensure_world_map",
    "find_building", "read_text", "eval",
}
VALID_TARGET_TYPES = {
    "button", "text", "icon", "primary_button",
    "red_dot", "green_check", "finger",
}
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
        for j, sub in enumerate(step["then"]):
            _validate_step(sub, f"{path}.then[{j}]")
        if "else" in step:
            for j, sub in enumerate(step["else"]):
                _validate_step(sub, f"{path}.else[{j}]")

    elif action == "find_building":
        if "building" not in step:
            raise ValueError(f"{path}: find_building requires 'building'")

    elif action == "read_text":
        if "region" not in step:
            raise ValueError(f"{path}: read_text requires 'region'")
        if "var" not in step:
            raise ValueError(f"{path}: read_text requires 'var'")

    elif action == "eval":
        if "var" not in step:
            raise ValueError(f"{path}: eval requires 'var'")
        if "expr" not in step:
            raise ValueError(f"{path}: eval requires 'expr'")


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

    for region in ("top_bar", "center", "bottom_bar"):
        items = screen.get(region)
        if items:
            elements.extend(items)

    popup = screen.get("popup")
    if popup and "children" in popup:
        elements.extend(popup["children"])

    return elements


def find_element(dom: dict, target: dict, nth: int = 1) -> dict | None:
    """Find a DOM element matching the target descriptor.

    Target format:
        {type: "button", text: "升级"}
        {type: "text", value: "升级完成"}
        {type: "icon", name: "search"}
        {type: "red_dot"}

    Args:
        dom: Screen DOM dict.
        target: Target descriptor.
        nth: Which match to return (1-indexed, -1 for last). Default 1.

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

    # Sort by reading order (top-to-bottom)
    matches.sort(key=lambda e: (e["pos"][1], e["pos"][0]))

    if nth > 0:
        if nth > len(matches):
            return None
        return matches[nth - 1]
    else:
        # Negative index: -1 = last
        try:
            return matches[nth]
        except IndexError:
            return None


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

# Scene detection constants (mirrored from QuestScriptRunner)
_SCENE_CORNER = (0.78, 0.85, 1.0, 1.0)
_SCENE_CONFIDENCE = 0.5


class ScriptRunner:
    """Execute YAML scripts step-by-step using ADB + smart target resolution.

    For ``target.type=text`` and ``target.type=icon``, calls OCR/template
    matching directly (no DOM construction) for performance.  Other target
    types fall through to the Screen DOM.

    Args:
        adb: ADBController for tap/swipe actions.
        dom_builder: ScreenDOMBuilder for building DOM from screenshots.
        screenshot_fn: Callable that returns a BGR numpy screenshot.
        ocr_locator: Optional OCRLocator for direct text search.
        template_matcher: Optional TemplateMatcher for direct icon search.
        building_finder: Optional BuildingFinder for find_building action.
    """

    def __init__(self, adb, dom_builder, screenshot_fn,
                 ocr_locator=None, template_matcher=None,
                 building_finder=None) -> None:
        self.adb = adb
        self.dom_builder = dom_builder
        self.screenshot_fn = screenshot_fn
        self.ocr_locator = ocr_locator
        self.template_matcher = template_matcher
        self.building_finder = building_finder
        self.variables: dict[str, str] = {}
        self._ensure_retries: int = 0

    def _subst(self, text: str) -> str:
        """Substitute ``{var_name}`` placeholders with variable values."""
        for name, value in self.variables.items():
            text = text.replace(f"{{{name}}}", value)
        return text

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
                repeat = step.get("repeat", 1)
                optional = step.get("optional", False)

                if dry_run:
                    repeat_str = f" x{repeat}" if repeat > 1 else ""
                    opt_str = " (optional)" if optional else ""
                    print(
                        f"  [{i+1}/{len(steps)}] {action}: "
                        f"{_step_summary(step)}{repeat_str}{opt_str}"
                    )
                    continue

                logger.info(
                    f"Step {i+1}/{len(steps)}: {action}: "
                    f"{_step_summary(step)}"
                )
                for r in range(repeat):
                    try:
                        self._execute_step(step)
                    except StepNotReady:
                        if optional:
                            logger.info(
                                f"Step {i+1}: optional, target not found — "
                                f"skipping (repeat {r+1}/{repeat})"
                            )
                            break
                        raise ScriptAbortError(
                            f"Step {i+1} ({action}): target not found"
                        )

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
            "ensure_main_city": self._execute_ensure_main_city,
            "ensure_world_map": self._execute_ensure_world_map,
            "find_building": self._execute_find_building,
            "read_text": self._execute_read_text,
            "eval": self._execute_eval,
        }.get(action)

        if handler is None:
            logger.warning(f"Unknown action: {action}")
            return
        handler(step)

    # -- Target resolution (smart dispatch) --

    def _resolve_target(self, target: dict,
                        screenshot: np.ndarray) -> tuple[int, int] | None:
        """Resolve a target descriptor to (x, y) coordinates.

        Dispatch strategy:
        - text: direct OCR (no DOM)
        - icon: direct template matching (no DOM)
        - primary_button: HSV color detection (no DOM)
        - button/red_dot/green_check/finger: DOM lookup

        Returns (x, y) or None if not found.
        """
        target_type = target.get("type", "")
        nth = target.get("nth", 1)

        if target_type == "text":
            return self._resolve_text_target(target, screenshot, nth)
        elif target_type == "icon":
            return self._resolve_icon_target(target, screenshot, nth)
        elif target_type == "primary_button":
            return self._resolve_primary_button(screenshot)
        else:
            # DOM-based lookup
            dom = self.dom_builder.build(screenshot)
            elem = find_element(dom, target, nth=nth)
            if elem:
                return tuple(elem["pos"])
            return None

    def _resolve_text_target(self, target: dict,
                             screenshot: np.ndarray,
                             nth: int = 1) -> tuple[int, int] | None:
        """Resolve text target via direct OCR (no DOM construction)."""
        if not self.ocr_locator:
            # Fallback to DOM
            dom = self.dom_builder.build(screenshot)
            elem = find_element(dom, target, nth=nth)
            return tuple(elem["pos"]) if elem else None

        search_text = self._subst(target.get("value", ""))
        region = target.get("region")

        if region:
            rx1, ry1, rx2, ry2 = (
                int(region[0]), int(region[1]),
                int(region[2]), int(region[3])
            )
            h, w = screenshot.shape[:2]
            rx1, ry1 = max(0, rx1), max(0, ry1)
            rx2, ry2 = min(w, rx2), min(h, ry2)
            crop = screenshot[ry1:ry2, rx1:rx2]
            all_results = self.ocr_locator.find_all_text(crop)
            for r in all_results:
                r.center = (r.center[0] + rx1, r.center[1] + ry1)
                r.bbox = (r.bbox[0] + rx1, r.bbox[1] + ry1,
                          r.bbox[2] + rx1, r.bbox[3] + ry1)
        else:
            all_results = self.ocr_locator.find_all_text(screenshot)

        target_lower = search_text.lower()
        matches = [r for r in all_results if target_lower in r.text.lower()]
        matches.sort(key=lambda r: (r.center[1], r.center[0]))

        if not matches:
            return None
        if nth > 0 and nth > len(matches):
            return None

        match = matches[nth - 1] if nth > 0 else matches[nth]
        cx, cy = match.center
        return (cx, cy)

    def _resolve_icon_target(self, target: dict,
                             screenshot: np.ndarray,
                             nth: int = 1) -> tuple[int, int] | None:
        """Resolve icon target via direct template matching (no DOM)."""
        if not self.template_matcher:
            dom = self.dom_builder.build(screenshot)
            elem = find_element(dom, target, nth=nth)
            return tuple(elem["pos"]) if elem else None

        icon_name = self._subst(target.get("name", ""))
        matches = self.template_matcher.match_one_multi(screenshot, icon_name)

        if not matches:
            return None
        if nth > 0 and nth > len(matches):
            return None

        match = matches[nth - 1] if nth > 0 else matches[nth]
        return (match.x, match.y)

    def _resolve_primary_button(
        self, screenshot: np.ndarray
    ) -> tuple[int, int] | None:
        """Resolve primary_button target via HSV color detection."""
        from vision.element_detector import find_primary_button
        result = find_primary_button(screenshot)
        if result is None:
            return None
        return (result.x, result.y)

    # -- Action handlers --

    def _execute_tap(self, step: dict) -> None:
        """Tap at pos or resolved target.

        Raises StepNotReady if target specified but not found.
        """
        pos = step.get("pos")
        target = step.get("target")
        wait = step.get("wait", 0.5)

        if target:
            screenshot = self.screenshot_fn()
            # Support step-level region override on target
            resolved_target = dict(target)
            if "region" in step and "region" not in resolved_target:
                resolved_target["region"] = step["region"]
            resolved = self._resolve_target(resolved_target, screenshot)
            if resolved is None:
                raise StepNotReady(f"target not found: {target}")
            x, y = resolved
            # Apply offsets
            x += step.get("offset_x", 0)
            y += step.get("offset_y", 0)
        elif pos:
            x, y = int(pos[0]), int(pos[1])
        else:
            raise ScriptAbortError("tap: no 'pos' or 'target'")

        self.adb.tap(x, y)
        logger.info(f"  → tap ({x}, {y})")
        time.sleep(wait)

    def _execute_swipe(self, step: dict) -> None:
        """Execute a swipe action."""
        x1, y1 = step["from"]
        x2, y2 = step["to"]
        duration = step.get("duration_ms", 300)
        wait = step.get("wait", 0.5)

        self.adb.swipe(x1, y1, x2, y2, duration)
        logger.info(f"  → swipe ({x1},{y1}) → ({x2},{y2}) {duration}ms")
        time.sleep(wait)

    def _execute_wait(self, step: dict) -> None:
        """Sleep for a specified duration."""
        seconds = step["seconds"]
        logger.info(f"  → wait {seconds}s")
        time.sleep(seconds)

    def _execute_wait_for(self, step: dict) -> None:
        """Poll until target element appears or timeout.

        Uses direct OCR for text targets (no DOM construction).
        Raises ScriptAbortError on timeout.
        """
        target = step["target"]
        timeout = step.get("timeout", 30)
        poll_interval = step.get("poll_interval", 2)

        deadline = time.time() + timeout
        logger.info(f"wait_for: looking for {target} (timeout={timeout}s)")

        while time.time() < deadline:
            screenshot = self.screenshot_fn()
            resolved = self._resolve_target(target, screenshot)
            if resolved is not None:
                logger.info(f"wait_for: found target at {resolved}")
                return
            time.sleep(poll_interval)

        raise ScriptAbortError(f"wait_for timeout ({timeout}s): {target}")

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

        logger.info(
            f"if: condition={result}, executing '{branch_name}' "
            f"({len(branch)} steps)"
        )
        for sub_step in branch:
            self._execute_step(sub_step)

    # -- Scene detection helpers (ported from QuestScriptRunner) --

    def _crop_corner(self, screenshot: np.ndarray) -> np.ndarray:
        """Crop the bottom-right corner for main_city/world_map detection."""
        h, w = screenshot.shape[:2]
        rx1, ry1, rx2, ry2 = _SCENE_CORNER
        return screenshot[int(ry1*h):int(ry2*h), int(rx1*w):int(rx2*w)]

    def _is_main_city(self, screenshot: np.ndarray) -> bool:
        """Check if screenshot shows main city (bottom-right 'world' icon)."""
        if not self.template_matcher:
            return False
        corner = self._crop_corner(screenshot)
        match = self.template_matcher.match_one(corner, "world")
        return match is not None and match.confidence >= _SCENE_CONFIDENCE

    def _is_world_map(self, screenshot: np.ndarray) -> bool:
        """Check if screenshot shows world map (bottom-right 'territory' icon)."""
        if not self.template_matcher:
            return False
        corner = self._crop_corner(screenshot)
        match = self.template_matcher.match_one(corner, "territory")
        return match is not None and match.confidence >= _SCENE_CONFIDENCE

    def _execute_ensure_main_city(self, step: dict) -> None:
        """Navigate to main city with retry logic.

        Takes screenshots and taps navigation elements until the main city
        scene is detected, or aborts after max_retries.
        """
        max_retries = step.get("max_retries", 10)
        wait = step.get("wait", 1.5)
        self._ensure_retries = 0

        while True:
            screenshot = self.screenshot_fn()
            if self._is_main_city(screenshot):
                logger.info("ensure_main_city: at main city")
                self._ensure_retries = 0
                return

            self._ensure_retries += 1
            if self._ensure_retries > max_retries:
                raise ScriptAbortError(
                    f"ensure_main_city failed after {max_retries} retries"
                )

            # If on world_map, tap territory icon
            if self._is_world_map(screenshot):
                match = self.template_matcher.match_one(
                    screenshot, "territory"
                )
                if match:
                    logger.info(
                        f"ensure_main_city: on world_map, tapping territory "
                        f"({match.x}, {match.y}), attempt {self._ensure_retries}"
                    )
                    self.adb.tap(match.x, match.y)
                    time.sleep(wait)
                    continue

            # Try back_arrow
            if self.template_matcher:
                match = self.template_matcher.match_one(
                    screenshot, "back_arrow"
                )
                if match:
                    logger.info(
                        f"ensure_main_city: tapping back_arrow "
                        f"({match.x}, {match.y}), attempt {self._ensure_retries}"
                    )
                    self.adb.tap(match.x, match.y)
                    time.sleep(wait)
                    continue

            # Try close_x
            if self.template_matcher:
                match = self.template_matcher.match_one(
                    screenshot, "close_x"
                )
                if match:
                    logger.info(
                        f"ensure_main_city: tapping close_x "
                        f"({match.x}, {match.y}), attempt {self._ensure_retries}"
                    )
                    self.adb.tap(match.x, match.y)
                    time.sleep(wait)
                    continue

            # Fallback: tap blank area
            blank_y = 600 if self._ensure_retries >= 5 else 100
            logger.info(
                f"ensure_main_city: tapping blank area (500, {blank_y}), "
                f"attempt {self._ensure_retries}"
            )
            self.adb.tap(500, blank_y)
            time.sleep(wait)

    def _execute_ensure_world_map(self, step: dict) -> None:
        """Navigate to world map with retry logic.

        Takes screenshots and taps navigation elements until the world map
        scene is detected, or aborts after max_retries.
        """
        max_retries = step.get("max_retries", 10)
        wait = step.get("wait", 1.5)
        self._ensure_retries = 0

        while True:
            screenshot = self.screenshot_fn()
            if self._is_world_map(screenshot):
                logger.info("ensure_world_map: at world map")
                self._ensure_retries = 0
                return

            self._ensure_retries += 1
            if self._ensure_retries > max_retries:
                raise ScriptAbortError(
                    f"ensure_world_map failed after {max_retries} retries"
                )

            # If on main_city, tap world icon
            if self._is_main_city(screenshot):
                match = self.template_matcher.match_one(screenshot, "world")
                if match:
                    logger.info(
                        f"ensure_world_map: on main_city, tapping world "
                        f"({match.x}, {match.y}), attempt {self._ensure_retries}"
                    )
                    self.adb.tap(match.x, match.y)
                    time.sleep(wait)
                    continue

            # Try back_arrow
            if self.template_matcher:
                match = self.template_matcher.match_one(
                    screenshot, "back_arrow"
                )
                if match:
                    logger.info(
                        f"ensure_world_map: tapping back_arrow "
                        f"({match.x}, {match.y}), attempt {self._ensure_retries}"
                    )
                    self.adb.tap(match.x, match.y)
                    time.sleep(wait)
                    continue

            # Try close_x
            if self.template_matcher:
                match = self.template_matcher.match_one(
                    screenshot, "close_x"
                )
                if match:
                    logger.info(
                        f"ensure_world_map: tapping close_x "
                        f"({match.x}, {match.y}), attempt {self._ensure_retries}"
                    )
                    self.adb.tap(match.x, match.y)
                    time.sleep(wait)
                    continue

            # Fallback: tap blank area
            blank_y = 600 if self._ensure_retries >= 5 else 100
            logger.info(
                f"ensure_world_map: tapping blank area (500, {blank_y}), "
                f"attempt {self._ensure_retries}"
            )
            self.adb.tap(500, blank_y)
            time.sleep(wait)

    def _execute_find_building(self, step: dict) -> None:
        """Find and tap a building on the city map."""
        building_name = self._subst(step["building"])
        scroll = step.get("scroll", True)
        max_attempts = step.get("max_attempts", 3)
        wait = step.get("wait", 2.0)

        if not self.building_finder:
            raise ScriptAbortError(
                "find_building requires building_finder"
            )

        result = self.building_finder.find_and_tap(
            building_name, scroll=scroll, max_attempts=max_attempts
        )
        if not result:
            raise ScriptAbortError(
                f"find_building: '{building_name}' not found"
            )
        logger.info(f"find_building: tapped '{building_name}'")
        time.sleep(wait)

    def _execute_read_text(self, step: dict) -> None:
        """OCR a region and store result in a variable."""
        region = step["region"]
        var_name = step["var"]
        rx1, ry1, rx2, ry2 = (
            int(region[0]), int(region[1]),
            int(region[2]), int(region[3])
        )

        screenshot = self.screenshot_fn()
        h, w = screenshot.shape[:2]
        rx1, ry1 = max(0, rx1), max(0, ry1)
        rx2, ry2 = min(w, rx2), min(h, ry2)
        crop = screenshot[ry1:ry2, rx1:rx2]

        if self.ocr_locator:
            all_text = self.ocr_locator.find_all_text(crop)
            combined = "".join(r.text for r in all_text)
        else:
            combined = ""
            logger.warning("read_text: no ocr_locator available")

        self.variables[var_name] = combined
        logger.info(
            f"read_text: region=[{rx1},{ry1},{rx2},{ry2}] -> "
            f"'{var_name}' = '{combined}'"
        )

    def _execute_eval(self, step: dict) -> None:
        """Evaluate expression and store result in variable."""
        var_name = step["var"]
        expression = step["expr"]

        try:
            result = _safe_eval(expression, self.variables)
            self.variables[var_name] = result
            logger.info(f"eval: '{expression}' -> '{var_name}' = '{result}'")
        except (ValueError, TypeError, ZeroDivisionError) as e:
            logger.warning(f"eval: '{expression}' failed: {e}")
            self.variables[var_name] = ""


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
        return (
            f"target={step.get('target')}, "
            f"timeout={step.get('timeout', 30)}s"
        )
    if action == "if":
        then_n = len(step.get("then", []))
        else_n = len(step.get("else", []))
        return (
            f"condition={step.get('condition')}, "
            f"then={then_n} steps, else={else_n} steps"
        )
    if action == "ensure_main_city":
        return f"max_retries={step.get('max_retries', 10)}"
    if action == "ensure_world_map":
        return f"max_retries={step.get('max_retries', 10)}"
    if action == "find_building":
        return f"building={step.get('building')}"
    if action == "read_text":
        return f"region={step.get('region')}, var={step.get('var')}"
    if action == "eval":
        return f"var={step.get('var')}, expr={step.get('expr')}"
    return str(step)

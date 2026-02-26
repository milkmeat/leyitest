"""Quest Script Runner - Execute multi-step quest scripts defined in JSON.

Each quest script is a list of steps with verb + args.  Supported verbs:

  tap_xy           [x, y]                — unconditional tap at fixed coordinates
  tap_text         [text] or [text, nth] — OCR search, tap nth match (1-indexed)
  tap_icon         [name] or [name, nth] — template match, tap nth match
  swipe            [x1,y1,x2,y2] or [x1,y1,x2,y2,ms] — swipe gesture
  wait_text        [text]                — wait until text appears (no tap)
  ensure_main_city [] or [max_retries]   — navigate to main city or abort
  ensure_world_map [] or [max_retries]   — navigate to world map or abort
  read_text        [x, y, var, ...]      — OCR region, store in variable
  eval             [var, expression]     — safe arithmetic on variables
  find_building    [name] or [name, {options}] — find building on city map and tap

Step fields:
  delay       float, default 1.0   — seconds to wait after action
  repeat      int, default 1       — repeat this step N times
  optional    bool, default False  — if True, skip step when target not found
                                     (instead of waiting/retrying forever)
  description str                  — human-readable label
  region      [x1,y1,x2,y2]      — (tap_text only) restrict OCR matching area
"""

import ast
import logging
import operator
import re

import numpy as np

logger = logging.getLogger(__name__)

# Operators allowed in eval expressions
_SAFE_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
}

# Functions allowed in eval expressions
_SAFE_FUNCS = {"int": int, "str": str, "len": len, "abs": abs}


def _safe_eval(expression: str, variables: dict[str, str]) -> str:
    """Evaluate a simple arithmetic expression with variable substitution.

    Variables are referenced as ``{var_name}`` and substituted before parsing.
    Only arithmetic operators and whitelisted builtins are allowed.

    Returns the result as a string.
    """
    # Substitute variables
    expr = expression
    for name, value in variables.items():
        expr = expr.replace(f"{{{name}}}", value)

    # Parse into AST
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
            raise ValueError(f"Unsupported function call")
        if isinstance(node, ast.Name):
            # Allow bare variable names (without braces) as fallback
            if node.id in variables:
                try:
                    return int(variables[node.id])
                except ValueError:
                    return variables[node.id]
            raise ValueError(f"Unknown variable: {node.id}")
        raise ValueError(f"Unsupported AST node: {type(node).__name__}")

    result = _eval_node(tree)
    return str(result)


class QuestScriptRunner:
    """Execute a list of quest script steps one at a time.

    Each call to ``execute_one()`` processes the current step and returns
    a list of action dicts (or ``None`` if the step is waiting for a
    condition like OCR text to appear).

    Usage::

        runner = QuestScriptRunner(ocr, template_matcher, adb, screenshot_fn)
        runner.load(steps)
        while not runner.is_done():
            screenshot = screenshot_fn()
            actions = runner.execute_one(screenshot)
            if actions:
                for a in actions:
                    action_runner.execute(a)
    """

    def __init__(self, ocr_locator, template_matcher, adb_controller,
                 screenshot_fn=None) -> None:
        """
        Args:
            ocr_locator: OCRLocator instance for text detection.
            template_matcher: TemplateMatcher instance for icon detection.
            adb_controller: ADBController (unused directly, available for
                            future verbs).
            screenshot_fn: Optional callable returning a screenshot ndarray.
        """
        self.ocr = ocr_locator
        self.template_matcher = template_matcher
        self.adb = adb_controller
        self.screenshot_fn = screenshot_fn
        self.variables: dict[str, str] = {}
        self.step_index: int = 0
        self.steps: list[dict] = []
        self._repeat_remaining: int = 0
        self.aborted: bool = False
        self.abort_reason: str = ""
        self._suppress_advance: bool = False
        self._ensure_retries: int = 0

    def _subst(self, text: str) -> str:
        """Substitute ``{var_name}`` placeholders with variable values."""
        for name, value in self.variables.items():
            text = text.replace(f"{{{name}}}", value)
        return text

    def load(self, steps: list[dict]) -> None:
        """Load a new script.  Resets all state."""
        self.steps = list(steps)
        self.step_index = 0
        self._repeat_remaining = 0
        self.variables.clear()
        self.aborted = False
        self.abort_reason = ""
        self._suppress_advance = False
        self._ensure_retries = 0

    def reset(self) -> None:
        """Reset execution state without clearing the loaded steps."""
        self.step_index = 0
        self._repeat_remaining = 0
        self.variables.clear()
        self.aborted = False
        self.abort_reason = ""
        self._suppress_advance = False
        self._ensure_retries = 0

    def is_done(self) -> bool:
        """Return True when all steps have been executed or script aborted."""
        return self.aborted or self.step_index >= len(self.steps)

    def is_aborted(self) -> bool:
        """Return True if the script was aborted due to unrecoverable error."""
        return self.aborted

    @property
    def current_step(self) -> dict | None:
        """Return current step dict, or None if done."""
        if self.is_done():
            return None
        return self.steps[self.step_index]

    def execute_one(self, screenshot: np.ndarray) -> list[dict] | None:
        """Execute the current step against the given screenshot.

        Returns:
            - A list of action dicts to execute (may be empty for no-op
              steps like read_text/eval).
            - ``None`` if the step is waiting (e.g. tap_text target not
              found on screen).  The caller should retry next iteration.
        """
        if self.is_done():
            return None

        step = self.steps[self.step_index]
        delay = step.get("delay", 1.0)
        repeat = step.get("repeat", 1)
        description = step.get("description", "")

        # Initialize repeat counter on first encounter of this step
        if self._repeat_remaining <= 0:
            self._repeat_remaining = repeat

        # Dispatch by verb
        actions: list[dict] | None = None

        if "tap_xy" in step:
            actions = self._do_tap_xy(step, delay, description)
        elif "tap_text" in step:
            actions = self._do_tap_text(step, screenshot, delay, description)
        elif "tap_icon" in step:
            actions = self._do_tap_icon(step, screenshot, delay, description)
        elif "swipe" in step:
            actions = self._do_swipe(step, delay, description)
        elif "wait_text" in step:
            actions = self._do_wait_text(step, screenshot, description)
        elif "ensure_main_city" in step:
            actions = self._do_ensure_main_city(step, screenshot, delay,
                                                description)
        elif "ensure_world_map" in step:
            actions = self._do_ensure_world_map(step, screenshot, delay,
                                                description)
        elif "read_text" in step:
            actions = self._do_read_text(step, screenshot, description)
        elif "eval" in step:
            actions = self._do_eval(step, description)
        elif "find_building" in step:
            actions = self._do_find_building(step, screenshot, delay,
                                             description)
        else:
            logger.warning(
                f"Quest script step {self.step_index}: unknown verb, skipping"
            )
            actions = []

        if actions is None:
            # Step is waiting (e.g. text not found) — don't advance
            if step.get("optional", False):
                # Optional step: not-found means skip (end repeat cycle too)
                logger.info(
                    f"Quest script step {self.step_index}: "
                    f"optional step skipped — {description}"
                )
                self._repeat_remaining = 0
                self.step_index += 1
                return []
            return None

        # Some verbs (ensure_main_city, ensure_world_map) return actions but stay on same step
        if self._suppress_advance:
            self._suppress_advance = False
            return actions

        # Successful execution — decrement repeat counter
        self._repeat_remaining -= 1
        if self._repeat_remaining <= 0:
            self.step_index += 1
            self._repeat_remaining = 0

        logger.info(
            f"Quest script step {self.step_index - (1 if self._repeat_remaining <= 0 else 0)}"
            f"/{len(self.steps)}: {description or step}"
            f" (repeats_left={self._repeat_remaining})"
        )

        return actions

    # -- Verb implementations --

    def _do_tap_xy(self, step: dict, delay: float,
                   description: str) -> list[dict]:
        args = step["tap_xy"]
        x, y = int(args[0]), int(args[1])
        return [{
            "type": "tap",
            "x": x,
            "y": y,
            "delay": delay,
            "reason": f"quest_script:tap_xy:{x},{y}:{description}",
        }]

    def _do_tap_text(self, step: dict, screenshot: np.ndarray,
                     delay: float, description: str) -> list[dict] | None:
        args = step["tap_text"]
        if isinstance(args, str):
            args = [args]
        target_text = self._subst(str(args[0]))
        nth = int(args[1]) if len(args) > 1 else 1

        # Optional region: [x1, y1, x2, y2] — crop screenshot and run
        # a dedicated OCR pass on just that area (better detection for
        # small text).  Coordinates are mapped back to full-screen space.
        region = step.get("region")
        if region:
            rx1, ry1, rx2, ry2 = int(region[0]), int(region[1]), int(region[2]), int(region[3])
            h, w = screenshot.shape[:2]
            rx1, ry1 = max(0, rx1), max(0, ry1)
            rx2, ry2 = min(w, rx2), min(h, ry2)
            crop = screenshot[ry1:ry2, rx1:rx2]
            all_results = self.ocr.find_all_text(crop)
            # Shift coordinates back to full-screen space
            for r in all_results:
                r.center = (r.center[0] + rx1, r.center[1] + ry1)
                r.bbox = (r.bbox[0] + rx1, r.bbox[1] + ry1,
                          r.bbox[2] + rx1, r.bbox[3] + ry1)
        else:
            all_results = self.ocr.find_all_text(screenshot)

        target_lower = target_text.lower()
        matches = [
            r for r in all_results
            if target_lower in r.text.lower()
        ]

        # Sort by reading order (top-to-bottom, left-to-right) so nth
        # indexing is spatially consistent: 1 = first, -1 = last.
        matches.sort(key=lambda r: (r.center[1], r.center[0]))
        if len(matches) > 1:
            logger.debug(
                f"Quest script: tap_text '{target_text}' found {len(matches)} "
                f"matches (sorted): {[(m.text, m.center) for m in matches]}"
            )

        if not matches or (nth > 0 and nth > len(matches)):
            logger.debug(
                f"Quest script: tap_text '{target_text}' not found "
                f"(need #{nth}, got {len(matches)} matches)"
            )
            return None

        # nth=1 means topmost match, -1 means bottommost match
        match = matches[nth - 1] if nth > 0 else matches[nth]
        cx, cy = match.center
        cx += step.get("offset_x", 0)
        cy += step.get("offset_y", 0)
        return [{
            "type": "tap",
            "x": cx,
            "y": cy,
            "delay": delay,
            "reason": f"quest_script:tap_text:{target_text}:{description}",
        }]

    def _do_tap_icon(self, step: dict, screenshot: np.ndarray,
                     delay: float, description: str) -> list[dict] | None:
        args = step["tap_icon"]
        if isinstance(args, str):
            args = [args]
        icon_name = self._subst(str(args[0]))
        nth = int(args[1]) if len(args) > 1 else 1

        matches = self.template_matcher.match_one_multi(screenshot, icon_name)
        if not matches or nth > len(matches):
            logger.debug(
                f"Quest script: tap_icon '{icon_name}' not found "
                f"(need #{nth}, got {len(matches)} matches)"
            )
            return None

        match = matches[nth - 1]
        return [{
            "type": "tap",
            "x": match.x,
            "y": match.y,
            "delay": delay,
            "reason": f"quest_script:tap_icon:{icon_name}:{description}",
        }]

    def _do_swipe(self, step: dict, delay: float,
                  description: str) -> list[dict]:
        args = step["swipe"]
        x1, y1, x2, y2 = int(args[0]), int(args[1]), int(args[2]), int(args[3])
        duration_ms = int(args[4]) if len(args) > 4 else 300
        return [{
            "type": "swipe",
            "x1": x1,
            "y1": y1,
            "x2": x2,
            "y2": y2,
            "duration_ms": duration_ms,
            "delay": delay,
            "reason": (f"quest_script:swipe:{x1},{y1}->{x2},{y2}"
                       f":{description}"),
        }]

    def _do_wait_text(self, step: dict, screenshot: np.ndarray,
                      description: str) -> list[dict] | None:
        args = step["wait_text"]
        if isinstance(args, str):
            args = [args]
        target_text = self._subst(str(args[0]))

        all_results = self.ocr.find_all_text(screenshot)
        target_lower = target_text.lower()
        matches = [
            r for r in all_results
            if target_lower in r.text.lower()
        ]

        if not matches:
            logger.debug(
                f"Quest script: wait_text '{target_text}' not found, waiting"
            )
            return None

        logger.info(
            f"Quest script: wait_text '{target_text}' found — {description}"
        )
        return []  # no action, just advance

    def _do_read_text(self, step: dict, screenshot: np.ndarray,
                      description: str) -> list[dict]:
        args = step["read_text"]
        x, y = int(args[0]), int(args[1])
        var_name = str(args[2])
        w = int(args[3]) if len(args) > 3 else 200
        h = int(args[4]) if len(args) > 4 else 80

        # Crop region centered on (x, y)
        sh, sw = screenshot.shape[:2]
        x1 = max(0, x - w // 2)
        y1 = max(0, y - h // 2)
        x2 = min(sw, x1 + w)
        y2 = min(sh, y1 + h)
        crop = screenshot[y1:y2, x1:x2]

        all_text = self.ocr.find_all_text(crop)
        combined = "".join(r.text for r in all_text)
        self.variables[var_name] = combined

        logger.info(
            f"Quest script: read_text at ({x},{y}) {w}x{h} -> "
            f"'{var_name}' = '{combined}'"
        )
        return []  # no action to execute

    def _do_eval(self, step: dict, description: str) -> list[dict]:
        args = step["eval"]
        var_name = str(args[0])
        expression = str(args[1])

        try:
            result = _safe_eval(expression, self.variables)
            self.variables[var_name] = result
            logger.info(
                f"Quest script: eval '{expression}' -> "
                f"'{var_name}' = '{result}'"
            )
        except (ValueError, TypeError, ZeroDivisionError) as e:
            logger.warning(
                f"Quest script: eval '{expression}' failed: {e}"
            )
            self.variables[var_name] = ""

        return []  # no action to execute

    def _do_find_building(self, step: dict, screenshot: np.ndarray,
                          delay: float,
                          description: str) -> list[dict]:
        """Produce a find_building action for the ActionRunner."""
        args = step["find_building"]
        if isinstance(args, str):
            args = [args]
        building_name = self._subst(str(args[0]))
        options = args[1] if isinstance(args, list) and len(args) > 1 else {}
        if not isinstance(options, dict):
            options = {}

        return [{
            "type": "find_building",
            "building_name": building_name,
            "scroll": options.get("scroll", True),
            "max_attempts": options.get("max_attempts", 3),
            "delay": delay,
            "reason": (f"quest_script:find_building:{building_name}"
                       f":{description}"),
        }]

    # -- Scene detection (mirrors SceneClassifier corner-region logic) --

    _SCENE_CORNER = (0.78, 0.85, 1.0, 1.0)
    _SCENE_CONFIDENCE = 0.5

    def _crop_corner(self, screenshot: np.ndarray) -> np.ndarray:
        """Crop the bottom-right corner used for main_city/world_map detection."""
        h, w = screenshot.shape[:2]
        rx1, ry1, rx2, ry2 = self._SCENE_CORNER
        return screenshot[int(ry1*h):int(ry2*h), int(rx1*w):int(rx2*w)]

    def _is_main_city(self, screenshot: np.ndarray) -> bool:
        """Check if screenshot shows main city (bottom-right corner icon)."""
        corner = self._crop_corner(screenshot)
        match = self.template_matcher.match_one(corner, "scenes/main_city")
        return match is not None and match.confidence >= self._SCENE_CONFIDENCE

    def _is_world_map(self, screenshot: np.ndarray) -> bool:
        """Check if screenshot shows world map (bottom-right corner icon)."""
        corner = self._crop_corner(screenshot)
        match = self.template_matcher.match_one(corner, "scenes/world_map")
        return match is not None and match.confidence >= self._SCENE_CONFIDENCE

    def _do_ensure_main_city(self, step: dict, screenshot: np.ndarray,
                             delay: float,
                             description: str) -> list[dict]:
        """Ensure we are on the main city screen.

        Returns ``[]`` to advance when main city is detected.
        Returns tap actions (with ``_suppress_advance``) to navigate back.
        Sets ``self.aborted`` if max retries exceeded.
        """
        if self._is_main_city(screenshot):
            logger.info(
                f"Quest script: ensure_main_city — at main city"
            )
            self._ensure_retries = 0
            return []  # advance to next step

        args = step.get("ensure_main_city", [])
        if isinstance(args, (int, float)):
            args = [args]
        max_retries = int(args[0]) if args else 10

        self._ensure_retries += 1
        if self._ensure_retries > max_retries:
            self.abort_reason = (
                f"ensure_main_city failed after {max_retries} retries"
            )
            logger.error(f"Quest script: {self.abort_reason}")
            self.aborted = True
            return []

        # Shortcut: if on world_map, tap territory icon to go back to main city
        if self._is_world_map(screenshot):
            match = self.template_matcher.match_one(screenshot,
                                                    "nav_bar/territory")
            if match:
                logger.info(
                    f"Quest script: ensure_main_city — on world_map, "
                    f"tapping territory ({match.x}, {match.y}), "
                    f"attempt {self._ensure_retries}"
                )
                self._suppress_advance = True
                return [{"type": "tap", "x": match.x, "y": match.y,
                         "delay": delay,
                         "reason": "quest_script:ensure_main_city:territory"}]

        # Try back_arrow first
        match = self.template_matcher.match_one(screenshot,
                                                "buttons/back_arrow")
        if match:
            logger.info(
                f"Quest script: ensure_main_city — tapping back_arrow "
                f"({match.x}, {match.y}), attempt {self._ensure_retries}"
            )
            self._suppress_advance = True
            return [{"type": "tap", "x": match.x, "y": match.y,
                     "delay": delay,
                     "reason": f"quest_script:ensure_main_city:back_arrow"}]

        # Try close_x
        match = self.template_matcher.match_one(screenshot,
                                                "buttons/close_x")
        if match:
            logger.info(
                f"Quest script: ensure_main_city — tapping close_x "
                f"({match.x}, {match.y}), attempt {self._ensure_retries}"
            )
            self._suppress_advance = True
            return [{"type": "tap", "x": match.x, "y": match.y,
                     "delay": delay,
                     "reason": f"quest_script:ensure_main_city:close_x"}]

        # After 5 failed attempts, tap blank area in upper screen to dismiss
        if self._ensure_retries >= 5:
            logger.info(
                f"Quest script: ensure_main_city — tapping blank area "
                f"(500, 600), attempt {self._ensure_retries}"
            )
            self._suppress_advance = True
            return [{"type": "tap", "x": 500, "y": 600, "delay": delay,
                     "reason": "quest_script:ensure_main_city:tap_blank"}]

        # Fallback: Android BACK key
        logger.info(
            f"Quest script: ensure_main_city — pressing BACK key, "
            f"attempt {self._ensure_retries}"
        )
        self._suppress_advance = True
        return [{"type": "key_event", "keycode": 4, "delay": delay,
                 "reason": f"quest_script:ensure_main_city:back_key"}]

    def _do_ensure_world_map(self, step: dict, screenshot: np.ndarray,
                             delay: float,
                             description: str) -> list[dict]:
        """Ensure we are on the world map screen.

        Returns ``[]`` to advance when world map is detected.
        Returns tap actions (with ``_suppress_advance``) to navigate there.
        Sets ``self.aborted`` if max retries exceeded.
        """
        if self._is_world_map(screenshot):
            logger.info(
                f"Quest script: ensure_world_map — at world map"
            )
            self._ensure_retries = 0
            return []  # advance to next step

        args = step.get("ensure_world_map", [])
        if isinstance(args, (int, float)):
            args = [args]
        max_retries = int(args[0]) if args else 10

        self._ensure_retries += 1
        if self._ensure_retries > max_retries:
            self.abort_reason = (
                f"ensure_world_map failed after {max_retries} retries"
            )
            logger.error(f"Quest script: {self.abort_reason}")
            self.aborted = True
            return []

        # Shortcut: if on main_city, tap world icon to switch to world map
        if self._is_main_city(screenshot):
            match = self.template_matcher.match_one(screenshot,
                                                    "nav_bar/world")
            if match:
                logger.info(
                    f"Quest script: ensure_world_map — on main_city, "
                    f"tapping world ({match.x}, {match.y}), "
                    f"attempt {self._ensure_retries}"
                )
                self._suppress_advance = True
                return [{"type": "tap", "x": match.x, "y": match.y,
                         "delay": delay,
                         "reason": "quest_script:ensure_world_map:world"}]

        # Try back_arrow first
        match = self.template_matcher.match_one(screenshot,
                                                "buttons/back_arrow")
        if match:
            logger.info(
                f"Quest script: ensure_world_map — tapping back_arrow "
                f"({match.x}, {match.y}), attempt {self._ensure_retries}"
            )
            self._suppress_advance = True
            return [{"type": "tap", "x": match.x, "y": match.y,
                     "delay": delay,
                     "reason": "quest_script:ensure_world_map:back_arrow"}]

        # Try close_x
        match = self.template_matcher.match_one(screenshot,
                                                "buttons/close_x")
        if match:
            logger.info(
                f"Quest script: ensure_world_map — tapping close_x "
                f"({match.x}, {match.y}), attempt {self._ensure_retries}"
            )
            self._suppress_advance = True
            return [{"type": "tap", "x": match.x, "y": match.y,
                     "delay": delay,
                     "reason": "quest_script:ensure_world_map:close_x"}]

        # After 5 failed attempts, tap blank area in upper screen to dismiss
        if self._ensure_retries >= 5:
            logger.info(
                f"Quest script: ensure_world_map — tapping blank area "
                f"(500, 600), attempt {self._ensure_retries}"
            )
            self._suppress_advance = True
            return [{"type": "tap", "x": 500, "y": 600, "delay": delay,
                     "reason": "quest_script:ensure_world_map:tap_blank"}]

        # Fallback: Android BACK key
        logger.info(
            f"Quest script: ensure_world_map — pressing BACK key, "
            f"attempt {self._ensure_retries}"
        )
        self._suppress_advance = True
        return [{"type": "key_event", "keycode": 4, "delay": delay,
                 "reason": "quest_script:ensure_world_map:back_key"}]

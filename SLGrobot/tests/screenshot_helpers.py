"""Screenshot test helpers — pipeline init + assertion logic.

Builds the DOM pipeline (ScreenDOMBuilder + AutoHandler) offline from saved
PNG screenshots and validates results against expected YAML specs.
"""

import os
import re
import sys
from dataclasses import dataclass, field

import cv2
import numpy as np
import yaml

# Add project root to path so we can import project modules
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from game_profile import load_game_profile
from vision.ocr_locator import OCRLocator
from vision.template_matcher import TemplateMatcher
from vision.grid_overlay import GridOverlay
from vision.element_detector import ElementDetector
from vision.screen_dom import ScreenDOMBuilder
from brain.finger_detector import FingerDetector
from brain.auto_handler import AutoHandler
from brain.script_runner import _flatten_elements


@dataclass
class CaseResult:
    """Result of running one test case."""
    name: str
    passed: bool
    errors: list[str] = field(default_factory=list)


# Pipeline cache keyed by game_id
_pipeline_cache: dict[str, dict] = {}


def build_pipeline(game_id: str) -> dict:
    """Construct ScreenDOMBuilder + AutoHandler from game profile, no ADB.

    Returns dict with keys: dom_builder, auto_handler, ocr, profile.
    Cached by game_id to avoid reinit per case.
    """
    if game_id in _pipeline_cache:
        return _pipeline_cache[game_id]

    profile = load_game_profile(game_id)
    ocr = OCRLocator(corrections=profile.ocr_corrections)
    tm = TemplateMatcher(profile.template_dir, profile.template_match_threshold or None)
    grid = GridOverlay(profile.grid_cols, profile.grid_rows)
    detector = ElementDetector(tm, ocr, grid)
    finger = FingerDetector(detector, profile)
    dom_builder = ScreenDOMBuilder(ocr, tm, finger, game_profile=profile)
    auto_handler = AutoHandler(game_profile=profile)

    pipeline = {
        "dom_builder": dom_builder,
        "auto_handler": auto_handler,
        "ocr": ocr,
        "profile": profile,
    }
    _pipeline_cache[game_id] = pipeline
    return pipeline


def _match_element(expected: dict, actual: dict) -> bool:
    """Check if an actual DOM element matches an expected element spec."""
    # Type must match exactly
    if expected.get("type") != actual.get("type"):
        return False

    # Optional name match (exact)
    if "name" in expected:
        if expected["name"] != actual.get("name"):
            return False

    # Optional text_match (regex on elem.text)
    if "text_match" in expected:
        text = actual.get("text", "")
        if not re.search(expected["text_match"], text, re.IGNORECASE):
            return False

    # Optional value_match (regex on elem.value)
    if "value_match" in expected:
        value = actual.get("value", "")
        if not re.search(expected["value_match"], value, re.IGNORECASE):
            return False

    # Optional color_match (regex on elem.color)
    if "color_match" in expected:
        color = actual.get("color", "")
        if not re.search(expected["color_match"], color, re.IGNORECASE):
            return False

    # Optional has_red_text (exact boolean match)
    if "has_red_text" in expected:
        if actual.get("has_red_text", False) != expected["has_red_text"]:
            return False

    return True


def run_one_case(pipeline: dict, png_path: str, yaml_path: str) -> CaseResult:
    """Run one screenshot test case.

    1. Load screenshot from PNG
    2. Build DOM
    3. Assert scene, required/forbidden elements, auto_action
    """
    case_name = os.path.splitext(os.path.basename(yaml_path))[0]
    errors = []

    # Load expected
    with open(yaml_path, "r", encoding="utf-8") as f:
        expected = yaml.safe_load(f)

    # Load screenshot
    screenshot = cv2.imread(png_path)
    if screenshot is None:
        return CaseResult(case_name, False, [f"Failed to load PNG: {png_path}"])

    # Build DOM
    ocr = pipeline["ocr"]
    dom_builder = pipeline["dom_builder"]
    auto_handler = pipeline["auto_handler"]

    ocr.set_frame(screenshot)
    dom = dom_builder.build(screenshot)

    # 1. Check scene
    actual_scene = dom.get("screen", {}).get("scene", "unknown")
    expected_scene = expected.get("scene")
    if expected_scene and actual_scene != expected_scene:
        errors.append(
            f"Scene mismatch: expected '{expected_scene}', got '{actual_scene}'"
        )

    # 2. Check required elements
    all_elements = _flatten_elements(dom)
    for req in expected.get("required_elements", []):
        found = any(_match_element(req, elem) for elem in all_elements)
        if not found:
            errors.append(f"Required element not found: {req}")

    # 3. Check forbidden elements
    for forb in expected.get("forbidden_elements", []):
        found = any(_match_element(forb, elem) for elem in all_elements)
        if found:
            errors.append(f"Forbidden element found: {forb}")

    # 4. Check auto_action
    expected_action = expected.get("auto_action", "SKIP")
    if expected_action != "SKIP":
        action = auto_handler.get_action(dom)

        if expected_action is None:
            # Expect no action
            if action is not None:
                errors.append(
                    f"Expected no action, got: {action}"
                )
        else:
            if action is None:
                errors.append(
                    f"Expected action type='{expected_action.get('type')}', "
                    f"got None"
                )
            else:
                # Check action type
                if "type" in expected_action:
                    if action.get("type") != expected_action["type"]:
                        errors.append(
                            f"Action type mismatch: expected "
                            f"'{expected_action['type']}', "
                            f"got '{action.get('type')}'"
                        )

                # Check reason_match (regex)
                if "reason_match" in expected_action:
                    reason = action.get("reason", "")
                    if not re.search(expected_action["reason_match"], reason):
                        errors.append(
                            f"Action reason mismatch: expected pattern "
                            f"'{expected_action['reason_match']}', "
                            f"got '{reason}'"
                        )

                # Check x/y with tolerance
                tolerance = expected_action.get("tolerance", 50)
                if "x" in expected_action:
                    dx = abs(action.get("x", 0) - expected_action["x"])
                    if dx > tolerance:
                        errors.append(
                            f"Action x mismatch: expected "
                            f"{expected_action['x']}±{tolerance}, "
                            f"got {action.get('x')}"
                        )
                if "y" in expected_action:
                    dy = abs(action.get("y", 0) - expected_action["y"])
                    if dy > tolerance:
                        errors.append(
                            f"Action y mismatch: expected "
                            f"{expected_action['y']}±{tolerance}, "
                            f"got {action.get('y')}"
                        )

    return CaseResult(case_name, len(errors) == 0, errors)

"""Script Runner Tests — unit tests for the unified YAML ScriptRunner.

Covers: variable substitution, repeat/optional, target resolution (text/icon),
ensure_main_city/ensure_world_map, find_building, read_text, eval, tap,
YAML loading, and full script integration flows.
"""

import os
import unittest
from unittest.mock import MagicMock, patch, call
from dataclasses import dataclass

import numpy as np

from brain.script_runner import (
    ScriptRunner, ScriptAbortError, StepNotReady,
    load_script, list_scripts, _safe_eval, _validate_script,
    find_element,
)


def _make_screenshot(h=1920, w=1080):
    """Create a blank BGR screenshot."""
    return np.zeros((h, w, 3), dtype=np.uint8)


@dataclass
class FakeOCRResult:
    text: str
    confidence: float
    bbox: tuple[int, int, int, int]
    center: tuple[int, int]


@dataclass
class FakeMatchResult:
    template_name: str
    confidence: float
    x: int
    y: int
    bbox: tuple[int, int, int, int]


def _make_runner(**kwargs):
    """Create a ScriptRunner with mocked dependencies."""
    adb = MagicMock()
    dom_builder = MagicMock()
    screenshot_fn = MagicMock(return_value=_make_screenshot())
    ocr = kwargs.get("ocr_locator", MagicMock())
    tm = kwargs.get("template_matcher", MagicMock())
    bf = kwargs.get("building_finder", MagicMock())

    runner = ScriptRunner(
        adb=adb,
        dom_builder=dom_builder,
        screenshot_fn=screenshot_fn,
        ocr_locator=ocr,
        template_matcher=tm,
        building_finder=bf,
    )
    return runner, adb, ocr, tm, bf, screenshot_fn


# ---------------------------------------------------------------------------
# Safe eval tests
# ---------------------------------------------------------------------------

class TestSafeEval(unittest.TestCase):
    def test_basic_arithmetic(self):
        assert _safe_eval("3 + 4", {}) == "7"

    def test_variable_substitution(self):
        assert _safe_eval("{x} + 1", {"x": "5"}) == "6"

    def test_multiple_variables(self):
        result = _safe_eval("{a} + {b}", {"a": "10", "b": "20"})
        assert result == "30"

    def test_invalid_expression(self):
        with self.assertRaises(ValueError):
            _safe_eval("import os", {})


# ---------------------------------------------------------------------------
# Validation tests
# ---------------------------------------------------------------------------

class TestValidation(unittest.TestCase):
    def test_valid_tap_pos(self):
        _validate_script({
            "name": "test",
            "steps": [{"action": "tap", "pos": [100, 200]}]
        })

    def test_valid_tap_target(self):
        _validate_script({
            "name": "test",
            "steps": [{"action": "tap", "target": {"type": "text", "value": "ok"}}]
        })

    def test_invalid_action(self):
        with self.assertRaises(ValueError):
            _validate_script({
                "name": "test",
                "steps": [{"action": "invalid_action"}]
            })

    def test_tap_missing_pos_and_target(self):
        with self.assertRaises(ValueError):
            _validate_script({
                "name": "test",
                "steps": [{"action": "tap"}]
            })

    def test_valid_ensure_main_city(self):
        _validate_script({
            "name": "test",
            "steps": [{"action": "ensure_main_city"}]
        })

    def test_valid_find_building(self):
        _validate_script({
            "name": "test",
            "steps": [{"action": "find_building", "building": "兵营"}]
        })

    def test_find_building_missing_name(self):
        with self.assertRaises(ValueError):
            _validate_script({
                "name": "test",
                "steps": [{"action": "find_building"}]
            })

    def test_valid_read_text(self):
        _validate_script({
            "name": "test",
            "steps": [{"action": "read_text", "region": [0, 0, 100, 100], "var": "x"}]
        })

    def test_valid_eval(self):
        _validate_script({
            "name": "test",
            "steps": [{"action": "eval", "var": "x", "expr": "1 + 1"}]
        })


# ---------------------------------------------------------------------------
# Tap tests
# ---------------------------------------------------------------------------

class TestTapPos(unittest.TestCase):
    def test_tap_fixed_pos(self):
        runner, adb, *_ = _make_runner()
        script = {
            "name": "test",
            "steps": [{"action": "tap", "pos": [100, 200], "wait": 0.0}]
        }
        ok = runner.run(script)
        assert ok
        adb.tap.assert_called_once_with(100, 200)

    def test_tap_repeat(self):
        runner, adb, *_ = _make_runner()
        script = {
            "name": "test",
            "steps": [{"action": "tap", "pos": [100, 200], "wait": 0.0, "repeat": 3}]
        }
        ok = runner.run(script)
        assert ok
        assert adb.tap.call_count == 3


class TestTapTextTarget(unittest.TestCase):
    def test_tap_text_found(self):
        runner, adb, ocr, *_ = _make_runner()
        ocr.find_all_text.return_value = [
            FakeOCRResult("开始战斗", 0.9, (300, 1000, 500, 1050), (400, 1025))
        ]
        script = {
            "name": "test",
            "steps": [{
                "action": "tap",
                "target": {"type": "text", "value": "开始战斗"},
                "wait": 0.0,
            }]
        }
        ok = runner.run(script)
        assert ok
        adb.tap.assert_called_once_with(400, 1025)

    def test_tap_text_not_found_non_optional(self):
        runner, adb, ocr, *_ = _make_runner()
        ocr.find_all_text.return_value = []
        script = {
            "name": "test",
            "steps": [{
                "action": "tap",
                "target": {"type": "text", "value": "不存在"},
                "wait": 0.0,
            }]
        }
        ok = runner.run(script)
        assert not ok  # Should abort

    def test_tap_text_not_found_optional(self):
        runner, adb, ocr, *_ = _make_runner()
        ocr.find_all_text.return_value = []
        script = {
            "name": "test",
            "steps": [{
                "action": "tap",
                "target": {"type": "text", "value": "不存在"},
                "wait": 0.0,
                "optional": True,
            }]
        }
        ok = runner.run(script)
        assert ok  # Optional skipped
        adb.tap.assert_not_called()

    def test_tap_text_nth_last(self):
        """nth=-1 selects the last match."""
        runner, adb, ocr, *_ = _make_runner()
        ocr.find_all_text.return_value = [
            FakeOCRResult("领取", 0.9, (800, 400, 900, 440), (850, 420)),
            FakeOCRResult("领取", 0.9, (800, 600, 900, 640), (850, 620)),
            FakeOCRResult("领取", 0.9, (800, 800, 900, 840), (850, 820)),
        ]
        script = {
            "name": "test",
            "steps": [{
                "action": "tap",
                "target": {"type": "text", "value": "领取", "nth": -1},
                "wait": 0.0,
            }]
        }
        ok = runner.run(script)
        assert ok
        adb.tap.assert_called_once_with(850, 820)

    def test_tap_text_nth_positive(self):
        """nth=2 selects the second match."""
        runner, adb, ocr, *_ = _make_runner()
        ocr.find_all_text.return_value = [
            FakeOCRResult("领取", 0.9, (800, 400, 900, 440), (850, 420)),
            FakeOCRResult("领取", 0.9, (800, 600, 900, 640), (850, 620)),
            FakeOCRResult("领取", 0.9, (800, 800, 900, 840), (850, 820)),
        ]
        script = {
            "name": "test",
            "steps": [{
                "action": "tap",
                "target": {"type": "text", "value": "领取", "nth": 2},
                "wait": 0.0,
            }]
        }
        ok = runner.run(script)
        assert ok
        adb.tap.assert_called_once_with(850, 620)

    def test_tap_text_with_region(self):
        """Region restricts OCR to a sub-area of the screen."""
        runner, adb, ocr, *_ = _make_runner()
        # OCR on cropped image returns relative coords
        ocr.find_all_text.return_value = [
            FakeOCRResult("搜索", 0.9, (200, 10, 300, 40), (250, 25))
        ]
        script = {
            "name": "test",
            "steps": [{
                "action": "tap",
                "target": {"type": "text", "value": "搜索", "nth": -1},
                "region": [0, 1350, 1080, 1500],
                "wait": 0.0,
            }]
        }
        ok = runner.run(script)
        assert ok
        # Coordinates should be offset by region origin
        call_args = adb.tap.call_args[0]
        assert call_args[0] == 250  # x offset by rx1=0
        assert call_args[1] == 1375  # y offset by ry1=1350

    def test_tap_text_with_offset(self):
        runner, adb, ocr, *_ = _make_runner()
        ocr.find_all_text.return_value = [
            FakeOCRResult("升级", 0.9, (400, 900, 500, 940), (450, 920))
        ]
        script = {
            "name": "test",
            "steps": [{
                "action": "tap",
                "target": {"type": "text", "value": "升级"},
                "offset_y": 10,
                "wait": 0.0,
            }]
        }
        ok = runner.run(script)
        assert ok
        adb.tap.assert_called_once_with(450, 930)


class TestTapIconTarget(unittest.TestCase):
    def test_tap_icon_found(self):
        runner, adb, _, tm, *_ = _make_runner()
        tm.match_one_multi.return_value = [
            FakeMatchResult("close_x", 0.9, 1020, 200, (990, 170, 1050, 230))
        ]
        script = {
            "name": "test",
            "steps": [{
                "action": "tap",
                "target": {"type": "icon", "name": "close_x"},
                "wait": 0.0,
            }]
        }
        ok = runner.run(script)
        assert ok
        adb.tap.assert_called_once_with(1020, 200)

    def test_tap_icon_not_found(self):
        runner, adb, _, tm, *_ = _make_runner()
        tm.match_one_multi.return_value = []
        script = {
            "name": "test",
            "steps": [{
                "action": "tap",
                "target": {"type": "icon", "name": "missing"},
                "wait": 0.0,
            }]
        }
        ok = runner.run(script)
        assert not ok

    def test_tap_icon_nth(self):
        runner, adb, _, tm, *_ = _make_runner()
        tm.match_one_multi.return_value = [
            FakeMatchResult("arrow", 0.9, 100, 100, (80, 80, 120, 120)),
            FakeMatchResult("arrow", 0.85, 200, 200, (180, 180, 220, 220)),
        ]
        script = {
            "name": "test",
            "steps": [{
                "action": "tap",
                "target": {"type": "icon", "name": "arrow", "nth": 2},
                "wait": 0.0,
            }]
        }
        ok = runner.run(script)
        assert ok
        adb.tap.assert_called_once_with(200, 200)


class TestTapPrimaryButton(unittest.TestCase):
    @patch("vision.element_detector.find_primary_button")
    def test_primary_button_found(self, mock_find):
        mock_find.return_value = FakeMatchResult("btn", 0.9, 540, 1500, (400, 1400, 680, 1600))
        runner, adb, *_ = _make_runner()
        script = {
            "name": "test",
            "steps": [{
                "action": "tap",
                "target": {"type": "primary_button"},
                "wait": 0.0,
            }]
        }
        ok = runner.run(script)
        assert ok
        adb.tap.assert_called_once_with(540, 1500)


# ---------------------------------------------------------------------------
# Repeat + Optional
# ---------------------------------------------------------------------------

class TestRepeatOptional(unittest.TestCase):
    def test_repeat_with_optional_stops_on_not_found(self):
        """repeat=10 + optional=true: stops repeating when target disappears."""
        runner, adb, ocr, *_ = _make_runner()
        call_count = [0]

        def mock_find_all_text(img):
            call_count[0] += 1
            if call_count[0] <= 3:
                return [
                    FakeOCRResult("领取", 0.9, (800, 800, 900, 840), (850, 820))
                ]
            return []

        ocr.find_all_text.side_effect = mock_find_all_text
        script = {
            "name": "test",
            "steps": [{
                "action": "tap",
                "target": {"type": "text", "value": "领取", "nth": -1},
                "wait": 0.0,
                "repeat": 10,
                "optional": True,
            }]
        }
        ok = runner.run(script)
        assert ok
        assert adb.tap.call_count == 3  # Tapped 3 times then stopped


# ---------------------------------------------------------------------------
# Ensure main_city / world_map
# ---------------------------------------------------------------------------

class TestEnsureMainCity(unittest.TestCase):
    def test_already_at_main_city(self):
        runner, adb, _, tm, *rest, screenshot_fn = _make_runner()

        def mock_match_one(img, name):
            if name == "world":
                return FakeMatchResult("world", 0.9, 50, 50, (0, 0, 100, 100))
            return None
        tm.match_one.side_effect = mock_match_one

        script = {
            "name": "test",
            "steps": [
                {"action": "ensure_main_city", "wait": 0.0},
                {"action": "tap", "pos": [100, 200], "wait": 0.0},
            ]
        }
        ok = runner.run(script)
        assert ok
        # Should only tap once (the pos tap, not navigation)
        adb.tap.assert_called_once_with(100, 200)

    def test_navigate_via_back_arrow(self):
        runner, adb, _, tm, *rest, screenshot_fn = _make_runner()
        check_count = [0]

        def mock_match_one(img, name):
            if name == "world":
                check_count[0] += 1
                if check_count[0] >= 3:
                    return FakeMatchResult("world", 0.9, 50, 50, (0, 0, 100, 100))
                return None
            if name == "back_arrow":
                return FakeMatchResult("back_arrow", 0.9, 60, 80, (30, 50, 90, 110))
            return None
        tm.match_one.side_effect = mock_match_one

        script = {
            "name": "test",
            "steps": [{"action": "ensure_main_city", "max_retries": 10, "wait": 0.0}]
        }
        ok = runner.run(script)
        assert ok

    def test_abort_after_max_retries(self):
        runner, adb, _, tm, *rest, screenshot_fn = _make_runner()
        tm.match_one.return_value = None

        script = {
            "name": "test",
            "steps": [{"action": "ensure_main_city", "max_retries": 3, "wait": 0.0}]
        }
        ok = runner.run(script)
        assert not ok  # Should abort

    def test_world_map_shortcut(self):
        """If on world_map, taps territory icon to return to main city."""
        runner, adb, _, tm, *rest, screenshot_fn = _make_runner()
        call_count = [0]

        def mock_match_one(img, name):
            call_count[0] += 1
            if name == "world":
                # 2nd call succeeds (after tapping territory)
                if call_count[0] >= 4:
                    return FakeMatchResult("world", 0.9, 50, 50, (0, 0, 100, 100))
                return None
            if name == "territory":
                return FakeMatchResult("territory", 0.9, 960, 1800, (900, 1750, 1020, 1850))
            return None
        tm.match_one.side_effect = mock_match_one

        script = {
            "name": "test",
            "steps": [{"action": "ensure_main_city", "wait": 0.0}]
        }
        ok = runner.run(script)
        assert ok


class TestEnsureWorldMap(unittest.TestCase):
    def test_already_at_world_map(self):
        runner, adb, _, tm, *rest, screenshot_fn = _make_runner()

        def mock_match_one(img, name):
            if name == "territory":
                return FakeMatchResult("territory", 0.9, 960, 1800, (900, 1750, 1020, 1850))
            return None
        tm.match_one.side_effect = mock_match_one

        script = {
            "name": "test",
            "steps": [{"action": "ensure_world_map", "wait": 0.0}]
        }
        ok = runner.run(script)
        assert ok

    def test_abort_after_max_retries(self):
        runner, adb, _, tm, *rest, screenshot_fn = _make_runner()
        tm.match_one.return_value = None

        script = {
            "name": "test",
            "steps": [{"action": "ensure_world_map", "max_retries": 3, "wait": 0.0}]
        }
        ok = runner.run(script)
        assert not ok


# ---------------------------------------------------------------------------
# find_building
# ---------------------------------------------------------------------------

class TestFindBuilding(unittest.TestCase):
    def test_find_building_success(self):
        runner, adb, _, _, bf, screenshot_fn = _make_runner()
        bf.find_and_tap.return_value = True

        script = {
            "name": "test",
            "steps": [{
                "action": "find_building",
                "building": "兵营",
                "wait": 0.0,
            }]
        }
        ok = runner.run(script)
        assert ok
        bf.find_and_tap.assert_called_once_with("兵营", scroll=True, max_attempts=3)

    def test_find_building_failure(self):
        runner, adb, _, _, bf, screenshot_fn = _make_runner()
        bf.find_and_tap.return_value = False

        script = {
            "name": "test",
            "steps": [{
                "action": "find_building",
                "building": "不存在",
                "wait": 0.0,
            }]
        }
        ok = runner.run(script)
        assert not ok  # Aborted

    def test_find_building_with_variable(self):
        runner, adb, _, _, bf, screenshot_fn = _make_runner()
        bf.find_and_tap.return_value = True
        runner.variables["building"] = "城镇中心"

        script = {
            "name": "test",
            "steps": [{
                "action": "find_building",
                "building": "{building}",
                "wait": 0.0,
            }]
        }
        ok = runner.run(script)
        assert ok
        bf.find_and_tap.assert_called_once_with("城镇中心", scroll=True, max_attempts=3)


# ---------------------------------------------------------------------------
# read_text + eval
# ---------------------------------------------------------------------------

class TestReadTextAndEval(unittest.TestCase):
    def test_read_text_stores_variable(self):
        runner, _, ocr, *_ = _make_runner()
        ocr.find_all_text.return_value = [
            FakeOCRResult("5", 0.9, (440, 770, 640, 830), (540, 800))
        ]
        script = {
            "name": "test",
            "steps": [{
                "action": "read_text",
                "region": [400, 900, 600, 960],
                "var": "level",
            }]
        }
        ok = runner.run(script)
        assert ok
        assert runner.variables["level"] == "5"

    def test_eval_computes_expression(self):
        runner, *_ = _make_runner()
        runner.variables["level"] = "5"
        script = {
            "name": "test",
            "steps": [{
                "action": "eval",
                "var": "next_level",
                "expr": "{level} + 1",
            }]
        }
        ok = runner.run(script)
        assert ok
        assert runner.variables["next_level"] == "6"

    def test_read_text_then_eval(self):
        runner, _, ocr, *_ = _make_runner()
        ocr.find_all_text.return_value = [
            FakeOCRResult("10", 0.9, (440, 770, 640, 830), (540, 800))
        ]
        script = {
            "name": "test",
            "steps": [
                {"action": "read_text", "region": [400, 900, 600, 960], "var": "level"},
                {"action": "eval", "var": "next", "expr": "{level} + 1"},
            ]
        }
        ok = runner.run(script)
        assert ok
        assert runner.variables["level"] == "10"
        assert runner.variables["next"] == "11"


# ---------------------------------------------------------------------------
# Variable substitution
# ---------------------------------------------------------------------------

class TestVariableSubstitution(unittest.TestCase):
    def test_text_target_with_variable(self):
        runner, adb, ocr, *_ = _make_runner()
        runner.variables["resource_type"] = "小麦"
        ocr.find_all_text.return_value = [
            FakeOCRResult("小麦", 0.9, (200, 500, 300, 540), (250, 520))
        ]
        script = {
            "name": "test",
            "steps": [{
                "action": "tap",
                "target": {"type": "text", "value": "{resource_type}"},
                "wait": 0.0,
            }]
        }
        ok = runner.run(script)
        assert ok
        adb.tap.assert_called_once_with(250, 520)


# ---------------------------------------------------------------------------
# wait_for
# ---------------------------------------------------------------------------

class TestWaitFor(unittest.TestCase):
    def test_wait_for_found_immediately(self):
        runner, _, ocr, *_ = _make_runner()
        ocr.find_all_text.return_value = [
            FakeOCRResult("升级完成", 0.9, (300, 800, 500, 840), (400, 820))
        ]
        script = {
            "name": "test",
            "steps": [{
                "action": "wait_for",
                "target": {"type": "text", "value": "升级完成"},
                "timeout": 5,
                "poll_interval": 0.0,
            }]
        }
        ok = runner.run(script)
        assert ok

    def test_wait_for_timeout(self):
        runner, _, ocr, *_ = _make_runner()
        ocr.find_all_text.return_value = []
        script = {
            "name": "test",
            "steps": [{
                "action": "wait_for",
                "target": {"type": "text", "value": "不存在"},
                "timeout": 0.1,
                "poll_interval": 0.01,
            }]
        }
        ok = runner.run(script)
        assert not ok  # Timeout


# ---------------------------------------------------------------------------
# if/else
# ---------------------------------------------------------------------------

class TestIfElse(unittest.TestCase):
    def test_if_then_branch(self):
        runner, adb, *_ = _make_runner()
        runner.dom_builder.build.return_value = {
            "screen": {
                "scene": "popup",
                "top_bar": [],
                "center": [
                    {"type": "text", "value": "资源不足", "pos": [540, 960]},
                ],
                "bottom_bar": [],
            }
        }
        script = {
            "name": "test",
            "steps": [{
                "action": "if",
                "condition": {"exists": {"type": "text", "value": "资源不足"}},
                "then": [
                    {"action": "tap", "pos": [680, 1000], "wait": 0.0}
                ],
                "else": [
                    {"action": "tap", "pos": [400, 1000], "wait": 0.0}
                ],
            }]
        }
        ok = runner.run(script)
        assert ok
        adb.tap.assert_called_once_with(680, 1000)

    def test_if_else_branch(self):
        runner, adb, *_ = _make_runner()
        runner.dom_builder.build.return_value = {
            "screen": {
                "scene": "popup",
                "top_bar": [],
                "center": [],
                "bottom_bar": [],
            }
        }
        script = {
            "name": "test",
            "steps": [{
                "action": "if",
                "condition": {"exists": {"type": "text", "value": "资源不足"}},
                "then": [
                    {"action": "tap", "pos": [680, 1000], "wait": 0.0}
                ],
                "else": [
                    {"action": "tap", "pos": [400, 1000], "wait": 0.0}
                ],
            }]
        }
        ok = runner.run(script)
        assert ok
        adb.tap.assert_called_once_with(400, 1000)


# ---------------------------------------------------------------------------
# YAML loading
# ---------------------------------------------------------------------------

class TestYAMLLoading(unittest.TestCase):
    def test_load_claim_quest_reward(self):
        """Load the claim_quest_reward YAML script and verify structure."""
        script_path = os.path.join(
            os.path.dirname(__file__),
            "games", "westgame2", "scripts", "claim_quest_reward.yaml"
        )
        if not os.path.isfile(script_path):
            self.skipTest(f"Script not found: {script_path}")

        script = load_script(script_path)
        assert script["name"] == "claim_quest_reward"
        assert "pattern" in script
        assert len(script["steps"]) >= 5

    def test_load_all_westgame2_scripts(self):
        """Load all westgame2 YAML scripts and verify they validate."""
        scripts_dir = os.path.join(
            os.path.dirname(__file__),
            "games", "westgame2", "scripts"
        )
        if not os.path.isdir(scripts_dir):
            self.skipTest(f"Scripts dir not found: {scripts_dir}")

        names = list_scripts(scripts_dir)
        assert len(names) >= 6, f"Expected >=6 scripts, got {names}"

        for name in names:
            path = os.path.join(scripts_dir, f"{name}.yaml")
            script = load_script(path)
            assert "name" in script
            assert "steps" in script

    def test_list_scripts(self):
        scripts_dir = os.path.join(
            os.path.dirname(__file__),
            "games", "westgame2", "scripts"
        )
        if not os.path.isdir(scripts_dir):
            self.skipTest(f"Scripts dir not found: {scripts_dir}")

        names = list_scripts(scripts_dir)
        assert "claim_quest_reward" in names
        assert "upgrade_building" in names


# ---------------------------------------------------------------------------
# find_element with nth
# ---------------------------------------------------------------------------

class TestFindElementNth(unittest.TestCase):
    def test_nth_default_first(self):
        dom = {
            "screen": {
                "top_bar": [],
                "center": [
                    {"type": "text", "value": "领取", "pos": [850, 420]},
                    {"type": "text", "value": "领取", "pos": [850, 820]},
                ],
                "bottom_bar": [],
            }
        }
        elem = find_element(dom, {"type": "text", "value": "领取"})
        assert elem is not None
        assert elem["pos"][1] == 420  # First (topmost)

    def test_nth_last(self):
        dom = {
            "screen": {
                "top_bar": [],
                "center": [
                    {"type": "text", "value": "领取", "pos": [850, 420]},
                    {"type": "text", "value": "领取", "pos": [850, 820]},
                ],
                "bottom_bar": [],
            }
        }
        elem = find_element(dom, {"type": "text", "value": "领取"}, nth=-1)
        assert elem is not None
        assert elem["pos"][1] == 820  # Last

    def test_nth_out_of_range(self):
        dom = {
            "screen": {
                "top_bar": [],
                "center": [
                    {"type": "text", "value": "领取", "pos": [850, 420]},
                ],
                "bottom_bar": [],
            }
        }
        elem = find_element(dom, {"type": "text", "value": "领取"}, nth=5)
        assert elem is None


# ---------------------------------------------------------------------------
# Full integration: claim_quest_reward flow
# ---------------------------------------------------------------------------

class TestClaimQuestRewardFlow(unittest.TestCase):
    def test_full_flow(self):
        """Simulates claim_quest_reward with mocked OCR/template matching.

        Script flow:
        1. ensure_main_city  (template_matcher.match_one → world icon)
        2. tap pos [70, 1600]
        3. tap text "章节任务" (optional)
        4. tap text "领取" x10 (optional) — returns 2 then stops
        5. tap text "成长任务" (optional)
        6. tap text "领取" x10 (optional) — returns 0
        7. tap text "每日任务" (optional)
        8. tap text "领取" x10 (optional) — returns 0
        9. tap icon "close_x"
        """
        runner, adb, ocr, tm, _, screenshot_fn = _make_runner()

        # ensure_main_city: always detected as main city
        def mock_match_one(img, name):
            if name == "world":
                return FakeMatchResult("world", 0.9, 50, 50, (0, 0, 100, 100))
            return None
        tm.match_one.side_effect = mock_match_one

        # tap_icon close_x (last step)
        tm.match_one_multi.return_value = [
            FakeMatchResult("close_x", 0.9, 1020, 200, (990, 170, 1050, 230))
        ]

        ocr_call_idx = [0]

        def mock_ocr(img):
            ocr_call_idx[0] += 1
            idx = ocr_call_idx[0]
            # Step 3: "章节任务" (call 1)
            if idx == 1:
                return [FakeOCRResult("章节任务", 0.9, (300, 200, 500, 240), (400, 220))]
            # Step 4: "领取" repeat — calls 2-3 find it, call 4 doesn't
            if idx <= 3:
                return [FakeOCRResult("领取", 0.9, (800, 800, 900, 840), (850, 820))]
            if idx == 4:
                return []  # No more 领取 → optional skips
            # Step 5: "成长任务" (call 5)
            if idx == 5:
                return [FakeOCRResult("成长任务", 0.9, (300, 250, 500, 290), (400, 270))]
            # Step 6: "领取" — not found (call 6)
            if idx == 6:
                return []
            # Step 7: "每日任务" (call 7)
            if idx == 7:
                return [FakeOCRResult("每日任务", 0.9, (300, 300, 500, 340), (400, 320))]
            # Step 8: "领取" — not found
            return []

        ocr.find_all_text.side_effect = mock_ocr

        script_path = os.path.join(
            os.path.dirname(__file__),
            "games", "westgame2", "scripts", "claim_quest_reward.yaml"
        )
        if not os.path.isfile(script_path):
            self.skipTest("claim_quest_reward.yaml not found")

        script = load_script(script_path)
        ok = runner.run(script)
        assert ok
        # Taps: pos[70,1600] + 章节任务 + 2x领取 + 成长任务 + 每日任务 + close_x = 7
        assert adb.tap.call_count == 7, f"Expected 7 taps, got {adb.tap.call_count}"


# ---------------------------------------------------------------------------
# Dry run
# ---------------------------------------------------------------------------

class TestDryRun(unittest.TestCase):
    def test_dry_run_no_adb_calls(self):
        runner, adb, *_ = _make_runner()
        script = {
            "name": "test",
            "steps": [
                {"action": "tap", "pos": [100, 200], "wait": 1.0},
                {"action": "tap", "pos": [300, 400], "wait": 1.0},
            ]
        }
        ok = runner.run(script, dry_run=True)
        assert ok
        adb.tap.assert_not_called()


if __name__ == "__main__":
    unittest.main()

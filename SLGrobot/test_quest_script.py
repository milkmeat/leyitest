"""Quest Script Runner Tests - Unit tests for QuestScriptRunner verbs."""

import unittest
from unittest.mock import MagicMock
from dataclasses import dataclass
import numpy as np

from brain.quest_script import QuestScriptRunner


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


def _make_runner():
    """Create a QuestScriptRunner with mocked dependencies."""
    ocr = MagicMock()
    tm = MagicMock()
    adb = MagicMock()
    runner = QuestScriptRunner(ocr, tm, adb)
    return runner, ocr, tm


class TestWaitText(unittest.TestCase):
    """Tests for the wait_text verb."""

    def test_wait_text_not_found_returns_none(self):
        """wait_text returns None when target text is not on screen."""
        runner, ocr, _ = _make_runner()
        ocr.find_all_text.return_value = []
        runner.load([
            {"wait_text": ["战斗成功"], "description": "等待战斗结束"}
        ])

        result = runner.execute_one(_make_screenshot())
        assert result is None, "Should return None when text not found"
        assert not runner.is_done(), "Should not advance"

    def test_wait_text_found_returns_empty(self):
        """wait_text returns [] and advances when text found."""
        runner, ocr, _ = _make_runner()
        ocr.find_all_text.return_value = [
            FakeOCRResult("战斗成功", 0.95, (300, 800, 500, 850), (400, 825))
        ]
        runner.load([
            {"wait_text": ["战斗成功"], "description": "等待战斗结束"}
        ])

        result = runner.execute_one(_make_screenshot())
        assert result == [], "Should return empty list (no actions)"
        assert runner.is_done(), "Should advance past this step"

    def test_wait_text_partial_match(self):
        """wait_text matches substring (like tap_text does)."""
        runner, ocr, _ = _make_runner()
        ocr.find_all_text.return_value = [
            FakeOCRResult("恭喜！战斗成功！", 0.9, (200, 800, 600, 850), (400, 825))
        ]
        runner.load([
            {"wait_text": ["战斗成功"], "description": "等待战斗结束"}
        ])

        result = runner.execute_one(_make_screenshot())
        assert result == []
        assert runner.is_done()

    def test_wait_text_case_insensitive(self):
        """wait_text matches case-insensitively."""
        runner, ocr, _ = _make_runner()
        ocr.find_all_text.return_value = [
            FakeOCRResult("Victory", 0.9, (200, 800, 400, 850), (300, 825))
        ]
        runner.load([
            {"wait_text": ["victory"], "description": "wait for victory"}
        ])

        result = runner.execute_one(_make_screenshot())
        assert result == []
        assert runner.is_done()

    def test_wait_text_string_arg(self):
        """wait_text accepts a plain string arg (not wrapped in list)."""
        runner, ocr, _ = _make_runner()
        ocr.find_all_text.return_value = [
            FakeOCRResult("战斗成功", 0.95, (300, 800, 500, 850), (400, 825))
        ]
        runner.load([
            {"wait_text": "战斗成功", "description": "plain string arg"}
        ])

        result = runner.execute_one(_make_screenshot())
        assert result == []
        assert runner.is_done()

    def test_wait_text_retry_then_succeed(self):
        """wait_text retries when not found, succeeds when found later."""
        runner, ocr, _ = _make_runner()
        runner.load([
            {"wait_text": ["战斗成功"], "description": "等待战斗结束"},
            {"tap_text": ["返回小镇"], "delay": 1.0, "description": "返回"}
        ])

        # First call: not found
        ocr.find_all_text.return_value = []
        result = runner.execute_one(_make_screenshot())
        assert result is None
        assert runner.step_index == 0

        # Second call: still not found
        result = runner.execute_one(_make_screenshot())
        assert result is None
        assert runner.step_index == 0

        # Third call: found
        ocr.find_all_text.return_value = [
            FakeOCRResult("战斗成功", 0.95, (300, 800, 500, 850), (400, 825))
        ]
        result = runner.execute_one(_make_screenshot())
        assert result == []
        assert runner.step_index == 1  # advanced to next step
        assert not runner.is_done()


class TestTapXY(unittest.TestCase):
    """Tests for the tap_xy verb."""

    def test_tap_xy_basic(self):
        runner, _, _ = _make_runner()
        runner.load([
            {"tap_xy": [100, 200], "delay": 0.5, "description": "test tap"}
        ])
        result = runner.execute_one(_make_screenshot())
        assert len(result) == 1
        assert result[0]["type"] == "tap"
        assert result[0]["x"] == 100
        assert result[0]["y"] == 200
        assert runner.is_done()

    def test_tap_xy_repeat(self):
        runner, _, _ = _make_runner()
        runner.load([
            {"tap_xy": [100, 200], "delay": 0.5, "repeat": 3}
        ])
        for i in range(3):
            assert not runner.is_done()
            result = runner.execute_one(_make_screenshot())
            assert len(result) == 1
        assert runner.is_done()


class TestTapText(unittest.TestCase):
    """Tests for the tap_text verb."""

    def test_tap_text_found(self):
        runner, ocr, _ = _make_runner()
        ocr.find_all_text.return_value = [
            FakeOCRResult("开始战斗", 0.9, (300, 1000, 500, 1050), (400, 1025))
        ]
        runner.load([
            {"tap_text": ["开始战斗"], "delay": 1.0}
        ])
        result = runner.execute_one(_make_screenshot())
        assert len(result) == 1
        assert result[0]["x"] == 400
        assert result[0]["y"] == 1025

    def test_tap_text_not_found(self):
        runner, ocr, _ = _make_runner()
        ocr.find_all_text.return_value = []
        runner.load([
            {"tap_text": ["不存在的文字"], "delay": 1.0}
        ])
        result = runner.execute_one(_make_screenshot())
        assert result is None


class TestTapIcon(unittest.TestCase):
    """Tests for the tap_icon verb."""

    def test_tap_icon_found(self):
        runner, _, tm = _make_runner()
        tm.match_one_multi.return_value = [
            FakeMatchResult("nav_bar/expedition", 0.9, 540, 1850,
                            (490, 1800, 590, 1900))
        ]
        runner.load([
            {"tap_icon": ["nav_bar/expedition"], "delay": 2.0}
        ])
        result = runner.execute_one(_make_screenshot())
        assert len(result) == 1
        assert result[0]["x"] == 540
        assert result[0]["y"] == 1850

    def test_tap_icon_not_found(self):
        runner, _, tm = _make_runner()
        tm.match_one_multi.return_value = []
        runner.load([
            {"tap_icon": ["nav_bar/expedition"], "delay": 2.0}
        ])
        result = runner.execute_one(_make_screenshot())
        assert result is None


class TestExpeditionQuestScript(unittest.TestCase):
    """Integration test for the full pass_one_expedition quest script."""

    def test_expedition_full_flow(self):
        """Run through all 6 steps of the expedition quest."""
        runner, ocr, tm = _make_runner()

        steps = [
            {"tap_icon": ["nav_bar/expedition"], "delay": 2.0,
             "description": "点击远征图标"},
            {"tap_text": ["开始战斗"], "delay": 1.5,
             "description": "点击开始战斗"},
            {"tap_text": ["一键上阵"], "delay": 1.5,
             "description": "点击一键上阵"},
            {"tap_xy": [900, 1870], "delay": 3.0,
             "description": "点击出战按钮"},
            {"wait_text": ["战斗成功"],
             "description": "等待战斗结束，出现战斗成功"},
            {"tap_text": ["返回小镇"], "delay": 1.5,
             "description": "点击返回小镇"},
        ]
        runner.load(steps)
        assert not runner.is_done()

        # Step 1: tap_icon expedition
        tm.match_one_multi.return_value = [
            FakeMatchResult("nav_bar/expedition", 0.9, 540, 1850,
                            (490, 1800, 590, 1900))
        ]
        result = runner.execute_one(_make_screenshot())
        assert result is not None and len(result) == 1
        assert result[0]["x"] == 540
        assert runner.step_index == 1

        # Step 2: tap_text 开始战斗
        ocr.find_all_text.return_value = [
            FakeOCRResult("开始战斗", 0.9, (400, 1000, 600, 1050), (500, 1025))
        ]
        result = runner.execute_one(_make_screenshot())
        assert result is not None and len(result) == 1
        assert runner.step_index == 2

        # Step 3: tap_text 一键上阵
        ocr.find_all_text.return_value = [
            FakeOCRResult("一键上阵", 0.9, (400, 1200, 600, 1250), (500, 1225))
        ]
        result = runner.execute_one(_make_screenshot())
        assert result is not None and len(result) == 1
        assert runner.step_index == 3

        # Step 4: tap_xy 出战按钮
        result = runner.execute_one(_make_screenshot())
        assert result is not None and len(result) == 1
        assert result[0]["x"] == 900
        assert result[0]["y"] == 1870
        assert runner.step_index == 4

        # Step 5: wait_text 战斗成功 — first attempt: not found
        ocr.find_all_text.return_value = []
        result = runner.execute_one(_make_screenshot())
        assert result is None
        assert runner.step_index == 4  # still waiting

        # Step 5: wait_text 战斗成功 — second attempt: found
        ocr.find_all_text.return_value = [
            FakeOCRResult("战斗成功", 0.95, (300, 800, 500, 850), (400, 825))
        ]
        result = runner.execute_one(_make_screenshot())
        assert result == []
        assert runner.step_index == 5

        # Step 6: tap_text 返回小镇
        ocr.find_all_text.return_value = [
            FakeOCRResult("返回小镇", 0.9, (400, 1500, 600, 1550), (500, 1525))
        ]
        result = runner.execute_one(_make_screenshot())
        assert result is not None and len(result) == 1
        assert runner.is_done()


class TestMultiStepScript(unittest.TestCase):
    """Test script with mixed verbs."""

    def test_read_text_and_eval(self):
        runner, ocr, _ = _make_runner()
        runner.load([
            {"read_text": [540, 800, "level", 200, 60],
             "description": "read level"},
            {"eval": ["next_level", "{level} + 1"],
             "description": "calc next"},
        ])

        ocr.find_all_text.return_value = [
            FakeOCRResult("5", 0.9, (440, 770, 640, 830), (540, 800))
        ]
        result = runner.execute_one(_make_screenshot())
        assert result == []
        assert runner.variables["level"] == "5"

        result = runner.execute_one(_make_screenshot())
        assert result == []
        assert runner.variables["next_level"] == "6"
        assert runner.is_done()


if __name__ == "__main__":
    unittest.main()

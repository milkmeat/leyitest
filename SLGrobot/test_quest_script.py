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


class TestEnsureMainCity(unittest.TestCase):
    """Tests for the ensure_main_city verb."""

    def _mock_main_city(self, tm, is_main_city):
        """Configure tm.match_one to return main_city match or None."""
        def mock_match_one(screenshot, name):
            if name == "scenes/main_city" and is_main_city:
                return FakeMatchResult("scenes/main_city", 0.9, 50, 50,
                                       (0, 0, 100, 100))
            return None
        tm.match_one.side_effect = mock_match_one

    def test_already_at_main_city(self):
        """ensure_main_city returns [] and advances when at main city."""
        runner, _, tm = _make_runner()
        self._mock_main_city(tm, True)
        runner.load([
            {"ensure_main_city": [], "description": "确认在主城"},
            {"tap_xy": [100, 200], "delay": 0.5}
        ])
        result = runner.execute_one(_make_screenshot())
        assert result == []
        assert runner.step_index == 1
        assert not runner.is_aborted()

    def test_back_arrow_found(self):
        """Taps back_arrow when not at main city, does not advance."""
        runner, _, tm = _make_runner()
        def mock_match_one(screenshot, name):
            if name == "scenes/main_city":
                return None
            if name == "buttons/back_arrow":
                return FakeMatchResult("buttons/back_arrow", 0.9, 60, 80,
                                       (30, 50, 90, 110))
            return None
        tm.match_one.side_effect = mock_match_one
        runner.load([{"ensure_main_city": [], "delay": 1.0}])
        result = runner.execute_one(_make_screenshot())
        assert len(result) == 1
        assert result[0]["type"] == "tap"
        assert result[0]["x"] == 60
        assert runner.step_index == 0  # did NOT advance
        assert not runner.is_aborted()

    def test_close_x_fallback(self):
        """Taps close_x when no back_arrow found."""
        runner, _, tm = _make_runner()
        def mock_match_one(screenshot, name):
            if name == "buttons/close_x":
                return FakeMatchResult("buttons/close_x", 0.85, 1000, 200,
                                       (970, 170, 1030, 230))
            return None
        tm.match_one.side_effect = mock_match_one
        runner.load([{"ensure_main_city": [], "delay": 1.0}])
        result = runner.execute_one(_make_screenshot())
        assert len(result) == 1
        assert result[0]["type"] == "tap"
        assert result[0]["x"] == 1000
        assert runner.step_index == 0

    def test_back_key_fallback(self):
        """Presses BACK key when no buttons found."""
        runner, _, tm = _make_runner()
        tm.match_one.return_value = None
        runner.load([{"ensure_main_city": [], "delay": 1.0}])
        result = runner.execute_one(_make_screenshot())
        assert len(result) == 1
        assert result[0]["type"] == "key_event"
        assert result[0]["keycode"] == 4
        assert runner.step_index == 0

    def test_abort_after_max_retries(self):
        """Aborts script after max_retries exceeded."""
        runner, _, tm = _make_runner()
        tm.match_one.return_value = None
        runner.load([{"ensure_main_city": [3], "delay": 0.1}])
        # 3 attempts: not aborted yet
        for _ in range(3):
            result = runner.execute_one(_make_screenshot())
            assert not runner.is_aborted()
        # 4th attempt: exceeds max_retries=3
        result = runner.execute_one(_make_screenshot())
        assert runner.is_aborted()
        assert "3 retries" in runner.abort_reason
        assert runner.is_done()

    def test_multi_round_then_success(self):
        """Navigates back over multiple rounds then succeeds."""
        runner, _, tm = _make_runner()
        main_city_check_count = [0]
        def mock_match_one(screenshot, name):
            if name == "scenes/main_city":
                main_city_check_count[0] += 1
                # Succeed on 3rd main_city check
                if main_city_check_count[0] >= 3:
                    return FakeMatchResult("scenes/main_city", 0.9, 50, 50,
                                           (0, 0, 100, 100))
                return None
            if name == "buttons/back_arrow":
                return FakeMatchResult("buttons/back_arrow", 0.9, 60, 80,
                                       (30, 50, 90, 110))
            return None
        tm.match_one.side_effect = mock_match_one
        runner.load([
            {"ensure_main_city": [], "delay": 0.1},
            {"tap_xy": [100, 200], "delay": 0.5}
        ])
        # Round 1-2: tap back_arrow, don't advance
        for _ in range(2):
            result = runner.execute_one(_make_screenshot())
            assert len(result) == 1
            assert runner.step_index == 0
        # Round 3: at main city, advance
        result = runner.execute_one(_make_screenshot())
        assert result == []
        assert runner.step_index == 1
        assert not runner.is_aborted()


class TestExpeditionQuestScript(unittest.TestCase):
    """Integration test for the full pass_one_expedition quest script."""

    def test_expedition_full_flow(self):
        """Run through all 7 steps of the expedition quest."""
        runner, ocr, tm = _make_runner()

        steps = [
            {"ensure_main_city": [], "delay": 1.5,
             "description": "确认在主城界面"},
            {"tap_icon": ["nav_bar/expedition"], "delay": 2.0,
             "description": "点击远征图标"},
            {"tap_text": ["开始战斗"], "delay": 1.5,
             "description": "点击开始战斗"},
            {"tap_text": ["一键上阵"], "delay": 1.5,
             "description": "点击一键上阵"},
            {"tap_xy": [900, 1870], "delay": 3.0,
             "description": "点击出战按钮"},
            {"wait_text": ["返回小镇"],
             "description": "等待战斗结束，出现返回小镇"},
            {"tap_text": ["返回小镇"], "delay": 1.5,
             "description": "点击返回小镇"},
        ]
        runner.load(steps)
        assert not runner.is_done()

        # Step 1: ensure_main_city — mock as already at main city
        tm.match_one.side_effect = lambda ss, name: (
            FakeMatchResult("scenes/main_city", 0.9, 50, 50, (0, 0, 100, 100))
            if name == "scenes/main_city" else None
        )
        result = runner.execute_one(_make_screenshot())
        assert result == []
        assert runner.step_index == 1

        # Step 2: tap_icon expedition
        tm.match_one_multi.return_value = [
            FakeMatchResult("nav_bar/expedition", 0.9, 540, 1850,
                            (490, 1800, 590, 1900))
        ]
        result = runner.execute_one(_make_screenshot())
        assert result is not None and len(result) == 1
        assert result[0]["x"] == 540
        assert runner.step_index == 2

        # Step 3: tap_text 开始战斗
        ocr.find_all_text.return_value = [
            FakeOCRResult("开始战斗", 0.9, (400, 1000, 600, 1050), (500, 1025))
        ]
        result = runner.execute_one(_make_screenshot())
        assert result is not None and len(result) == 1
        assert runner.step_index == 3

        # Step 4: tap_text 一键上阵
        ocr.find_all_text.return_value = [
            FakeOCRResult("一键上阵", 0.9, (400, 1200, 600, 1250), (500, 1225))
        ]
        result = runner.execute_one(_make_screenshot())
        assert result is not None and len(result) == 1
        assert runner.step_index == 4

        # Step 5: tap_xy 出战按钮
        result = runner.execute_one(_make_screenshot())
        assert result is not None and len(result) == 1
        assert result[0]["x"] == 900
        assert result[0]["y"] == 1870
        assert runner.step_index == 5

        # Step 6: wait_text 返回小镇 — first attempt: not found
        ocr.find_all_text.return_value = []
        result = runner.execute_one(_make_screenshot())
        assert result is None
        assert runner.step_index == 5  # still waiting

        # Step 6: wait_text 返回小镇 — second attempt: found
        ocr.find_all_text.return_value = [
            FakeOCRResult("返回小镇", 0.9, (200, 1400, 400, 1450), (300, 1425))
        ]
        result = runner.execute_one(_make_screenshot())
        assert result == []
        assert runner.step_index == 6

        # Step 7: tap_text 返回小镇
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


class TestTapTextNth(unittest.TestCase):
    """Tests for tap_text with nth parameter (selecting specific match)."""

    def test_tap_text_nth_negative_one_selects_last(self):
        """tap_text with nth=-1 taps the LAST matching text."""
        runner, ocr, _ = _make_runner()
        ocr.find_all_text.return_value = [
            FakeOCRResult("领取", 0.9, (800, 400, 900, 440), (850, 420)),
            FakeOCRResult("领取", 0.9, (800, 600, 900, 640), (850, 620)),
            FakeOCRResult("领取", 0.9, (800, 800, 900, 840), (850, 820)),
        ]
        runner.load([
            {"tap_text": ["领取", -1], "delay": 1.0, "description": "tap last"}
        ])
        result = runner.execute_one(_make_screenshot())
        assert len(result) == 1
        assert result[0]["y"] == 820, "Should tap the last (bottom-most) match"

    def test_tap_text_nth_positive_selects_indexed(self):
        """tap_text with nth=2 taps the second match (1-indexed)."""
        runner, ocr, _ = _make_runner()
        ocr.find_all_text.return_value = [
            FakeOCRResult("领取", 0.9, (800, 400, 900, 440), (850, 420)),
            FakeOCRResult("领取", 0.9, (800, 600, 900, 640), (850, 620)),
            FakeOCRResult("领取", 0.9, (800, 800, 900, 840), (850, 820)),
        ]
        runner.load([
            {"tap_text": ["领取", 2], "delay": 1.0, "description": "tap 2nd"}
        ])
        result = runner.execute_one(_make_screenshot())
        assert len(result) == 1
        assert result[0]["y"] == 620, "Should tap the 2nd match"

    def test_tap_text_default_nth_selects_first(self):
        """tap_text without nth defaults to first match."""
        runner, ocr, _ = _make_runner()
        ocr.find_all_text.return_value = [
            FakeOCRResult("领取", 0.9, (800, 400, 900, 440), (850, 420)),
            FakeOCRResult("领取", 0.9, (800, 800, 900, 840), (850, 820)),
        ]
        runner.load([
            {"tap_text": ["领取"], "delay": 1.0, "description": "tap first"}
        ])
        result = runner.execute_one(_make_screenshot())
        assert len(result) == 1
        assert result[0]["y"] == 420, "Should tap the first match"


class TestClaimQuestRewardScript(unittest.TestCase):
    """Integration test for the claim_quest_reward quest script from game.json."""

    def _load_claim_quest_reward(self):
        """Load the claim_quest_reward steps from game.json."""
        import json
        import os
        game_json_path = os.path.join(
            os.path.dirname(__file__),
            "games", "westgame2", "game.json"
        )
        with open(game_json_path, encoding="utf-8") as f:
            game = json.load(f)
        for script in game["quest_scripts"]:
            if script["name"] == "claim_quest_reward":
                return script["steps"]
        raise RuntimeError("claim_quest_reward not found in game.json")

    def test_claim_quest_reward_uses_last_match(self):
        """Verify the 领取 steps use nth=-1 (last match)."""
        steps = self._load_claim_quest_reward()
        claim_steps = [
            s for s in steps
            if "tap_text" in s and s["tap_text"][0] == "领取"
        ]
        assert len(claim_steps) == 3, "Should have 3 领取 steps (章节/成长/每日)"
        for s in claim_steps:
            assert len(s["tap_text"]) == 2, f"Missing nth param: {s}"
            assert s["tap_text"][1] == -1, (
                f"nth should be -1 (last match): {s}"
            )

    def test_claim_quest_reward_full_flow(self):
        """Run through the full claim_quest_reward script."""
        runner, ocr, tm = _make_runner()
        steps = self._load_claim_quest_reward()
        runner.load(steps)

        # Step 1: ensure_main_city — mock as already at main city
        tm.match_one.side_effect = lambda ss, name: (
            FakeMatchResult("scenes/main_city", 0.9, 50, 50, (0, 0, 100, 100))
            if name == "scenes/main_city" else None
        )
        result = runner.execute_one(_make_screenshot())
        assert result == []
        assert runner.step_index == 1

        # Step 2: tap_xy [70, 1600] — quest scroll icon
        result = runner.execute_one(_make_screenshot())
        assert len(result) == 1
        assert result[0]["x"] == 70
        assert result[0]["y"] == 1600
        assert runner.step_index == 2

        # Step 3: tap_text 章节任务
        ocr.find_all_text.return_value = [
            FakeOCRResult("章节任务", 0.9, (300, 200, 500, 240), (400, 220)),
            FakeOCRResult("成长任务", 0.9, (300, 250, 500, 290), (400, 270)),
            FakeOCRResult("每日任务", 0.9, (300, 300, 500, 340), (400, 320)),
        ]
        result = runner.execute_one(_make_screenshot())
        assert len(result) == 1
        assert runner.step_index == 3

        # Step 4: tap_text ["领取", -1] — last 领取 (repeat 10, optional)
        # First iteration: 3 领取 buttons visible, should tap last one (y=820)
        ocr.find_all_text.return_value = [
            FakeOCRResult("领取", 0.9, (800, 400, 900, 440), (850, 420)),
            FakeOCRResult("领取", 0.9, (800, 600, 900, 640), (850, 620)),
            FakeOCRResult("领取", 0.9, (800, 800, 900, 840), (850, 820)),
        ]
        result = runner.execute_one(_make_screenshot())
        assert len(result) == 1
        assert result[0]["y"] == 820, "Should tap LAST 领取 (bottom-most)"
        assert runner.step_index == 3  # still on this step (repeat)

        # Second iteration: still matches
        result = runner.execute_one(_make_screenshot())
        assert len(result) == 1
        assert result[0]["y"] == 820

        # Third iteration: no more 领取 — optional step skips
        ocr.find_all_text.return_value = [
            FakeOCRResult("已完成", 0.9, (800, 400, 900, 440), (850, 420)),
        ]
        result = runner.execute_one(_make_screenshot())
        assert result == []  # optional step skipped
        assert runner.step_index == 4  # advanced to 成长任务

        # Step 5: tap_text 成长任务
        ocr.find_all_text.return_value = [
            FakeOCRResult("成长任务", 0.9, (300, 250, 500, 290), (400, 270)),
        ]
        result = runner.execute_one(_make_screenshot())
        assert len(result) == 1
        assert runner.step_index == 5

        # Step 6: tap_text ["领取", -1] — no 领取 found, optional skip
        ocr.find_all_text.return_value = []
        result = runner.execute_one(_make_screenshot())
        assert result == []
        assert runner.step_index == 6

        # Step 7: tap_text 每日任务
        ocr.find_all_text.return_value = [
            FakeOCRResult("每日任务", 0.9, (300, 300, 500, 340), (400, 320)),
        ]
        result = runner.execute_one(_make_screenshot())
        assert len(result) == 1
        assert runner.step_index == 7

        # Step 8: tap_text ["领取", -1] — one 领取, then disappears
        ocr.find_all_text.return_value = [
            FakeOCRResult("领取", 0.9, (800, 500, 900, 540), (850, 520)),
        ]
        result = runner.execute_one(_make_screenshot())
        assert len(result) == 1
        assert result[0]["y"] == 520
        # Gone next time
        ocr.find_all_text.return_value = []
        result = runner.execute_one(_make_screenshot())
        assert result == []
        assert runner.step_index == 8

        # Step 9: tap_icon close_x
        tm.match_one_multi.return_value = [
            FakeMatchResult("buttons/close_x", 0.9, 1020, 200,
                            (990, 170, 1050, 230))
        ]
        result = runner.execute_one(_make_screenshot())
        assert len(result) == 1
        assert result[0]["x"] == 1020
        assert runner.is_done()
        assert not runner.is_aborted()


if __name__ == "__main__":
    unittest.main()

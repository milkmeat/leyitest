"""Quest Workflow Tests - QuestBarDetector and QuestWorkflow state machine."""

import unittest
from unittest.mock import MagicMock, patch, PropertyMock
import numpy as np


def _make_screenshot(h=1920, w=1080):
    """Create a blank BGR screenshot."""
    return np.zeros((h, w, 3), dtype=np.uint8)


class TestQuestBarDetector(unittest.TestCase):
    """Tests for vision.quest_bar_detector.QuestBarDetector."""

    def _make_detector(self):
        from vision.quest_bar_detector import QuestBarDetector
        tm = MagicMock()
        ocr = MagicMock()
        return QuestBarDetector(tm, ocr), tm, ocr

    def test_no_scroll_icon(self):
        """No scroll icon match -> not visible."""
        det, tm, ocr = self._make_detector()
        tm.match_one.return_value = None
        info = det.detect(_make_screenshot())
        assert not info.visible
        assert info.current_quest_text == ""

    def test_scroll_icon_wrong_y(self):
        """Scroll icon outside 82%-92% range -> not visible."""
        det, tm, ocr = self._make_detector()
        match = MagicMock()
        match.x = 100
        match.y = 100  # top of screen, way out of range
        match.bbox = (50, 50, 150, 150)
        tm.match_one.return_value = match
        info = det.detect(_make_screenshot())
        assert not info.visible

    def test_scroll_icon_valid_y(self):
        """Scroll icon in valid Y range -> visible=True."""
        det, tm, ocr = self._make_detector()
        match = MagicMock()
        match.x = 100
        match.y = 1650  # ~86% of 1920, in range
        match.bbox = (50, 1600, 150, 1700)
        match.template_name = "icons/task_scroll"

        # First call returns scroll icon, subsequent calls return None (no finger)
        def match_one_side_effect(screenshot, name):
            if name == "icons/task_scroll":
                return match
            return None
        tm.match_one.side_effect = match_one_side_effect

        ocr.find_all_text.return_value = []
        info = det.detect(_make_screenshot())
        assert info.visible
        assert info.scroll_icon_pos == (100, 1650)

    def test_quest_text_ocr(self):
        """OCR text is read from region right of scroll icon."""
        det, tm, ocr = self._make_detector()
        match = MagicMock()
        match.x = 100
        match.y = 1650
        match.bbox = (50, 1600, 150, 1700)

        def match_one_side_effect(screenshot, name):
            if name == "icons/task_scroll":
                return match
            return None
        tm.match_one.side_effect = match_one_side_effect

        ocr_result = MagicMock()
        ocr_result.text = "升级城堡到3级"
        ocr_result.confidence = 0.9
        ocr_result.bbox = (10, 10, 200, 40)
        ocr.find_all_text.return_value = [ocr_result]

        info = det.detect(_make_screenshot())
        assert info.visible
        assert info.current_quest_text == "升级城堡到3级"
        assert info.current_quest_bbox is not None

    def test_red_badge_detection(self):
        """Red pixels in upper-right quadrant -> has_red_badge=True."""
        det, tm, ocr = self._make_detector()

        # Create screenshot with red pixels in the badge area
        screenshot = _make_screenshot()
        # Paint red in upper-right of scroll bbox area (50,1600)-(150,1700)
        # Upper-right quadrant: x=100-150, y=1600-1650
        screenshot[1600:1650, 100:150] = [0, 0, 255]  # BGR red

        match = MagicMock()
        match.x = 100
        match.y = 1650
        match.bbox = (50, 1600, 150, 1700)

        def match_one_side_effect(screenshot_arg, name):
            if name == "icons/task_scroll":
                return match
            return None
        tm.match_one.side_effect = match_one_side_effect
        ocr.find_all_text.return_value = []

        info = det.detect(screenshot)
        assert info.visible
        assert info.has_red_badge

    def test_green_check_detection(self):
        """Green pixels right of quest text -> has_green_check=True."""
        det, tm, ocr = self._make_detector()

        screenshot = _make_screenshot()

        match = MagicMock()
        match.x = 100
        match.y = 1650
        match.bbox = (50, 1600, 150, 1700)

        def match_one_side_effect(screenshot_arg, name):
            if name == "icons/task_scroll":
                return match
            return None
        tm.match_one.side_effect = match_one_side_effect

        ocr_result = MagicMock()
        ocr_result.text = "升级城堡"
        ocr_result.confidence = 0.9
        ocr_result.bbox = (10, 10, 200, 40)
        ocr.find_all_text.return_value = [ocr_result]

        # Quest text bbox in full coords: (160, 1610, 350, 1640)
        # Green check region: right of that
        # Paint green pixels right of quest text bbox
        # The bbox gets translated: (10+150, 10+1600-25, 200+150, 40+1600-25) roughly
        # Let's compute: text_x1=150, text_y1=1600-25=1575, so bbox = (10+150,10+1575,200+150,40+1575)
        #               = (160, 1585, 350, 1615)
        # Green check region: x=350 to 350+60, y=1585 to 1615
        screenshot[1585:1615, 350:410] = [0, 255, 0]  # BGR green

        info = det.detect(screenshot)
        assert info.visible
        assert info.has_green_check

    def test_tutorial_finger(self):
        """Tutorial finger template match -> has_tutorial_finger=True."""
        det, tm, ocr = self._make_detector()

        scroll_match = MagicMock()
        scroll_match.x = 100
        scroll_match.y = 1650
        scroll_match.bbox = (50, 1600, 150, 1700)

        finger_match = MagicMock()
        finger_match.x = 540
        finger_match.y = 960

        def match_one_side_effect(screenshot, name):
            if name == "icons/task_scroll":
                return scroll_match
            if name == "icons/tutorial_finger":
                return finger_match
            return None
        tm.match_one.side_effect = match_one_side_effect
        ocr.find_all_text.return_value = []

        info = det.detect(_make_screenshot())
        assert info.visible
        assert info.has_tutorial_finger
        assert info.tutorial_finger_pos == (540, 960)

    def test_tutorial_finger_missing_template(self):
        """Missing tutorial_finger template -> gracefully skipped."""
        det, tm, ocr = self._make_detector()

        match = MagicMock()
        match.x = 100
        match.y = 1650
        match.bbox = (50, 1600, 150, 1700)

        def match_one_side_effect(screenshot, name):
            if name == "icons/task_scroll":
                return match
            return None
        tm.match_one.side_effect = match_one_side_effect
        ocr.find_all_text.return_value = []

        info = det.detect(_make_screenshot())
        assert info.visible
        assert not info.has_tutorial_finger


class TestQuestWorkflow(unittest.TestCase):
    """Tests for brain.quest_workflow.QuestWorkflow state machine."""

    def _make_workflow(self):
        from brain.quest_workflow import QuestWorkflow
        from state.game_state import GameState

        qbd = MagicMock()
        ed = MagicMock()
        # _find_close_x calls ed.template_matcher.match_one_multi — return
        # empty list so the method short-circuits to None without touching
        # the cache.
        ed.template_matcher.match_one_multi.return_value = []
        gs = GameState()

        wf = QuestWorkflow(
            quest_bar_detector=qbd,
            element_detector=ed,
            game_state=gs,
        )
        return wf, qbd, ed, gs

    def _make_quest_info(self, visible=True, text="升级城堡", red_badge=False,
                         green_check=False, bbox=(200, 1620, 400, 1660)):
        from vision.quest_bar_detector import QuestBarInfo
        info = QuestBarInfo(
            visible=visible,
            scroll_icon_pos=(100, 1650),
            scroll_icon_bbox=(50, 1600, 150, 1700),
            has_red_badge=red_badge,
            current_quest_text=text,
            current_quest_bbox=bbox,
            has_green_check=green_check,
        )
        return info

    # -- Lifecycle tests --

    def test_initial_state_idle(self):
        wf, *_ = self._make_workflow()
        assert not wf.is_active()
        assert wf.phase == "idle"

    def test_start_activates(self):
        wf, *_ = self._make_workflow()
        wf.start()
        assert wf.is_active()
        assert wf.phase == "ensure_main_city"

    def test_abort_returns_to_idle(self):
        wf, *_ = self._make_workflow()
        wf.start()
        wf.abort()
        assert not wf.is_active()
        assert wf.phase == "idle"

    def test_step_idle_returns_empty(self):
        wf, *_ = self._make_workflow()
        actions = wf.step(_make_screenshot(), "main_city")
        assert actions == []

    # -- ENSURE_MAIN_CITY tests --

    def test_ensure_main_city_already_there(self):
        """If already at main_city, transition to READ_QUEST."""
        wf, *_ = self._make_workflow()
        wf.start()
        actions = wf.step(_make_screenshot(), "main_city")
        assert wf.phase == "read_quest"
        assert actions == []

    def test_ensure_main_city_navigate_via_ocr(self):
        """If not at main_city, try OCR to find navigation text."""
        wf, qbd, ed, gs = self._make_workflow()
        wf.start()

        element = MagicMock()
        element.x = 540
        element.y = 1800
        ed.locate.return_value = element

        actions = wf.step(_make_screenshot(), "world_map")
        assert wf.phase == "ensure_main_city"  # still waiting
        assert len(actions) == 1
        assert actions[0]["type"] == "tap"
        assert actions[0]["x"] == 540

    def test_ensure_main_city_fallback_back_arrow(self):
        """If no navigation text found, try back_arrow template."""
        wf, qbd, ed, gs = self._make_workflow()
        wf.start()

        back_arrow = MagicMock()
        back_arrow.x = 60
        back_arrow.y = 80

        def locate_side_effect(screenshot, target, methods=None):
            if target == "buttons/back_arrow" and methods == ["template"]:
                return back_arrow
            return None
        ed.locate.side_effect = locate_side_effect

        actions = wf.step(_make_screenshot(), "battle")
        assert len(actions) == 1
        assert actions[0]["type"] == "tap"
        assert actions[0]["x"] == 60
        assert actions[0]["y"] == 80
        assert "back_arrow" in actions[0]["reason"]

    def test_ensure_main_city_fallback_tap_blank(self):
        """If no navigation text and no back_arrow, tap blank area."""
        wf, qbd, ed, gs = self._make_workflow()
        wf.start()
        ed.locate.return_value = None

        screenshot = _make_screenshot()
        actions = wf.step(screenshot, "battle")
        assert len(actions) == 1
        assert actions[0]["type"] == "tap"
        assert actions[0]["y"] == int(1920 * 0.95)
        assert "tap_blank" in actions[0]["reason"]

    # -- READ_QUEST tests --

    def test_read_quest_normal(self):
        """Normal quest reading -> records name, moves to CLICK_QUEST."""
        wf, qbd, ed, gs = self._make_workflow()
        wf.start()
        wf.phase = "read_quest"

        qbd.detect.return_value = self._make_quest_info(text="训练士兵")
        actions = wf.step(_make_screenshot(), "main_city")
        assert wf.phase == "click_quest"
        assert wf.target_quest_name == "训练士兵"

    def test_read_quest_red_badge_skipped(self):
        """Red badge is noted but doesn't interrupt — proceeds to read quest."""
        wf, qbd, ed, gs = self._make_workflow()
        wf.start()
        wf.phase = "read_quest"

        qbd.detect.return_value = self._make_quest_info(
            text="升级城堡", red_badge=True
        )
        actions = wf.step(_make_screenshot(), "main_city")
        assert wf.phase == "click_quest"  # proceeds past red badge
        assert wf.target_quest_name == "升级城堡"

    def test_read_quest_not_visible(self):
        """Quest bar not visible -> abort."""
        wf, qbd, ed, gs = self._make_workflow()
        wf.start()
        wf.phase = "read_quest"

        qbd.detect.return_value = self._make_quest_info(visible=False)
        actions = wf.step(_make_screenshot(), "main_city")
        assert wf.phase == "idle"

    # -- CLICK_QUEST tests --

    def test_click_quest(self):
        """Click quest text and move to EXECUTE_QUEST."""
        wf, qbd, ed, gs = self._make_workflow()
        wf.start()
        wf.phase = "click_quest"

        info = self._make_quest_info(text="升级城堡", bbox=(200, 1620, 400, 1660))
        qbd.detect.return_value = info

        actions = wf.step(_make_screenshot(), "main_city")
        assert wf.phase == "execute_quest"
        assert len(actions) == 1
        assert actions[0]["type"] == "tap"
        assert actions[0]["x"] == 300  # center of (200, 400)
        assert actions[0]["y"] == 1640  # center of (1620, 1660)

    # -- EXECUTE_QUEST tests --

    def test_execute_quest_back_to_main_city(self):
        """If scene is main_city and no finger during execution -> CHECK_COMPLETION."""
        wf, qbd, ed, gs = self._make_workflow()
        wf.start()
        wf.phase = "execute_quest"
        wf.target_quest_name = "升级城堡"

        ed.locate.return_value = None  # no tutorial finger
        actions = wf.step(_make_screenshot(), "main_city")
        assert wf.phase == "check_completion"
        assert actions == []

    def test_execute_quest_tutorial_finger_with_button(self):
        """Tutorial finger on popup -> follow fingertip (buttons ignored)."""
        wf, qbd, ed, gs = self._make_workflow()
        wf.start()
        wf.phase = "execute_quest"
        wf.target_quest_name = "升级城堡"

        finger = MagicMock()
        finger.x = 540
        finger.y = 960
        finger.confidence = 0.9

        # OCR buttons exist but finger takes priority on popup
        ocr_top = MagicMock(text="升级", confidence=0.9, center=(700, 600))
        ocr_bot = MagicMock(text="升级", confidence=0.95, center=(900, 970))

        def locate_side_effect(screenshot, target, methods=None):
            if target == "icons/tutorial_finger" and methods == ["template"]:
                return finger
            return None
        ed.locate.side_effect = locate_side_effect
        ed.ocr.find_all_text.return_value = [ocr_top, ocr_bot]

        actions = wf.step(_make_screenshot(), "popup")
        assert wf.phase == "execute_quest"
        assert len(actions) == 1
        # Finger on popup -> follow fingertip directly
        assert actions[0]["x"] == 540 + wf._FINGERTIP_OFFSET[0]
        assert actions[0]["y"] == 960 + wf._FINGERTIP_OFFSET[1]
        assert "follow_finger" in actions[0]["reason"]

    def test_execute_quest_tutorial_finger_no_button(self):
        """Tutorial finger (normal) found but no OCR button -> tap fingertip."""
        wf, qbd, ed, gs = self._make_workflow()
        wf.start()
        wf.phase = "execute_quest"
        wf.target_quest_name = "升级城堡"

        finger = MagicMock()
        finger.x = 540
        finger.y = 960
        finger.confidence = 0.9

        def locate_side_effect(screenshot, target, methods=None):
            if target == "icons/tutorial_finger" and methods == ["template"]:
                return finger
            return None
        ed.locate.side_effect = locate_side_effect

        actions = wf.step(_make_screenshot(), "popup")
        assert wf.phase == "execute_quest"
        assert len(actions) == 1
        assert actions[0]["x"] == 540 + wf._FINGERTIP_OFFSET[0]  # -65
        assert actions[0]["y"] == 960 + wf._FINGERTIP_OFFSET[1]  # +100
        assert "follow_finger" in actions[0]["reason"]

    def test_execute_quest_tutorial_finger_flipped(self):
        """Flipped finger (hflip) found -> tap with mirrored x offset."""
        wf, qbd, ed, gs = self._make_workflow()
        wf.start()
        wf.phase = "execute_quest"
        wf.target_quest_name = "升级城堡"

        flipped = MagicMock()
        flipped.x = 700
        flipped.y = 1500
        flipped.confidence = 0.95

        def locate_side_effect(screenshot, target, methods=None):
            if target == "icons/tutorial_finger_hflip" and methods == ["template"]:
                return flipped
            return None
        ed.locate.side_effect = locate_side_effect

        actions = wf.step(_make_screenshot(), "unknown")
        assert len(actions) == 1
        # hflip: dx is negated -> +25 instead of -25
        assert actions[0]["x"] == 700 + (-wf._FINGERTIP_OFFSET[0])
        assert actions[0]["y"] == 1500 + wf._FINGERTIP_OFFSET[1]
        assert "follow_tutorial_finger" in actions[0]["reason"]

    def test_execute_quest_max_iterations(self):
        """Exceeding max iterations -> RETURN_TO_CITY."""
        wf, qbd, ed, gs = self._make_workflow()
        wf.start()
        wf.phase = "execute_quest"
        wf.target_quest_name = "升级城堡"
        wf.execute_iterations = wf.max_execute_iterations

        ed.locate.return_value = None

        actions = wf.step(_make_screenshot(), "popup")
        assert wf.phase == "return_to_city"

    # -- RETURN_TO_CITY tests --

    def test_return_to_city_arrived(self):
        """Scene is main_city -> CHECK_COMPLETION."""
        wf, *_ = self._make_workflow()
        wf.start()
        wf.phase = "return_to_city"

        actions = wf.step(_make_screenshot(), "main_city")
        assert wf.phase == "check_completion"

    # -- CHECK_COMPLETION tests --

    def test_check_completion_green_check(self):
        """Green check -> CLAIM_REWARD."""
        wf, qbd, ed, gs = self._make_workflow()
        wf.start()
        wf.phase = "check_completion"

        qbd.detect.return_value = self._make_quest_info(green_check=True)
        actions = wf.step(_make_screenshot(), "main_city")
        assert wf.phase == "claim_reward"

    def test_check_completion_no_check_retry(self):
        """No green check -> retry via CLICK_QUEST."""
        wf, qbd, ed, gs = self._make_workflow()
        wf.start()
        wf.phase = "check_completion"

        qbd.detect.return_value = self._make_quest_info(green_check=False)
        actions = wf.step(_make_screenshot(), "main_city")
        assert wf.phase == "click_quest"
        assert wf.check_retries == 1

    def test_check_completion_max_retries(self):
        """Exceeding max check retries -> abort."""
        wf, qbd, ed, gs = self._make_workflow()
        wf.start()
        wf.phase = "check_completion"
        wf.check_retries = wf.max_check_retries

        qbd.detect.return_value = self._make_quest_info(green_check=False)
        actions = wf.step(_make_screenshot(), "main_city")
        assert wf.phase == "idle"

    # -- CLAIM_REWARD tests --

    def test_claim_reward(self):
        """Click quest text to claim, move to VERIFY."""
        wf, qbd, ed, gs = self._make_workflow()
        wf.start()
        wf.phase = "claim_reward"

        qbd.detect.return_value = self._make_quest_info(
            text="升级城堡", bbox=(200, 1620, 400, 1660)
        )
        actions = wf.step(_make_screenshot(), "main_city")
        assert wf.phase == "verify"
        assert len(actions) == 1
        assert actions[0]["type"] == "tap"
        assert "reward" in actions[0]["reason"]

    # -- VERIFY tests --

    def test_verify_quest_changed(self):
        """Quest name changed -> complete, back to IDLE."""
        wf, qbd, ed, gs = self._make_workflow()
        wf.start()
        wf.phase = "verify"
        wf.target_quest_name = "升级城堡"

        qbd.detect.return_value = self._make_quest_info(text="训练士兵")
        actions = wf.step(_make_screenshot(), "main_city")
        assert wf.phase == "idle"

    def test_verify_quest_unchanged_retry(self):
        """Quest name unchanged -> retry with wait."""
        wf, qbd, ed, gs = self._make_workflow()
        wf.start()
        wf.phase = "verify"
        wf.target_quest_name = "升级城堡"

        qbd.detect.return_value = self._make_quest_info(text="升级城堡")
        actions = wf.step(_make_screenshot(), "main_city")
        assert wf.phase == "verify"
        assert wf.verify_retries == 1
        assert len(actions) == 1
        assert actions[0]["type"] == "wait"

    def test_verify_max_retries(self):
        """Exceeding verify retries -> give up, IDLE."""
        wf, qbd, ed, gs = self._make_workflow()
        wf.start()
        wf.phase = "verify"
        wf.target_quest_name = "升级城堡"
        wf.verify_retries = wf.max_verify_retries

        qbd.detect.return_value = self._make_quest_info(text="升级城堡")
        actions = wf.step(_make_screenshot(), "main_city")
        assert wf.phase == "idle"

    # -- Full flow test --

    def test_full_quest_lifecycle(self):
        """Walk through the complete lifecycle: start -> claim -> idle."""
        wf, qbd, ed, gs = self._make_workflow()

        # 1. Start
        wf.start()
        assert wf.phase == "ensure_main_city"

        # 2. Already at main city
        actions = wf.step(_make_screenshot(), "main_city")
        assert wf.phase == "read_quest"

        # 3. Read quest
        qbd.detect.return_value = self._make_quest_info(text="升级城堡")
        actions = wf.step(_make_screenshot(), "main_city")
        assert wf.phase == "click_quest"
        assert wf.target_quest_name == "升级城堡"

        # 4. Click quest
        qbd.detect.return_value = self._make_quest_info(
            text="升级城堡", bbox=(200, 1620, 400, 1660)
        )
        actions = wf.step(_make_screenshot(), "main_city")
        assert wf.phase == "execute_quest"
        assert len(actions) == 1

        # 5. Execute -> no finger, returns to main city -> check completion
        ed.locate.return_value = None
        actions = wf.step(_make_screenshot(), "main_city")
        assert wf.phase == "check_completion"

        # 6. Check completion -> green check
        qbd.detect.return_value = self._make_quest_info(
            text="升级城堡", green_check=True
        )
        actions = wf.step(_make_screenshot(), "main_city")
        assert wf.phase == "claim_reward"

        # 7. Claim reward
        qbd.detect.return_value = self._make_quest_info(
            text="升级城堡", bbox=(200, 1620, 400, 1660)
        )
        actions = wf.step(_make_screenshot(), "main_city")
        assert wf.phase == "verify"
        assert len(actions) == 1

        # 8. Verify -> quest changed
        qbd.detect.return_value = self._make_quest_info(text="训练士兵")
        actions = wf.step(_make_screenshot(), "main_city")
        assert wf.phase == "idle"
        assert not wf.is_active()

    # -- Game state sync tests --

    def test_game_state_sync_on_start(self):
        wf, qbd, ed, gs = self._make_workflow()
        wf.start()
        assert gs.quest_workflow_phase == "ensure_main_city"

    def test_game_state_sync_on_abort(self):
        wf, qbd, ed, gs = self._make_workflow()
        wf.start()
        wf.abort()
        assert gs.quest_workflow_phase == "idle"
        assert gs.quest_workflow_target == ""

    def test_game_state_sync_on_step(self):
        wf, qbd, ed, gs = self._make_workflow()
        wf.start()
        wf.step(_make_screenshot(), "main_city")  # -> read_quest
        assert gs.quest_workflow_phase == "read_quest"

    # -- Button fatigue tracking tests --

    def test_action_button_exhausted_after_threshold(self):
        """Tapping the same button _ACTION_BUTTON_EXHAUST_THRESHOLD times
        adds it to _exhausted_buttons."""
        wf, *_ = self._make_workflow()
        wf.start()
        assert wf._exhausted_buttons == set()

        wf._track_button_tap("一键上阵")
        assert "一键上阵" not in wf._exhausted_buttons  # 1st tap, below threshold

        wf._track_button_tap("一键上阵")
        assert "一键上阵" in wf._exhausted_buttons  # 2nd tap, hits threshold=2

    def test_exhausted_button_skipped(self):
        """Exhausted buttons are skipped by _find_action_buttons OCR stage."""
        wf, qbd, ed, gs = self._make_workflow()
        wf.start()
        wf.phase = "execute_quest"

        # Simulate OCR returning both "一键上阵" and "出战"
        from unittest.mock import MagicMock
        ocr_btn1 = MagicMock(text="一键上阵", confidence=0.95,
                             center=(540, 800))
        ocr_btn1.text = "一键上阵"
        ocr_btn2 = MagicMock(text="出战", confidence=0.90,
                             center=(540, 900))
        ocr_btn2.text = "出战"
        ed.ocr.find_all_text.return_value = [ocr_btn1, ocr_btn2]
        # No template matches
        ed.locate.return_value = None
        ed.template_matcher.match_one_multi.return_value = []

        # Without fatigue, "一键上阵" has higher priority
        buttons = wf._find_action_buttons(_make_screenshot(), None)
        assert len(buttons) == 1
        assert buttons[0].name == "一键上阵"

        # Mark "一键上阵" as exhausted
        wf._exhausted_buttons.add("一键上阵")

        # Now should skip "一键上阵" and return "出战"
        buttons = wf._find_action_buttons(_make_screenshot(), None)
        assert len(buttons) == 1
        assert buttons[0].name == "出战"

    def test_exhausted_reset_on_scene_change(self):
        """Scene change clears exhausted buttons."""
        wf, qbd, ed, gs = self._make_workflow()
        wf.start()
        wf.phase = "execute_quest"
        wf.target_quest_name = "通关远征"

        # Exhaust a button
        wf._exhausted_buttons.add("一键上阵")
        wf._last_action_button_text = "一键上阵"
        wf._action_button_repeat_count = 1
        wf._last_execute_scene = "unknown"

        # Step with a different scene triggers reset
        ed.locate.return_value = None
        wf.step(_make_screenshot(), "popup")

        assert wf._exhausted_buttons == set()
        assert wf._last_action_button_text == ""
        assert wf._action_button_repeat_count == 0
        assert wf._last_execute_scene == "popup"

    def test_exhausted_reset_on_start_and_abort(self):
        """start() and abort() clear all button fatigue state."""
        wf, *_ = self._make_workflow()

        # Pollute fatigue state
        wf._exhausted_buttons = {"一键上阵", "出战"}
        wf._last_action_button_text = "攻击"
        wf._action_button_repeat_count = 5
        wf._last_execute_scene = "battle"

        wf.start()
        assert wf._exhausted_buttons == set()
        assert wf._last_action_button_text == ""
        assert wf._action_button_repeat_count == 0
        assert wf._last_execute_scene == ""

        # Pollute again
        wf._exhausted_buttons = {"建造"}
        wf._last_action_button_text = "建造"
        wf._action_button_repeat_count = 3
        wf._last_execute_scene = "unknown"

        wf.abort()
        assert wf._exhausted_buttons == set()
        assert wf._last_action_button_text == ""
        assert wf._action_button_repeat_count == 0
        assert wf._last_execute_scene == ""


if __name__ == "__main__":
    unittest.main()

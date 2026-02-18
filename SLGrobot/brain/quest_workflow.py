"""Quest Workflow - State machine for executing game quests across auto_loop iterations.

Lifecycle:
  IDLE -> ENSURE_MAIN_CITY -> READ_QUEST -> CLICK_QUEST -> EXECUTE_QUEST
       -> CHECK_COMPLETION -> CLAIM_REWARD -> VERIFY -> IDLE

The workflow manages one quest at a time. Each step() call returns a list of
action dicts for the auto_loop to execute. The workflow tracks its own phase
and persists across iterations.
"""

import logging

import numpy as np

from vision.quest_bar_detector import QuestBarDetector, QuestBarInfo
from vision.element_detector import ElementDetector
from state.game_state import GameState

logger = logging.getLogger(__name__)


class QuestWorkflow:
    """State machine for quest execution lifecycle.

    Phases:
        idle             - Not active, auto_loop decides when to start
        ensure_main_city - Navigate to main city if not there
        read_quest       - Detect quest bar, read quest name
        click_quest      - Click quest text to jump to execution entry
        execute_quest    - Execute quest (follow finger / LLM suggestions)
        return_to_city   - Navigate back to main city after execution
        check_completion - Check if quest has green check mark
        claim_reward     - Click quest text to claim reward
        verify           - Verify quest name changed (reward claimed)
    """

    # Offset from template center (128, 128) to fingertip (60, 235)
    # in template-local coords (pixels) for the 256x256 tutorial_finger.png.
    _FINGERTIP_OFFSET = (-65, 100)

    # Number of rapid taps when clicking an action button (furniture upgrade
    # needs ~10 clicks to go from 0% to 100%, "下一个" auto-advances).
    _RAPID_TAP_COUNT = 15

    # Button templates to try via template matching (highest priority).
    _ACTION_BUTTON_TEMPLATES = [
        "buttons/upgrade_building", "buttons/upgrade", "buttons/build",
    ]

    # Fallback: OCR text search for actionable buttons.
    _ACTION_BUTTON_TEXTS = [
        "一键上阵", "出战", "开始战斗",
        "建造", "升级", "训练", "研究", "确定", "前往",
        "开始", "使用", "派遣", "出征", "下一个", "领取",
    ]

    # Phase constants
    IDLE = "idle"
    ENSURE_MAIN_CITY = "ensure_main_city"
    READ_QUEST = "read_quest"
    CLICK_QUEST = "click_quest"
    EXECUTE_QUEST = "execute_quest"
    RETURN_TO_CITY = "return_to_city"
    CHECK_COMPLETION = "check_completion"
    CLAIM_REWARD = "claim_reward"
    VERIFY = "verify"

    def __init__(self, quest_bar_detector: QuestBarDetector,
                 element_detector: ElementDetector,
                 llm_planner,
                 game_state: GameState) -> None:
        self.quest_bar_detector = quest_bar_detector
        self.element_detector = element_detector
        self.llm_planner = llm_planner
        self.game_state = game_state

        # Create horizontally flipped tutorial_finger template for mirror detection
        self._ensure_flipped_finger_template()

        # State
        self.phase: str = self.IDLE
        self.target_quest_name: str = ""
        self.execute_iterations: int = 0
        self.max_execute_iterations: int = 40
        self.check_retries: int = 0
        self.max_check_retries: int = 3
        self.verify_retries: int = 0
        self.max_verify_retries: int = 3
        self.popup_back_count: int = 0

    def is_active(self) -> bool:
        """Return True if workflow is currently executing a quest."""
        return self.phase != self.IDLE

    def start(self) -> None:
        """Start the quest workflow from ENSURE_MAIN_CITY phase."""
        logger.info("Quest workflow: starting")
        self.phase = self.ENSURE_MAIN_CITY
        self.target_quest_name = ""
        self.execute_iterations = 0
        self.check_retries = 0
        self.verify_retries = 0
        self.popup_back_count = 0
        self._sync_to_game_state()

    def abort(self) -> None:
        """Abort the workflow and reset to IDLE."""
        logger.info(f"Quest workflow: aborting from phase={self.phase}")
        self.phase = self.IDLE
        self.target_quest_name = ""
        self.execute_iterations = 0
        self.check_retries = 0
        self.verify_retries = 0
        self._sync_to_game_state()

    def step(self, screenshot: np.ndarray, scene: str) -> list[dict]:
        """Execute one step of the workflow based on current phase.

        Called each auto_loop iteration when workflow is active.

        Args:
            screenshot: Current game screenshot.
            scene: Current scene classification.

        Returns:
            List of action dicts for the executor to run.
        """
        if self.phase == self.IDLE:
            return []

        logger.info(f"Quest workflow step: phase={self.phase}, scene={scene}")

        actions = []
        if self.phase == self.ENSURE_MAIN_CITY:
            actions = self._step_ensure_main_city(screenshot, scene)
        elif self.phase == self.READ_QUEST:
            actions = self._step_read_quest(screenshot)
        elif self.phase == self.CLICK_QUEST:
            actions = self._step_click_quest(screenshot)
        elif self.phase == self.EXECUTE_QUEST:
            actions = self._step_execute_quest(screenshot, scene)
        elif self.phase == self.RETURN_TO_CITY:
            actions = self._step_return_to_city(screenshot, scene)
        elif self.phase == self.CHECK_COMPLETION:
            actions = self._step_check_completion(screenshot)
        elif self.phase == self.CLAIM_REWARD:
            actions = self._step_claim_reward(screenshot)
        elif self.phase == self.VERIFY:
            actions = self._step_verify(screenshot)

        self._sync_to_game_state()
        return actions

    # -- Phase handlers --

    def _step_ensure_main_city(self, screenshot: np.ndarray,
                               scene: str) -> list[dict]:
        """Ensure we are on the main city screen.

        If not in main_city, try to navigate there via OCR text or BACK key.
        """
        if scene == "main_city":
            logger.info("Quest workflow: at main city, moving to READ_QUEST")
            self.phase = self.READ_QUEST
            return []

        # Try to find navigation text to go back to city
        for target_text in ["城池", "home", "主城"]:
            element = self.element_detector.locate(
                screenshot, target_text, methods=["ocr"]
            )
            if element is not None:
                logger.info(
                    f"Quest workflow: tapping '{target_text}' to navigate to main city"
                )
                return [{
                    "type": "tap",
                    "x": element.x,
                    "y": element.y,
                    "delay": 1.0,
                    "reason": f"quest_workflow:navigate_main_city:{target_text}",
                }]

        # Fallback: press BACK
        logger.info("Quest workflow: pressing BACK to navigate to main city")
        return [{
            "type": "key_event",
            "keycode": 4,
            "reason": "quest_workflow:navigate_main_city:back",
        }]

    def _step_read_quest(self, screenshot: np.ndarray) -> list[dict]:
        """Read quest bar to get current quest name."""
        info = self.quest_bar_detector.detect(screenshot)

        if not info.visible:
            logger.warning("Quest workflow: quest bar not visible, aborting")
            self.abort()
            return []

        if info.has_red_badge:
            logger.info("Quest workflow: red badge noted (will handle after quest)")

        # Record quest name and proceed
        if not info.current_quest_text:
            logger.warning("Quest workflow: no quest text found, aborting")
            self.abort()
            return []

        self.target_quest_name = info.current_quest_text
        logger.info(f"Quest workflow: target quest = '{self.target_quest_name}'")

        # If quest is already complete (green check), skip execution
        # and go straight to claiming the reward.
        if info.has_green_check:
            logger.info(
                "Quest workflow: green check already visible, "
                "skipping to CHECK_COMPLETION"
            )
            self.phase = self.CHECK_COMPLETION
            self.check_retries = 0
            return []

        self.phase = self.CLICK_QUEST
        return []

    def _step_click_quest(self, screenshot: np.ndarray) -> list[dict]:
        """Click the quest text to jump to the quest execution entry."""
        info = self.quest_bar_detector.detect(screenshot)

        if not info.visible or info.current_quest_bbox is None:
            logger.warning("Quest workflow: quest bar not visible for click, aborting")
            self.abort()
            return []

        # Click the center of the quest text bbox
        bx1, by1, bx2, by2 = info.current_quest_bbox
        cx = (bx1 + bx2) // 2
        cy = (by1 + by2) // 2

        logger.info(
            f"Quest workflow: clicking quest text '{info.current_quest_text}' "
            f"at ({cx}, {cy})"
        )
        self.phase = self.EXECUTE_QUEST
        self.execute_iterations = 0

        return [{
            "type": "tap",
            "x": cx,
            "y": cy,
            "delay": 1.5,
            "reason": f"quest_workflow:click_quest:{info.current_quest_text}",
        }]

    def _step_execute_quest(self, screenshot: np.ndarray,
                            scene: str) -> list[dict]:
        """Execute the quest: follow tutorial finger or ask LLM.

        Transitions:
        - tutorial finger detected -> tap fingertip (highest priority)
        - scene == main_city (no finger) -> CHECK_COMPLETION
        - else -> ask LLM for guidance
        - iterations exceeded -> RETURN_TO_CITY
        """
        self.execute_iterations += 1

        # Check iteration limit
        if self.execute_iterations > self.max_execute_iterations:
            logger.warning(
                f"Quest workflow: execute iterations exceeded "
                f"({self.execute_iterations}), returning to city"
            )
            self.phase = self.RETURN_TO_CITY
            return []

        # Handle popup FIRST (e.g. battle result with "返回领地").
        # Must be checked before finger detection — the finger template
        # can false-match on popup screens.
        if scene == "popup":
            # Stage 1: OCR text search for known dismiss buttons
            ocr = self.element_detector.ocr
            all_text = ocr.find_all_text(screenshot)
            for dismiss_text in ["返回领地", "返回", "确定", "确认", "关闭"]:
                for r in all_text:
                    if dismiss_text in r.text:
                        cx, cy = r.center
                        logger.info(
                            f"Quest workflow: popup detected, tapping "
                            f"'{dismiss_text}' at ({cx}, {cy})"
                        )
                        self.popup_back_count = 0
                        return [{
                            "type": "tap",
                            "x": cx,
                            "y": cy,
                            "delay": 1.5,
                            "reason": f"quest_workflow:dismiss_popup:{dismiss_text}",
                        }]

            # Stage 2: template matching for close_x button
            # Only accept matches in the top-right region to avoid
            # false positives on game UI elements.
            h, w = screenshot.shape[:2]
            for tpl_name in ["buttons/close_x", "buttons/close"]:
                match = self.element_detector.locate(
                    screenshot, tpl_name, methods=["template"]
                )
                if match is not None:
                    if match.y > h * 0.35 or match.x < w * 0.45:
                        logger.debug(
                            f"Quest workflow: rejected close '{tpl_name}' "
                            f"at ({match.x}, {match.y}) — outside expected region"
                        )
                        continue
                    logger.info(
                        f"Quest workflow: popup close button '{tpl_name}' "
                        f"at ({match.x}, {match.y})"
                    )
                    self.popup_back_count = 0
                    return [{
                        "type": "tap",
                        "x": match.x,
                        "y": match.y,
                        "delay": 1.0,
                        "reason": f"quest_workflow:dismiss_popup:{tpl_name}",
                    }]

            # No known dismiss method found — escalate
            self.popup_back_count += 1

            if self.popup_back_count <= 2:
                # Level 1: try BACK key
                logger.info(
                    f"Quest workflow: popup no dismiss found, pressing BACK "
                    f"({self.popup_back_count}/2)"
                )
                return [{"type": "key_event", "keycode": 4,
                         "reason": "quest_workflow:dismiss_popup:back"}]

            if self.popup_back_count <= 4:
                # Level 2: tap screen center (some popups dismiss on any tap)
                h, w = screenshot.shape[:2]
                logger.info(
                    f"Quest workflow: popup BACK ineffective, tapping center "
                    f"({self.popup_back_count})"
                )
                return [{
                    "type": "tap",
                    "x": w // 2,
                    "y": h // 2,
                    "delay": 1.0,
                    "reason": "quest_workflow:dismiss_popup:center_tap",
                }]

            # Level 3: ask LLM to analyze the popup
            if self.llm_planner and self.llm_planner.api_key:
                logger.info(
                    f"Quest workflow: popup stuck ({self.popup_back_count}), "
                    f"asking LLM for help"
                )
                self.popup_back_count = 0  # reset to avoid infinite LLM calls
                try:
                    actions = self.llm_planner.analyze_unknown_scene(
                        screenshot, self.game_state
                    )
                    if actions:
                        return actions
                except Exception as e:
                    logger.warning(f"Quest workflow: LLM popup analysis failed: {e}")

            # Final fallback: tap screen center
            h, w = screenshot.shape[:2]
            self.popup_back_count = 0
            return [{
                "type": "tap",
                "x": w // 2,
                "y": h // 2,
                "delay": 1.0,
                "reason": "quest_workflow:dismiss_popup:final_center_tap",
            }]

        # At main city — check green checkmark BEFORE following finger.
        # When the quest is complete the finger points at the quest bar
        # to claim the reward; we must detect the green check first so
        # the workflow transitions to CLAIM_REWARD instead of endlessly
        # re-tapping the finger.
        if scene == "main_city":
            info = self.quest_bar_detector.detect(screenshot)
            if info.visible and info.has_green_check:
                logger.info(
                    "Quest workflow: green check detected at main city, "
                    "moving to CHECK_COMPLETION"
                )
                self.phase = self.CHECK_COMPLETION
                self.check_retries = 0
                return []

        # Check for tutorial finger icon (even on main_city)
        # Matches both normal and horizontally flipped orientations
        finger_match, is_flipped = self._detect_tutorial_finger(screenshot)
        if finger_match is not None:
            # Finger detected — look for actionable buttons via OCR
            buttons = self._find_action_buttons(screenshot, finger_match)
            if buttons:
                actions = []
                for b in buttons:
                    if b.name in ("建造", "下一个"):
                        # Furniture building/next: rapid-tap to fill
                        # progress bar (~10% per click).
                        logger.info(
                            f"Quest workflow: finger detected, rapid-tapping "
                            f"'{b.name}' at ({b.x}, {b.y}) x{self._RAPID_TAP_COUNT}"
                        )
                        actions.extend([{
                            "type": "tap",
                            "x": b.x,
                            "y": b.y,
                            "delay": 0.3,
                            "reason": f"quest_workflow:finger_button:{b.name}",
                        }] * self._RAPID_TAP_COUNT)
                    else:
                        logger.info(
                            f"Quest workflow: finger detected, tapping "
                            f"'{b.name}' at ({b.x}, {b.y})"
                        )
                        actions.append({
                            "type": "tap",
                            "x": b.x,
                            "y": b.y,
                            "delay": 1.0,
                            "reason": f"quest_workflow:finger_button:{b.name}",
                        })
                return actions

            # No button text found — fall back to fingertip offset
            dx, dy = self._FINGERTIP_OFFSET
            if is_flipped:
                dx = -dx  # mirror the horizontal offset
            tap_x = finger_match.x + dx
            tap_y = finger_match.y + dy
            logger.info(
                f"Quest workflow: finger center=({finger_match.x}, {finger_match.y}), "
                f"flipped={is_flipped}, fingertip=({tap_x}, {tap_y})"
            )
            return [{
                "type": "tap",
                "x": tap_x,
                "y": tap_y,
                "delay": 1.0,
                "reason": "quest_workflow:follow_tutorial_finger",
            }]

        # No finger — if back at main city, quest execution might be done
        if scene == "main_city":
            logger.info("Quest workflow: back at main city (no finger), checking completion")
            self.phase = self.CHECK_COMPLETION
            self.check_retries = 0
            return []

        # On non-popup screens (e.g. reward dialogs classified as "unknown"),
        # look for actionable buttons FIRST — especially "领取" (claim reward).
        # Only fall back to close_x if no action button is found.
        # Require short text (≤ btn + 2 chars) to avoid matching substrings
        # inside long quest descriptions (e.g. "建造" in "建造雷达通告栏").
        ocr = self.element_detector.ocr
        all_text = ocr.find_all_text(screenshot)
        for btn_text in self._ACTION_BUTTON_TEXTS:
            for r in all_text:
                if btn_text in r.text and len(r.text) <= len(btn_text) + 2:
                    cx, cy = r.center
                    logger.info(
                        f"Quest workflow: action button '{btn_text}' found "
                        f"at ({cx}, {cy}) on non-popup screen"
                    )
                    return [{
                        "type": "tap",
                        "x": cx,
                        "y": cy,
                        "delay": 1.0,
                        "reason": f"quest_workflow:action_button:{btn_text}",
                    }]

        # Try close_x for full-screen popups that lack dark borders
        # (e.g. "First Purchase Reward") — classified as "unknown" not "popup"
        h, w = screenshot.shape[:2]
        for tpl_name in ["buttons/close_x", "buttons/close"]:
            match = self.element_detector.locate(
                screenshot, tpl_name, methods=["template"]
            )
            if match is not None and match.y <= h * 0.35 and match.x >= w * 0.45:
                logger.info(
                    f"Quest workflow: close button '{tpl_name}' found "
                    f"at ({match.x}, {match.y}) on non-popup screen"
                )
                return [{
                    "type": "tap",
                    "x": match.x,
                    "y": match.y,
                    "delay": 1.0,
                    "reason": f"quest_workflow:dismiss_unknown_popup:{tpl_name}",
                }]

        # Fallback: ask LLM for quest execution guidance
        if self.llm_planner and self.llm_planner.api_key:
            try:
                actions = self.llm_planner.analyze_quest_execution(
                    screenshot, self.target_quest_name, self.game_state
                )
                if actions:
                    logger.info(
                        f"Quest workflow: LLM suggested {len(actions)} actions"
                    )
                    return actions
            except Exception as e:
                logger.warning(f"Quest workflow: LLM analysis failed: {e}")

        # No guidance available, try tapping screen center as last resort
        h, w = screenshot.shape[:2]
        logger.info("Quest workflow: no guidance, tapping center")
        return [{
            "type": "tap",
            "x": w // 2,
            "y": h // 2,
            "delay": 1.0,
            "reason": "quest_workflow:execute_tap_center",
        }]

    def _step_return_to_city(self, screenshot: np.ndarray,
                             scene: str) -> list[dict]:
        """Navigate back to main city after quest execution.

        Handles popups with the same escalation logic as _step_execute_quest
        (OCR dismiss → close_x template → BACK → center tap → LLM).
        """
        if scene == "main_city":
            logger.info("Quest workflow: returned to main city, checking completion")
            self.phase = self.CHECK_COMPLETION
            self.check_retries = 0
            self.popup_back_count = 0
            return []

        # Handle popup with full escalation logic
        if scene == "popup":
            # Stage 1: OCR text search for known dismiss buttons
            ocr = self.element_detector.ocr
            all_text = ocr.find_all_text(screenshot)
            for dismiss_text in ["返回领地", "返回", "确定", "确认", "关闭"]:
                for r in all_text:
                    if dismiss_text in r.text:
                        cx, cy = r.center
                        logger.info(
                            f"Quest workflow (return): popup tapping "
                            f"'{dismiss_text}' at ({cx}, {cy})"
                        )
                        self.popup_back_count = 0
                        return [{
                            "type": "tap",
                            "x": cx,
                            "y": cy,
                            "delay": 1.5,
                            "reason": f"quest_workflow:return_dismiss_popup:{dismiss_text}",
                        }]

            # Stage 2: template matching for close_x button
            # Only accept matches in the top-right region.
            h, w = screenshot.shape[:2]
            for tpl_name in ["buttons/close_x", "buttons/close"]:
                match = self.element_detector.locate(
                    screenshot, tpl_name, methods=["template"]
                )
                if match is not None:
                    if match.y > h * 0.35 or match.x < w * 0.45:
                        logger.debug(
                            f"Quest workflow (return): rejected close '{tpl_name}' "
                            f"at ({match.x}, {match.y}) — outside expected region"
                        )
                        continue
                    logger.info(
                        f"Quest workflow (return): popup close '{tpl_name}' "
                        f"at ({match.x}, {match.y})"
                    )
                    self.popup_back_count = 0
                    return [{
                        "type": "tap",
                        "x": match.x,
                        "y": match.y,
                        "delay": 1.0,
                        "reason": f"quest_workflow:return_dismiss_popup:{tpl_name}",
                    }]

            # Escalation: BACK → center tap
            self.popup_back_count += 1
            if self.popup_back_count <= 2:
                logger.info(
                    f"Quest workflow (return): popup pressing BACK "
                    f"({self.popup_back_count}/2)"
                )
                return [{"type": "key_event", "keycode": 4,
                         "reason": "quest_workflow:return_dismiss_popup:back"}]

            h, w = screenshot.shape[:2]
            if self.popup_back_count <= 4:
                logger.info(
                    f"Quest workflow (return): popup tapping center "
                    f"({self.popup_back_count})"
                )
                return [{
                    "type": "tap",
                    "x": w // 2,
                    "y": h // 2,
                    "delay": 1.0,
                    "reason": "quest_workflow:return_dismiss_popup:center_tap",
                }]

            # Final: reset and try BACK again
            self.popup_back_count = 0
            return [{"type": "key_event", "keycode": 4,
                     "reason": "quest_workflow:return_dismiss_popup:back_reset"}]

        # Not a popup — try OCR navigation text or BACK
        return self._step_ensure_main_city(screenshot, scene)

    def _step_check_completion(self, screenshot: np.ndarray) -> list[dict]:
        """Check if quest has a green check mark (completed)."""
        info = self.quest_bar_detector.detect(screenshot)

        if not info.visible:
            logger.warning("Quest workflow: quest bar not visible for check")
            self.check_retries += 1
            if self.check_retries > self.max_check_retries:
                logger.warning("Quest workflow: too many check retries, aborting")
                self.abort()
            return []

        if info.has_green_check:
            logger.info("Quest workflow: green check detected, claiming reward")
            self.phase = self.CLAIM_REWARD
            return []

        # No green check - go back to execute the quest
        self.check_retries += 1
        if self.check_retries > self.max_check_retries:
            logger.warning(
                f"Quest workflow: no green check after {self.check_retries} checks, "
                f"aborting"
            )
            self.abort()
            return []

        logger.info(
            f"Quest workflow: no green check (attempt {self.check_retries}/"
            f"{self.max_check_retries}), retrying quest execution"
        )
        self.phase = self.CLICK_QUEST
        return []

    def _step_claim_reward(self, screenshot: np.ndarray) -> list[dict]:
        """Click quest text area to claim the reward (when green check is shown)."""
        info = self.quest_bar_detector.detect(screenshot)

        if not info.visible or info.current_quest_bbox is None:
            logger.warning("Quest workflow: quest bar not visible for reward claim")
            self.abort()
            return []

        # Click the quest text to claim reward
        bx1, by1, bx2, by2 = info.current_quest_bbox
        cx = (bx1 + bx2) // 2
        cy = (by1 + by2) // 2

        logger.info(f"Quest workflow: claiming reward at ({cx}, {cy})")
        self.phase = self.VERIFY

        return [{
            "type": "tap",
            "x": cx,
            "y": cy,
            "delay": 2.0,
            "reason": "quest_workflow:claim_reward",
        }]

    def _step_verify(self, screenshot: np.ndarray) -> list[dict]:
        """Verify that quest name changed (reward was successfully claimed).

        After CLAIM_REWARD clicks the quest bar text, the Tasks panel may
        open.  This phase handles:
        1. Finding and clicking "领取" / "全部领取" on the Tasks panel.
        2. Closing the panel (BACK or close_x) to return to main city.
        3. Re-reading the quest bar to confirm the quest changed.
        """
        info = self.quest_bar_detector.detect(screenshot)

        if not info.visible:
            # Quest bar not visible — likely the Tasks panel is open.
            # Look for "领取" or "全部领取" to claim the reward.
            ocr = self.element_detector.ocr
            all_text = ocr.find_all_text(screenshot)
            for claim_text in ["领取", "全部领取"]:
                for r in all_text:
                    if claim_text in r.text and len(r.text) <= len(claim_text) + 2:
                        cx, cy = r.center
                        logger.info(
                            f"Quest workflow (verify): claiming '{claim_text}' "
                            f"at ({cx}, {cy})"
                        )
                        return [{
                            "type": "tap",
                            "x": cx,
                            "y": cy,
                            "delay": 1.5,
                            "reason": f"quest_workflow:verify_claim:{claim_text}",
                        }]

            # No claim button — try closing the panel to get back
            logger.info(
                "Quest workflow: quest bar not visible, no claim button, "
                "pressing BACK"
            )
            return [{"type": "key_event", "keycode": 4,
                     "reason": "quest_workflow:verify_close_panel"}]

        new_quest = info.current_quest_text
        if new_quest and new_quest != self.target_quest_name:
            logger.info(
                f"Quest workflow: quest changed from '{self.target_quest_name}' "
                f"to '{new_quest}', quest complete!"
            )
            self.phase = self.IDLE
            return []

        # Quest name didn't change
        self.verify_retries += 1
        if self.verify_retries > self.max_verify_retries:
            logger.warning("Quest workflow: quest name unchanged, giving up")
            self.phase = self.IDLE
            return []

        logger.info(
            f"Quest workflow: quest name unchanged (attempt {self.verify_retries}/"
            f"{self.max_verify_retries}), waiting"
        )
        return [{
            "type": "wait",
            "seconds": 1.5,
            "reason": "quest_workflow:verify_wait",
        }]

    # -- Internal helpers --

    def _ensure_flipped_finger_template(self) -> None:
        """Create a horizontally flipped tutorial_finger in the template cache.

        The game shows the finger icon mirrored (pointing left or right).
        We need both orientations for reliable matching.
        """
        try:
            import cv2
            tm = self.element_detector.template_matcher
            cache = tm._cache
            if not isinstance(cache, dict):
                return

            name = "icons/tutorial_finger"
            flip_name = "icons/tutorial_finger_flip"

            if flip_name in cache:
                return

            entry = cache.get(name)
            if entry is None or not isinstance(entry, tuple):
                return

            tpl, mask = entry
            flip_tpl = cv2.flip(tpl, 1)  # horizontal flip
            flip_mask = cv2.flip(mask, 1) if mask is not None else None
            cache[flip_name] = (flip_tpl, flip_mask)
            logger.debug("Created flipped tutorial_finger template")
        except Exception:
            pass  # graceful degradation — flipped matching won't be available

    # Finger template matches below this confidence are ignored.
    # Real finger: 0.96+, false positives (e.g. battle result icons): ~0.91.
    _FINGER_CONFIDENCE_THRESHOLD = 0.95

    def _detect_tutorial_finger(self, screenshot: np.ndarray) -> tuple:
        """Detect tutorial finger in both normal and mirrored orientation.

        Returns:
            (match, is_flipped) where match is an Element or None,
            and is_flipped indicates if the mirrored version matched better.
        """
        normal = self.element_detector.locate(
            screenshot, "icons/tutorial_finger", methods=["template"]
        )
        flipped = self.element_detector.locate(
            screenshot, "icons/tutorial_finger_flip", methods=["template"]
        )

        # Filter out low-confidence matches (false positives)
        if normal is not None and normal.confidence < self._FINGER_CONFIDENCE_THRESHOLD:
            logger.debug(
                f"Finger match rejected: confidence={normal.confidence:.3f} "
                f"< {self._FINGER_CONFIDENCE_THRESHOLD}"
            )
            normal = None
        if flipped is not None and flipped.confidence < self._FINGER_CONFIDENCE_THRESHOLD:
            logger.debug(
                f"Flipped finger match rejected: confidence={flipped.confidence:.3f} "
                f"< {self._FINGER_CONFIDENCE_THRESHOLD}"
            )
            flipped = None

        if normal is None and flipped is None:
            return None, False
        if normal is not None and flipped is None:
            return normal, False
        if normal is None and flipped is not None:
            return flipped, True

        # Both matched — pick higher confidence
        if flipped.confidence > normal.confidence:
            return flipped, True
        return normal, False

    def _find_action_buttons(self, screenshot: np.ndarray,
                             finger_match) -> "list[Element]":
        """Find actionable buttons on screen.

        Returns a list of Elements, deduplicated by button text and ordered
        by priority (list position in _ACTION_BUTTON_TEXTS).

        Priority:
        1. Template matching for known button images (most reliable).
        2. OCR text search as fallback.
        """
        from vision.element_detector import Element

        # Stage 1: template matching for button images
        for tpl_name in self._ACTION_BUTTON_TEMPLATES:
            match = self.element_detector.locate(
                screenshot, tpl_name, methods=["template"]
            )
            if match is not None:
                logger.debug(f"Action button template match: {tpl_name} "
                             f"at ({match.x},{match.y}) conf={match.confidence:.3f}")
                return [match]

        # Stage 2: OCR fallback — find all matching buttons
        ocr = self.element_detector.ocr
        all_results = ocr.find_all_text(screenshot)
        if not all_results:
            return []

        # Collect best (highest on screen) match per button text,
        # preserving _ACTION_BUTTON_TEXTS priority order.
        found: list[Element] = []
        seen_texts: set[str] = set()
        for btn_text in self._ACTION_BUTTON_TEXTS:
            if btn_text in seen_texts:
                continue
            btn_lower = btn_text.lower()
            matches = [(r.center[0], r.center[1]) for r in all_results
                       if btn_lower in r.text.lower()]
            if matches:
                # Pick topmost occurrence of this button text
                best = min(matches, key=lambda m: m[1])
                found.append(Element(name=btn_text, x=best[0], y=best[1],
                                     confidence=1.0, source="ocr",
                                     bbox=(best[0], best[1], best[0], best[1])))
                seen_texts.add(btn_text)

        if found:
            # Return only the highest-priority button to avoid tapping
            # multiple buttons (e.g. "开始战斗" + "领取") in one iteration.
            best = found[0]
            logger.debug(
                f"Action button OCR: best='{best.name}' at ({best.x},{best.y}), "
                f"total candidates={len(found)}"
            )
            return [best]
        return found

    def _sync_to_game_state(self) -> None:
        """Sync workflow state to game_state for persistence."""
        self.game_state.quest_workflow_phase = self.phase
        self.game_state.quest_workflow_target = self.target_quest_name

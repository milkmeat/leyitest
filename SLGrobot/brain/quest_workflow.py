"""Quest Workflow - State machine for executing game quests across auto_loop iterations.

Lifecycle:
  IDLE -> ENSURE_MAIN_CITY -> READ_QUEST -> CLICK_QUEST -> EXECUTE_QUEST
       -> CHECK_COMPLETION -> CLAIM_REWARD -> VERIFY -> IDLE

The workflow manages one quest at a time. Each step() call returns a list of
action dicts for the auto_loop to execute. The workflow tracks its own phase
and persists across iterations.
"""

import logging
import re
import time

import numpy as np

from vision.quest_bar_detector import QuestBarDetector, QuestBarInfo
from vision.element_detector import ElementDetector
from vision.ocr_locator import is_on_colored_button
from state.game_state import GameState
from brain.quest_script import QuestScriptRunner

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

    # Offset from template center (40, 57) to fingertip (15, 100)
    # in template-local coords (pixels) for the 80x114 tutorial_finger.png
    # (trimmed fingertip crop of the original 256x256).
    _FINGERTIP_OFFSET = (-25, 43)

    # Pre-computed fingertip offsets for rotation variants.
    # Derived by rotating _FINGERTIP_OFFSET (-25, 43) by the CW angle
    # using screen-coordinate rotation (y-down).
    _ROTATION_FINGERTIP_OFFSETS: dict[str, tuple[int, int]] = {
        "rot117cw": (-27, -42),
    }

    def _fingertip_pos(self, cx: int, cy: int, flip_type: str) -> tuple[int, int]:
        """Compute fingertip tap position from match center and flip type."""
        if flip_type in self._ROTATION_FINGERTIP_OFFSETS:
            dx, dy = self._ROTATION_FINGERTIP_OFFSETS[flip_type]
            return cx + dx, cy + dy
        dx, dy = self._FINGERTIP_OFFSET
        if flip_type in ("hflip", "hvflip"):
            dx = -dx
        if flip_type in ("vflip", "hvflip"):
            dy = -dy
        return cx + dx, cy + dy

    # Number of rapid taps when clicking an action button (furniture upgrade
    # needs ~10 clicks to go from 0% to 100%, "下一个" auto-advances).
    _RAPID_TAP_COUNT = 15

    # After tapping the same action button this many times consecutively
    # without scene change, mark it as "exhausted" and try the next button.
    _ACTION_BUTTON_EXHAUST_THRESHOLD = 2

    # Button templates to try via template matching (highest priority).
    _ACTION_BUTTON_TEMPLATES = [
        "buttons/upgrade_building", "buttons/upgrade", "buttons/build",
    ]

    # OCR text search for popup dismiss buttons (used in execute_quest
    # and return_to_city).  Overridden from game_profile.popup_close_texts.
    _POPUP_DISMISS_TEXTS = ["返回领地", "返回", "确定", "确认", "关闭"]

    # Fallback: OCR text search for actionable buttons.
    _ACTION_BUTTON_TEXTS = [
        "一键上阵", "出战", "开始战斗", "攻击",
        "建造", "升级", "训练", "研究", "确定", "前往",
        "开始", "使用", "派遣", "出征", "行军", "下一个", "领取",
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
                 game_state: GameState,
                 game_profile=None,
                 adb_controller=None,
                 screenshot_fn=None) -> None:
        self.quest_bar_detector = quest_bar_detector
        self.element_detector = element_detector
        self.llm_planner = llm_planner
        self.game_state = game_state

        # Override button patterns from game profile
        if game_profile and game_profile.action_button_templates:
            self._ACTION_BUTTON_TEMPLATES = game_profile.action_button_templates
        if game_profile and game_profile.action_button_texts:
            self._ACTION_BUTTON_TEXTS = game_profile.action_button_texts
        if game_profile and game_profile.finger_ncc_threshold > 0:
            self._FINGER_NCC_THRESHOLD = game_profile.finger_ncc_threshold
        if game_profile and game_profile.popup_close_texts:
            self._POPUP_DISMISS_TEXTS = game_profile.popup_close_texts
        self._quest_scripts = (
            game_profile.quest_scripts
            if game_profile and game_profile.quest_scripts
            else []
        )
        # Create horizontally flipped tutorial_finger template for mirror detection
        self._ensure_flipped_finger_template()

        # Quest script runner for executing multi-step quest rules
        self._script_runner = QuestScriptRunner(
            ocr_locator=element_detector.ocr,
            template_matcher=element_detector.template_matcher,
            adb_controller=adb_controller,
            screenshot_fn=screenshot_fn,
        )
        self._loaded_quest_pattern: str = ""  # pattern currently loaded

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

        # Button fatigue tracking — avoid repeatedly tapping the same
        # ineffective button (e.g. "一键上阵" when we need "出战").
        self._last_action_button_text: str = ""
        self._action_button_repeat_count: int = 0
        self._exhausted_buttons: set[str] = set()
        self._last_execute_scene: str = ""

        # Abort cooldown — prevent immediate restart of the same quest
        self._last_abort_time: float = 0.0
        self._last_aborted_quest: str = ""
        self._ABORT_COOLDOWN: int = 180  # seconds (3 minutes)

    def is_active(self) -> bool:
        """Return True if workflow is currently executing a quest."""
        return self.phase != self.IDLE

    def should_start(self, quest_name: str, has_green_check: bool = False) -> bool:
        """Check if we should start a new quest workflow for this quest.

        Returns True unless the quest was recently aborted and is still
        within the cooldown period (and doesn't have a green check).
        """
        if has_green_check:
            return True  # Always start if quest is already complete
        if self._last_aborted_quest and quest_name == self._last_aborted_quest:
            elapsed = time.time() - self._last_abort_time
            if elapsed < self._ABORT_COOLDOWN:
                logger.debug(
                    f"Quest workflow: cooldown active for '{quest_name}' "
                    f"({int(elapsed)}s / {self._ABORT_COOLDOWN}s)"
                )
                return False
        return True

    def start(self) -> None:
        """Start the quest workflow from ENSURE_MAIN_CITY phase."""
        logger.info("Quest workflow: starting")
        self.phase = self.ENSURE_MAIN_CITY
        self.target_quest_name = ""
        self.execute_iterations = 0
        self.check_retries = 0
        self.verify_retries = 0
        self.popup_back_count = 0
        self._last_action_button_text = ""
        self._action_button_repeat_count = 0
        self._exhausted_buttons = set()
        self._last_execute_scene = ""
        self._script_runner.reset()
        self._loaded_quest_pattern = ""
        self._sync_to_game_state()

    def abort(self) -> None:
        """Abort the workflow and reset to IDLE."""
        logger.info(f"Quest workflow: aborting from phase={self.phase}")
        self._last_abort_time = time.time()
        self._last_aborted_quest = self.target_quest_name
        self.phase = self.IDLE
        self.target_quest_name = ""
        self.execute_iterations = 0
        self.check_retries = 0
        self.verify_retries = 0
        self._last_action_button_text = ""
        self._action_button_repeat_count = 0
        self._exhausted_buttons = set()
        self._last_execute_scene = ""
        self._script_runner.reset()
        self._loaded_quest_pattern = ""
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

        If not in main_city, try to navigate there via OCR text, back_arrow
        template, or tapping blank area.
        """
        if scene == "main_city":
            logger.info("Quest workflow: at main city, moving to READ_QUEST")
            self.phase = self.READ_QUEST
            return []

        # Popup during ensure_main_city — likely a quest-related screen
        # opened by a tutorial finger tap.  Advance to EXECUTE_QUEST which
        # has comprehensive popup handling (dismiss buttons, close_x, finger,
        # action buttons, LLM escalation).
        if scene == "popup":
            logger.info(
                "Quest workflow: popup during ensure_main_city, "
                "advancing to EXECUTE_QUEST"
            )
            self.phase = self.EXECUTE_QUEST
            self.execute_iterations = 0
            return self._step_execute_quest(screenshot, scene)

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

        # Fallback: try back_arrow template
        match = self._find_back_arrow(screenshot)
        if match is not None:
            logger.info(
                f"Quest workflow: tapping back_arrow at ({match.x}, {match.y}) "
                f"to navigate to main city"
            )
            return [{
                "type": "tap",
                "x": match.x,
                "y": match.y,
                "delay": 1.0,
                "reason": "quest_workflow:navigate_main_city:back_arrow",
            }]

        # Last resort: tap blank area outside any dialog
        h, w = screenshot.shape[:2]
        logger.info("Quest workflow: tapping blank area to navigate to main city")
        return [{
            "type": "tap",
            "x": w // 2,
            "y": int(h * 0.95),
            "delay": 1.0,
            "reason": "quest_workflow:navigate_main_city:tap_blank",
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

        # Green check means quest is already completed — skip execution
        if info.has_green_check:
            logger.info(
                "Quest workflow: green check detected, skipping to CLAIM_REWARD"
            )
            self.phase = self.CLAIM_REWARD
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
        self._last_action_button_text = ""
        self._action_button_repeat_count = 0
        self._exhausted_buttons = set()
        self._last_execute_scene = ""

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

        # Scene change -> clear button fatigue (screen content changed)
        if scene != self._last_execute_scene and self._last_execute_scene:
            self._exhausted_buttons.clear()
            self._last_action_button_text = ""
            self._action_button_repeat_count = 0
        self._last_execute_scene = scene

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
            for dismiss_text in self._POPUP_DISMISS_TEXTS:
                for r in all_text:
                    if dismiss_text in r.text:
                        # Verify text is on a colored button, not body text
                        if not is_on_colored_button(screenshot, r.bbox):
                            logger.debug(
                                f"Quest workflow: skipping '{dismiss_text}' "
                                f"at {r.center} — not on colored button"
                            )
                            continue
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

            # Stage 2: template matching for close_x button (with red-pixel
            # verification to eliminate false positives on colored backgrounds).
            # Only accept matches in the top-right region.
            h, w = screenshot.shape[:2]
            match = self._find_close_x(screenshot)
            if match is not None:
                if match.y > h * 0.35 or match.x < w * 0.45:
                    logger.debug(
                        f"Quest workflow: rejected close_x "
                        f"at ({match.x}, {match.y}) — outside expected region"
                    )
                else:
                    logger.info(
                        f"Quest workflow: popup close_x "
                        f"at ({match.x}, {match.y})"
                    )
                    self.popup_back_count = 0
                    return [{
                        "type": "tap",
                        "x": match.x,
                        "y": match.y,
                        "delay": 1.0,
                        "reason": "quest_workflow:dismiss_popup:close_x",
                    }]

            # Stage 3: Tutorial finger on popup (e.g. "出征提示" with
            # finger pointing at "前往训练").  Follow the fingertip directly —
            # OCR is unreliable here (matches title/body text, finger covers
            # button text).
            finger_match, flip_type = self._detect_tutorial_finger(screenshot)
            if finger_match is not None:
                tap_x, tap_y = self._fingertip_pos(
                    finger_match.x, finger_match.y, flip_type)
                logger.info(
                    f"Quest workflow: popup finger at ({finger_match.x}, "
                    f"{finger_match.y}), {flip_type}, "
                    f"tapping fingertip ({tap_x}, {tap_y})"
                )
                self.popup_back_count = 0
                return [{
                    "type": "tap",
                    "x": tap_x,
                    "y": tap_y,
                    "delay": 1.5,
                    "reason": "quest_workflow:popup_follow_finger",
                }]

            # Stage 4: Action buttons on popup (no finger, but has
            # tappable buttons like "前往训练", "攻击", etc.)
            # Use short-text filter to exclude body text matches.
            action_buttons = self._find_action_buttons(screenshot, None)
            if action_buttons:
                best = action_buttons[0]
                self._track_button_tap(best.name)
                logger.info(
                    f"Quest workflow: popup action button '{best.name}' "
                    f"at ({best.x}, {best.y})"
                )
                self.popup_back_count = 0
                return [{
                    "type": "tap",
                    "x": best.x,
                    "y": best.y,
                    "delay": 1.5,
                    "reason": f"quest_workflow:popup_action:{best.name}",
                }]

            # No known dismiss method found — escalate
            self.popup_back_count += 1

            if self.popup_back_count <= 2:
                # Level 1: try back_arrow template, or tap blank area
                # outside the dialog (game ignores Android BACK).
                match = self._find_back_arrow(screenshot)
                if match is not None:
                    logger.info(
                        f"Quest workflow: popup tapping back_arrow "
                        f"at ({match.x}, {match.y}) "
                        f"({self.popup_back_count}/2)"
                    )
                    return [{
                        "type": "tap",
                        "x": match.x,
                        "y": match.y,
                        "delay": 1.0,
                        "reason": "quest_workflow:dismiss_popup:back_arrow",
                    }]
                h, w = screenshot.shape[:2]
                logger.info(
                    f"Quest workflow: popup tapping blank area "
                    f"({self.popup_back_count}/2)"
                )
                return [{
                    "type": "tap",
                    "x": w // 2,
                    "y": int(h * 0.95),
                    "delay": 1.0,
                    "reason": "quest_workflow:dismiss_popup:tap_blank",
                }]

            if self.popup_back_count <= 4:
                # Level 2: tap screen center (some popups dismiss on any tap)
                h, w = screenshot.shape[:2]
                logger.info(
                    f"Quest workflow: popup tap_blank ineffective, tapping center "
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

        # Check for tutorial finger icon (even on main_city).
        # Always follow the fingertip directly — OCR is unreliable when the
        # finger covers button text and can false-match on titles/body text.
        finger_match, flip_type = self._detect_tutorial_finger(screenshot)
        if finger_match is not None:
            tap_x, tap_y = self._fingertip_pos(
                finger_match.x, finger_match.y, flip_type)
            logger.info(
                f"Quest workflow: finger center=({finger_match.x}, {finger_match.y}), "
                f"{flip_type}, fingertip=({tap_x}, {tap_y})"
            )
            return [{
                "type": "tap",
                "x": tap_x,
                "y": tap_y,
                "delay": 1.0,
                "reason": "quest_workflow:follow_tutorial_finger",
            }]

        # Story dialogue — try skip button first, then down-triangle
        if scene == "story_dialogue":
            # Try OCR skip button first
            skip_element = None
            for skip_text in ["跳过", "skip"]:
                skip_element = self.element_detector.locate(
                    screenshot, skip_text, methods=["ocr"]
                )
                if skip_element is not None:
                    break
            if skip_element is not None:
                logger.info(
                    f"Quest workflow: story skip '{skip_element.name}' "
                    f"at ({skip_element.x}, {skip_element.y})"
                )
                return [{
                    "type": "tap",
                    "x": skip_element.x,
                    "y": skip_element.y,
                    "delay": 0.5,
                    "reason": f"quest_workflow:story_skip:{skip_element.name}",
                }]
            match = self.element_detector.locate(
                screenshot, "icons/down_triangle", methods=["template"]
            )
            if match is not None:
                logger.info(
                    f"Quest workflow: story dialogue, tapping triangle "
                    f"at ({match.x}, {match.y})"
                )
                return [{
                    "type": "tap",
                    "x": match.x,
                    "y": match.y,
                    "delay": 0.5,
                    "reason": "quest_workflow:story_dialogue_advance",
                }]

        # No finger — if back at main city, quest execution might be done
        if scene == "main_city":
            logger.info("Quest workflow: back at main city (no finger), checking completion")
            self.phase = self.CHECK_COMPLETION
            self.check_retries = 0
            return []

        # Quest-specific action rules (multi-step patterns like "派遣镇民")
        rule_action = self._match_quest_rule(screenshot)
        if rule_action:
            return rule_action

        # OCR search for action buttons (e.g. "领取" on reward dialog)
        # before close_x — so reward dialogs get claimed, not dismissed.
        action_buttons = self._find_action_buttons(screenshot, None)
        if action_buttons:
            best = action_buttons[0]
            self._track_button_tap(best.name)
            logger.info(
                f"Quest workflow: action button '{best.name}' found "
                f"at ({best.x}, {best.y}) on non-popup screen"
            )
            return [{
                "type": "tap",
                "x": best.x,
                "y": best.y,
                "delay": 1.5,
                "reason": f"quest_workflow:action_button:{best.name}",
            }]
        elif self._exhausted_buttons:
            # All known buttons exhausted — action likely triggered, go check
            logger.info("Quest workflow: all action buttons exhausted, returning to city")
            self.phase = self.RETURN_TO_CITY
            return []

        # Try close_x for full-screen popups that lack dark borders
        # (e.g. "First Purchase Reward") — classified as "unknown" not "popup"
        h, w = screenshot.shape[:2]
        match = self._find_close_x(screenshot)
        if match is not None and match.y <= h * 0.35 and match.x >= w * 0.45:
            logger.info(
                f"Quest workflow: close_x found "
                f"at ({match.x}, {match.y}) on non-popup screen"
            )
            return [{
                "type": "tap",
                "x": match.x,
                "y": match.y,
                "delay": 1.0,
                "reason": "quest_workflow:dismiss_unknown_popup:close_x",
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
        (OCR dismiss → close_x template → back_arrow → tap blank → center tap).
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
            for dismiss_text in self._POPUP_DISMISS_TEXTS:
                for r in all_text:
                    if dismiss_text in r.text:
                        # Verify text is on a colored button, not body text
                        if not is_on_colored_button(screenshot, r.bbox):
                            logger.debug(
                                f"Quest workflow (return): skipping "
                                f"'{dismiss_text}' at {r.center} "
                                f"— not on colored button"
                            )
                            continue
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

            # Stage 2: template matching for close_x button (with red-pixel
            # verification to eliminate false positives).
            # Only accept matches in the top-right region.
            h, w = screenshot.shape[:2]
            match = self._find_close_x(screenshot)
            if match is not None:
                if match.y > h * 0.35 or match.x < w * 0.45:
                    logger.debug(
                        f"Quest workflow (return): rejected close_x "
                        f"at ({match.x}, {match.y}) — outside expected region"
                    )
                else:
                    logger.info(
                        f"Quest workflow (return): popup close_x "
                        f"at ({match.x}, {match.y})"
                    )
                    self.popup_back_count = 0
                    return [{
                        "type": "tap",
                        "x": match.x,
                        "y": match.y,
                        "delay": 1.0,
                        "reason": "quest_workflow:return_dismiss_popup:close_x",
                    }]

            # Escalation: back_arrow → tap blank → center tap
            # (game ignores Android BACK button)
            self.popup_back_count += 1
            if self.popup_back_count <= 2:
                match = self._find_back_arrow(screenshot)
                if match is not None:
                    logger.info(
                        f"Quest workflow (return): popup tapping back_arrow "
                        f"at ({match.x}, {match.y}) "
                        f"({self.popup_back_count}/2)"
                    )
                    return [{
                        "type": "tap",
                        "x": match.x,
                        "y": match.y,
                        "delay": 1.0,
                        "reason": "quest_workflow:return_dismiss_popup:back_arrow",
                    }]
                h, w = screenshot.shape[:2]
                logger.info(
                    f"Quest workflow (return): popup tapping blank area "
                    f"({self.popup_back_count}/2)"
                )
                return [{
                    "type": "tap",
                    "x": w // 2,
                    "y": int(h * 0.95),
                    "delay": 1.0,
                    "reason": "quest_workflow:return_dismiss_popup:tap_blank",
                }]

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

            # Final: reset and tap blank area
            self.popup_back_count = 0
            logger.info("Quest workflow (return): popup reset, tapping blank area")
            return [{
                "type": "tap",
                "x": w // 2,
                "y": int(h * 0.95),
                "delay": 1.0,
                "reason": "quest_workflow:return_dismiss_popup:tap_blank_reset",
            }]

        # Not a popup — try OCR navigation text or back_arrow
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

        After CLAIM_REWARD clicks the quest text, a reward dialog may appear
        that requires clicking "领取".  If the quest bar is not visible
        (covered by dialog), look for claim buttons before assuming done.
        """
        info = self.quest_bar_detector.detect(screenshot)

        if not info.visible:
            # Quest bar hidden — likely a reward dialog is covering it.
            # Look for "领取" or other claim buttons before assuming done.
            ocr = self.element_detector.ocr
            all_text = ocr.find_all_text(screenshot)
            for claim_text in ["领取", "领取奖励", "确定", "确认"]:
                for r in all_text:
                    if claim_text in r.text:
                        cx, cy = r.center
                        logger.info(
                            f"Quest workflow (verify): tapping '{claim_text}' "
                            f"at ({cx}, {cy}) in reward dialog"
                        )
                        return [{
                            "type": "tap",
                            "x": cx,
                            "y": cy,
                            "delay": 2.0,
                            "reason": f"quest_workflow:verify_claim:{claim_text}",
                        }]

            # No claim button found — probably done
            logger.info("Quest workflow: quest bar not visible after claim, assuming done")
            self.phase = self.IDLE
            return []

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

    # All finger template variants: (cache_name, transform, flip_type)
    # transform: None=original, int=cv2.flip code, str "cwN"=CW rotation by N°
    _FINGER_VARIANTS = [
        ("icons/tutorial_finger",           None,    "normal"),
        ("icons/tutorial_finger_hflip",     1,       "hflip"),
        ("icons/tutorial_finger_vflip",     0,       "vflip"),
        ("icons/tutorial_finger_hvflip",   -1,       "hvflip"),
        ("icons/tutorial_finger_rot117cw", "cw117",  "rot117cw"),
    ]

    def _ensure_flipped_finger_template(self) -> None:
        """Create all finger template variants (flips and rotations).

        The game shows the finger icon in various orientations.
        For each variant, caches the template + mask for stage-1 matching,
        and stores BGR + boolean mask for stage-2 masked NCC.
        """
        self._finger_ncc = {}
        try:
            import cv2
            tm = self.element_detector.template_matcher
            cache = tm._cache
            if not isinstance(cache, dict):
                return

            base_name = "icons/tutorial_finger"
            entry = cache.get(base_name)
            if entry is None or not isinstance(entry, tuple):
                return

            tpl, mask = entry

            # Build boolean mask for NCC
            if mask is not None:
                base_bool_mask = mask[:, :, 0] > 128
            else:
                base_bool_mask = np.ones(tpl.shape[:2], dtype=bool)

            # Store per-variant NCC data: {flip_type: (bgr, bool_mask)}
            self._finger_ncc = {
                "normal": (tpl.copy(), base_bool_mask),
            }

            for cache_name, transform, flip_type in self._FINGER_VARIANTS:
                if transform is None:
                    continue  # normal — already in cache
                if cache_name in cache:
                    continue

                if isinstance(transform, str) and transform.startswith("cw"):
                    # Clockwise rotation variant (e.g. "cw135" = 135° CW)
                    angle_cw = int(transform[2:])
                    h, w = tpl.shape[:2]
                    center = (w / 2, h / 2)
                    M = cv2.getRotationMatrix2D(center, -angle_cw, 1.0)
                    cos_v = abs(M[0, 0])
                    sin_v = abs(M[0, 1])
                    new_w = int(h * sin_v + w * cos_v)
                    new_h = int(h * cos_v + w * sin_v)
                    M[0, 2] += (new_w - w) / 2
                    M[1, 2] += (new_h - h) / 2
                    var_tpl = cv2.warpAffine(tpl, M, (new_w, new_h))
                    var_mask = (cv2.warpAffine(mask, M, (new_w, new_h))
                                if mask is not None else None)
                    var_bool = cv2.warpAffine(
                        base_bool_mask.astype(np.uint8), M, (new_w, new_h)
                    ).astype(bool)
                else:
                    # Flip variant (transform is int: -1, 0, or 1)
                    var_tpl = cv2.flip(tpl, transform)
                    var_mask = (cv2.flip(mask, transform)
                                if mask is not None else None)
                    var_bool = cv2.flip(
                        base_bool_mask.astype(np.uint8), transform
                    ).astype(bool)

                cache[cache_name] = (var_tpl, var_mask)
                self._finger_ncc[flip_type] = (var_tpl.copy(), var_bool)

            logger.debug(
                f"Created finger template variants: "
                f"{list(self._finger_ncc.keys())}"
            )
        except Exception:
            self._finger_ncc = {}

    # Stage-1 threshold (TM_CCORR_NORMED with mask).
    # Lowered from 0.93 to 0.85 to catch partially-visible fingers;
    # false positives are caught by stage-2 validation instead.
    _FINGER_CONFIDENCE_THRESHOLD = 0.85

    # Stage-2 threshold (masked NCC — correlation on opaque pixels only).
    # Quest-guide finger: NCC 0.98+.  Battle-scene finger (with glow
    # overlay): NCC ~0.47–0.53.  False positives: ~0.20–0.40.
    # Threshold 0.45 catches both contexts with ≥0.05 margin over
    # false positives.
    _FINGER_NCC_THRESHOLD = 0.45

    def _verify_finger_ncc(self, screenshot: np.ndarray,
                            cx: int, cy: int,
                            flip_type: str) -> float:
        """Stage-2 validation: NCC on masked (opaque) pixels only.

        Computes normalized cross-correlation between template and screenshot
        crop, considering only the pixels where the template is opaque.
        This ignores background entirely, making it robust to varying
        game backgrounds around the finger.

        Returns the NCC score, or -1.0 on error / 1.0 if validation unavailable.
        """
        ncc_entry = self._finger_ncc.get(flip_type)
        if ncc_entry is None:
            return 1.0  # skip validation if unavailable

        tpl, msk = ncc_entry
        th, tw = tpl.shape[:2]
        sh, sw = screenshot.shape[:2]
        x1, y1 = cx - tw // 2, cy - th // 2
        if x1 < 0 or y1 < 0 or x1 + tw > sw or y1 + th > sh:
            return -1.0

        crop = screenshot[y1:y1 + th, x1:x1 + tw]
        t = tpl[msk].astype(np.float32).flatten()
        s = crop[msk].astype(np.float32).flatten()
        t = t - t.mean()
        s = s - s.mean()
        denom = np.sqrt(np.dot(t, t) * np.dot(s, s))
        if denom < 1e-10:
            return 0.0
        return float(np.dot(t, s) / denom)

    def _detect_tutorial_finger(self, screenshot: np.ndarray) -> tuple:
        """Detect tutorial finger with two-stage validation.

        Checks all orientation variants (normal, h-flip, v-flip, hv-flip).

        Stage 1: TM_CCORR_NORMED with mask (sensitive, may have false positives).
        Stage 2: Masked NCC on opaque pixels only (pattern-based,
                 eliminates false positives).

        Returns:
            (match, flip_type) where match is an Element or None,
            and flip_type is one of "normal", "hflip", "vflip", "hvflip".
        """
        verified = []
        for cache_name, _, flip_type in self._FINGER_VARIANTS:
            match = self.element_detector.locate(
                screenshot, cache_name, methods=["template"]
            )
            if match is None:
                continue

            # Stage-1: filter by CCORR confidence
            if match.confidence < self._FINGER_CONFIDENCE_THRESHOLD:
                logger.debug(
                    f"Finger {flip_type} rejected (stage1): "
                    f"conf={match.confidence:.3f}"
                )
                continue

            # Stage-2: masked NCC
            ncc = self._verify_finger_ncc(
                screenshot, match.x, match.y, flip_type)
            if ncc < self._FINGER_NCC_THRESHOLD:
                logger.debug(
                    f"Finger {flip_type} rejected (stage2): ncc={ncc:.3f} "
                    f"at ({match.x}, {match.y})"
                )
                continue

            logger.debug(
                f"Finger {flip_type} verified: conf={match.confidence:.3f}, "
                f"ncc={ncc:.3f} at ({match.x}, {match.y})"
            )
            verified.append((match, flip_type))

        if not verified:
            return None, "normal"

        # Pick highest confidence; prefer "normal" on ties.
        verified.sort(key=lambda v: (v[0].confidence, v[1] == "normal"),
                      reverse=True)
        return verified[0]

    def _find_back_arrow(self, screenshot: np.ndarray):
        """Detect back_arrow button (left arrow) via template matching.

        Returns an Element or None.
        """
        return self.element_detector.locate(
            screenshot, "buttons/back_arrow", methods=["template"]
        )

    # ---- close_x detection with red-pixel verification ----

    # Red-pixel verification thresholds for close_x detection.
    # Real close_x: red X on non-red background -> red_opaque ~0.84, red_bg ~0.03.
    # Skin false positive: red everywhere        -> red_opaque ~0.94, red_bg ~0.74.
    _CLOSE_X_RED_OPAQUE_MIN = 0.15   # min red ratio in opaque (X shape) area
    _CLOSE_X_RED_BG_MAX = 0.30       # max red ratio in transparent (between arms) area

    def _find_close_x(self, screenshot: np.ndarray):
        """Detect close_x button with red-pixel verification.

        Uses multi-match to find all CCORR candidates, then verifies each
        by checking:
        1. The opaque (X shape) area contains enough red pixels.
        2. The transparent (background between X arms) area does NOT contain
           too many red pixels (eliminates skin-tone false positives).

        Returns an Element or None.
        """
        import cv2
        from vision.element_detector import Element

        tm = self.element_detector.template_matcher

        # CCORR_NORMED with alpha mask produces many false positives on
        # colored backgrounds (all scoring higher than the real match).
        # We scan up to 50 candidates and pick the best verified one.
        candidates = tm.match_one_multi(screenshot, "buttons/close_x",
                                        max_matches=50)
        if not candidates:
            return None

        entry = tm._cache.get("buttons/close_x")
        if entry is None:
            return Element(name="close_x", source="template",
                           x=candidates[0].x, y=candidates[0].y,
                           confidence=candidates[0].confidence,
                           bbox=candidates[0].bbox)
        _, mask = entry
        if mask is not None:
            opaque = mask[:, :, 0] > 0
            transparent = ~opaque
        else:
            opaque = None
            transparent = None

        best = None
        best_score = -1.0
        for m in candidates:
            x1, y1, x2, y2 = m.bbox
            patch = screenshot[y1:y2, x1:x2]
            hsv = cv2.cvtColor(patch, cv2.COLOR_BGR2HSV)
            # Red in HSV: H in [0,10] or [170,180], S > 80, V > 80
            red1 = cv2.inRange(hsv, (0, 80, 80), (10, 255, 255))
            red2 = cv2.inRange(hsv, (170, 80, 80), (180, 255, 255))
            red_px = red1 | red2

            if opaque is not None and transparent is not None:
                red_opaque = (red_px[opaque] > 0).sum() / opaque.sum()
                red_bg = (red_px[transparent] > 0).sum() / transparent.sum()
            else:
                red_opaque = (red_px > 0).sum() / red_px.size
                red_bg = 0.0

            # Reject: not enough red in X area, or too much red in background
            if (red_opaque < self._CLOSE_X_RED_OPAQUE_MIN
                    or red_bg > self._CLOSE_X_RED_BG_MAX):
                continue

            # Score: high red_opaque with low red_bg is best
            score = red_opaque - red_bg
            if score > best_score:
                best_score = score
                best = m

        if best is None:
            logger.debug("close_x: no candidate passed red-pixel verification")
            return None

        logger.debug(
            f"close_x verified at ({best.x}, {best.y}) "
            f"ccorr={best.confidence:.3f}"
        )
        return Element(name="close_x", source="template",
                       x=best.x, y=best.y,
                       confidence=best.confidence, bbox=best.bbox)

    def _track_button_tap(self, button_text: str) -> None:
        """Track consecutive taps on the same action button.

        If the same button is tapped _ACTION_BUTTON_EXHAUST_THRESHOLD times
        in a row, add it to the exhausted set so _find_action_buttons skips
        it on subsequent iterations.
        """
        if button_text == self._last_action_button_text:
            self._action_button_repeat_count += 1
        else:
            self._last_action_button_text = button_text
            self._action_button_repeat_count = 1
        if self._action_button_repeat_count >= self._ACTION_BUTTON_EXHAUST_THRESHOLD:
            self._exhausted_buttons.add(button_text)
            self._last_action_button_text = ""
            self._action_button_repeat_count = 0

    def _match_quest_rule(self, screenshot: np.ndarray) -> list[dict] | None:
        """Match current quest against quest_scripts and delegate to QuestScriptRunner.

        On first match, loads steps into ``_script_runner``.  Subsequent
        calls to ``execute_one()`` advance through the script one step per
        iteration.

        Returns ``None`` when all steps are done or no rule matches,
        letting the caller fall through to generic action buttons / LLM.
        """
        if not self._quest_scripts or not self.target_quest_name:
            return None

        for rule in self._quest_scripts:
            pattern = rule.get("pattern", "")
            if not pattern or not re.search(pattern, self.target_quest_name):
                continue

            steps = rule.get("steps", [])
            if not steps:
                return None

            # Load steps into runner if not already loaded for this pattern
            if self._loaded_quest_pattern != pattern:
                self._script_runner.load(steps)
                self._loaded_quest_pattern = pattern
                logger.info(
                    f"Quest rule '{pattern}': loaded {len(steps)} steps "
                    f"into script runner"
                )

            # Script aborted — reset and fall through
            if self._script_runner.is_aborted():
                logger.warning(
                    f"Quest rule '{pattern}': script aborted — "
                    f"{self._script_runner.abort_reason}"
                )
                self._script_runner.reset()
                self._loaded_quest_pattern = ""
                return None

            # All steps done — fall through to generic logic
            if self._script_runner.is_done():
                return None

            # Execute one step
            actions = self._script_runner.execute_one(screenshot)
            if actions is not None:
                step_desc = ""
                cur = self._script_runner.current_step
                if cur:
                    step_desc = cur.get("description", "")
                logger.info(
                    f"Quest rule '{pattern}' step "
                    f"{self._script_runner.step_index}/{len(steps)}: "
                    f"{step_desc}"
                )
            return actions

        return None

    def _grid_to_pixel(self, screenshot: np.ndarray,
                       grid_label: str) -> tuple[int, int] | None:
        """Convert a grid label like 'F5' to pixel coordinates.

        Uses the screenshot dimensions and the configured grid size.
        Column A=0, B=1, ...; Row 1=0, 2=1, ...
        Returns center pixel of the grid cell, or None on invalid label.
        """
        if len(grid_label) < 2:
            return None
        col_char = grid_label[0].upper()
        row_str = grid_label[1:]
        if not col_char.isalpha() or not row_str.isdigit():
            return None
        col = ord(col_char) - ord('A')
        row = int(row_str) - 1
        h, w = screenshot.shape[:2]
        cols = 8  # default
        rows = 6
        cell_w = w / cols
        cell_h = h / rows
        if col < 0 or col >= cols or row < 0 or row >= rows:
            return None
        cx = int(cell_w * (col + 0.5))
        cy = int(cell_h * (row + 0.5))
        return cx, cy

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
            if tpl_name in self._exhausted_buttons:
                continue
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
        # Pass 1 (strict): require colored button background.
        # Pass 2 (relaxed): near-exact OCR matches in bottom half of screen,
        #   skipping is_on_colored_button.  Catches buttons with dark/dim
        #   backgrounds (e.g. battle prep "一键上阵", "出战").
        found: list[Element] = []
        seen_texts: set[str] = set()
        h = screenshot.shape[0]
        for btn_text in self._ACTION_BUTTON_TEXTS:
            if btn_text in seen_texts:
                continue
            if btn_text in self._exhausted_buttons:
                continue
            btn_lower = btn_text.lower()
            # Filters to exclude body text matches:
            # 1. Short text: keyword + ≤4 extra chars (rejects "建议建造兵营" matching "建造")
            # 2. Colored button: high-saturation background (rejects beige/white body text)
            matches = [(r.center[0], r.center[1]) for r in all_results
                       if btn_lower in r.text.lower()
                       and len(r.text) <= len(btn_text) + 4
                       and is_on_colored_button(screenshot, r.bbox)
                       # "行军" in top half is a march queue label, not a button
                       and not (btn_text == "行军" and r.center[1] < h * 0.5)]
            if matches:
                # Pick topmost occurrence of this button text
                best = min(matches, key=lambda m: m[1])
                found.append(Element(name=btn_text, x=best[0], y=best[1],
                                     confidence=1.0, source="ocr",
                                     bbox=(best[0], best[1], best[0], best[1])))
                seen_texts.add(btn_text)

        # Pass 2 (relaxed): near-exact matches without colored button check.
        # Only for bottom-half of screen (where action buttons live) and
        # OCR text that closely matches the keyword (≤1 extra char).
        if not found:
            for btn_text in self._ACTION_BUTTON_TEXTS:
                if btn_text in seen_texts:
                    continue
                if btn_text in self._exhausted_buttons:
                    continue
                btn_lower = btn_text.lower()
                matches = [(r.center[0], r.center[1]) for r in all_results
                           if btn_lower in r.text.lower()
                           and len(r.text) <= len(btn_text) + 1
                           and r.center[1] > h * 0.5
                           and not (btn_text == "行军" and r.center[1] < h * 0.5)]
                if matches:
                    best = min(matches, key=lambda m: m[1])
                    logger.debug(
                        f"Action button OCR (relaxed): '{btn_text}' "
                        f"at ({best[0]},{best[1]})"
                    )
                    found.append(Element(name=btn_text, x=best[0], y=best[1],
                                         confidence=0.9, source="ocr",
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

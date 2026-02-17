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
        "建造", "升级", "训练", "研究", "确定", "前往",
        "开始", "领取", "使用", "派遣", "出征",
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
        self.max_execute_iterations: int = 20
        self.check_retries: int = 0
        self.max_check_retries: int = 3
        self.verify_retries: int = 0
        self.max_verify_retries: int = 3

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

        # Check for tutorial finger icon FIRST (even on main_city)
        # Matches both normal and horizontally flipped orientations
        finger_match, is_flipped = self._detect_tutorial_finger(screenshot)
        if finger_match is not None:
            # Finger detected — look for actionable button text via OCR
            button = self._find_action_button(screenshot, finger_match)
            if button is not None:
                logger.info(
                    f"Quest workflow: finger detected, tapping button "
                    f"'{button.name}' at ({button.x}, {button.y}) x{self._RAPID_TAP_COUNT}"
                )
                # Rapid-tap: furniture upgrade buttons can be clicked
                # continuously (~10% progress per click), so send multiple
                # taps in one step to fill the progress bar quickly.
                return [{
                    "type": "tap",
                    "x": button.x,
                    "y": button.y,
                    "delay": 0.3,
                    "reason": f"quest_workflow:finger_button:{button.name}",
                }] * self._RAPID_TAP_COUNT

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
        """Navigate back to main city after quest execution."""
        if scene == "main_city":
            logger.info("Quest workflow: returned to main city, checking completion")
            self.phase = self.CHECK_COMPLETION
            self.check_retries = 0
            return []

        # Use same navigation logic as ensure_main_city
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
        """Verify that quest name changed (reward was successfully claimed)."""
        info = self.quest_bar_detector.detect(screenshot)

        if not info.visible:
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

    def _find_action_button(self, screenshot: np.ndarray,
                            finger_match) -> "Element | None":
        """Find an actionable button on screen.

        Priority:
        1. Template matching for known button images (most reliable).
        2. OCR text search as fallback, preferring topmost match.
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
                return match

        # Stage 2: OCR fallback — find all text, pick topmost match
        ocr = self.element_detector.ocr
        all_results = ocr.find_all_text(screenshot)
        if not all_results:
            return None

        candidates: list[tuple[str, int, int]] = []
        for btn_text in self._ACTION_BUTTON_TEXTS:
            btn_lower = btn_text.lower()
            for r in all_results:
                if btn_lower in r.text.lower():
                    candidates.append((btn_text, r.center[0], r.center[1]))

        if not candidates:
            return None

        best = min(candidates, key=lambda c: c[2])
        logger.debug(
            f"Action button OCR: {len(candidates)} candidates, "
            f"picked '{best[0]}' at ({best[1]},{best[2]})"
        )
        return Element(name=best[0], x=best[1], y=best[2],
                       confidence=1.0, source="ocr",
                       bbox=(best[1], best[2], best[1], best[2]))

    def _sync_to_game_state(self) -> None:
        """Sync workflow state to game_state for persistence."""
        self.game_state.quest_workflow_phase = self.phase
        self.game_state.quest_workflow_target = self.target_quest_name

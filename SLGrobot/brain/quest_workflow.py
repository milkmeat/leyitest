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
        """Read quest bar to get current quest name.

        If red badge detected, prioritize claiming pending rewards first
        by clicking the scroll icon.
        """
        info = self.quest_bar_detector.detect(screenshot)

        if not info.visible:
            logger.warning("Quest workflow: quest bar not visible, aborting")
            self.abort()
            return []

        # Red badge = pending rewards, click scroll to claim first
        if info.has_red_badge and info.scroll_icon_pos:
            logger.info("Quest workflow: red badge detected, clicking scroll to claim")
            return [{
                "type": "tap",
                "x": info.scroll_icon_pos[0],
                "y": info.scroll_icon_pos[1],
                "delay": 1.0,
                "reason": "quest_workflow:claim_pending_reward",
            }]

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
        - scene == main_city -> CHECK_COMPLETION (quest might be done)
        - tutorial finger detected -> tap finger position
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

        # If we're back at main city, quest execution might be done
        if scene == "main_city":
            logger.info("Quest workflow: back at main city, checking completion")
            self.phase = self.CHECK_COMPLETION
            self.check_retries = 0
            return []

        # Check for tutorial finger icon
        finger_match = self.element_detector.locate(
            screenshot, "icons/tutorial_finger", methods=["template"]
        )
        if finger_match is not None:
            logger.info(
                f"Quest workflow: tutorial finger at ({finger_match.x}, {finger_match.y})"
            )
            return [{
                "type": "tap",
                "x": finger_match.x,
                "y": finger_match.y,
                "delay": 1.0,
                "reason": "quest_workflow:follow_tutorial_finger",
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

    def _sync_to_game_state(self) -> None:
        """Sync workflow state to game_state for persistence."""
        self.game_state.quest_workflow_phase = self.phase
        self.game_state.quest_workflow_target = self.target_quest_name

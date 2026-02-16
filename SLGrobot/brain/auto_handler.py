"""Auto Handler - Instant automatic operations that never need LLM (<100ms).

Handles:
- Close popups (template match X button)
- Claim rewards (detect red dots / reward indicators)
- Skip loading/waiting screens
"""

import logging

import numpy as np

from vision.template_matcher import TemplateMatcher
from vision.element_detector import ElementDetector, Element
from state.game_state import GameState

logger = logging.getLogger(__name__)


class AutoHandler:
    """Instant auto-actions: close popups, claim rewards, skip loading.

    These actions are safe to execute without any strategic planning.
    They run every loop iteration and should complete in <100ms.
    """

    # Templates that indicate dismissible popups
    POPUP_CLOSE_TEMPLATES = [
        "buttons/close",
        "buttons/close_x",
        "buttons/x",
    ]

    # Templates that indicate claimable rewards
    REWARD_TEMPLATES = [
        "buttons/claim",
        "buttons/collect",
        "buttons/ok",
        "buttons/confirm",
    ]

    # Text patterns for auto-actions (OCR-based)
    CLOSE_TEXT_PATTERNS = ["关闭", "close", "×", "X"]
    CLAIM_TEXT_PATTERNS = ["领取", "claim", "collect", "收集"]

    def __init__(self, template_matcher: TemplateMatcher,
                 element_detector: ElementDetector) -> None:
        self.template_matcher = template_matcher
        self.detector = element_detector

    def get_actions(self, screenshot: np.ndarray, game_state: GameState) -> list[dict]:
        """Detect and return auto-actions for the current screen.

        Returns list of action dicts ready for execution.
        Actions are ordered by priority: popups first, then rewards.
        """
        actions = []

        # 1. Close popups
        popup_action = self._check_popup(screenshot)
        if popup_action:
            actions.append(popup_action)
            return actions  # Close popup first, then re-evaluate

        # 2. Claim visible rewards / red dots
        reward_action = self._check_rewards(screenshot)
        if reward_action:
            actions.append(reward_action)

        # 3. Skip loading screens
        skip_action = self._check_loading(screenshot, game_state)
        if skip_action:
            actions.append(skip_action)

        return actions

    def _check_popup(self, screenshot: np.ndarray) -> dict | None:
        """Check for popup close buttons."""
        # Try template matching first
        for template_name in self.POPUP_CLOSE_TEMPLATES:
            match = self.template_matcher.match_one(screenshot, template_name)
            if match is not None:
                logger.info(f"Auto: popup close button found '{template_name}'")
                return {
                    "type": "tap",
                    "x": match.x,
                    "y": match.y,
                    "delay": 0.5,
                    "reason": f"auto_close_popup:{template_name}",
                }

        # Try OCR-based detection
        for text in self.CLOSE_TEXT_PATTERNS:
            element = self.detector.locate(screenshot, text, methods=["ocr"])
            if element is not None:
                logger.info(f"Auto: close text found '{text}'")
                return {
                    "type": "tap",
                    "x": element.x,
                    "y": element.y,
                    "delay": 0.5,
                    "reason": f"auto_close_popup_text:{text}",
                }

        return None

    def _check_rewards(self, screenshot: np.ndarray) -> dict | None:
        """Check for claimable rewards."""
        # Try template matching
        for template_name in self.REWARD_TEMPLATES:
            match = self.template_matcher.match_one(screenshot, template_name)
            if match is not None:
                logger.info(f"Auto: reward button found '{template_name}'")
                return {
                    "type": "tap",
                    "x": match.x,
                    "y": match.y,
                    "delay": 0.5,
                    "reason": f"auto_claim_reward:{template_name}",
                }

        # Try OCR-based detection
        for text in self.CLAIM_TEXT_PATTERNS:
            element = self.detector.locate(screenshot, text, methods=["ocr"])
            if element is not None:
                logger.info(f"Auto: claim text found '{text}'")
                return {
                    "type": "tap",
                    "x": element.x,
                    "y": element.y,
                    "delay": 0.5,
                    "reason": f"auto_claim_reward_text:{text}",
                }

        return None

    def _check_loading(self, screenshot: np.ndarray, game_state: GameState) -> dict | None:
        """Check for loading/waiting screens that can be skipped."""
        if game_state.scene == "loading":
            # Tap center to try to skip
            h, w = screenshot.shape[:2]
            logger.debug("Auto: tapping center to skip loading")
            return {
                "type": "tap",
                "x": w // 2,
                "y": h // 2,
                "delay": 1.0,
                "reason": "auto_skip_loading",
            }
        return None

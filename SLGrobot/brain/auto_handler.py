"""Auto Handler - Instant automatic operations that never need LLM (<100ms).

Handles:
- Close known popups (identified by content, then tap close_x)
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

    # Known popup patterns: (identifier_template, close_template)
    # When identifier is matched, tap the close template to dismiss.
    KNOWN_POPUPS = [
        ("buttons/view", "buttons/close_x"),       # Alliance recruit message
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
    CLAIM_TEXT_PATTERNS = ["领取", "claim", "collect", "收集", "一键领取"]

    def __init__(self, template_matcher: TemplateMatcher,
                 element_detector: ElementDetector,
                 game_profile=None) -> None:
        self.template_matcher = template_matcher
        self.detector = element_detector
        if game_profile:
            if game_profile.known_popups:
                self._known_popups = [tuple(p) for p in game_profile.known_popups]
            else:
                self._known_popups = self.KNOWN_POPUPS
            self._reward_templates = (
                game_profile.reward_templates or self.REWARD_TEMPLATES)
            self._close_text_patterns = (
                game_profile.close_text_patterns or self.CLOSE_TEXT_PATTERNS)
            self._claim_text_patterns = (
                game_profile.claim_text_patterns or self.CLAIM_TEXT_PATTERNS)
        else:
            self._known_popups = self.KNOWN_POPUPS
            self._reward_templates = self.REWARD_TEMPLATES
            self._close_text_patterns = self.CLOSE_TEXT_PATTERNS
            self._claim_text_patterns = self.CLAIM_TEXT_PATTERNS

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
        """Check for known dismissible popups by content, then tap close button.

        Each known popup is identified by a content template (e.g. "查看" button
        for alliance recruitment). Only when the identifier matches do we look
        for the corresponding close button. This avoids accidentally closing
        dialogs that the bot intentionally opened.
        """
        for identifier, close_template in self._known_popups:
            id_match = self.template_matcher.match_one(screenshot, identifier)
            if id_match is None:
                continue

            # Identifier matched — find the close button
            close_match = self.template_matcher.match_one(screenshot, close_template)
            if close_match is not None:
                logger.info(
                    f"Auto: known popup detected ('{identifier}'), "
                    f"closing via '{close_template}' at ({close_match.x}, {close_match.y})"
                )
                return {
                    "type": "tap",
                    "x": close_match.x,
                    "y": close_match.y,
                    "delay": 0.5,
                    "reason": f"auto_close_popup:{identifier}",
                }

            logger.warning(
                f"Auto: popup identified ('{identifier}') but close button "
                f"'{close_template}' not found"
            )

        return None

    def _check_rewards(self, screenshot: np.ndarray) -> dict | None:
        """Check for claimable rewards."""
        # Try template matching
        for template_name in self._reward_templates:
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
        for text in self._claim_text_patterns:
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

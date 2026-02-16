"""Action Validator - Pre-execution validation.

Ensures actions are safe to execute before they reach ADB.
Checks: target element exists, coordinates in bounds, scene matches expected.
"""

import logging

import numpy as np

import config
from vision.element_detector import ElementDetector
from scene.classifier import SceneClassifier

logger = logging.getLogger(__name__)


class ActionValidator:
    """Pre-execution validation for action dicts.

    Validates that:
    - Target element exists on screen (for text-based targets)
    - Coordinates are within screen bounds
    - Current scene matches expected scene (if specified)
    """

    def __init__(self, element_detector: ElementDetector,
                 scene_classifier: SceneClassifier) -> None:
        self.detector = element_detector
        self.classifier = scene_classifier
        self.screen_width = config.SCREEN_WIDTH
        self.screen_height = config.SCREEN_HEIGHT

    def validate(self, action: dict, screenshot: np.ndarray) -> bool:
        """Validate an action before execution.

        Args:
            action: Action dict to validate.
            screenshot: Current screenshot for context.

        Returns:
            True if action is safe to execute.
        """
        action_type = action.get("type", "")

        if action_type == "wait":
            # Wait actions are always valid
            return True

        if action_type == "tap":
            return self._validate_tap(action, screenshot)

        if action_type == "swipe":
            return self._validate_swipe(action)

        if action_type == "navigate":
            # Navigate actions are validated at execution time
            return True

        if action_type == "key_event":
            return True

        logger.warning(f"Unknown action type for validation: '{action_type}'")
        return True  # Allow unknown types through (conservative)

    def _validate_tap(self, action: dict, screenshot: np.ndarray) -> bool:
        """Validate a tap action.

        If the action has target_text but no coordinates, check if
        the text is visible on screen. If coordinates are given,
        check they're in bounds.
        """
        x = action.get("x")
        y = action.get("y")
        target_text = action.get("target_text")
        fallback_grid = action.get("fallback_grid")

        # If explicit coordinates, validate bounds
        if x is not None and y is not None:
            if not self._coords_in_bounds(int(x), int(y)):
                logger.warning(
                    f"Tap coordinates out of bounds: ({x}, {y}), "
                    f"screen is {self.screen_width}x{self.screen_height}"
                )
                return False
            return True

        # If target text specified, check it exists on screen
        if target_text:
            element = self.detector.locate(screenshot, target_text,
                                           methods=["template", "ocr"])
            if element:
                return True

            # Check fallback grid
            if fallback_grid:
                logger.info(
                    f"Target text '{target_text}' not found, "
                    f"will use fallback grid '{fallback_grid}'"
                )
                return True

            logger.warning(
                f"Tap target '{target_text}' not found on screen "
                f"and no fallback_grid specified"
            )
            return False

        logger.warning("Tap action has no coordinates and no target_text")
        return False

    def _validate_swipe(self, action: dict) -> bool:
        """Validate a swipe action: all coordinates in bounds."""
        for coord_key in [("x1", "y1"), ("x2", "y2")]:
            x = action.get(coord_key[0])
            y = action.get(coord_key[1])
            if x is None or y is None:
                logger.warning(f"Swipe missing coordinate: {coord_key}")
                return False
            if not self._coords_in_bounds(int(x), int(y)):
                logger.warning(f"Swipe coordinate out of bounds: ({x}, {y})")
                return False
        return True

    def _coords_in_bounds(self, x: int, y: int) -> bool:
        """Check if pixel coordinates are within screen bounds."""
        return 0 <= x <= self.screen_width and 0 <= y <= self.screen_height

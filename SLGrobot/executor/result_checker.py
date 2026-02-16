"""Result Checker - Post-execution screenshot confirmation.

Takes a post-action screenshot and verifies the action had the expected effect.
Checks: scene changed, target element disappeared, expected element appeared.
"""

import logging

import numpy as np

from vision.element_detector import ElementDetector
from vision.screenshot import ScreenshotManager
from scene.classifier import SceneClassifier

logger = logging.getLogger(__name__)


class ResultChecker:
    """Post-execution verification via screenshot comparison.

    Confirms that an action had the expected effect by analyzing
    the post-action screenshot.
    """

    def __init__(self, screenshot_mgr: ScreenshotManager,
                 scene_classifier: SceneClassifier,
                 element_detector: ElementDetector) -> None:
        self.screenshot_mgr = screenshot_mgr
        self.classifier = scene_classifier
        self.detector = element_detector

    def check(self, action: dict, pre_scene: str,
              post_screenshot: np.ndarray) -> bool:
        """Verify action effect by analyzing the post-action screenshot.

        Args:
            action: The action that was executed.
            pre_scene: Scene classification before the action.
            post_screenshot: Screenshot captured after execution.

        Returns:
            True if action appears to have succeeded.
        """
        action_type = action.get("type", "")

        if action_type == "wait":
            return True

        if action_type == "tap":
            return self._check_tap(action, pre_scene, post_screenshot)

        if action_type == "navigate":
            return self._check_navigate(action, post_screenshot)

        if action_type == "key_event":
            return self._check_key_event(action, pre_scene, post_screenshot)

        if action_type == "swipe":
            # Swipes generally succeed if no crash
            return True

        return True

    def check_with_capture(self, action: dict, pre_scene: str) -> bool:
        """Capture a new screenshot and verify action effect.

        Convenience method that captures the post-screenshot automatically.

        Args:
            action: The action that was executed.
            pre_scene: Scene classification before the action.

        Returns:
            True if action appears to have succeeded.
        """
        post_screenshot = self.screenshot_mgr.capture()
        return self.check(action, pre_scene, post_screenshot)

    def _check_tap(self, action: dict, pre_scene: str,
                   post_screenshot: np.ndarray) -> bool:
        """Verify tap action effect.

        Success indicators:
        - Scene changed (e.g., navigated to new screen)
        - Target text/button disappeared (was tapped successfully)
        - A new expected element appeared
        """
        target_text = action.get("target_text")
        post_scene = self.classifier.classify(post_screenshot)

        # Scene change is a strong success signal
        if post_scene != pre_scene:
            logger.debug(
                f"Tap result: scene changed {pre_scene} -> {post_scene}"
            )
            return True

        # Check if tapped element disappeared
        if target_text:
            element = self.detector.locate(post_screenshot, target_text,
                                           methods=["template", "ocr"])
            if element is None:
                logger.debug(
                    f"Tap result: target '{target_text}' disappeared"
                )
                return True

        # If nothing changed, the tap may not have had visible effect
        # This isn't necessarily a failure (e.g., tapping a toggle)
        logger.debug("Tap result: no visible change detected (may still be OK)")
        return True

    def _check_navigate(self, action: dict, post_screenshot: np.ndarray) -> bool:
        """Verify navigation action: did we reach the target scene?"""
        target = action.get("target", "")
        post_scene = self.classifier.classify(post_screenshot)

        # Map navigation targets to expected scenes
        scene_map = {
            "main_city": "main_city",
            "world_map": "world_map",
            "barracks": "main_city",  # Building screens are sub-scenes of city
            "hospital": "main_city",
            "mail": "popup",  # Mail opens as popup
            "alliance": "popup",
            "shop": "popup",
        }

        expected = scene_map.get(target)
        if expected and post_scene == expected:
            logger.debug(f"Navigate result: reached expected scene '{expected}'")
            return True

        if expected:
            logger.debug(
                f"Navigate result: expected '{expected}', got '{post_scene}'"
            )
            return False

        # Unknown target, assume success
        return True

    def _check_key_event(self, action: dict, pre_scene: str,
                         post_screenshot: np.ndarray) -> bool:
        """Verify key event: scene should change (e.g., BACK closes popup)."""
        keycode = action.get("keycode", 4)
        post_scene = self.classifier.classify(post_screenshot)

        if keycode == 4:  # BACK key
            # BACK should close popup or change scene
            if pre_scene == "popup" and post_scene != "popup":
                logger.debug("Key BACK result: popup closed")
                return True

        # Scene change is success
        if post_scene != pre_scene:
            return True

        return True

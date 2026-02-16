"""Action Runner - Execute validated actions via ADB.

Translates action dicts into ADB commands (tap, swipe, key events).
Handles text-based targeting via element detection with fallback to grid cells.
"""

import json
import os
import logging
import time

import numpy as np

import config
from device.adb_controller import ADBController
from device.input_actions import InputActions
from vision.element_detector import ElementDetector
from vision.grid_overlay import GridOverlay
from vision.screenshot import ScreenshotManager

logger = logging.getLogger(__name__)


class ActionRunner:
    """Execute validated action dicts via ADB.

    Supports action types:
    - tap: tap at coordinates or locate target text
    - swipe: swipe between coordinates
    - navigate: follow predefined navigation path
    - wait: sleep for duration or until condition
    - key_event: send Android key event
    """

    def __init__(self, adb: ADBController,
                 input_actions: InputActions,
                 element_detector: ElementDetector,
                 grid_overlay: GridOverlay,
                 screenshot_mgr: ScreenshotManager,
                 nav_paths_file: str = None) -> None:
        self.adb = adb
        self.input_actions = input_actions
        self.detector = element_detector
        self.grid = grid_overlay
        self.screenshot_mgr = screenshot_mgr
        self.nav_paths: dict = {}
        self._load_nav_paths(nav_paths_file or config.NAV_PATHS_FILE)

    def _load_nav_paths(self, filepath: str) -> None:
        """Load predefined navigation paths from JSON."""
        if os.path.exists(filepath):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    self.nav_paths = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"Failed to load nav paths: {e}")

    def execute(self, action: dict) -> bool:
        """Execute a single action dict.

        Args:
            action: Action dict with 'type' and type-specific fields.

        Returns:
            True if action executed successfully.
        """
        action_type = action.get("type", "")
        delay = action.get("delay", 0.5)
        reason = action.get("reason", "")

        logger.info(f"ActionRunner: {action_type} reason='{reason}'")

        success = False

        if action_type == "tap":
            success = self._execute_tap(action)
        elif action_type == "swipe":
            success = self._execute_swipe(action)
        elif action_type == "navigate":
            success = self._execute_navigate(action)
        elif action_type == "wait":
            success = self._execute_wait(action)
            return success  # No extra delay for wait actions
        elif action_type == "key_event":
            success = self._execute_key_event(action)
        else:
            logger.warning(f"Unknown action type: '{action_type}'")
            return False

        # Post-action delay
        if delay > 0:
            time.sleep(delay)

        return success

    def execute_sequence(self, actions: list[dict]) -> int:
        """Execute a sequence of actions.

        Args:
            actions: List of action dicts.

        Returns:
            Number of successfully executed actions.
        """
        success_count = 0
        for action in actions:
            if self.execute(action):
                success_count += 1
            else:
                logger.warning(f"Action failed: {action}")
        return success_count

    def _execute_tap(self, action: dict) -> bool:
        """Execute a tap action.

        Resolution order:
        1. Explicit (x, y) coordinates
        2. Locate target_text via element detection
        3. Use fallback_grid cell center
        """
        x = action.get("x")
        y = action.get("y")
        target_text = action.get("target_text")
        fallback_grid = action.get("fallback_grid")

        # Try explicit coordinates
        if x is not None and y is not None:
            self.adb.tap(int(x), int(y))
            logger.debug(f"Tapped ({x}, {y})")
            return True

        # Try locating target text
        if target_text:
            screenshot = self.screenshot_mgr.capture()
            element = self.detector.locate(screenshot, target_text,
                                           methods=["template", "ocr"])
            if element:
                self.adb.tap(element.x, element.y)
                logger.debug(f"Tapped '{target_text}' at ({element.x}, {element.y})")
                return True

        # Fallback to grid cell
        if fallback_grid:
            try:
                gx, gy = self.grid.cell_to_pixel(fallback_grid)
                self.adb.tap(gx, gy)
                logger.debug(f"Tapped grid cell '{fallback_grid}' at ({gx}, {gy})")
                return True
            except ValueError as e:
                logger.warning(f"Invalid grid cell '{fallback_grid}': {e}")

        logger.warning("Tap action: no valid target found")
        return False

    def _execute_swipe(self, action: dict) -> bool:
        """Execute a swipe action."""
        try:
            x1 = int(action["x1"])
            y1 = int(action["y1"])
            x2 = int(action["x2"])
            y2 = int(action["y2"])
            duration = int(action.get("duration_ms", 300))
            self.adb.swipe(x1, y1, x2, y2, duration)
            logger.debug(f"Swiped ({x1},{y1})->({x2},{y2}) {duration}ms")
            return True
        except (KeyError, ValueError) as e:
            logger.warning(f"Swipe action failed: {e}")
            return False

    def _execute_navigate(self, action: dict) -> bool:
        """Execute a navigation action by following predefined path."""
        target = action.get("target", "")

        if target in self.nav_paths:
            steps = self.nav_paths[target]
            logger.info(f"Navigating to '{target}' ({len(steps)} steps)")
            for step in steps:
                self.execute(step)
            return True

        logger.warning(f"Unknown navigation target: '{target}'")
        return False

    def _execute_wait(self, action: dict) -> bool:
        """Execute a wait action."""
        seconds = action.get("seconds", 1)
        condition = action.get("condition")

        if condition:
            return self._wait_for_condition(condition, timeout=seconds or 10)

        time.sleep(seconds)
        return True

    def _wait_for_condition(self, condition: str, timeout: float = 10) -> bool:
        """Wait until a condition is met or timeout.

        Supported conditions:
        - popup_confirm: wait for a confirmation popup
        - scene_change: wait for scene to change
        - element:<text>: wait for specific text to appear
        """
        start = time.time()
        check_interval = 0.5

        while time.time() - start < timeout:
            screenshot = self.screenshot_mgr.capture()

            if condition == "popup_confirm":
                # Look for confirm/OK buttons
                for text in ["确定", "确认", "OK", "Confirm"]:
                    element = self.detector.locate(screenshot, text,
                                                   methods=["template", "ocr"])
                    if element:
                        logger.debug(f"Condition met: found '{text}'")
                        return True

            elif condition == "scene_change":
                # Any scene classification counts as change detected
                return True

            elif condition.startswith("element:"):
                target = condition[8:]
                element = self.detector.locate(screenshot, target,
                                               methods=["template", "ocr"])
                if element:
                    logger.debug(f"Condition met: element '{target}' found")
                    return True

            time.sleep(check_interval)

        logger.warning(f"Wait condition '{condition}' timed out after {timeout}s")
        return False

    def _execute_key_event(self, action: dict) -> bool:
        """Execute an Android key event."""
        keycode = action.get("keycode", 4)  # Default: BACK
        self.adb.key_event(keycode)
        logger.debug(f"Key event: {keycode}")
        return True

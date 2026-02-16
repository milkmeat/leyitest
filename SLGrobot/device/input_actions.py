"""Input Actions - High-level input wrappers built on ADBController."""

import time
import logging

from .adb_controller import ADBController
import config

logger = logging.getLogger(__name__)


class InputActions:
    """High-level input operations: long press, drag, tap center."""

    def __init__(self, adb: ADBController) -> None:
        self.adb = adb

    def long_press(self, x: int, y: int, duration_ms: int = 1000) -> None:
        """Long press at (x, y) by swiping to the same position."""
        logger.debug(f"Long press at ({x}, {y}) for {duration_ms}ms")
        self.adb.swipe(x, y, x, y, duration_ms)

    def drag(self, x1: int, y1: int, x2: int, y2: int, duration_ms: int = 500) -> None:
        """Drag from (x1,y1) to (x2,y2)."""
        logger.debug(f"Drag from ({x1},{y1}) to ({x2},{y2})")
        self.adb.swipe(x1, y1, x2, y2, duration_ms)

    def tap_center(self) -> None:
        """Tap screen center (dismiss dialogs)."""
        cx = config.SCREEN_WIDTH // 2
        cy = config.SCREEN_HEIGHT // 2
        logger.debug(f"Tap center ({cx}, {cy})")
        self.adb.tap(cx, cy)

    def press_back(self) -> None:
        """Press the Android back button."""
        logger.debug("Press back")
        self.adb.key_event(4)

    def press_home(self) -> None:
        """Press the Android home button."""
        logger.debug("Press home")
        self.adb.key_event(3)

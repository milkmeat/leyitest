"""Screenshot Manager - Screenshot capture, save, and history management."""

import os
import time
from collections import deque
from datetime import datetime

import cv2
import numpy as np
import logging

from device.adb_controller import ADBController

logger = logging.getLogger(__name__)


class ScreenshotManager:
    """Manage screenshot lifecycle: capture, save, and history."""

    def __init__(self, adb: ADBController, save_dir: str, history_size: int = 10) -> None:
        self.adb = adb
        self.save_dir = save_dir
        self._history: deque[np.ndarray] = deque(maxlen=history_size)

        os.makedirs(save_dir, exist_ok=True)

    def capture(self) -> np.ndarray:
        """Capture and return current screenshot. Also stores in history."""
        image = self.adb.screenshot()
        self._history.append(image)
        return image

    def save(self, image: np.ndarray, label: str = "") -> str:
        """Save screenshot to disk with timestamp. Returns file path."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        if label:
            filename = f"{timestamp}_{label}.png"
        else:
            filename = f"{timestamp}.png"

        filepath = os.path.join(self.save_dir, filename)
        cv2.imwrite(filepath, image)
        logger.debug(f"Screenshot saved: {filepath}")
        return filepath

    def capture_and_save(self, label: str = "") -> tuple[np.ndarray, str]:
        """Capture screenshot and save it. Returns (image, filepath)."""
        image = self.capture()
        filepath = self.save(image, label)
        return image, filepath

    def get_recent(self, count: int = 5) -> list[np.ndarray]:
        """Return last N screenshots from memory."""
        recent = list(self._history)
        return recent[-count:] if len(recent) >= count else recent

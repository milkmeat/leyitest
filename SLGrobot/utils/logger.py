"""Game Logger - Logging with screenshot recording."""

import os
import logging
from datetime import datetime

import cv2
import numpy as np

logger = logging.getLogger(__name__)


class GameLogger:
    """Game-specific logger that can attach screenshots to log entries."""

    def __init__(self, log_dir: str = "logs") -> None:
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        self._setup_logging()

    def _setup_logging(self) -> None:
        """Configure Python logging with file and console handlers."""
        root_logger = logging.getLogger()
        if root_logger.handlers:
            return  # already configured

        root_logger.setLevel(logging.DEBUG)

        # Console handler - INFO level
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_fmt = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%H:%M:%S"
        )
        console_handler.setFormatter(console_fmt)

        # File handler - DEBUG level
        log_file = os.path.join(
            self.log_dir,
            f"game_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        )
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_fmt = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        )
        file_handler.setFormatter(file_fmt)

        root_logger.addHandler(console_handler)
        root_logger.addHandler(file_handler)

        logger.info(f"Logging initialized. Log file: {log_file}")

    def _save_screenshot(self, image: np.ndarray, tag: str) -> str:
        """Save a screenshot with a tag for debugging."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        filename = f"{timestamp}_{tag}.png"
        filepath = os.path.join(self.log_dir, filename)
        cv2.imwrite(filepath, image)
        return filepath

    def log_action(self, action: dict, screenshot: np.ndarray | None = None) -> None:
        """Log action with optional screenshot for debugging."""
        action_type = action.get("type", "unknown")
        logger.info(f"Action: {action}")
        if screenshot is not None:
            path = self._save_screenshot(screenshot, f"action_{action_type}")
            logger.debug(f"Action screenshot: {path}")

    def log_state(self, game_state) -> None:
        """Log current game state."""
        logger.info(f"Game state: scene={getattr(game_state, 'scene', 'N/A')}")

    def log_error(self, error: str, screenshot: np.ndarray | None = None) -> None:
        """Log error with screenshot context."""
        logger.error(f"Error: {error}")
        if screenshot is not None:
            path = self._save_screenshot(screenshot, "error")
            logger.error(f"Error screenshot: {path}")

"""Game Logger - Logging with screenshot recording and structured JSON output."""

import json
import os
import logging
from datetime import datetime

import cv2
import numpy as np

logger = logging.getLogger(__name__)


class JSONFormatter(logging.Formatter):
    """Format log records as single-line JSON for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        entry = {
            "ts": self.formatTime(record, "%Y-%m-%dT%H:%M:%S"),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        if record.exc_info and record.exc_info[0] is not None:
            entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(entry, ensure_ascii=False)


class GameLogger:
    """Game-specific logger that can attach screenshots to log entries."""

    def __init__(self, log_dir: str = "logs") -> None:
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        self._screenshot_dir = os.path.join(log_dir, "screenshots")
        os.makedirs(self._screenshot_dir, exist_ok=True)
        self._setup_logging()

    def _setup_logging(self) -> None:
        """Configure Python logging with file, console, and JSON handlers."""
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

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        # File handler - DEBUG level (plain text)
        log_file = os.path.join(self.log_dir, f"game_{timestamp}.log")
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_fmt = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        )
        file_handler.setFormatter(file_fmt)

        # JSON handler - DEBUG level (structured .jsonl)
        jsonl_file = os.path.join(self.log_dir, f"game_{timestamp}.jsonl")
        json_handler = logging.FileHandler(jsonl_file, encoding="utf-8")
        json_handler.setLevel(logging.DEBUG)
        json_handler.setFormatter(JSONFormatter())

        root_logger.addHandler(console_handler)
        root_logger.addHandler(file_handler)
        root_logger.addHandler(json_handler)

        logger.info(f"Logging initialized. Log file: {log_file}")
        logger.info(f"JSON log: {jsonl_file}")

    def _save_screenshot(self, image: np.ndarray, tag: str) -> str:
        """Save a screenshot with a tag for debugging."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        filename = f"{timestamp}_{tag}.png"
        filepath = os.path.join(self.log_dir, filename)
        cv2.imwrite(filepath, image)
        return filepath

    def _save_screenshot_to_dir(self, image: np.ndarray, tag: str) -> str:
        """Save a screenshot to the organized screenshots directory."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        filename = f"{timestamp}_{tag}.png"
        filepath = os.path.join(self._screenshot_dir, filename)
        cv2.imwrite(filepath, image)
        return filepath

    def log_action(self, action: dict, screenshot: np.ndarray | None = None) -> None:
        """Log action with optional screenshot for debugging."""
        action_type = action.get("type", "unknown")
        logger.info(f"Action: {action}")
        if screenshot is not None:
            path = self._save_screenshot(screenshot, f"action_{action_type}")
            logger.debug(f"Action screenshot: {path}")

    def log_action_with_screenshots(self, action: dict,
                                     before: np.ndarray | None = None,
                                     after: np.ndarray | None = None) -> None:
        """Log an action with before/after screenshots for audit trail.

        Args:
            action: Action dict that was executed.
            before: Screenshot taken before the action.
            after: Screenshot taken after the action.
        """
        action_type = action.get("type", "unknown")
        reason = action.get("reason", "")
        logger.info(f"Action executed: {action_type} reason='{reason}'")

        before_path = None
        after_path = None
        if before is not None:
            before_path = self._save_screenshot_to_dir(
                before, f"before_{action_type}"
            )
        if after is not None:
            after_path = self._save_screenshot_to_dir(
                after, f"after_{action_type}"
            )

        logger.debug(
            json.dumps({
                "event": "action",
                "action": action,
                "before_screenshot": before_path,
                "after_screenshot": after_path,
            }, ensure_ascii=False)
        )

    def log_recovery(self, event: str, details: str,
                      screenshot: np.ndarray | None = None) -> None:
        """Log a recovery event with optional screenshot.

        Args:
            event: Recovery event type (e.g., 'stuck_recovery', 'adb_reconnect').
            details: Human-readable description.
            screenshot: Optional screenshot at time of recovery.
        """
        screenshot_path = None
        if screenshot is not None:
            screenshot_path = self._save_screenshot_to_dir(
                screenshot, f"recovery_{event}"
            )

        logger.warning(f"Recovery: {event} - {details}")
        logger.debug(
            json.dumps({
                "event": "recovery",
                "recovery_type": event,
                "details": details,
                "screenshot": screenshot_path,
            }, ensure_ascii=False)
        )

    def log_state(self, game_state) -> None:
        """Log current game state."""
        logger.info(f"Game state: scene={getattr(game_state, 'scene', 'N/A')}")

    def log_error(self, error: str, screenshot: np.ndarray | None = None) -> None:
        """Log error with screenshot context."""
        logger.error(f"Error: {error}")
        if screenshot is not None:
            path = self._save_screenshot(screenshot, "error")
            logger.error(f"Error screenshot: {path}")

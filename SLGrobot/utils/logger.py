"""Game Logger - Logging with screenshot recording and structured JSON output."""

import os
import json
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
        self.loop_count = 0  # set by auto_loop each iteration
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

        # Suppress verbose SDK debug logs (they dump full base64 payloads)
        logging.getLogger("openai").setLevel(logging.INFO)
        logging.getLogger("httpx").setLevel(logging.INFO)
        logging.getLogger("anthropic").setLevel(logging.INFO)

        logger.info(f"Logging initialized. Log file: {log_file}")
        logger.info(f"JSON log: {jsonl_file}")

    def save_loop_screenshot(self, image: np.ndarray, scene: str) -> str:
        """Save one screenshot per loop to the screenshots directory."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        filename = f"L{self.loop_count:03d}_{timestamp}_{scene}.png"
        filepath = os.path.join(self._screenshot_dir, filename)
        cv2.imwrite(filepath, image)
        logger.debug(f"Loop screenshot: {filepath}")
        return filepath

    def log_action(self, action: dict) -> None:
        """Log an executed action."""
        action_type = action.get("type", "unknown")
        reason = action.get("reason", "")
        logger.info(f"Action executed: {action_type} reason='{reason}'")

    def log_recovery(self, event: str, details: str) -> None:
        """Log a recovery event."""
        logger.warning(f"Recovery: {event} - {details}")

    def log_state(self, game_state) -> None:
        """Log current game state."""
        logger.info(f"Game state: scene={getattr(game_state, 'scene', 'N/A')}")

    def log_error(self, error: str) -> None:
        """Log an error."""
        logger.error(f"Error: {error}")

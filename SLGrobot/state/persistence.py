"""State Persistence - Save/load GameState to/from JSON file."""

import json
import os
import logging

from .game_state import GameState

logger = logging.getLogger(__name__)


class StatePersistence:
    """JSON file persistence for GameState."""

    def __init__(self, file_path: str) -> None:
        self.file_path = file_path

    def save(self, game_state: GameState) -> None:
        """Save game state to JSON file.

        Creates parent directories if needed. Writes atomically via temp file.
        """
        os.makedirs(os.path.dirname(self.file_path) or ".", exist_ok=True)

        data = game_state.to_dict()
        tmp_path = self.file_path + ".tmp"
        try:
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            # Atomic rename
            if os.path.exists(self.file_path):
                os.remove(self.file_path)
            os.rename(tmp_path, self.file_path)
            logger.debug(f"State saved to {self.file_path}")
        except Exception as e:
            logger.error(f"Failed to save state: {e}")
            # Cleanup temp file
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
            raise

    def load(self) -> dict | None:
        """Load game state from JSON file.

        Returns state dict or None if file doesn't exist.
        """
        if not os.path.exists(self.file_path):
            logger.info(f"No saved state at {self.file_path}")
            return None

        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            logger.info(f"State loaded from {self.file_path}")
            return data
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Failed to load state from {self.file_path}: {e}")
            return None

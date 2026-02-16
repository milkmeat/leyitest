"""Base Scene Handler - Abstract base class for scene-specific handlers."""

from abc import ABC, abstractmethod

import numpy as np

from vision.element_detector import ElementDetector
from state.game_state import GameState


class BaseSceneHandler(ABC):
    """Abstract base for scene-specific processing.

    Each handler knows how to:
    1. Extract scene-specific information from a screenshot
    2. Report what actions are available in this scene
    """

    def __init__(self, element_detector: ElementDetector,
                 game_state: GameState) -> None:
        self.detector = element_detector
        self.state = game_state

    @abstractmethod
    def extract_info(self, screenshot: np.ndarray) -> dict:
        """Extract scene-specific information from screenshot.

        Returns dict of extracted data (resources, buildings, etc.).
        """

    @abstractmethod
    def get_available_actions(self, screenshot: np.ndarray) -> list[str]:
        """Return list of available action names in this scene."""

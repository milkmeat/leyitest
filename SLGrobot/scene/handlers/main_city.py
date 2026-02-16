"""Main City Scene Handler - Extract resources, buildings, queues."""

import re
import logging

import numpy as np

from vision.element_detector import ElementDetector
from state.game_state import GameState
from .base import BaseSceneHandler

logger = logging.getLogger(__name__)


class MainCityHandler(BaseSceneHandler):
    """Handle main city scene: resource bars, building levels, action buttons."""

    def __init__(self, element_detector: ElementDetector,
                 game_state: GameState) -> None:
        super().__init__(element_detector, game_state)

    def extract_info(self, screenshot: np.ndarray) -> dict:
        """Extract: resource bars, building levels, red dots, queues."""
        info = {
            "resources": {},
            "buildings": [],
            "red_dots": [],
            "buttons": [],
        }

        # Detect all elements on screen
        elements = self.detector.locate_all(screenshot)

        for elem in elements:
            # Categorize elements
            if elem.source == "template":
                if "buttons/" in elem.name:
                    info["buttons"].append({
                        "name": elem.name,
                        "x": elem.x, "y": elem.y,
                    })
                elif "icons/" in elem.name:
                    if "red_dot" in elem.name:
                        info["red_dots"].append({
                            "name": elem.name,
                            "x": elem.x, "y": elem.y,
                        })
            elif elem.source == "ocr":
                # Check for resource-like numbers
                text = elem.text if hasattr(elem, 'text') else elem.name
                if re.search(r'\d+', text):
                    info["resources"][text] = {
                        "x": elem.x, "y": elem.y,
                        "confidence": elem.confidence,
                    }

        logger.debug(
            f"MainCity: {len(info['buttons'])} buttons, "
            f"{len(info['red_dots'])} red dots, "
            f"{len(info['resources'])} resource texts"
        )
        return info

    def get_available_actions(self, screenshot: np.ndarray) -> list[str]:
        """Return available actions in main city."""
        actions = [
            "collect_resources",
            "navigate_world_map",
        ]

        elements = self.detector.locate_all(screenshot)

        for elem in elements:
            name_lower = elem.name.lower()
            if "upgrade" in name_lower or "升级" in name_lower:
                if "upgrade_building" not in actions:
                    actions.append("upgrade_building")
            if "train" in name_lower or "训练" in name_lower:
                if "train_troops" not in actions:
                    actions.append("train_troops")
            if "mail" in name_lower or "邮件" in name_lower:
                if "check_mail" not in actions:
                    actions.append("check_mail")

        return actions

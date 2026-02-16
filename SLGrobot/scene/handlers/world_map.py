"""World Map Scene Handler - Extract tiles, resource nodes, enemies."""

import re
import logging

import numpy as np

from vision.element_detector import ElementDetector
from state.game_state import GameState
from .base import BaseSceneHandler

logger = logging.getLogger(__name__)


class WorldMapHandler(BaseSceneHandler):
    """Handle world map scene: resource nodes, enemies, alliance territory."""

    def __init__(self, element_detector: ElementDetector,
                 game_state: GameState) -> None:
        super().__init__(element_detector, game_state)

    def extract_info(self, screenshot: np.ndarray) -> dict:
        """Extract: visible tiles, resource nodes, enemy positions."""
        info = {
            "resource_nodes": [],
            "enemies": [],
            "marches": [],
            "coordinates": None,
        }

        elements = self.detector.locate_all(screenshot)

        for elem in elements:
            name_lower = elem.name.lower()

            # Detect coordinate display (e.g., "X:123 Y:456")
            coord_match = re.search(
                r'[Xx]\s*[:：]\s*(\d+)\s*[Yy]\s*[:：]\s*(\d+)',
                elem.name
            )
            if coord_match:
                info["coordinates"] = {
                    "x": int(coord_match.group(1)),
                    "y": int(coord_match.group(2)),
                }

            # Detect resource nodes by keywords
            for res in ["食物", "木材", "石材", "金矿", "food", "wood", "stone", "gold"]:
                if res in name_lower:
                    info["resource_nodes"].append({
                        "type": res,
                        "x": elem.x, "y": elem.y,
                    })

            # Detect level indicators for enemies
            level_match = re.search(r'[Ll]v\.?\s*(\d+)', elem.name)
            if level_match:
                info["enemies"].append({
                    "level": int(level_match.group(1)),
                    "x": elem.x, "y": elem.y,
                })

        logger.debug(
            f"WorldMap: {len(info['resource_nodes'])} resource nodes, "
            f"{len(info['enemies'])} enemies, coords={info['coordinates']}"
        )
        return info

    def get_available_actions(self, screenshot: np.ndarray) -> list[str]:
        """Return available actions on world map."""
        actions = [
            "navigate_main_city",
        ]

        info = self.extract_info(screenshot)

        if info["resource_nodes"]:
            actions.append("gather_resource")
        if info["enemies"]:
            actions.append("scout_enemy")
            actions.append("attack_enemy")

        return actions

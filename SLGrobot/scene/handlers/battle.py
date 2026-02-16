"""Battle Scene Handler - Extract battle results, rewards, losses."""

import re
import logging

import numpy as np

from vision.element_detector import ElementDetector
from state.game_state import GameState
from .base import BaseSceneHandler

logger = logging.getLogger(__name__)


class BattleHandler(BaseSceneHandler):
    """Handle battle/combat scene: results, rewards, return actions."""

    def __init__(self, element_detector: ElementDetector,
                 game_state: GameState) -> None:
        super().__init__(element_detector, game_state)

    def extract_info(self, screenshot: np.ndarray) -> dict:
        """Extract: battle result (win/lose), rewards, losses."""
        info = {
            "result": "unknown",  # "victory" | "defeat" | "ongoing" | "unknown"
            "rewards": [],
            "losses": [],
        }

        elements = self.detector.locate_all(screenshot)

        for elem in elements:
            text = elem.name.lower()

            # Detect battle result
            if "胜利" in text or "victory" in text or "win" in text:
                info["result"] = "victory"
            elif "失败" in text or "defeat" in text or "lose" in text:
                info["result"] = "defeat"

            # Detect rewards (numbers near reward labels)
            reward_match = re.search(r'[+＋]\s*([\d,]+)', elem.name)
            if reward_match:
                info["rewards"].append({
                    "text": elem.name,
                    "value": reward_match.group(1),
                    "x": elem.x, "y": elem.y,
                })

            # Detect losses
            loss_match = re.search(r'[-－]\s*([\d,]+)', elem.name)
            if loss_match:
                info["losses"].append({
                    "text": elem.name,
                    "value": loss_match.group(1),
                    "x": elem.x, "y": elem.y,
                })

        logger.debug(f"Battle: result={info['result']}, "
                     f"{len(info['rewards'])} rewards, {len(info['losses'])} losses")
        return info

    def get_available_actions(self, screenshot: np.ndarray) -> list[str]:
        """Return available actions in battle scene."""
        actions = []

        info = self.extract_info(screenshot)

        if info["result"] in ("victory", "defeat"):
            actions.append("collect_reward")
            actions.append("return_to_city")
        elif info["result"] == "ongoing":
            actions.append("wait_battle")

        return actions

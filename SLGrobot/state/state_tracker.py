"""State Tracker - Extract and update game state from screenshots."""

import re
import logging
from datetime import datetime

import numpy as np

from .game_state import GameState, BuildingState
from vision.ocr_locator import OCRLocator
from vision.template_matcher import TemplateMatcher
from vision.quest_bar_detector import QuestBarDetector

logger = logging.getLogger(__name__)


class StateTracker:
    """Extract game state from screenshots via OCR + template matching.

    Called each main loop iteration to keep GameState up to date.
    """

    # Resource names to look for (Chinese game UI)
    RESOURCE_KEYWORDS = {
        "food": ["食物", "粮食", "food"],
        "wood": ["木材", "木头", "wood"],
        "stone": ["石头", "石材", "stone"],
        "gold": ["金币", "金", "gold"],
    }

    def __init__(self, game_state: GameState,
                 ocr_locator: OCRLocator,
                 template_matcher: TemplateMatcher) -> None:
        self.state = game_state
        self.ocr = ocr_locator
        self.template_matcher = template_matcher
        self.quest_bar_detector = QuestBarDetector(template_matcher, ocr_locator)

    def update(self, screenshot: np.ndarray, scene: str) -> None:
        """Update game_state based on current screenshot and scene.

        Extracts resources (OCR), building status, troop info, etc.
        """
        self.state.scene = scene
        self.state.last_update = datetime.now().isoformat()
        self.state.loop_count += 1

        if scene == "main_city":
            self._update_resources(screenshot)
            self._update_buildings(screenshot)
            self._update_quest_bar(screenshot)
        elif scene == "world_map":
            self._update_marches(screenshot)
        elif scene == "battle":
            self._update_battle_result(screenshot)

        logger.debug(
            f"State updated: scene={scene}, "
            f"resources={self.state.resources}, "
            f"loop={self.state.loop_count}"
        )

    def _update_resources(self, screenshot: np.ndarray) -> None:
        """OCR the resource bar at the top of the main city screen.

        Resource bar is typically in the top ~8% of the screen.
        """
        h, w = screenshot.shape[:2]
        # Scan the top resource bar region
        resource_region = (0, 0, w, int(h * 0.08))

        try:
            text_results = self.ocr.find_all_text(
                screenshot[resource_region[1]:resource_region[3],
                           resource_region[0]:resource_region[2]]
            )
        except Exception as e:
            logger.warning(f"OCR failed for resource bar: {e}")
            return

        for result in text_results:
            value = self._parse_number(result.text)
            if value is None:
                continue

            # Try to associate number with a resource by proximity or keyword
            for resource_name, keywords in self.RESOURCE_KEYWORDS.items():
                for kw in keywords:
                    if kw.lower() in result.text.lower():
                        self.state.resources[resource_name] = value
                        logger.debug(f"Resource {resource_name} = {value}")
                        break

        # Also try to extract standalone numbers and assign by position (left to right)
        # In many SLG games, resources are ordered: food, wood, stone, gold
        numbers = []
        for result in text_results:
            value = self._parse_number(result.text)
            if value is not None and value > 0:
                numbers.append((result.center[0], value))  # (x_pos, value)

        if len(numbers) >= 2:
            numbers.sort(key=lambda x: x[0])  # Sort by x position
            resource_order = ["food", "wood", "stone", "gold"]
            for i, (_, value) in enumerate(numbers):
                if i < len(resource_order):
                    # Only update if we got a plausible value
                    if value > 0:
                        self.state.resources[resource_order[i]] = value

    def _update_buildings(self, screenshot: np.ndarray) -> None:
        """Detect building levels and upgrade status via OCR and templates."""
        # Look for building-related text in the screenshot
        try:
            all_text = self.ocr.find_all_text(screenshot)
        except Exception as e:
            logger.warning(f"OCR failed for buildings: {e}")
            return

        for result in all_text:
            text = result.text
            # Look for patterns like "Lv.12", "等级12", "Level 12"
            level_match = re.search(r'[Ll]v\.?\s*(\d+)|等级\s*(\d+)|[Ll]evel\s*(\d+)', text)
            if level_match:
                level = int(next(g for g in level_match.groups() if g is not None))
                # Try to identify which building this level belongs to
                # Look at nearby text for building name
                for other in all_text:
                    if other is result:
                        continue
                    # Check if text is near the level number
                    dx = abs(other.center[0] - result.center[0])
                    dy = abs(other.center[1] - result.center[1])
                    if dx < 200 and dy < 100:
                        building_name = other.text.strip()
                        if building_name and len(building_name) > 1:
                            upgrading = "升级中" in text or "upgrading" in text.lower()
                            self.state.buildings[building_name] = BuildingState(
                                name=building_name,
                                level=level,
                                upgrading=upgrading,
                            )

    def _update_marches(self, screenshot: np.ndarray) -> None:
        """Detect troop march status from world map view."""
        try:
            all_text = self.ocr.find_all_text(screenshot)
        except Exception as e:
            logger.warning(f"OCR failed for marches: {e}")
            return

        # Look for march-related text (return time, target names)
        for result in all_text:
            text = result.text
            # Look for time patterns like "00:12:34" indicating march timer
            time_match = re.search(r'(\d{1,2}:\d{2}:\d{2})', text)
            if time_match:
                logger.debug(f"March timer detected: {time_match.group(1)}")

    def _update_battle_result(self, screenshot: np.ndarray) -> None:
        """Extract battle results from battle screen."""
        try:
            all_text = self.ocr.find_all_text(screenshot)
        except Exception as e:
            logger.warning(f"OCR failed for battle result: {e}")
            return

        for result in all_text:
            text = result.text.lower()
            if "胜利" in text or "victory" in text or "win" in text:
                logger.info("Battle result: Victory")
            elif "失败" in text or "defeat" in text or "lose" in text:
                logger.info("Battle result: Defeat")

    def _update_quest_bar(self, screenshot: np.ndarray) -> None:
        """Detect quest bar and update game state fields."""
        try:
            info = self.quest_bar_detector.detect(screenshot)
            self.state.quest_bar_visible = info.visible
            self.state.quest_bar_has_red_badge = info.has_red_badge
            self.state.quest_bar_current_quest = info.current_quest_text
            self.state.quest_bar_has_green_check = info.has_green_check
            self.state.quest_bar_has_tutorial_finger = info.has_tutorial_finger
        except Exception as e:
            logger.warning(f"Quest bar detection failed: {e}")

    @staticmethod
    def _parse_number(text: str) -> int | None:
        """Parse a number string from OCR text.

        Handles formats: "12,345", "1.2M", "500K", "1.5B", plain digits.
        """
        # Remove whitespace
        text = text.strip()

        # Try suffixed formats: 1.2M, 500K, 1.5B
        suffix_match = re.search(r'([\d,.]+)\s*([KkMmBb])', text)
        if suffix_match:
            try:
                num_str = suffix_match.group(1).replace(",", "")
                num = float(num_str)
                suffix = suffix_match.group(2).upper()
                multiplier = {"K": 1_000, "M": 1_000_000, "B": 1_000_000_000}
                return int(num * multiplier.get(suffix, 1))
            except ValueError:
                pass

        # Try plain number with possible commas
        plain_match = re.search(r'([\d,]+)', text)
        if plain_match:
            try:
                return int(plain_match.group(1).replace(",", ""))
            except ValueError:
                pass

        return None

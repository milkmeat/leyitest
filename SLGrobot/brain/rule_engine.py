"""Rule Engine - Rule-based task execution without LLM (<500ms).

Decomposes high-level tasks into action sequences using predefined rules.
No LLM calls -- purely deterministic, pattern-matched logic.
"""

import json
import os
import logging

import numpy as np

from vision.element_detector import ElementDetector
from state.game_state import GameState
from .task_queue import Task

logger = logging.getLogger(__name__)


class RuleEngine:
    """Rule-based task decomposition and action planning.

    Maps task names to predefined action sequences.
    Uses element detection to adapt actions to current screen state.
    """

    # Tasks this engine can handle without LLM
    KNOWN_TASKS = {
        "collect_resources",
        "upgrade_building",
        "train_troops",
        "claim_rewards",
        "navigate_main_city",
        "navigate_world_map",
        "close_popup",
        "check_mail",
        "collect_daily",
    }

    def __init__(self, element_detector: ElementDetector,
                 game_state: GameState,
                 nav_paths_file: str = "data/navigation_paths.json") -> None:
        self.detector = element_detector
        self.state = game_state
        self.nav_paths: dict = {}
        self._load_nav_paths(nav_paths_file)

    def _load_nav_paths(self, filepath: str) -> None:
        """Load predefined navigation paths from JSON."""
        if os.path.exists(filepath):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    self.nav_paths = json.load(f)
                logger.info(f"Loaded {len(self.nav_paths)} navigation paths")
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"Failed to load nav paths: {e}")

    def can_handle(self, task: Task) -> bool:
        """Check if this task has predefined rules."""
        return task.name in self.KNOWN_TASKS

    def plan(self, task: Task, screenshot: np.ndarray,
             game_state: GameState) -> list[dict]:
        """Decompose a task into a sequence of action dicts.

        Returns list of action dicts ready for execution.
        Returns empty list if task cannot be planned.
        """
        handler = getattr(self, f"_plan_{task.name}", None)
        if handler is None:
            logger.warning(f"No rule for task: '{task.name}'")
            return []

        actions = handler(task, screenshot, game_state)
        logger.info(f"Rule engine planned {len(actions)} actions for '{task.name}'")
        return actions

    def _plan_collect_resources(self, task: Task, screenshot: np.ndarray,
                                game_state: GameState) -> list[dict]:
        """Plan: collect resources from production buildings.

        Strategy: look for resource icons or collectible indicators on screen.
        """
        actions = []

        # Try to find collectible resource indicators (floating icons)
        for resource in ["food", "wood", "stone", "gold"]:
            element = self.detector.locate(screenshot, resource, methods=["template", "ocr"])
            if element and element.source == "template":
                actions.append({
                    "type": "tap",
                    "x": element.x,
                    "y": element.y,
                    "delay": 0.3,
                    "reason": f"collect_{resource}",
                })

        # If no specific resources found, try tapping known collection areas
        if not actions:
            # Navigate path if available
            if "collect_resources" in self.nav_paths:
                for step in self.nav_paths["collect_resources"]:
                    actions.append(step)

        return actions

    def _plan_upgrade_building(self, task: Task, screenshot: np.ndarray,
                               game_state: GameState) -> list[dict]:
        """Plan: upgrade a building.

        Params: task.params may contain 'building_name'.
        """
        building_name = task.params.get("building_name", "")
        actions = []

        if building_name:
            # Navigate to building if path is known
            nav_key = f"building_{building_name}"
            if nav_key in self.nav_paths:
                for step in self.nav_paths[nav_key]:
                    actions.append(step)

            # Try to find and tap the building
            element = self.detector.locate(screenshot, building_name)
            if element:
                actions.append({
                    "type": "tap",
                    "x": element.x,
                    "y": element.y,
                    "delay": 1.0,
                    "reason": f"select_building:{building_name}",
                })

        # Look for upgrade button
        upgrade_element = self.detector.locate(screenshot, "升级", methods=["ocr"])
        if upgrade_element is None:
            upgrade_element = self.detector.locate(screenshot, "upgrade", methods=["ocr"])

        if upgrade_element:
            actions.append({
                "type": "tap",
                "x": upgrade_element.x,
                "y": upgrade_element.y,
                "delay": 1.0,
                "reason": "tap_upgrade_button",
            })

            # Confirm upgrade
            actions.append({
                "type": "wait",
                "seconds": 0.5,
            })

        return actions

    def _plan_train_troops(self, task: Task, screenshot: np.ndarray,
                           game_state: GameState) -> list[dict]:
        """Plan: train troops in barracks."""
        actions = []

        # Navigate to barracks
        if "barracks" in self.nav_paths:
            for step in self.nav_paths["barracks"]:
                actions.append(step)

        # Look for train button
        train_element = self.detector.locate(screenshot, "训练", methods=["ocr"])
        if train_element is None:
            train_element = self.detector.locate(screenshot, "train", methods=["ocr"])

        if train_element:
            actions.append({
                "type": "tap",
                "x": train_element.x,
                "y": train_element.y,
                "delay": 1.0,
                "reason": "tap_train_button",
            })

        return actions

    def _plan_claim_rewards(self, task: Task, screenshot: np.ndarray,
                            game_state: GameState) -> list[dict]:
        """Plan: claim available rewards (mail, achievements, daily)."""
        actions = []

        # Look for reward/claim buttons
        for text in ["领取", "claim", "collect", "收集"]:
            element = self.detector.locate(screenshot, text, methods=["ocr"])
            if element:
                actions.append({
                    "type": "tap",
                    "x": element.x,
                    "y": element.y,
                    "delay": 0.5,
                    "reason": f"claim_reward:{text}",
                })
                break

        return actions

    def _plan_navigate_main_city(self, task: Task, screenshot: np.ndarray,
                                 game_state: GameState) -> list[dict]:
        """Plan: navigate back to main city view."""
        actions = []

        if game_state.scene != "main_city":
            # Try home button / back to city
            home_element = self.detector.locate(screenshot, "城池", methods=["ocr"])
            if home_element is None:
                home_element = self.detector.locate(screenshot, "home", methods=["ocr"])

            if home_element:
                actions.append({
                    "type": "tap",
                    "x": home_element.x,
                    "y": home_element.y,
                    "delay": 1.0,
                    "reason": "navigate_to_city",
                })
            else:
                # Fallback: press back button
                actions.append({
                    "type": "key_event",
                    "keycode": 4,
                    "delay": 1.0,
                    "reason": "press_back_to_city",
                })

        return actions

    def _plan_navigate_world_map(self, task: Task, screenshot: np.ndarray,
                                 game_state: GameState) -> list[dict]:
        """Plan: navigate to world map."""
        actions = []

        if game_state.scene != "world_map":
            map_element = self.detector.locate(screenshot, "世界", methods=["ocr"])
            if map_element is None:
                map_element = self.detector.locate(screenshot, "world", methods=["ocr"])

            if map_element:
                actions.append({
                    "type": "tap",
                    "x": map_element.x,
                    "y": map_element.y,
                    "delay": 1.5,
                    "reason": "navigate_to_world_map",
                })

        return actions

    def _plan_close_popup(self, task: Task, screenshot: np.ndarray,
                          game_state: GameState) -> list[dict]:
        """Plan: close current popup using three-stage strategy.

        Stage 1: Template-only matching for close button images.
        Stage 2: OCR for multi-character text (no single-char to avoid mismatches).
        Stage 3: Fallback to BACK key.
        """
        # Stage 1: template matching only — safe, no OCR false positives
        for template_name in ["buttons/close", "buttons/close_x", "buttons/x",
                              "buttons/cancel", "buttons/confirm", "buttons/ok"]:
            element = self.detector.locate(
                screenshot, template_name, methods=["template"]
            )
            if element:
                return [{
                    "type": "tap",
                    "x": element.x,
                    "y": element.y,
                    "delay": 0.5,
                    "reason": f"close_popup:template:{template_name}",
                }]

        # Stage 2: OCR for multi-character text only (avoid single-char "X"/"×")
        for text in ["关闭", "close", "确定", "取消", "cancel"]:
            element = self.detector.locate(
                screenshot, text, methods=["ocr"]
            )
            if element:
                return [{
                    "type": "tap",
                    "x": element.x,
                    "y": element.y,
                    "delay": 0.5,
                    "reason": f"close_popup:ocr:{text}",
                }]

        # Stage 3: fallback — press BACK key
        logger.info("close_popup: no button found, falling back to BACK key")
        return [{
            "type": "key_event",
            "keycode": 4,
            "delay": 0.5,
            "reason": "close_popup:back_key_fallback",
        }]

    def _plan_check_mail(self, task: Task, screenshot: np.ndarray,
                         game_state: GameState) -> list[dict]:
        """Plan: check and claim mail rewards."""
        actions = []

        if "mail" in self.nav_paths:
            for step in self.nav_paths["mail"]:
                actions.append(step)
        else:
            mail_element = self.detector.locate(screenshot, "邮件", methods=["ocr"])
            if mail_element is None:
                mail_element = self.detector.locate(screenshot, "mail", methods=["ocr"])
            if mail_element:
                actions.append({
                    "type": "tap",
                    "x": mail_element.x,
                    "y": mail_element.y,
                    "delay": 1.0,
                    "reason": "open_mail",
                })

        return actions

    def _plan_collect_daily(self, task: Task, screenshot: np.ndarray,
                            game_state: GameState) -> list[dict]:
        """Plan: collect daily login/activity rewards."""
        actions = []

        for text in ["每日", "daily", "签到", "check-in"]:
            element = self.detector.locate(screenshot, text, methods=["ocr"])
            if element:
                actions.append({
                    "type": "tap",
                    "x": element.x,
                    "y": element.y,
                    "delay": 1.0,
                    "reason": f"daily_reward:{text}",
                })
                break

        return actions

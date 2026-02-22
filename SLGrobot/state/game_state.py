"""Game State - In-memory game state data model."""

import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class BuildingState:
    """State of a single building."""
    name: str
    level: int = 1
    upgrading: bool = False
    finish_time: str | None = None


@dataclass
class MarchState:
    """State of a troop march."""
    target: str
    action: str  # "gather" | "attack" | "scout"
    return_time: str = ""


class GameState:
    """Central game state container.

    Tracks resources, buildings, troops, task queue status, and action history.
    Serializable to/from dict for JSON persistence and LLM context.
    """

    def __init__(self, default_resources: dict[str, int] | None = None) -> None:
        self.scene: str = "unknown"
        self.resources: dict[str, int] = default_resources.copy() if default_resources else {
            "food": 0,
            "wood": 0,
            "stone": 0,
            "gold": 0,
        }
        self.buildings: dict[str, BuildingState] = {}
        self.troops_marching: list[MarchState] = []
        self.task_queue: list[str] = []
        self.last_actions: list[dict] = []
        self.cooldowns: dict[str, str] = {}
        self.last_llm_consult: str = ""
        self.last_update: str = ""
        self.loop_count: int = 0

        # Quest bar state (updated each main_city screenshot)
        self.quest_bar_visible: bool = False
        self.quest_bar_has_red_badge: bool = False
        self.quest_bar_current_quest: str = ""
        self.quest_bar_has_green_check: bool = False
        self.quest_bar_has_tutorial_finger: bool = False

        # Quest workflow execution state (persisted across iterations)
        self.quest_workflow_phase: str = "idle"
        self.quest_workflow_target: str = ""

    def to_dict(self) -> dict:
        """Serialize to dict for JSON persistence and LLM context."""
        return {
            "scene": self.scene,
            "resources": self.resources,
            "buildings": {
                name: asdict(b) for name, b in self.buildings.items()
            },
            "troops_marching": [asdict(m) for m in self.troops_marching],
            "task_queue": self.task_queue,
            "last_actions": self.last_actions[-20:],  # Keep last 20
            "cooldowns": self.cooldowns,
            "last_llm_consult": self.last_llm_consult,
            "last_update": self.last_update,
            "loop_count": self.loop_count,
            "quest_bar_visible": self.quest_bar_visible,
            "quest_bar_has_red_badge": self.quest_bar_has_red_badge,
            "quest_bar_current_quest": self.quest_bar_current_quest,
            "quest_bar_has_green_check": self.quest_bar_has_green_check,
            "quest_bar_has_tutorial_finger": self.quest_bar_has_tutorial_finger,
            "quest_workflow_phase": self.quest_workflow_phase,
            "quest_workflow_target": self.quest_workflow_target,
        }

    def from_dict(self, data: dict) -> None:
        """Load state from dict."""
        self.scene = data.get("scene", "unknown")
        self.resources = data.get("resources", self.resources)

        # Rebuild BuildingState objects
        self.buildings = {}
        for name, bdata in data.get("buildings", {}).items():
            self.buildings[name] = BuildingState(**bdata)

        # Rebuild MarchState objects
        self.troops_marching = []
        for mdata in data.get("troops_marching", []):
            self.troops_marching.append(MarchState(**mdata))

        self.task_queue = data.get("task_queue", [])
        self.last_actions = data.get("last_actions", [])
        self.cooldowns = data.get("cooldowns", {})
        self.last_llm_consult = data.get("last_llm_consult", "")
        self.last_update = data.get("last_update", "")
        self.loop_count = data.get("loop_count", 0)

        # Quest bar state
        self.quest_bar_visible = data.get("quest_bar_visible", False)
        self.quest_bar_has_red_badge = data.get("quest_bar_has_red_badge", False)
        self.quest_bar_current_quest = data.get("quest_bar_current_quest", "")
        self.quest_bar_has_green_check = data.get("quest_bar_has_green_check", False)
        self.quest_bar_has_tutorial_finger = data.get("quest_bar_has_tutorial_finger", False)

        # Quest workflow state
        self.quest_workflow_phase = data.get("quest_workflow_phase", "idle")
        self.quest_workflow_target = data.get("quest_workflow_target", "")

        logger.info("Game state loaded from dict")

    def record_action(self, action: dict) -> None:
        """Record an executed action with timestamp."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "scene": self.scene,
        }
        self.last_actions.append(entry)
        # Keep bounded
        if len(self.last_actions) > 50:
            self.last_actions = self.last_actions[-20:]

    def summary_for_llm(self) -> str:
        """Generate concise text summary for LLM prompt (minimize tokens)."""
        lines = [f"Scene: {self.scene}"]

        # Resources
        res_parts = [f"{k}={v}" for k, v in self.resources.items() if v > 0]
        if res_parts:
            lines.append(f"Resources: {', '.join(res_parts)}")

        # Buildings
        if self.buildings:
            bld_parts = []
            for name, b in self.buildings.items():
                s = f"{name} Lv{b.level}"
                if b.upgrading:
                    s += f" (upgrading, done {b.finish_time or '?'})"
                bld_parts.append(s)
            lines.append(f"Buildings: {'; '.join(bld_parts)}")

        # Marches
        if self.troops_marching:
            march_parts = [
                f"{m.action}->{m.target} (ret {m.return_time})"
                for m in self.troops_marching
            ]
            lines.append(f"Marches: {'; '.join(march_parts)}")

        # Pending tasks
        if self.task_queue:
            lines.append(f"Pending tasks: {', '.join(self.task_queue[:5])}")

        # Quest bar
        if self.quest_bar_visible:
            quest_parts = [f"quest='{self.quest_bar_current_quest}'"]
            if self.quest_bar_has_red_badge:
                quest_parts.append("red_badge")
            if self.quest_bar_has_green_check:
                quest_parts.append("green_check")
            if self.quest_bar_has_tutorial_finger:
                quest_parts.append("tutorial_finger")
            lines.append(f"Quest bar: {', '.join(quest_parts)}")

        # Quest workflow (always include so LLM knows current objective)
        lines.append(
            f"Quest workflow: phase={self.quest_workflow_phase}, "
            f"target='{self.quest_workflow_target}'"
        )

        return "\n".join(lines)

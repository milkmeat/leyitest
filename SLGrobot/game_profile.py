"""Game Profile - Per-game configuration loaded from games/<id>/game.json."""

import json
import os
import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class GameProfile:
    """All game-specific configuration for one supported game.

    Loaded from ``games/<game_id>/game.json`` by :func:`load_game_profile`.
    Modules accept an optional ``game_profile`` parameter; when ``None``
    they fall back to their existing class-level defaults.
    """

    # Identity
    game_id: str = ""
    name: str = ""
    display_name: str = ""
    package: str = ""

    # Resolved filesystem paths (set by loader, not stored in JSON)
    game_dir: str = ""
    template_dir: str = ""
    nav_paths_file: str = ""
    state_file: str = ""
    tasks_file: str = ""

    # Resources
    default_resources: dict[str, int] = field(default_factory=dict)
    resource_keywords: dict[str, list[str]] = field(default_factory=dict)
    resource_order: list[str] = field(default_factory=list)

    # Scenes and tasks
    scenes: list[str] = field(default_factory=list)
    known_tasks: list[str] = field(default_factory=list)

    # LLM prompt fragments
    llm_game_description: str = ""
    llm_task_types: str = ""

    # Auto-handler patterns
    known_popups: list[list[str]] = field(default_factory=list)
    reward_templates: list[str] = field(default_factory=list)
    close_text_patterns: list[str] = field(default_factory=list)
    claim_text_patterns: list[str] = field(default_factory=list)

    # Quest workflow
    action_button_templates: list[str] = field(default_factory=list)
    action_button_texts: list[str] = field(default_factory=list)

    # Popup filter
    popup_close_templates: list[str] = field(default_factory=list)
    popup_close_texts: list[str] = field(default_factory=list)

    # Grid
    grid_cols: int = 8
    grid_rows: int = 6

    # Finger detection — NCC threshold (0.0 = use class default)
    finger_ncc_threshold: float = 0.0

    # OCR error corrections (common misrecognitions)
    ocr_corrections: dict[str, str] = field(default_factory=dict)

    # Quest scripts (multi-step patterns)
    quest_scripts: list[dict] = field(default_factory=list)

    # City layout for building finder
    city_layout: dict = field(default_factory=dict)


def load_game_profile(game_id: str,
                      games_dir: str = "games") -> GameProfile:
    """Load a GameProfile from ``games/<game_id>/game.json``.

    Resolves template_dir, nav_paths_file, state_file, tasks_file
    relative to the game directory.

    Raises:
        FileNotFoundError: if the game directory or game.json is missing.
    """
    game_dir = os.path.join(games_dir, game_id)
    json_path = os.path.join(game_dir, "game.json")

    if not os.path.isfile(json_path):
        raise FileNotFoundError(
            f"Game profile not found: {json_path}"
        )

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    profile = GameProfile(
        game_id=game_id,
        name=data.get("name", game_id),
        display_name=data.get("display_name", game_id),
        package=data.get("package", ""),

        # Resolved paths
        game_dir=game_dir,
        template_dir=os.path.join(game_dir, "templates"),
        nav_paths_file=os.path.join(game_dir, "navigation_paths.json"),
        state_file=os.path.join(game_dir, "game_state.json"),
        tasks_file=os.path.join(game_dir, "tasks.json"),

        # Resources
        default_resources=data.get("default_resources", {}),
        resource_keywords=data.get("resource_keywords", {}),
        resource_order=data.get("resource_order", []),

        # Scenes and tasks
        scenes=data.get("scenes", []),
        known_tasks=data.get("known_tasks", []),

        # LLM
        llm_game_description=data.get("llm_game_description", ""),
        llm_task_types=data.get("llm_task_types", ""),

        # Auto-handler
        known_popups=data.get("known_popups", []),
        reward_templates=data.get("reward_templates", []),
        close_text_patterns=data.get("close_text_patterns", []),
        claim_text_patterns=data.get("claim_text_patterns", []),

        # Quest workflow
        action_button_templates=data.get("action_button_templates", []),
        action_button_texts=data.get("action_button_texts", []),

        # Popup filter
        popup_close_templates=data.get("popup_close_templates", []),
        popup_close_texts=data.get("popup_close_texts", []),

        # Grid
        grid_cols=data.get("grid_cols", 8),
        grid_rows=data.get("grid_rows", 6),

        # Finger detection
        finger_ncc_threshold=data.get("finger_ncc_threshold", 0.0),

        # OCR corrections
        ocr_corrections=data.get("ocr_corrections", {}),

        # Quest scripts
        quest_scripts=data.get("quest_scripts", []),

        # City layout
        city_layout=data.get("city_layout", {}),
    )

    logger.info(f"Loaded game profile: {profile.display_name} ({game_id})")
    return profile


def list_games(games_dir: str = "games") -> list[str]:
    """Return sorted list of available game IDs.

    A game ID is a subdirectory of *games_dir* containing ``game.json``.
    """
    if not os.path.isdir(games_dir):
        return []
    ids = []
    for entry in sorted(os.listdir(games_dir)):
        path = os.path.join(games_dir, entry, "game.json")
        if os.path.isfile(path):
            ids.append(entry)
    return ids

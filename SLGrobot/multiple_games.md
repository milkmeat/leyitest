# Multi-Game Support for SLGrobot

## Usage

### CLI argument

```bash
python main.py --game frozenisland          # Specify game profile
python main.py --game frozenisland status   # One-shot command with game
python main.py --auto --loops 50 --game frozenisland  # Auto loop with game
python main.py                              # Uses config.ACTIVE_GAME default
```

### Interactive commands

```
> games                  # List available games (* marks active)
  frozenisland *  (Frozen Island Pro)

> game                   # Show current game
Active game: Frozen Island Pro (frozenisland)

> game frozenisland      # Show info about a specific game
Game: Frozen Island Pro (frozenisland)
  Package: leyi.frozenislandpro
  Templates: games\frozenisland\templates
  To switch: restart with --game frozenisland
```

### Adding a new game

1. Create directory `games/<game_id>/`
2. Create `games/<game_id>/game.json` (see schema below)
3. Add template images to `games/<game_id>/templates/`
4. Add navigation paths to `games/<game_id>/navigation_paths.json`
5. Run with `python main.py --game <game_id>`

---

## Design

### Architecture

```
games/
  frozenisland/
    game.json              # All game-specific config
    templates/             # Template images (buttons/, icons/, scenes/, nav_bar/)
    navigation_paths.json  # Predefined tap sequences for navigation
    game_state.json        # Per-game persisted state
    tasks.json             # Per-game task queue
```

### GameProfile dataclass

`game_profile.py` defines a `GameProfile` dataclass that holds all game-specific configuration. It is loaded from `games/<id>/game.json` by `load_game_profile()`. Every module accepts an optional `game_profile` parameter; when `None`, the module falls back to its existing class-level defaults.

### Data flow

```
main() --game arg
  |
  v
load_game_profile(game_id, games_dir)
  |
  v
GameProfile (paths resolved, all fields populated)
  |
  v
GameBot(game_profile=profile)
  |-- TemplateMatcher(profile.template_dir)
  |-- StatePersistence(profile.state_file)
  |-- StateTracker(resource_keywords=..., resource_order=...)
  |-- GameState(default_resources=...)
  |-- RuleEngine(nav_paths_file=..., game_profile=...)
  |-- LLMPlanner(game_profile=...)     # templated prompts
  |-- AutoHandler(game_profile=...)    # popup/reward patterns
  |-- QuestWorkflow(game_profile=...)  # action button patterns
  |-- PopupFilter(game_profile=...)    # close templates/texts
  |-- StuckRecovery(game_package=...)  # app restart package name
```

### Backward compatibility

All original files (`templates/`, `data/navigation_paths.json`, `data/game_state.json`, `data/tasks.json`) are kept in place. When `game_profile=None`, every module falls back to its hardcoded class constants and `config.py` paths. Existing tests continue to work without modification.

### game.json schema

```json
{
  "name": "frozenisland",
  "display_name": "Frozen Island Pro",
  "package": "leyi.frozenislandpro",

  "default_resources": {"food": 0, "wood": 0, "stone": 0, "gold": 0},
  "resource_keywords": {
    "food": ["食物", "粮食", "food"],
    "wood": ["木材", "木头", "wood"],
    "stone": ["石头", "石材", "stone"],
    "gold": ["金币", "金", "gold"]
  },
  "resource_order": ["food", "wood", "stone", "gold"],

  "scenes": ["main_city", "world_map", "hero", "hero_recruit",
             "battle", "popup", "loading", "story_dialogue", "unknown"],

  "known_tasks": ["collect_resources", "upgrade_building", "train_troops",
                  "claim_rewards", "navigate_main_city", "navigate_world_map",
                  "close_popup", "check_mail", "collect_daily"],

  "llm_game_description": "a mobile SLG game called \"Frozen Island\" (冰封岛屿)",
  "llm_task_types": "collect_resources, upgrade_building, ..., custom",

  "known_popups": [["buttons/view", "buttons/close_x"]],
  "reward_templates": ["buttons/claim", "buttons/collect", "buttons/ok", "buttons/confirm"],
  "close_text_patterns": ["关闭", "close", "×", "X"],
  "claim_text_patterns": ["领取", "claim", "collect", "收集", "一键领取"],

  "action_button_templates": ["buttons/upgrade_building", "buttons/upgrade", "buttons/build"],
  "action_button_texts": ["一键上阵", "出战", "开始战斗", "攻击", "建造", "升级", "..."],

  "popup_close_templates": ["buttons/close", "buttons/close_x", "buttons/x",
                            "buttons/cancel", "buttons/confirm", "buttons/ok"],
  "popup_close_texts": ["返回领地", "领取", "返回", "关闭", "确定", "确认"],

  "grid_cols": 8,
  "grid_rows": 6
}
```

---

## Implementation summary

### New files

| File | Description |
|------|-------------|
| `game_profile.py` | `GameProfile` dataclass, `load_game_profile()`, `list_games()` |
| `games/frozenisland/game.json` | Frozen Island game config (extracted from hardcoded values) |
| `games/frozenisland/templates/` | Copied from `templates/` |
| `games/frozenisland/navigation_paths.json` | Copied from `data/navigation_paths.json` |
| `games/frozenisland/game_state.json` | Copied from `data/game_state.json` |
| `games/frozenisland/tasks.json` | Copied from `data/tasks.json` |

### Modified files

| File | Changes |
|------|---------|
| `config.py` | Added `GAMES_DIR = "games"`, `ACTIVE_GAME = "frozenisland"` |
| `state/game_state.py` | `__init__` accepts `default_resources` param |
| `state/state_tracker.py` | `__init__` accepts `resource_keywords`, `resource_order`; uses instance attrs `_resource_keywords` / `_resource_order` in `_update_resources` |
| `brain/llm_planner.py` | Three prompt constants converted to templates with `{game_description}` / `{task_types}` placeholders; `__init__` accepts `game_profile`, builds resolved prompts |
| `brain/rule_engine.py` | `__init__` accepts `game_profile`; uses `_known_tasks` instance attr in `can_handle()` |
| `brain/auto_handler.py` | `__init__` accepts `game_profile`; uses instance attrs `_known_popups`, `_reward_templates`, `_close_text_patterns`, `_claim_text_patterns` |
| `brain/quest_workflow.py` | `__init__` accepts `game_profile`; overrides `_ACTION_BUTTON_TEMPLATES` and `_ACTION_BUTTON_TEXTS` from profile |
| `scene/popup_filter.py` | `__init__` accepts `game_profile`; uses instance attrs `_close_templates`, `_close_texts` |
| `brain/stuck_recovery.py` | `__init__` accepts `game_package` param; uses it in `_restart_app` before falling back to `config.GAME_PACKAGE` |
| `main.py` | `GameBot` accepts `GameProfile`, resolves template_dir / state_file / tasks_file / nav_paths_file / game_package from profile; `main()` adds `--game` arg and loads profile; CLI gains `games` and `game` commands; `cmd_status` shows active game; `cmd_save_tasks` / `cmd_load_tasks` / `cmd_capture_template` use game-specific paths |

### Module parameter pattern

Every modified module follows the same pattern:

```python
class SomeModule:
    # Class-level defaults (unchanged, serve as fallback)
    SOME_CONSTANT = [...]

    def __init__(self, ..., game_profile=None):
        # Instance attr: profile value or class default
        self._some_constant = (
            game_profile.some_field
            if game_profile and game_profile.some_field
            else self.SOME_CONSTANT
        )

    def some_method(self):
        # Uses instance attr instead of class constant
        for item in self._some_constant:
            ...
```

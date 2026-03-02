# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Summary

SLGrobot is a Python AI agent that autonomously plays "Frozen Island Pro" (`leyi.frozenislandpro`), an SLG mobile game, via an Android emulator (BlueStacks or Nox) on Windows. It uses ADB for device control, OpenCV for screen understanding, OCR for text extraction, and LLM APIs (Anthropic Claude or Zhipu GLM) for strategic planning.

## Commands

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Run
```bash
python main.py              # Interactive CLI (default: BlueStacks)
python main.py --auto       # Autonomous loop (infinite)
python main.py --auto --loops 50   # Autonomous loop with limit
python main.py --emulator nox status  # Use Nox emulator
python main.py tap 100,200         # One-shot command
python main.py screenshot label    # One-shot screenshot
python main.py scene               # Detect current scene
python main.py status              # Show connection/game state
```

### Tests
Tests use raw `assert` statements (no pytest fixtures). Each file tests one development phase and requires a running emulator with ADB connected:
```bash
python test_phase1.py       # ADB + device layer
python test_vision.py       # Template matching, OCR, grid overlay
python test_state.py        # Game state, persistence, auto-handler
python test_llm.py          # LLM planner API calls
python test_hardening.py    # Stuck recovery, reconnect, retry
```

## Architecture

### Scene-Driven Auto Loop

The auto loop is scene-first: each iteration takes a screenshot, classifies the scene, then dispatches to the appropriate handler:
- **AutoHandler** — pattern-matched actions for each scene type (popups, loading, main city idle, etc.)
- **Quest Scripts** — multi-step scripted sequences triggered by quest bar matching or manual CLI command
- **LLM (optional)** — Claude or GLM-4V, consulted for strategic planning when needed

90% of operations are handled locally by AutoHandler + Quest Scripts without LLM calls.

### Module Layers

| Directory | Layer | Role |
|-----------|-------|------|
| `device/` | Device Control | ADB connection, tap, swipe, screenshots, reconnect |
| `vision/` | Visual Perception | Template matching, OCR text detection, grid overlay, element detection, building finder |
| `scene/` | Scene Understanding | Scene classification, popup detection/auto-close, scene-specific handlers |
| `state/` | State Management | In-memory game state, OCR-based state extraction, JSON persistence |
| `brain/` | Decision Making | Quest script runner, auto-handler, LLM planner, stuck recovery |
| `executor/` | Execution Pipeline | Action validation → execution (with retry) → result verification |
| `utils/` | Utilities | Logging (console + `.log` + `.jsonl`), image helpers |

### Key Design Principles

- **LLM selects grid cells (A1–H6), not pixel coordinates** — CV handles coordinate resolution, the LLM picks from an annotated grid overlay
- **LLM is stateless** — game state is persisted in `data/game_state.json` and passed as context to each LLM call
- **Scene-first dispatch** — every auto-loop iteration starts with scene classification before deciding what to do
- **Validate-execute-confirm pipeline** — `ActionValidator` → `ActionRunner` (with retry) → `ResultChecker`
- **禁止使用 Android 系统 BACK 键 (keycode=4)** — SLG 游戏的建筑面板和内嵌 UI 不响应系统 BACK 键，使用 BACK 会导致循环卡死。退出策略优先级：① 点击 `buttons/back_arrow` 模板 ② 点击空白区域 `(500, 100)` ③ 使用 `popup_filter` 关闭弹窗

### Action Dict Protocol

All modules exchange actions as dicts with a `type` field:
```python
{"type": "tap", "x": 540, "y": 960, "delay": 0.5, "reason": "..."}
{"type": "tap", "target_text": "升级", "fallback_grid": "C4"}
{"type": "navigate", "target": "barracks"}  # follows navigation_paths.json
{"type": "swipe", "x1": 640, "y1": 500, "x2": 640, "y2": 200, "duration_ms": 300}
{"type": "wait", "seconds": 2}
{"type": "key_event", "keycode": 3}  # 3=HOME (BACK 键已禁用，见下方规则)
{"type": "find_building", "building_name": "兵营", "scroll": True, "max_attempts": 3}
```

### Scene Types

Scene types: `main_city`, `world_map`, `hero`, `hero_recruit`, `battle`, `popup`, `loading`, `unknown`

### Quest Scripting System

Game operations are defined as JSON quest scripts in `games/<id>/game.json` under `quest_scripts`. Each script has an optional `name` (English identifier) and a `pattern` (Chinese regex). CLI supports bilingual matching: `quest claim_quest_reward` or `quest 领取任务奖励` both work (name match first, then pattern regex). Scripts are multi-step sequences with verbs: `tap_xy`, `tap_text`, `tap_icon`, `swipe`, `wait_text`, `ensure_main_city`, `ensure_world_map`, `read_text`, `eval`, `find_building`. Executed by `QuestScriptRunner` (`brain/quest_script.py`), triggered automatically via quest bar matching or manually via `quest` CLI command. See `quest_scripting.md` for full reference.

Quest script MD 文件中图标引用可以只写文件名（如 `[[upgrade_arrow.png]]`），生成 JSON 时需根据模板文件在 `templates/` 下的实际位置补全目录前缀（如 `"icons/upgrade_arrow"`）。`QuestScriptRunner` 的 `tap_icon` 直接调用 `TemplateMatcher`，不会自动补全前缀。

### Template Matcher 路径规则

`TemplateMatcher` 加载 `games/<id>/templates/` 下的所有 PNG 文件，缓存 key 为**相对路径去掉扩展名**，`\` 替换为 `/`。

- 磁盘文件: `games/westgame2/templates/icons/search.png`
- 缓存 key: `icons/search`
- 代码调用: `template_matcher.match_one(screenshot, "icons/search")`

常用目录前缀：`buttons/`、`icons/`、`nav_bar/`、`scenes/`、`popups/`。

**编写脚本时**：`tap_icon` 的参数必须是缓存 key（含目录前缀、不含 `.png`），如 `["icons/balance_config"]`，不能只写文件名 `"balance_config"`。

**调试模板匹配**：使用 `python -c` 脚本时，`TemplateMatcher` 必须传入正确的模板目录 `games/<id>/templates`（而非默认的 `config.TEMPLATE_DIR`，那个指向旧的 `templates/`）。

### Building Finder

`BuildingFinder` (`vision/building_finder.py`) finds and taps buildings on the scrollable city map. It uses a press-drag-read technique: ADB swipe reveals building names, a concurrent screenshot + OCR identifies the target, then taps at the compensated position after the swipe ends. Integrated as the `find_building` quest script verb and action type. Configuration in `game.json` under `city_layout`. See `docs/building_finder.md` for details.

## Configuration

- `config.py` — all global constants (ADB host/port, screen resolution, timing, thresholds, file paths). Emulator presets (`EMULATOR_PRESETS`) allow switching between BlueStacks and Nox via `ACTIVE_EMULATOR` or `--emulator` CLI flag
- `model_presets.py` — LLM provider presets. Switch provider by changing `ACTIVE_PRESET` (currently `"zhipu"`)
- `data/navigation_paths.json` — predefined tap sequences for navigating between game screens (17 paths)
- `games/<id>/templates/` — PNG template images organized by category (`buttons/`, `icons/`, `nav_bar/`, `scenes/`, `popups/`), loaded by `TemplateMatcher` via `game_profile.template_dir`
- `games/<id>/city_layout.md` — building positions on the city map (used by BuildingFinder)

## Platform Requirements

- **Windows only** — emulator ADB paths auto-detected in `config.py`
- **Python 3.10+** — uses PEP 604 union types (`dict | None`) and PEP 585 generics (`tuple[int, int]`)
- **Emulator**: BlueStacks (default, port 5555) or Nox (port 62001) at 1080×1920 portrait resolution

## ADB / Emulator Notes

本项目支持蓝叠 (BlueStacks) 和夜神 (Nox) 模拟器，通过 `config.py` 的 `EMULATOR_PRESETS` 预设系统切换，**蓝叠为默认**。

- **切换方式**: 修改 `config.py` 中的 `ACTIVE_EMULATOR`（`"bluestacks"` 或 `"nox"`），或使用 CLI 参数 `--emulator nox`
- **蓝叠 ADB 路径**: 自动检测 `C:\Program Files\BlueStacks_nxt\HD-Adb.exe` 等位置，回退到系统 PATH 中的 `adb`
- **夜神 ADB 路径**: 自动检测 `D:\Program Files\Nox\bin\nox_adb.exe` 等位置，回退到注册表查询
- **统一配置变量**: `config.ADB_PATH`（当前生效的 ADB 路径）、`config.ADB_PORT`（当前端口）
- **向后兼容**: `config.NOX_ADB_PATH` 保留为 `config.ADB_PATH` 的别名
- **ADBController 初始化必须传三个参数**: `ADBController(config.ADB_HOST, config.ADB_PORT, config.ADB_PATH)`
- 直接用 `python -c` 写脚本访问模拟器时，必须用 `config.ADB_PATH`，否则会报 `ADB executable not found: adb`
- `main.py` 的 CLI 命令已经正确初始化 ADB，直接用 `python main.py <command>` 即可

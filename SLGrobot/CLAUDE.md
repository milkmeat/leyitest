# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Summary

SLGrobot is a Python AI agent that autonomously plays "Frozen Island Pro" (`leyi.frozenislandpro`), an SLG mobile game, via a Nox Android emulator on Windows. It uses ADB for device control, OpenCV for screen understanding, OCR for text extraction, and LLM APIs (Anthropic Claude or Zhipu GLM) for strategic planning.

## Commands

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Run
```bash
python main.py              # Interactive CLI
python main.py --auto       # Autonomous loop (infinite)
python main.py --auto --loops 50   # Autonomous loop with limit
python main.py tap 100,200         # One-shot command
python main.py screenshot label    # One-shot screenshot
python main.py scene               # Detect current scene
python main.py status              # Show connection/game state
```

### Tests
Tests use raw `assert` statements (no pytest fixtures). Each file tests one development phase and requires a running Nox emulator with ADB connected:
```bash
python test_phase1.py       # ADB + device layer
python test_vision.py       # Template matching, OCR, grid overlay
python test_state.py        # Game state, persistence, task queue
python test_llm.py          # LLM planner API calls
python test_hardening.py    # Stuck recovery, reconnect, retry
```

## Architecture

### Three-Layer Decision Loop

1. **Strategic Layer** — LLM (Claude or GLM-4V), consulted every ~30 minutes, generates high-level task plans
2. **Tactical Layer** — Local rule engine (<500ms), decomposes tasks into action sequences
3. **Execution Layer** — CV + ADB (<100ms), screenshot → detect → tap

90% of operations bypass the LLM entirely; the local CV + rule engine handles routine tasks.

### Module Layers

| Directory | Layer | Role |
|-----------|-------|------|
| `device/` | Device Control | ADB connection, tap, swipe, screenshots, reconnect |
| `vision/` | Visual Perception | Template matching, OCR text detection, grid overlay, element detection, building finder |
| `scene/` | Scene Understanding | Scene classification, popup detection/auto-close, scene-specific handlers |
| `state/` | State Management | In-memory game state, OCR-based state extraction, JSON persistence |
| `brain/` | Decision Making | Quest script runner, task queue, rule engine, LLM planner, stuck recovery, auto-handler |
| `executor/` | Execution Pipeline | Action validation → execution (with retry) → result verification |
| `utils/` | Utilities | Logging (console + `.log` + `.jsonl`), image helpers |

### Key Design Principles

- **LLM selects grid cells (A1–H6), not pixel coordinates** — CV handles coordinate resolution, the LLM picks from an annotated grid overlay
- **LLM is stateless** — game state is persisted in `data/game_state.json` and passed as context to each LLM call
- **Scene-first dispatch** — every auto-loop iteration starts with scene classification before deciding what to do
- **Validate-execute-confirm pipeline** — `ActionValidator` → `ActionRunner` (with retry) → `ResultChecker`

### Action Dict Protocol

All modules exchange actions as dicts with a `type` field:
```python
{"type": "tap", "x": 540, "y": 960, "delay": 0.5, "reason": "..."}
{"type": "tap", "target_text": "升级", "fallback_grid": "C4"}
{"type": "navigate", "target": "barracks"}  # follows navigation_paths.json
{"type": "swipe", "x1": 640, "y1": 500, "x2": 640, "y2": 200, "duration_ms": 300}
{"type": "wait", "seconds": 2}
{"type": "key_event", "keycode": 4}  # 4=BACK, 3=HOME
{"type": "find_building", "building_name": "兵营", "scroll": True, "max_attempts": 3}
```

### Scene Types and Task Types

Scene types: `main_city`, `world_map`, `hero`, `hero_recruit`, `battle`, `popup`, `loading`, `unknown`

Known task types (handled by `RuleEngine`): `collect_resources`, `upgrade_building`, `train_troops`, `claim_rewards`, `navigate_main_city`, `navigate_world_map`, `close_popup`, `check_mail`, `collect_daily`

### Quest Scripting System

Game operations are defined as JSON quest scripts in `games/<id>/game.json` under `quest_scripts`. Scripts are multi-step sequences with verbs: `tap_xy`, `tap_text`, `tap_icon`, `wait_text`, `ensure_main_city`, `read_text`, `eval`, `find_building`. Executed by `QuestScriptRunner` (`brain/quest_script.py`), triggered automatically via quest bar matching or manually via `quest` CLI command. See `quest_scripting.md` for full reference.

### Building Finder

`BuildingFinder` (`vision/building_finder.py`) finds and taps buildings on the scrollable city map. It uses a press-drag-read technique: ADB swipe reveals building names, a concurrent screenshot + OCR identifies the target, then taps at the compensated position after the swipe ends. Integrated as the `find_building` quest script verb and action type. Configuration in `game.json` under `city_layout`. See `docs/building_finder.md` for details.

## Configuration

- `config.py` — all global constants (ADB host/port, screen resolution, timing, thresholds, file paths)
- `model_presets.py` — LLM provider presets. Switch provider by changing `ACTIVE_PRESET` (currently `"zhipu"`)
- `data/navigation_paths.json` — predefined tap sequences for navigating between game screens (17 paths)
- `templates/` — PNG template images organized by category (`buttons/`, `icons/`, `nav_bar/`, `scenes/`, `popups/`)
- `games/<id>/city_layout.md` — building positions on the city map (used by BuildingFinder)

## Platform Requirements

- **Windows only** — Nox ADB path is hardcoded at `D:\Program Files\Nox\bin\nox_adb.exe` in `config.py`
- **Python 3.10+** — uses PEP 604 union types (`dict | None`) and PEP 585 generics (`tuple[int, int]`)
- **Nox emulator** at 1080×1920 portrait resolution on ADB port 62001

## ADB / Nox Emulator Notes

本项目使用 Nox 模拟器自带的 ADB，**不是系统 PATH 中的 adb**。

- **ADB 路径**: `D:\Program Files\Nox\bin\nox_adb.exe`，配置在 `config.py` 的 `NOX_ADB_PATH`
- **设备地址**: `127.0.0.1:62001`，配置在 `config.py` 的 `ADB_HOST` / `ADB_PORT`
- **ADBController 初始化必须传三个参数**: `ADBController(config.ADB_HOST, config.ADB_PORT, config.NOX_ADB_PATH)`
- 直接用 `python -c` 写脚本访问模拟器时，必须用 `config.NOX_ADB_PATH`，否则会报 `ADB executable not found: adb`
- `main.py` 的 CLI 命令已经正确初始化 ADB，直接用 `python main.py <command>` 即可

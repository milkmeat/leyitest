# Prompt Record

- Date: 2026-03-15 12:00
- Branch: master
- Commit: implement Phase 2: YAML script runner with DOM-aware element finding and CLI commands

---

### 1. Implement Phase 2 plan

Implement the following plan:

# Phase 2: Script Runner + CLI — Implementation Plan

## Context

Phase 1 built the Screen DOM Builder (`vision/screen_dom.py`) that converts screenshots into structured YAML DOM. Phase 2 builds a YAML-based script execution engine that uses DOM output for element finding and condition evaluation. This replaces the old `quest_script.py` verb-based system with a cleaner, DOM-aware script runner.

## Files to Create/Modify

| File | Action | Purpose |
|------|--------|---------|
| `brain/script_runner.py` | **Create** | Core: ScriptRunner, find_element, evaluate_condition, load_script |
| `game_profile.py` | Edit | Add `scripts_dir` field |
| `main.py` | Edit | Add `cmd_run`, `cmd_scripts`, update HELP_TEXT |
| `games/frozenisland/scripts/` | Create dir | Scripts directory for frozenisland |
| `games/westgame2/scripts/` | Create dir | Scripts directory for westgame2 |

**Files:** `brain/script_runner.py`, `game_profile.py`, `main.py`, `games/frozenisland/scripts/.gitkeep`, `games/westgame2/scripts/.gitkeep`

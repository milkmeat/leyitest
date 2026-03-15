# Prompt Record

- Date: 2026-03-15 00:00
- Branch: master
- Commit: implement Phase 3: DOM-based auto handler with priority rule engine

---

### 1. Phase 3 Auto Handler Rewrite implementation plan

Implement the following plan:

# Phase 3: Auto Handler Rewrite — Implementation Plan

## Context

The current auto loop in `main.py` uses `SceneClassifier` (template-based) for scene detection, then dispatches to a 400-line `_process_scene()` method with hardcoded if/elif chains for each scene type. Phase 3 replaces this with a DOM-driven approach: build DOM → infer scene from DOM → match priority rules against DOM elements → execute the winning action. This removes the dependency on the old `SceneClassifier` and makes the auto loop data-driven.

## Design Decision: Hybrid Approach

The existing `_process_scene` has complex game-specific logic (expedition formation 2-step tap, hero upgrade red-text check, shooting mini-game swipe, exit dialog 60s cooldown, popup primary-button position tracking). Pure priority rules can't express all of this.

**Approach**: Priority rules handle 80% of cases (popup close, finger tap, reward claim, back arrow, loading wait). Scene-specific **handler functions** cover the remaining complex cases. Both are configured per-game, not hardcoded.

## Files to Create/Modify

| File | Action | Purpose |
|------|--------|---------|
| `brain/auto_handler.py` | **Rewrite** | New DOM-based AutoHandler with priority engine |
| `main.py` | **Edit** | Rewrite `auto_loop` and `_process_scene` to use DOM |

## Priority Rule Format (in game.json `auto_priorities`)

```json
{
  "auto_priorities": {
    "popup": [
      {"type": "button", "text_match": "领取|claim|collect", "action": "tap"},
      {"type": "button", "text_match": "确[认定]|ok|confirm", "action": "tap"},
      {"type": "icon", "name": "buttons/close_x", "action": "tap"},
      {"type": "button", "text_match": "关闭|close", "action": "tap"},
      {"action": "tap_blank"}
    ],
    "loading": [],
    "main_city": [
      {"type": "finger", "action": "tap_fingertip"},
      {"type": "green_check", "action": "tap"},
      {"type": "red_dot", "action": "tap"}
    ],
    "story_dialogue": [
      {"type": "text", "value_match": "跳过|skip", "action": "tap"},
      {"type": "icon", "name": "icons/down_triangle", "action": "tap"},
      {"action": "tap_center"}
    ],
    "_default": [
      {"type": "finger", "action": "tap_fingertip"},
      {"type": "icon", "name": "buttons/back_arrow", "action": "tap"},
      {"type": "button", "color": "green|blue", "action": "tap"},
      {"action": "tap_blank"}
    ]
  }
}
```

Each rule is tried in order. First match wins. Rules with no `type` are unconditional fallbacks.

## Implementation: `brain/auto_handler.py` Rewrite

### `match_priority(dom, rules) -> dict | None`

Module-level function. Iterates rules against DOM elements.

### `class AutoHandler`

New signature: `get_action(dom) -> dict | None`. Single action (first match wins), DOM-only input.

## Implementation: `main.py` Changes

### `auto_loop` rewrite

```
Old: screenshot → classifier.classify() → finger_detector → _process_scene (400 lines)
New: screenshot → DOM → scene from DOM → auto_handler.get_action(dom) → execute tap
```

### `_process_scene` → thin pre-check

Only exit_dialog (60s cooldown) and shoot_mini_game (swipe) remain as special cases. All other scene logic moves to priority rules.

## Implementation Order

1. `game_profile.py` — add `auto_priorities` field
2. `brain/auto_handler.py` — rewrite with `match_priority` + `AutoHandler`
3. `games/frozenisland/game.json` — add `auto_priorities` section
4. `games/westgame2/game.json` — add `auto_priorities` section
5. `main.py` — rewrite auto_loop, simplify _process_scene, update simulate_auto_iteration

**Files:** `brain/auto_handler.py`, `game_profile.py`, `games/frozenisland/game.json`, `games/westgame2/game.json`, `main.py`

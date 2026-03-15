# Prompt Record

- Date: 2026-03-15 22:00
- Branch: master
- Commit: fix building_upgrade_001: scene detection, back_arrow false positive, auto action

---

### 1. Implement plan to fix building_upgrade_001 three bugs

Implement the following plan:

# Fix building_upgrade_001 — 3 bugs

## Context
Screenshot test `building_upgrade_001` has 3 failures: wrong scene (`unknown` → `building_upgrade`), back_arrow false positive, wrong auto action.

## Changes

### 1. Scene detection: add `building_upgrade` — `vision/screen_dom.py`

In `infer_scene()`, add check after shoot_mini_game (line 74) and before primary scene checks (line 77). Detect by finding a "升级" button in the characteristic position (top-right area of center, blue, wide).

```python
# 6. Building upgrade panel
for region in ("top_bar", "center", "bottom_bar"):
    for elem in screen.get(region, []):
        if (elem.get("type") == "button"
                and "升级" in elem.get("text", "")
                and elem.get("pos", [0, 0])[0] > 700
                and 800 < elem.get("pos", [0, 0])[1] < 1050
                and elem.get("size", [0, 0])[0] > 150):
            return "building_upgrade"
```

### 2. Fix back_arrow false positive — `vision/screen_dom.py`

**Root cause**: `_match_all_fast()` uses `TM_CCORR_NORMED` for masked templates but skips the NCC verification that `match_one()` performs (lines 481-525 in template_matcher.py). For templates with <90% opacity (like back_arrow), `match_one` computes masked NCC and rejects if < 0.7. `_match_all_fast` never does this.

**Fix**: After the ROI refinement in `_match_all_fast()` (around line 395), add NCC verification for low-opacity masked templates. Use `TemplateMatcher.compute_masked_ncc()` static method.

### 3. Add auto_priorities for `building_upgrade` — `games/westgame2/game.json`

```json
"building_upgrade": [
    {"type": "button", "text_match": "升级", "color_match": "blue", "action": "tap"},
    {"action": "tap_blank"}
]
```

**Files:** `vision/screen_dom.py`, `games/westgame2/game.json`

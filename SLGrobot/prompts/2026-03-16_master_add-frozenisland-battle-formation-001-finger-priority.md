# Prompt Record

- Date: 2026-03-16 07:30
- Branch: master
- Commit: add frozenisland battle_formation_001 test and finger priority in _process_scene

---

### 1. Add screenshot test

add screenshot test

**Files:** `tests/screenshots/frozenisland/battle_formation_001.png`, `tests/screenshots/frozenisland/battle_formation_001.yaml`

### 2. Finger takes priority over original battle_formation logic

这个上阵场景有手指图标，应该点击手指（required）而非按原来的逻辑

**Files:** `main.py`, `games/frozenisland/game.json`, `games/westgame2/game.json`

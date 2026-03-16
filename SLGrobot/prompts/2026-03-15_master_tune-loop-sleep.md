# Prompt Record

- Date: 2026-03-15 17:20
- Branch: master
- Commit: tune loop_start_sleep: base 1.4s, building_upgrade reduces to 0.7s

---

### 1. Increase base loop_start_sleep

loop_start_sleep 的初始值设置成1.4s

**Files:** `games/westgame2/game.json`

### 2. Building_upgrade should reduce sleep instead of increase

如果持续停留在building_upgrade场景， building_upgrade应该减少至0.7s而不是增加

**Files:** `main.py`

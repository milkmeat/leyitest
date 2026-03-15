# Prompt Record

- Date: 2026-03-15 16:00
- Branch: master
- Commit: add building_upgrade_003 test and support 升级/建造/下一个 keywords

---

### 1. Add screenshot test

add screenshot test

**Files:** `tests/screenshots/westgame2/building_upgrade_003.png`, `tests/screenshots/westgame2/building_upgrade_003.yaml`

### 2. Upgrade button text can be 升级/建造/下一个

> **Q:** The screenshot shows a building upgrade panel for 采石场 (Quarry) with an 升级 button. Does this look correct? And should I auto-name it?

Auto-name it

### 3. Expand upgrade button keywords

这个升级按钮的文字有可能是 升级/建造/下一个， 都同样处理

**Files:** `tests/screenshots/westgame2/building_upgrade_003.yaml`, `games/westgame2/game.json`

### 4. Update scene classification to match new keywords

> **Q:** 按钮文字也可能是"建造"或"下一个"，这里只检查了"升级"。需要同步更新这个判断吗？

yes

**Files:** `vision/screen_dom.py`

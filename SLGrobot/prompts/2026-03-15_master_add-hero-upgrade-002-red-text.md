# Prompt Record

- Date: 2026-03-15 16:59
- Branch: master
- Commit: add hero_upgrade_002 test and has_red_text button detection

---

### 1. Add screenshot test

add screenshot test

**Files:** `tests/screenshots/westgame2/hero_upgrade_002.png`, `tests/screenshots/westgame2/hero_upgrade_002.yaml`

### 2. Red text means insufficient resources, tap back_arrow

这个用例比较特殊，升级按钮上面有红色文字，说明升级资源不够了。此时��该点击back_arrow

**Files:** `vision/button_detector.py`, `vision/screen_dom.py`, `brain/auto_handler.py`, `games/westgame2/game.json`, `tests/screenshots/westgame2/hero_upgrade_002.yaml`

### 3. Add has_red_text as required element condition

把 has_red_text 当作 required条件加入yaml

**Files:** `tests/screenshot_helpers.py`, `tests/screenshots/westgame2/hero_upgrade_002.yaml`

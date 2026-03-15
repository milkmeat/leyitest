# Prompt Record

- Date: 2026-03-15 16:24
- Branch: master
- Commit: add popup_003 test, reduce max loop sleep, add 返回小镇/继续 popup rules

---

### 1. Reduce max loop sleep to 5s

loop_start_sleep -> 15.0s , 这个循环设置成最多5s

**Files:** `main.py`

### 2. Ask where shoot_mini_game logic lives

Shooting mini-game detected — swiping right 150px and waiting 10s
这个逻辑现在放在哪里

### 3. Add screenshot test

add screenshot test

**Files:** `tests/screenshots/westgame2/popup_003.png`, `tests/screenshots/westgame2/popup_003.yaml`

### 4. Battle victory popup should tap 返回小镇

> **Q:** This is a 战斗成功 popup with 返回小镇 and 继续 buttons. Should I add 继续 to the popup priority rules, or is tap_blank correct here?

在"战斗成功"这个popup这里，应该 返回小镇

**Files:** `games/westgame2/game.json`, `tests/screenshots/westgame2/popup_003.yaml`

### 5. Also add 继续 to popup rules

game.json:  返回小镇 下一行，把 继续 也加上

**Files:** `games/westgame2/game.json`

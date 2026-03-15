# Prompt Record

- Date: 2026-03-15 18:49
- Branch: master
- Commit: add battle_formation_001 test, scene detection, and _process_scene handler

---

### 1. Add screenshot test

add screenshot test

### 2. Define battle_formation scene and action

> **Q:** Battle formation screen with 一键上阵 and 出战. What should the scene type and action be?

这是battle_formation scene,判断依据是底部有 一键上阵 and 出战 按钮， action应该是 先点击 一键上阵 再点击 出战

**Files:** `vision/screen_dom.py`, `games/westgame2/game.json`

### 3. Two-tap sequence needs _process_scene

auto_action 需要tap两个按钮，先 一键上阵， 再 出战。下一次循环 一键上阵 不会消失，进行不下去的

**Files:** `main.py`, `games/westgame2/game.json`, `tests/screenshots/westgame2/battle_formation_001.yaml`

### 4. Review previous implementation

以前有过 "先 一键上阵， 再 出战"，这个逻辑的，你看看以前是怎么实现的

### 5. Add YAML comment explaining null auto_action

yaml加一个注释：这是特殊场景，在...处理了。所以返回null

**Files:** `tests/screenshots/westgame2/battle_formation_001.yaml`

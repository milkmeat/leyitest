# Prompt Record

- Date: 2026-03-15 16:48
- Branch: master
- Commit: add hero_upgrade_001 test, fix scene detection and priority rules

---

### 1. Add screenshot test

add screenshot test

### 2. Hero upgrade scene definition and priority rules

> **Q:** This is a hero detail screen (德洛丽丝, SR). Scene is unknown, action is tap back_arrow. What's the correct scene type and action?

这是 hero_upgrade scene，判断标准是底部有 属性 和 技能 两个按钮。在本用例中，手指需要被识别并优先点击。如果没有手指的情况下，如果 升级 按钮是蓝色就点击，都没有的话就back arrow退出

**Files:** `vision/screen_dom.py`, `games/westgame2/game.json`

### 3. Save test with finger action

> **Q:** Finger not detected by pipeline. Save with back_arrow or fix finger detection first?

save the testcase with auto_action=tap_finger

**Files:** `tests/screenshots/westgame2/hero_upgrade_001.png`, `tests/screenshots/westgame2/hero_upgrade_001.yaml`

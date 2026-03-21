# Prompt Record

- Date: 2026-03-21
- Branch: master
- Commit: feat: add building_upgrade_004 screenshot test + fix AutoHandler to click 前往 button

---

### 1. Add screenshot test case

User invoked `/add-screenshot-test` command to create a regression test case from the emulator screenshot.

**Files:** `tests/screenshots/westgame2/building_upgrade_004.png`, `tests/screenshots/westgame2/building_upgrade_004.yaml`

### 2. Name the test case

User: "test case name is building_upgrade"

### 3. Correct expected action

User: "building_upgrade_004 预期行动是点击 前往 按钮"

> **Insight**
> The format for `reason_match` in auto_action is `tap:button:<button_text>`, so clicking "前往" button should be written as `reason_match: "tap:button:前往"`.

**Files:** `tests/screenshots/westgame2/building_upgrade_004.yaml`

### 4. Reference existing YAML format

> **Q:** Let me check how other YAML files write clicking the 前往 button.

User: "看一下其他yaml里面 点击 前往 按钮 怎么写的"

**Files:** `tests/screenshots/westgame2/building_upgrade_001.yaml`, `tests/screenshots/westgame2/building_upgrade_002.yaml`, `tests/screenshots/westgame2/building_upgrade_003.yaml`

### 5. Fix AutoHandler behavior

User: "Fix the AutoHandler to click the 前往 button"

> **Insight**
> The scene was classified as "unknown" which uses `_default` rules. The `popup` scene already had a rule for "前往" button, but `_default` didn't. Solution: add the same rule to `_default` so it works for unknown scenes too.

**Files:** `games/westgame2/game.json`

### 6. Commit changes

User: "commit this"

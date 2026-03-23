# Prompt Record

- Date: 2026-03-21
- Branch: master
- Commit: refactor: green_check from HSV to template matching + add tap offset

---

### 1. Add main_city screenshot test

User invoked `/add-screenshot-test` command to create a regression test case.

**Files:** `tests/screenshots/westgame2/main_city_002.png`, `tests/screenshots/westgame2/main_city_002.yaml`

### 2. Crop green_check template and use template matching

> **Q:** Does this output look correct? Any adjustments needed? Please provide a test case name.

User: "ok"

User: "对于green check的匹配太宽松了。屏幕上检测到太多的green check.我放了一个模板green_check.png，1.先剪裁这个模板，只剩下green check和透明背景，2.用这个模板进行匹配。继续"

> **Insight**
> The green_check was being detected by HSV color detection (11 matches), which is too broad. Need to: 1) Crop the template to remove background, 2) Remove HSV detection and rely only on template matching.

**Files:** `games/westgame2/templates/green_check.png`, `vision/indicator_detector.py`

### 3. Check confidence values in DOM output

User: "confidence值你在哪里看到的"

I explained that confidence values are shown in DOM output for icon elements from template matching, but HSV-based indicators don't show confidence.

### 4. Remove HSV green_check detection entirely

User: "去掉 HSV 的 green_check 检测，只使用模板检测"

Removed `_detect_green_checks()` call from `IndicatorDetector.detect()`. Updated `main_city` priority rules in game.json to use `type: icon, name: green_check` instead of `type: green_check`.

**Files:** `vision/indicator_detector.py`, `games/westgame2/game.json`, `tests/screenshots/westgame2/main_city_002.yaml`

### 5. Add tap offset for green_check icon

User: "对于游戏中的green check 图标， 要tap其中央坐标的 x-60 位置，有个偏移"

Added special offset handling in `AutoHandler._make_element_action()` to subtract 60 from x position when tapping green_check icons.

**Files:** `brain/auto_handler.py`

### 6. Commit changes

User: "commit"

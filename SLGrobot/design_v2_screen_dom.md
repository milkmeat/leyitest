# V2 Screen DOM Architecture Design

## 1. Overview

Replace the current fragmented vision pipeline (detect_finger, detect_close_x, scene_classify, find_button, find_text, etc.) with a unified **Screen DOM** system:

```
Screenshot ─→ ScreenDOMBuilder ─→ YAML DOM ─→ ScriptRunner / AutoHandler
                (OCR + CV)          (text)        (no LLM)
```

**Key principles:**
- Project itself makes **zero LLM calls**
- Claude Code (external) reads DOM output, generates scripts during conversation
- Scripts execute offline with coordinate-first, element-fallback strategy
- Auto mode uses DOM feature → scene classification → priority-based clicking

---

## 2. Screen DOM Format (YAML)

### 2.1 Structure

Three fixed spatial regions by Y coordinate (configurable in game.json):

| Region | Default Y range | Typical content |
|--------|----------------|-----------------|
| `top_bar` | y < 200 | Resources, level, mail icon |
| `center` | 200 ≤ y ≤ 1700 | Main content, buildings, panels |
| `bottom_bar` | y > 1700 | Navigation bar |

If a popup overlay is detected (semi-transparent dark mask), a `popup` section is added.

### 2.2 Example Output

```yaml
screen:
  resolution: [1080, 1920]
  scene: main_city          # inferred from DOM features (see §6)

  top_bar:
    - type: text
      value: "Lv.15"
      pos: [120, 35]
      size: [80, 30]
    - type: icon
      name: "icons/mail"
      pos: [980, 45]
      confidence: 0.92
    - type: red_dot
      near: "icons/mail"    # associated with nearest element
      pos: [1000, 30]

  center:
    - type: button
      text: "升级"
      pos: [540, 800]
      size: [240, 70]
      color: green
    - type: text
      value: "兵营 Lv.8"
      pos: [540, 400]
      size: [200, 40]
    - type: icon
      name: "icons/upgrade_arrow"
      pos: [650, 790]
      confidence: 0.88
    - type: green_check
      pos: [300, 650]

  bottom_bar:
    - type: icon
      name: "nav_bar/hero"
      pos: [216, 1850]
      confidence: 0.91
    - type: icon
      name: "nav_bar/map"
      pos: [432, 1850]
      confidence: 0.87
    - type: red_dot
      near: "nav_bar/hero"
      pos: [240, 1830]
```

### 2.3 Popup Overlay

When detected, popup elements are separated into their own section:

```yaml
  popup:
    bounds: [100, 300, 980, 1400]
    children:
      - type: text
        value: "确认升级？"
        pos: [540, 600]
      - type: button
        text: "确认"
        pos: [400, 1000]
        color: green
      - type: button
        text: "取消"
        pos: [680, 1000]
        color: gray
      - type: icon
        name: "buttons/close_x"
        pos: [950, 320]
        confidence: 0.95
```

### 2.4 Element Types

| type | Fields | Source |
|------|--------|--------|
| `text` | value, pos, size | OCR |
| `icon` | name, pos, confidence | Template matching |
| `button` | text, pos, size, color | Edge detection + OCR |
| `red_dot` | pos, near(optional) | Color detection |
| `green_check` | pos, near(optional) | Color detection |
| `finger` | pos, fingertip | Finger detector (existing 3-stage) |

---

## 3. DOM Builder Pipeline

### 3.1 Module: `vision/screen_dom.py`

```python
class ScreenDOMBuilder:
    def __init__(self, ocr_locator, template_matcher, game_profile):
        self.ocr = ocr_locator
        self.tm = template_matcher
        self.button_detector = ButtonDetector()
        self.indicator_detector = IndicatorDetector()
        self.finger_detector = FingerDetector(...)  # reuse existing
        self.popup_detector = PopupDetector()
        # Region boundaries from game_profile or defaults
        self.top_y = game_profile.dom_top_y or 200
        self.bottom_y = game_profile.dom_bottom_y or 1700

    def build(self, screenshot) -> dict:
        """Full pipeline: screenshot → DOM dict."""
        # 1. Popup detection (must be first — affects region assignment)
        popup_bounds = self.popup_detector.detect(screenshot)

        # 2. OCR — all visible text
        texts = self.ocr.find_all_text(screenshot)

        # 3. Template matching — all templates
        icons = self.tm.match_all(screenshot)

        # 4. Button detection — rectangular colored regions + OCR association
        buttons = self.button_detector.detect(screenshot, texts)

        # 5. Indicator detection — red dots, green checks
        indicators = self.indicator_detector.detect(screenshot)

        # 6. Finger detection — reuse existing 3-stage detector
        finger_match, flip_type = self.finger_detector.detect(screenshot)

        # 7. Remove OCR texts that are already associated with buttons
        free_texts = subtract_button_texts(texts, buttons)

        # 8. Assign elements to regions and build DOM
        dom = self._assemble(free_texts, icons, buttons, indicators,
                             finger_match, flip_type, popup_bounds)

        # 9. Infer scene from DOM features
        dom["screen"]["scene"] = self._classify_scene(dom)

        return dom

    def to_yaml(self, dom: dict) -> str:
        """Serialize DOM dict to YAML string."""
        ...

    def _classify_scene(self, dom: dict) -> str:
        """Infer scene type from DOM content. See §6."""
        ...

    def _assemble(self, texts, icons, buttons, indicators,
                  finger, flip_type, popup_bounds) -> dict:
        """Assign elements to spatial regions, build nested dict."""
        ...
```

### 3.2 Module: `vision/button_detector.py`

```python
class ButtonDetector:
    """Detect rectangular buttons by color + contour analysis."""

    # HSV ranges for common button colors
    COLOR_RANGES = {
        "green":  {"h": (35, 85),  "s": (80, 255), "v": (80, 255)},
        "blue":   {"h": (90, 130), "s": (80, 255), "v": (80, 255)},
        "orange": {"h": (10, 25),  "s": (100, 255), "v": (100, 255)},
        "red":    {"h": (0, 10),   "s": (100, 255), "v": (100, 255)},
        "gray":   {"h": (0, 180),  "s": (0, 50),  "v": (80, 180)},
    }

    # Contour filters
    MIN_AREA = 3000       # minimum button area in px²
    MAX_AREA = 200000     # maximum
    ASPECT_RANGE = (1.5, 8.0)  # width/height ratio
    RECT_SCORE = 0.75     # minimum rectangularity (contour area / bounding rect area)

    def detect(self, screenshot, ocr_results) -> list[ButtonElement]:
        """
        1. Convert to HSV
        2. For each color range: threshold → morphology close → findContours
        3. Filter by area, aspect ratio, rectangularity
        4. For each valid contour: find OCR text inside bounding rect
        5. Merge overlapping detections
        6. Return ButtonElement(text, pos, size, color)
        """
        ...
```

### 3.3 Module: `vision/indicator_detector.py`

```python
class IndicatorDetector:
    """Detect red dots and green check marks by color + shape."""

    def detect(self, screenshot) -> list[IndicatorElement]:
        """
        Red dots:
          - HSV red range (h: 0-10 or 170-180, s: 100+, v: 100+)
          - Small circular contours (area 50-800 px², circularity > 0.6)

        Green checks:
          - HSV green range (h: 35-85, s: 80+, v: 80+)
          - Small area (100-2000 px²)
          - Non-circular (distinguish from green buttons)

        Returns IndicatorElement(type, pos)
        """
        ...
```

### 3.4 Module: `vision/popup_detector.py`

```python
class PopupDetector:
    """Detect popup overlay by semi-transparent dark mask analysis."""

    def detect(self, screenshot) -> tuple[int,int,int,int] | None:
        """
        1. Convert to grayscale
        2. Compute border mean brightness (top/bottom/left/right 10% strips)
        3. Compute center mean brightness (center 50% area)
        4. If border_mean < center_mean * 0.5 and center_mean > 50:
           → popup detected
        5. Find popup bounds: threshold dark pixels, find largest
           bright connected component → that's the popup rect
        6. Return (x1, y1, x2, y2) or None
        """
        ...
```

### 3.5 Performance Budget

| Step | Time | Notes |
|------|------|-------|
| OCR (RapidOCR, zh+en) | ~500ms | Already optimized in current code |
| Template matching (50 templates) | ~800ms | 0.5x prescale + full-res verify |
| Button detection | ~150ms | HSV + contour per color |
| Indicator detection | ~100ms | HSV + contour, small areas only |
| Finger detection | ~50ms | Existing prescan optimization |
| Popup detection | ~30ms | Simple pixel stats |
| Assembly + scene classify | ~20ms | Dict manipulation |
| **Total** | **~1.7s** | Well within 3s budget |

---

## 4. Script Format

### 4.1 File Location

`games/<id>/scripts/<name>.yaml` — replaces `games/<id>/quest_scripts/`

### 4.2 Script Structure

```yaml
name: upgrade_barracks
description: "升级兵营到下一级"

steps:
  - action: tap
    pos: [540, 800]
    target: {type: button, text: "升级"}
    wait: 1.0

  - action: tap
    pos: [400, 1000]
    target: {type: button, text: "确认"}
    wait: 2.0

  - action: if
    condition:
      exists: {type: text, value: "资源不足"}
    then:
      - action: tap
        pos: [680, 1000]
        target: {type: button, text: "取消"}
        wait: 0.5
    else:
      - action: tap
        pos: [950, 180]
        target: {type: icon, name: "buttons/close_x"}
        wait: 0.5

  - action: swipe
    from: [540, 1000]
    to: [540, 400]
    duration_ms: 300
    wait: 0.5

  - action: wait_for
    target: {type: text, value: "升级完成"}
    timeout: 60
    poll_interval: 3
```

### 4.3 Action Types

| action | Required fields | Description |
|--------|----------------|-------------|
| `tap` | pos, target | Tap at pos; fallback: find target in DOM |
| `swipe` | from, to, duration_ms | Swipe gesture |
| `wait` | seconds | Static wait |
| `wait_for` | target, timeout | Poll DOM until target element appears |
| `if` | condition, then, else(opt) | Conditional branch |

### 4.4 Condition Syntax (for `if` and `wait_for`)

```yaml
# Element exists in current DOM
condition:
  exists: {type: button, text: "确认"}

# Element does NOT exist
condition:
  not_exists: {type: text, value: "冷却中"}

# Scene matches
condition:
  scene: main_city

# Combine (AND)
condition:
  all:
    - exists: {type: button, text: "升级"}
    - not_exists: {type: text, value: "资源不足"}

# Combine (OR)
condition:
  any:
    - exists: {type: text, value: "完成"}
    - exists: {type: text, value: "领取"}
```

### 4.5 Execution Logic: `brain/script_runner.py`

```python
class ScriptRunner:
    def __init__(self, adb, dom_builder):
        self.adb = adb
        self.dom_builder = dom_builder

    def run(self, script: dict):
        for step in script["steps"]:
            self._execute_step(step)

    def _execute_step(self, step):
        action = step["action"]

        if action == "tap":
            self._execute_tap(step)
        elif action == "swipe":
            self._execute_swipe(step)
        elif action == "wait":
            time.sleep(step["seconds"])
        elif action == "wait_for":
            self._execute_wait_for(step)
        elif action == "if":
            self._execute_if(step)

    def _execute_tap(self, step):
        """
        Normal path (fast, no DOM needed):
          1. Tap at step["pos"]
          2. Wait step["wait"] seconds
          3. Done → ~0.1s + wait

        Failure detection + fallback path:
          4. Take screenshot → build DOM
          5. Compare with pre-tap DOM:
             - If DOM changed → tap succeeded → continue
             - If DOM unchanged → tap missed
          6. Find step["target"] in new DOM
          7. Tap at found element's pos
          8. Retry up to 3 times
        """
        # Fast path
        x, y = step["pos"]
        self.adb.tap(x, y)
        wait = step.get("wait", 0.5)
        time.sleep(wait)

        # Verify if needed (only when target is provided)
        if "target" not in step:
            return

        # Take screenshot and build DOM
        screenshot = self.adb.screenshot()
        dom = self.dom_builder.build(screenshot)

        # Check if expected change occurred
        # (e.g., button should have disappeared or new element appeared)
        target = step["target"]
        found = find_element(dom, target)

        if found is None:
            # Target gone → tap likely succeeded (button was clicked and disappeared)
            return

        # Target still there → tap may have missed, retry at new position
        logger.warning(f"Target still present, retrying at ({found.pos})")
        self.adb.tap(*found.pos)

    def _execute_if(self, step):
        """
        1. Take screenshot → build DOM
        2. Evaluate condition against DOM
        3. Execute then-branch or else-branch
        """
        screenshot = self.adb.screenshot()
        dom = self.dom_builder.build(screenshot)

        if evaluate_condition(step["condition"], dom):
            for sub_step in step["then"]:
                self._execute_step(sub_step)
        elif "else" in step:
            for sub_step in step["else"]:
                self._execute_step(sub_step)
```

---

## 5. Element Matching Algorithm

When the fallback path needs to find a target element in the DOM:

```python
def find_element(dom: dict, target: dict) -> Element | None:
    """Find element in DOM matching target descriptor."""
    candidates = flatten_all_elements(dom)
    target_type = target.get("type")

    if target_type == "button":
        matches = [e for e in candidates
                   if e["type"] == "button"
                   and target["text"] in e.get("text", "")]
    elif target_type == "text":
        matches = [e for e in candidates
                   if e["type"] == "text"
                   and target["value"] in e.get("value", "")]
    elif target_type == "icon":
        matches = [e for e in candidates
                   if e["type"] == "icon"
                   and e.get("name") == target["name"]]
    elif target_type in ("red_dot", "green_check", "finger"):
        matches = [e for e in candidates
                   if e["type"] == target_type]
    else:
        matches = []

    if len(matches) == 1:
        return matches[0]
    elif len(matches) > 1:
        # Multiple matches: pick closest to original pos if available
        if "pos" in target:
            return min(matches, key=lambda e:
                       distance(e["pos"], target["pos"]))
        return matches[0]
    return None
```

---

## 6. Scene Classification via DOM

Replace the current `SceneClassifier` with rule-based inference from DOM content.

### 6.1 Rules (configured in `game.json`)

```json
{
  "scene_rules": [
    {
      "scene": "popup",
      "condition": {"popup_detected": true}
    },
    {
      "scene": "loading",
      "condition": {"element_count_below": 3}
    },
    {
      "scene": "main_city",
      "condition": {"exists": {"type": "icon", "name": "scenes/main_city"}}
    },
    {
      "scene": "world_map",
      "condition": {"exists": {"type": "icon", "name": "scenes/world_map"}}
    },
    {
      "scene": "hero",
      "condition": {"exists": {"type": "icon", "name": "scenes/hero"}}
    },
    {
      "scene": "story_dialogue",
      "condition": {"exists": {"type": "icon", "name": "icons/down_triangle"}}
    }
  ]
}
```

Rules are evaluated top-to-bottom, first match wins. Fallback: `unknown`.

### 6.2 Implementation

```python
def _classify_scene(self, dom: dict) -> str:
    # Popup is structural (has popup section)
    if "popup" in dom.get("screen", {}):
        return "popup"

    # Loading: very few elements detected
    all_elements = flatten_all_elements(dom)
    if len(all_elements) < 3:
        return "loading"

    # Rule-based matching from game.json scene_rules
    for rule in self.scene_rules:
        if evaluate_condition(rule["condition"], dom):
            return rule["scene"]

    return "unknown"
```

---

## 7. Auto Mode

### 7.1 Logic

Auto mode runs without LLM, without fixed scripts. Each iteration:

```
loop:
  1. Screenshot → ScreenDOMBuilder.build() → DOM
  2. DOM → classify scene
  3. Scene config → get element click priority for this scene
  4. Iterate elements by priority, tap the first available one
  5. Wait → repeat
```

### 7.2 Scene Click Priority (configured in `game.json`)

```json
{
  "auto_priorities": {
    "popup": [
      {"type": "icon", "name": "buttons/close_x"},
      {"type": "icon", "name": "buttons/close"},
      {"type": "button", "text_match": "确[定认]|关闭|返回"},
      {"type": "button", "text_match": "取消"}
    ],
    "main_city": [
      {"type": "finger"},
      {"type": "green_check"},
      {"type": "red_dot"},
      {"type": "button", "text_match": "领取|收集|claim"}
    ],
    "world_map": [
      {"type": "finger"},
      {"type": "button", "text_match": "返回"}
    ],
    "story_dialogue": [
      {"type": "icon", "name": "icons/down_triangle"}
    ],
    "loading": [],
    "_default": [
      {"type": "finger"},
      {"type": "icon", "name": "buttons/close_x"},
      {"type": "button", "color": "green"}
    ]
  }
}
```

### 7.3 Priority Matching Logic

```python
class AutoHandler:
    def __init__(self, dom_builder, game_profile):
        self.dom_builder = dom_builder
        self.priorities = game_profile.auto_priorities

    def get_action(self, dom: dict) -> dict | None:
        """Return single best action for current DOM, or None."""
        scene = dom["screen"]["scene"]
        priority_list = self.priorities.get(scene,
                                            self.priorities.get("_default", []))

        all_elements = flatten_all_elements(dom)

        for priority in priority_list:
            match = find_priority_match(priority, all_elements)
            if match:
                return {"type": "tap", "x": match["pos"][0],
                        "y": match["pos"][1],
                        "reason": f"auto: {priority}"}

        return None  # nothing to click, wait
```

### 7.4 Auto Loop Implementation

```python
def auto_loop(self, max_loops=None):
    count = 0
    while max_loops is None or count < max_loops:
        screenshot = self.adb.screenshot()
        dom = self.dom_builder.build(screenshot)

        # Log DOM for debugging
        logger.info(f"DOM: scene={dom['screen']['scene']}, "
                    f"elements={count_elements(dom)}")

        action = self.auto_handler.get_action(dom)
        if action:
            self.adb.tap(action["x"], action["y"])
            logger.info(f"Auto tap: ({action['x']}, {action['y']}) "
                        f"- {action['reason']}")
        else:
            logger.info("Auto: nothing to click, waiting")

        time.sleep(config.LOOP_INTERVAL)
        count += 1
```

---

## 8. Module Changes Summary

### New files
| File | Purpose |
|------|---------|
| `vision/screen_dom.py` | ScreenDOMBuilder — main pipeline |
| `vision/button_detector.py` | Rectangular button detection |
| `vision/indicator_detector.py` | Red dot / green check detection |
| `vision/popup_detector.py` | Semi-transparent overlay detection |
| `brain/script_runner.py` | YAML script executor (replaces QuestScriptRunner) |

### Modified files
| File | Change |
|------|--------|
| `brain/auto_handler.py` | Rewrite: DOM-based priority clicking |
| `main.py` | New CLI commands: `dom`, `run`, `list-scripts` |
| `game_profile.py` | New fields: scene_rules, auto_priorities, dom region config |
| `games/<id>/game.json` | Add scene_rules, auto_priorities sections |

### Removed files
| File | Replaced by |
|------|-------------|
| `scene/classifier.py` | DOM scene rules in screen_dom.py |
| `scene/popup_filter.py` | popup_detector.py + auto_handler priority |
| `brain/quest_script.py` | brain/script_runner.py |
| `brain/llm_planner.py` | Removed (no LLM in project) |
| `vision/quest_bar_detector.py` | DOM text/indicator detection |
| `vision/grid_overlay.py` | Removed (LLM grid no longer needed) |

### Preserved (no change)
| File | Notes |
|------|-------|
| `vision/ocr_locator.py` | Used by DOM builder |
| `vision/template_matcher.py` | Used by DOM builder |
| `vision/building_finder.py` | Still needed for city scrolling |
| `brain/finger_detector.py` | Used by DOM builder |
| `brain/stuck_recovery.py` | May still be useful |
| `device/*` | No changes |
| `executor/*` | Simplified but kept for script_runner |
| `state/*` | Kept for resource tracking etc. |

---

## 9. CLI Commands

### New commands
```bash
python main.py dom                 # Screenshot → print YAML DOM to stdout
python main.py dom --save          # Also save screenshot + DOM to data/dom_history/
python main.py run <script_name>   # Execute a script
python main.py run <name> --dry    # Dry run (print steps, no execution)
python main.py scripts             # List available scripts
python main.py auto [loops]        # DOM-based auto loop (no LLM)
```

### Removed commands
```bash
# These are replaced by `dom`:
python main.py scene               # → dom shows scene in output
python main.py detect_finger       # → dom shows finger element
python main.py detect_close_x      # → dom shows close_x icon

# These are replaced by `run`:
python main.py quest <name>        # → run <name>
python main.py quest_rules         # → scripts
python main.py quest_test <name>   # → run <name> --dry
```

---

## 10. Claude Code Workflow

How Claude Code (the external LLM) interacts with this system:

### 10.1 Reading Screen State

```
User:   python main.py dom
Output: (YAML DOM printed to stdout)
User:   (pastes DOM into Claude Code conversation)
Claude: "I see you're on the main city screen with a level 8 barracks.
         The upgrade button is available (green). Want me to create
         a script to upgrade it?"
```

### 10.2 Generating Scripts

```
User:   "Yes, create an upgrade script"
Claude: (writes games/westgame2/scripts/upgrade_barracks.yaml)
        "Script saved. Run with: python main.py run upgrade_barracks"
```

### 10.3 Iterative Development

```
User:   python main.py run upgrade_barracks
Output: "Step 2 failed: target {type: button, text: 确认} not found"
User:   python main.py dom
Output: (shows current screen — maybe a different confirmation dialog)
User:   (pastes to Claude Code)
Claude: (updates the script with corrected target)
```

### 10.4 History Context

Claude Code conversation naturally maintains history (up to ~10 DOM snapshots + actions taken). No special mechanism needed — it's just conversation context.

---

## 11. Migration Plan

1. **Create branch snapshot**: `git checkout -b v1-archive && git checkout -b v2-screen-dom`
2. **Phase 1**: Build `vision/screen_dom.py` + sub-detectors, `dom` CLI command
3. **Phase 2**: Build `brain/script_runner.py`, `run` CLI command
4. **Phase 3**: Rewrite `brain/auto_handler.py` with DOM-based priorities
5. **Phase 4**: Update `game.json` with scene_rules and auto_priorities
6. **Phase 5**: Remove old modules (scene/, quest_script, llm_planner, grid_overlay)
7. **Phase 6**: Update `main.py` CLI, clean up imports

Each phase is independently testable. Phase 1 can be validated immediately by running `python main.py dom` and inspecting the output.

---

## 12. Open Design Decisions

These can be decided during implementation:

1. **DOM diff for tap verification** — should we compute a structural diff between pre-tap and post-tap DOMs? Or just check if the target element disappeared?
   → Start simple: check if target disappeared. Add diff later if needed.

2. **Template matching optimization** — match all 50 templates every time, or skip categories based on detected region?
   → Start with match all. Profile and optimize if >1s.

3. **Button detector color calibration** — HSV ranges may need per-game tuning.
   → Start with hardcoded ranges, move to game.json if needed.

4. **Indicator near-element association** — how close must a red_dot be to an icon to be "near" it?
   → Default: 80px radius. Configurable.

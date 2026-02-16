# SLGrobot - SLG Game AI Agent Detailed Design

## Project Overview

SLGrobot is a Python-based AI Agent that uses Claude LLM to autonomously play "Frozen Island" (an SLG mobile game) on an Android emulator (LDPlayer/MuMu) via ADB, running on Windows.

### Core Design Principles

1. **LLM does not do pixel-level positioning** -- it does "semantic selection", CV handles coordinates.
2. **LLM does not remember state** -- structured JSON/SQLite stores game state.
3. **90% of operations do not need LLM** -- local CV + rule engine handles routine tasks.
4. **Pre-classify scenes** before processing, dispatch to specialized handlers.
5. **Validate before execution, confirm after** -- never blindly execute LLM output.

### Five Problems This Architecture Solves

| Problem | Solution |
|---------|----------|
| Coordinate precision (grounding) | Grid overlay + template matching + OCR, LLM only picks grid cell |
| Context & long-term memory | Persistent game state in JSON, not LLM context |
| Inference latency & cost | 90% local CV/rules (<500ms), LLM called every ~30min |
| UI complexity & popups | Scene classifier + popup auto-filter before any processing |
| Hallucination & misoperation | Pre-validation + post-execution screenshot confirmation |

---

## 1. System Architecture

```
+---------------------------------------------------+
|               Strategic Layer                      |
|        (Claude LLM - low-frequency, ~30min)        |
|  Long-term planning: development path, resource    |
|  allocation, war decisions                         |
+------------------------+--------------------------+
                         | Strategic commands (JSON)
+------------------------v--------------------------+
|               Tactical Layer                       |
|        (Local rule engine - second-level)          |
|  Task queue: decompose strategy into task          |
|  sequences. State machine: track scene/progress    |
+------------------------+--------------------------+
                         | Operation commands
+------------------------v--------------------------+
|              Execution Layer                       |
|        (CV + ADB - millisecond-level)              |
|  Screenshot -> Scene ID -> Element locate -> Tap   |
+---------------------------------------------------+
```

### Directory Structure

```
SLGrobot/
  config.py              # Global configuration
  main.py                # Main loop entry point
  requirements.txt       # Python dependencies
  device/
    __init__.py
    adb_controller.py    # ADB connection, screenshot, tap, swipe
    input_actions.py     # High-level input (long press, drag, multi-touch)
  vision/
    __init__.py
    screenshot.py        # Screenshot capture and management
    template_matcher.py  # Template matching engine
    ocr_locator.py       # OCR text detection and positioning
    grid_overlay.py      # Grid annotation for LLM communication
    element_detector.py  # Unified detection entry point
  scene/
    __init__.py
    classifier.py        # Scene classification
    popup_filter.py      # Popup detection and auto-close
    handlers/
      __init__.py
      base.py            # Base handler class
      main_city.py       # Main city scene handler
      world_map.py       # World map scene handler
      battle.py          # Battle scene handler
  state/
    __init__.py
    game_state.py        # Game state data model
    state_tracker.py     # Extract and update state from screenshots
    persistence.py       # JSON persistence
  brain/
    __init__.py
    auto_handler.py      # Automatic operations (no LLM, <100ms)
    rule_engine.py       # Rule-based decisions (<500ms)
    llm_planner.py       # Claude API strategic planning (3-10s)
    task_queue.py        # Task queue management
  executor/
    __init__.py
    action_validator.py  # Pre-execution validation
    action_runner.py     # Action execution
    result_checker.py    # Post-execution confirmation
  utils/
    __init__.py
    logger.py            # Logging with screenshot recording
    image_utils.py       # Image processing helpers
  templates/
    buttons/             # Button template images
    icons/               # Icon template images
    scenes/              # Scene feature templates
  data/
    game_state.json      # Persisted game state
    navigation_paths.json # Predefined navigation click paths
```

---

## 2. Module Detailed Design

### 2.1 `config.py` - Global Configuration

**Responsibility:** Centralized configuration for all modules.

```python
# config.py

# ADB
ADB_HOST = "127.0.0.1"
ADB_PORT = 5555
SCREENSHOT_DIR = "data/screenshots"

# Resolution
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

# Claude API
ANTHROPIC_API_KEY = "sk-..."
LLM_MODEL = "claude-sonnet-4-20250514"
LLM_MAX_TOKENS = 1024

# Timing
LOOP_INTERVAL = 2.0          # seconds between main loop iterations
LLM_CONSULT_INTERVAL = 1800  # seconds between LLM strategic calls (~30min)

# Template matching
TEMPLATE_MATCH_THRESHOLD = 0.8

# Grid overlay
GRID_COLS = 8
GRID_ROWS = 6

# Paths
TEMPLATE_DIR = "templates"
STATE_FILE = "data/game_state.json"
NAV_PATHS_FILE = "data/navigation_paths.json"
```

**Dependencies:** None (leaf module).

---

### 2.2 `device/` - Device Control Layer

#### `device/adb_controller.py`

**Responsibility:** Low-level ADB operations -- connect, screenshot, tap, swipe.

```python
class ADBController:
    def __init__(self, host: str, port: int) -> None:
        """Connect to emulator via ADB."""

    def connect(self) -> bool:
        """Establish ADB connection. Returns True on success."""

    def screenshot(self) -> np.ndarray:
        """Capture screenshot, return as BGR numpy array (OpenCV format)."""

    def tap(self, x: int, y: int) -> None:
        """Tap at pixel coordinate (x, y)."""

    def swipe(self, x1: int, y1: int, x2: int, y2: int, duration_ms: int = 300) -> None:
        """Swipe from (x1,y1) to (x2,y2)."""

    def is_connected(self) -> bool:
        """Check if ADB connection is alive."""
```

**Dependencies:** `config.py`, external `adbutils` or `pure-python-adb`.

#### `device/input_actions.py`

**Responsibility:** High-level input wrappers built on `ADBController`.

```python
class InputActions:
    def __init__(self, adb: ADBController) -> None: ...

    def long_press(self, x: int, y: int, duration_ms: int = 1000) -> None:
        """Long press at (x, y)."""

    def drag(self, x1: int, y1: int, x2: int, y2: int, duration_ms: int = 500) -> None:
        """Drag from (x1,y1) to (x2,y2)."""

    def tap_center(self) -> None:
        """Tap screen center (dismiss dialogs)."""
```

**Dependencies:** `device/adb_controller.py`.

---

### 2.3 `vision/` - Visual Perception Layer

#### `vision/screenshot.py`

**Responsibility:** Screenshot lifecycle management -- capture, save, history.

```python
class ScreenshotManager:
    def __init__(self, adb: ADBController, save_dir: str) -> None: ...

    def capture(self) -> np.ndarray:
        """Capture and return current screenshot."""

    def save(self, image: np.ndarray, label: str = "") -> str:
        """Save screenshot to disk with timestamp. Returns file path."""

    def get_recent(self, count: int = 5) -> list[np.ndarray]:
        """Return last N screenshots from memory."""
```

**Dependencies:** `device/adb_controller.py`, `config.py`.

#### `vision/template_matcher.py`

**Responsibility:** Match pre-stored template images against screenshots.

```python
@dataclass
class MatchResult:
    template_name: str
    confidence: float
    x: int          # center x of matched region
    y: int          # center y of matched region
    bbox: tuple[int, int, int, int]  # (x1, y1, x2, y2)

class TemplateMatcher:
    def __init__(self, template_dir: str, threshold: float = 0.8) -> None:
        """Load all templates from directory into memory cache."""

    def match_one(self, screenshot: np.ndarray, template_name: str) -> MatchResult | None:
        """Match a specific template. Returns None if below threshold."""

    def match_all(self, screenshot: np.ndarray, category: str = "") -> list[MatchResult]:
        """Match all templates (optionally filtered by category). Returns matches above threshold."""

    def match_best(self, screenshot: np.ndarray, template_names: list[str]) -> MatchResult | None:
        """Find the best match among given templates."""
```

**Dependencies:** `config.py`, OpenCV.

#### `vision/ocr_locator.py`

**Responsibility:** OCR text detection with bounding box positions.

```python
@dataclass
class OCRResult:
    text: str
    confidence: float
    bbox: tuple[int, int, int, int]  # (x1, y1, x2, y2)
    center: tuple[int, int]          # (cx, cy)

class OCRLocator:
    def __init__(self) -> None:
        """Initialize OCR engine (PaddleOCR or Tesseract)."""

    def find_text(self, screenshot: np.ndarray, target_text: str) -> OCRResult | None:
        """Find specific text in screenshot. Returns position or None."""

    def find_all_text(self, screenshot: np.ndarray) -> list[OCRResult]:
        """Extract all text with positions from screenshot."""

    def find_numbers_in_region(self, screenshot: np.ndarray, region: tuple[int, int, int, int]) -> str:
        """Extract numeric text from a specific region (for resource values)."""
```

**Dependencies:** `config.py`, PaddleOCR or pytesseract.

#### `vision/grid_overlay.py`

**Responsibility:** Overlay a labeled grid (A1, B3, C4...) on screenshots for LLM communication.

```python
class GridOverlay:
    def __init__(self, cols: int = 8, rows: int = 6) -> None: ...

    def annotate(self, screenshot: np.ndarray) -> np.ndarray:
        """Draw labeled grid on screenshot. Returns annotated image."""

    def cell_to_pixel(self, cell: str) -> tuple[int, int]:
        """Convert grid cell label (e.g., 'B3') to pixel center (x, y)."""

    def pixel_to_cell(self, x: int, y: int) -> str:
        """Convert pixel coordinate to grid cell label."""

    def get_cell_region(self, cell: str) -> tuple[int, int, int, int]:
        """Return bounding box (x1, y1, x2, y2) for a grid cell."""
```

**Dependencies:** `config.py`, OpenCV.

#### `vision/element_detector.py`

**Responsibility:** Unified element detection entry point. Dispatches by priority.

```python
@dataclass
class Element:
    name: str
    source: str       # "template" | "ocr" | "contour" | "llm"
    confidence: float
    x: int
    y: int
    bbox: tuple[int, int, int, int]

class ElementDetector:
    def __init__(self, template_matcher: TemplateMatcher,
                 ocr_locator: OCRLocator,
                 grid_overlay: GridOverlay) -> None: ...

    def locate(self, screenshot: np.ndarray, target: str,
               methods: list[str] | None = None) -> Element | None:
        """
        Locate a UI element by name/text.
        Detection priority (unless overridden by methods):
          1. Template matching
          2. OCR text search
          3. Color/contour detection
          4. LLM fallback (grid overlay)
        Returns Element with coordinates, or None.
        """

    def locate_all(self, screenshot: np.ndarray) -> list[Element]:
        """Detect all recognizable elements in screenshot."""
```

**Dependencies:** `vision/template_matcher.py`, `vision/ocr_locator.py`, `vision/grid_overlay.py`.

---

### 2.4 `scene/` - Scene Understanding Layer

#### `scene/classifier.py`

**Responsibility:** Classify the current game screen into a known scene type.

```python
class SceneClassifier:
    SCENES = ["main_city", "world_map", "battle", "popup", "loading", "unknown"]

    def __init__(self, template_matcher: TemplateMatcher) -> None:
        """Load scene-identifying feature templates."""

    def classify(self, screenshot: np.ndarray) -> str:
        """
        Classify screenshot into one of SCENES.
        Uses feature-region template matching (fast, <50ms).
        Returns scene name string.
        """

    def get_confidence(self, screenshot: np.ndarray) -> dict[str, float]:
        """Return confidence scores for all scenes."""
```

**Dependencies:** `vision/template_matcher.py`.

#### `scene/popup_filter.py`

**Responsibility:** Detect and auto-close popup dialogs before they interfere.

```python
class PopupFilter:
    def __init__(self, template_matcher: TemplateMatcher,
                 adb: ADBController) -> None: ...

    def is_popup(self, screenshot: np.ndarray) -> bool:
        """Check if current screen has a popup overlay."""

    def handle(self, screenshot: np.ndarray) -> bool:
        """
        Detect and close popup. Returns True if popup was found and closed.
        Strategy: find X/Close button via template match, tap it.
        """
```

**Dependencies:** `vision/template_matcher.py`, `device/adb_controller.py`.

#### `scene/handlers/base.py`

**Responsibility:** Abstract base class for scene-specific handlers.

```python
from abc import ABC, abstractmethod

class BaseSceneHandler(ABC):
    def __init__(self, element_detector: ElementDetector,
                 game_state: GameState) -> None: ...

    @abstractmethod
    def extract_info(self, screenshot: np.ndarray) -> dict:
        """Extract scene-specific information from screenshot."""

    @abstractmethod
    def get_available_actions(self, screenshot: np.ndarray) -> list[str]:
        """Return list of available actions in this scene."""
```

#### `scene/handlers/main_city.py`

```python
class MainCityHandler(BaseSceneHandler):
    def extract_info(self, screenshot: np.ndarray) -> dict:
        """Extract: resource bars, building levels, red dots, queues."""

    def get_available_actions(self, screenshot: np.ndarray) -> list[str]:
        """Return: ['upgrade_building', 'collect_resources', 'train_troops', ...]"""
```

#### `scene/handlers/world_map.py`

```python
class WorldMapHandler(BaseSceneHandler):
    def extract_info(self, screenshot: np.ndarray) -> dict:
        """Extract: visible tiles, resource nodes, enemy positions."""

    def get_available_actions(self, screenshot: np.ndarray) -> list[str]:
        """Return: ['gather_resource', 'scout_enemy', 'send_troops', ...]"""
```

#### `scene/handlers/battle.py`

```python
class BattleHandler(BaseSceneHandler):
    def extract_info(self, screenshot: np.ndarray) -> dict:
        """Extract: battle result (win/lose), rewards, losses."""

    def get_available_actions(self, screenshot: np.ndarray) -> list[str]:
        """Return: ['collect_reward', 'return_to_city', ...]"""
```

**Dependencies:** `vision/element_detector.py`, `state/game_state.py`.

---

### 2.5 `state/` - State Management Layer

#### `state/game_state.py`

**Responsibility:** In-memory game state data model.

```python
@dataclass
class BuildingState:
    name: str
    level: int
    upgrading: bool = False
    finish_time: str | None = None

@dataclass
class MarchState:
    target: str
    action: str          # "gather" | "attack" | "scout"
    return_time: str

class GameState:
    def __init__(self) -> None:
        self.scene: str = "unknown"
        self.resources: dict[str, int] = {}       # {"food": 50000, "wood": 32000, ...}
        self.buildings: dict[str, BuildingState] = {}
        self.troops_marching: list[MarchState] = []
        self.task_queue: list[str] = []
        self.last_actions: list[dict] = []
        self.cooldowns: dict[str, str] = {}
        self.last_llm_consult: str = ""

    def to_dict(self) -> dict:
        """Serialize to dict for JSON persistence and LLM context."""

    def from_dict(self, data: dict) -> None:
        """Load from dict."""

    def summary_for_llm(self) -> str:
        """Generate concise text summary for LLM prompt (minimize tokens)."""
```

**Dependencies:** None (data model).

#### `state/state_tracker.py`

**Responsibility:** Extract game state from screenshots and update `GameState`.

```python
class StateTracker:
    def __init__(self, game_state: GameState,
                 ocr_locator: OCRLocator,
                 template_matcher: TemplateMatcher) -> None: ...

    def update(self, screenshot: np.ndarray, scene: str) -> None:
        """
        Update game_state based on current screenshot and scene.
        Extracts resources (OCR), building status, troop info, etc.
        """

    def _update_resources(self, screenshot: np.ndarray) -> None:
        """OCR resource bar numbers."""

    def _update_buildings(self, screenshot: np.ndarray) -> None:
        """Detect building levels and upgrade status."""
```

**Dependencies:** `state/game_state.py`, `vision/ocr_locator.py`, `vision/template_matcher.py`.

#### `state/persistence.py`

**Responsibility:** Save/load `GameState` to/from JSON file.

```python
class StatePersistence:
    def __init__(self, file_path: str) -> None: ...

    def save(self, game_state: GameState) -> None:
        """Save game state to JSON file."""

    def load(self) -> dict | None:
        """Load game state from JSON file. Returns None if file doesn't exist."""
```

**Dependencies:** `config.py`.

---

### 2.6 `brain/` - Decision Layer

#### `brain/task_queue.py`

**Responsibility:** Manage ordered task queue.

```python
@dataclass
class Task:
    name: str
    priority: int = 0
    params: dict = field(default_factory=dict)
    status: str = "pending"   # "pending" | "running" | "done" | "failed"
    retry_count: int = 0

class TaskQueue:
    def __init__(self) -> None:
        self._queue: list[Task] = []

    def add(self, task: Task) -> None:
        """Add task, maintaining priority order."""

    def add_tasks(self, tasks: list[Task]) -> None:
        """Add multiple tasks from LLM plan."""

    def next(self) -> Task | None:
        """Pop and return highest-priority pending task."""

    def has_pending(self) -> bool:
        """Check if there are pending tasks."""

    def mark_done(self, task: Task) -> None: ...
    def mark_failed(self, task: Task) -> None: ...
    def get_status(self) -> list[dict]: ...
```

**Dependencies:** None.

#### `brain/auto_handler.py`

**Responsibility:** Instant automatic operations that never need LLM (<100ms).

```python
class AutoHandler:
    def __init__(self, template_matcher: TemplateMatcher,
                 element_detector: ElementDetector) -> None: ...

    def get_actions(self, screenshot: np.ndarray, game_state: GameState) -> list[dict]:
        """
        Detect and return auto-actions:
        - Close popups (template match X button)
        - Claim rewards (detect red dots)
        - Skip waiting screens
        Returns list of action dicts.
        """
```

**Dependencies:** `vision/template_matcher.py`, `vision/element_detector.py`.

#### `brain/rule_engine.py`

**Responsibility:** Rule-based task execution without LLM (<500ms).

```python
class RuleEngine:
    def __init__(self, element_detector: ElementDetector,
                 game_state: GameState) -> None: ...

    def plan(self, task: Task, screenshot: np.ndarray,
             game_state: GameState) -> list[dict]:
        """
        Decompose a task into a sequence of actions using predefined rules.
        Example: "upgrade_barracks" ->
          [navigate("barracks"), tap("Upgrade"), wait("popup_confirm"), tap("Confirm")]
        Returns list of action dicts.
        """

    def can_handle(self, task: Task) -> bool:
        """Check if this task has predefined rules."""
```

**Dependencies:** `vision/element_detector.py`, `state/game_state.py`, `data/navigation_paths.json`.

#### `brain/llm_planner.py`

**Responsibility:** Claude API calls for strategic planning (3-10s, called infrequently).

```python
class LLMPlanner:
    def __init__(self, api_key: str, model: str,
                 grid_overlay: GridOverlay) -> None: ...

    def get_plan(self, screenshot: np.ndarray,
                 game_state: GameState) -> list[Task]:
        """
        Send annotated screenshot + state summary to Claude.
        Parse JSON response into Task list.
        Called every ~30 minutes or when encountering unknown situations.
        """

    def analyze_unknown_scene(self, screenshot: np.ndarray,
                               game_state: GameState) -> list[dict]:
        """Ask Claude to analyze an unknown/unexpected screen and suggest actions."""

    def should_consult(self, game_state: GameState) -> bool:
        """Check if enough time has passed since last LLM consultation."""
```

**LLM Output Format (forced JSON):**
```json
{
    "reasoning": "Castle upgrade requires barracks at level 12 first",
    "actions": [
        {"type": "navigate", "target": "barracks"},
        {"type": "tap", "target_text": "Upgrade", "fallback_grid": "C4"},
        {"type": "wait", "condition": "popup_confirm"},
        {"type": "tap", "target_text": "Confirm"}
    ]
}
```

**Dependencies:** `vision/grid_overlay.py`, `state/game_state.py`, `anthropic` SDK.

---

### 2.7 `executor/` - Execution & Validation Layer

#### `executor/action_validator.py`

**Responsibility:** Pre-execution validation -- ensure action is safe to execute.

```python
class ActionValidator:
    def __init__(self, element_detector: ElementDetector,
                 scene_classifier: SceneClassifier) -> None: ...

    def validate(self, action: dict, screenshot: np.ndarray) -> bool:
        """
        Validate before execution:
        - Does target element exist on screen?
        - Is coordinate within screen bounds?
        - Does current scene match expected scene?
        Returns True if action is safe to execute.
        """
```

**Dependencies:** `vision/element_detector.py`, `scene/classifier.py`.

#### `executor/action_runner.py`

**Responsibility:** Execute validated actions via ADB.

```python
class ActionRunner:
    def __init__(self, adb: ADBController,
                 input_actions: InputActions,
                 element_detector: ElementDetector) -> None: ...

    def execute(self, action: dict) -> bool:
        """
        Execute a single action dict:
        - {"type": "tap", "target_text": "Upgrade"} -> locate text, tap
        - {"type": "tap", "x": 640, "y": 360}      -> direct coordinate tap
        - {"type": "navigate", "target": "barracks"} -> follow predefined path
        - {"type": "wait", "seconds": 2}             -> sleep
        - {"type": "swipe", ...}                     -> swipe gesture
        Returns True on success.
        """
```

**Dependencies:** `device/adb_controller.py`, `device/input_actions.py`, `vision/element_detector.py`.

#### `executor/result_checker.py`

**Responsibility:** Post-execution screenshot confirmation.

```python
class ResultChecker:
    def __init__(self, adb: ADBController,
                 scene_classifier: SceneClassifier,
                 element_detector: ElementDetector) -> None: ...

    def check(self, action: dict, post_screenshot: np.ndarray) -> bool:
        """
        Verify action effect:
        - Did the scene change as expected?
        - Did the target element disappear (button was clicked)?
        - Did a new expected element appear?
        Returns True if action succeeded.
        """
```

**Dependencies:** `device/adb_controller.py`, `scene/classifier.py`, `vision/element_detector.py`.

---

### 2.8 `utils/` - Utilities

#### `utils/logger.py`

```python
class GameLogger:
    def __init__(self, log_dir: str = "logs") -> None: ...

    def log_action(self, action: dict, screenshot: np.ndarray | None = None) -> None:
        """Log action with optional screenshot for debugging."""

    def log_state(self, game_state: GameState) -> None:
        """Log current game state."""

    def log_error(self, error: str, screenshot: np.ndarray | None = None) -> None:
        """Log error with screenshot context."""
```

#### `utils/image_utils.py`

```python
def crop_region(image: np.ndarray, bbox: tuple[int, int, int, int]) -> np.ndarray:
    """Crop image to bounding box region."""

def resize(image: np.ndarray, width: int, height: int) -> np.ndarray:
    """Resize image."""

def to_base64(image: np.ndarray) -> str:
    """Convert image to base64 string (for Claude API)."""

def save_debug_image(image: np.ndarray, label: str, output_dir: str = "logs") -> str:
    """Save image with timestamp for debugging. Returns path."""
```

**Dependencies:** OpenCV, Pillow.

---

### 2.9 `main.py` - Main Loop

```python
def main():
    # 1. Initialize all components (dependency injection)
    adb = ADBController(ADB_HOST, ADB_PORT)
    adb.connect()
    input_actions = InputActions(adb)
    screenshot_mgr = ScreenshotManager(adb, SCREENSHOT_DIR)
    template_matcher = TemplateMatcher(TEMPLATE_DIR)
    ocr = OCRLocator()
    grid = GridOverlay(GRID_COLS, GRID_ROWS)
    detector = ElementDetector(template_matcher, ocr, grid)
    classifier = SceneClassifier(template_matcher)
    popup_filter = PopupFilter(template_matcher, adb)
    game_state = GameState()
    persistence = StatePersistence(STATE_FILE)
    state_tracker = StateTracker(game_state, ocr, template_matcher)
    task_queue = TaskQueue()
    auto_handler = AutoHandler(template_matcher, detector)
    rule_engine = RuleEngine(detector, game_state)
    llm_planner = LLMPlanner(ANTHROPIC_API_KEY, LLM_MODEL, grid)
    validator = ActionValidator(detector, classifier)
    runner = ActionRunner(adb, input_actions, detector)
    checker = ResultChecker(adb, classifier, detector)

    # 2. Load persisted state
    saved = persistence.load()
    if saved:
        game_state.from_dict(saved)

    # 3. Main loop
    while True:
        screenshot = screenshot_mgr.capture()
        scene = classifier.classify(screenshot)

        # Auto-close popups
        if scene == "popup":
            popup_filter.handle(screenshot)
            continue

        # Update state
        state_tracker.update(screenshot, scene)

        # Decision: task queue -> rule engine -> LLM
        if task_queue.has_pending():
            task = task_queue.next()
            actions = rule_engine.plan(task, screenshot, game_state)
        elif llm_planner.should_consult(game_state):
            tasks = llm_planner.get_plan(screenshot, game_state)
            task_queue.add_tasks(tasks)
            continue
        else:
            actions = auto_handler.get_actions(screenshot, game_state)

        # Execute with validation
        for action in actions:
            if validator.validate(action, screenshot):
                runner.execute(action)
                time.sleep(action.get("delay", 0.5))
                post_screenshot = screenshot_mgr.capture()
                checker.check(action, post_screenshot)

        # Persist state
        persistence.save(game_state)
        time.sleep(LOOP_INTERVAL)
```

---

## 3. Module Dependency Graph

```
main.py
  +-> config.py
  +-> device/adb_controller.py ------> config.py
  +-> device/input_actions.py -------> device/adb_controller.py
  +-> vision/screenshot.py ----------> device/adb_controller.py, config.py
  +-> vision/template_matcher.py ----> config.py, [opencv]
  +-> vision/ocr_locator.py --------> config.py, [paddleocr/tesseract]
  +-> vision/grid_overlay.py -------> config.py, [opencv]
  +-> vision/element_detector.py ----> vision/template_matcher.py
  |                                    vision/ocr_locator.py
  |                                    vision/grid_overlay.py
  +-> scene/classifier.py -----------> vision/template_matcher.py
  +-> scene/popup_filter.py ---------> vision/template_matcher.py
  |                                    device/adb_controller.py
  +-> scene/handlers/* --------------> vision/element_detector.py
  |                                    state/game_state.py
  +-> state/game_state.py -----------> (none)
  +-> state/state_tracker.py --------> state/game_state.py
  |                                    vision/ocr_locator.py
  |                                    vision/template_matcher.py
  +-> state/persistence.py ----------> config.py
  +-> brain/task_queue.py -----------> (none)
  +-> brain/auto_handler.py ---------> vision/template_matcher.py
  |                                    vision/element_detector.py
  +-> brain/rule_engine.py ----------> vision/element_detector.py
  |                                    state/game_state.py
  +-> brain/llm_planner.py ----------> vision/grid_overlay.py
  |                                    state/game_state.py
  |                                    [anthropic SDK]
  +-> executor/action_validator.py --> vision/element_detector.py
  |                                    scene/classifier.py
  +-> executor/action_runner.py -----> device/adb_controller.py
  |                                    device/input_actions.py
  |                                    vision/element_detector.py
  +-> executor/result_checker.py ----> device/adb_controller.py
  |                                    scene/classifier.py
  |                                    vision/element_detector.py
  +-> utils/logger.py
  +-> utils/image_utils.py ----------> [opencv, Pillow]
```

### External Dependencies (`requirements.txt`)

```
anthropic          # Claude API
opencv-python      # Template matching, image processing
paddleocr          # OCR (alternative: pytesseract + tesseract-ocr)
Pillow             # Image handling
adbutils           # ADB control (alternative: pure-python-adb)
numpy              # Numeric computation
```

---

## 4. Development Phases

Each phase is self-contained: it produces runnable, testable code with clear verification criteria. Each phase can be completed by an independent Claude Code session.

---

### Phase 1: Infrastructure - "Make It Move"

**Goal:** ADB connection, screenshot capture, basic tap, minimal main loop.

**Files to create:**
- `config.py`
- `requirements.txt`
- `device/__init__.py`
- `device/adb_controller.py`
- `device/input_actions.py`
- `vision/__init__.py`
- `vision/screenshot.py`
- `utils/__init__.py`
- `utils/logger.py`
- `utils/image_utils.py`
- `main.py` (minimal version: connect, screenshot, tap loop)

**Input:**
- Emulator running with game installed
- ADB accessible at configured host:port

**Output:**
- Running `python main.py` connects to emulator
- Takes a screenshot and saves to `data/screenshots/`
- Taps a hardcoded coordinate
- Prints connection status and screenshot dimensions to console

**Manual Verification:**
1. Run `python main.py` -- confirm "Connected to emulator" message
2. Check `data/screenshots/` -- confirm PNG file exists with correct game content
3. Observe emulator screen -- confirm tap visually registers at the specified coordinate
4. Run `python -c "from device.adb_controller import ADBController; a = ADBController('127.0.0.1', 5555); a.connect(); print(a.screenshot().shape)"` -- confirm returns `(720, 1280, 3)` or similar

**Session prompt for this phase:**
> Read `design.md` in the project root. Implement Phase 1 (Infrastructure). Create all listed files with full implementations. The emulator ADB is at 127.0.0.1:5555. After writing the code, provide a test script that verifies ADB connection, screenshot capture, and tap execution.

---

### Phase 2: Visual Perception - "Make It See"

**Goal:** Template matching, OCR, grid overlay, scene classification, popup filtering.

**Prerequisite:** Phase 1 complete and verified.

**Files to create:**
- `vision/template_matcher.py`
- `vision/ocr_locator.py`
- `vision/grid_overlay.py`
- `vision/element_detector.py`
- `scene/__init__.py`
- `scene/classifier.py`
- `scene/popup_filter.py`
- `templates/` directory with a few sample templates (X button, common icons)

**Input:**
- Phase 1 code working (ADB + screenshot)
- A few template images placed in `templates/buttons/` (at minimum: close button X)
- Game screenshots for testing

**Output:**
- `TemplateMatcher` finds buttons in screenshots with confidence > 0.8
- `OCRLocator` extracts text and positions from game UI
- `GridOverlay` produces annotated screenshots with labeled grid cells
- `SceneClassifier` returns scene name for a given screenshot
- `PopupFilter` detects and closes popup dialogs

**Manual Verification:**
1. Capture a game screenshot, run template matcher against it -- confirm known button is detected with correct bounding box
2. Run OCR on a screenshot -- confirm resource numbers are correctly extracted
3. Run grid overlay -- confirm output image has visible labeled grid (save to file and inspect)
4. Run scene classifier on 3 different screenshots (main city, world map, popup) -- confirm correct classification
5. Navigate to a popup in game, run popup filter -- confirm popup is closed

**Session prompt for this phase:**
> Read `design.md` in the project root. Phase 1 is already implemented. Implement Phase 2 (Visual Perception). Create all listed files. Use existing `device/` and `vision/screenshot.py` modules. Write a test script `test_vision.py` that: (1) captures a screenshot, (2) runs template matching, (3) runs OCR, (4) generates grid overlay image, (5) classifies the scene.

---

### Phase 3: State & Tactical Decision - "Make It Think Locally"

**Goal:** Game state tracking, persistence, task queue, rule engine, auto-handler.

**Prerequisite:** Phase 2 complete and verified.

**Files to create:**
- `state/__init__.py`
- `state/game_state.py`
- `state/state_tracker.py`
- `state/persistence.py`
- `brain/__init__.py`
- `brain/task_queue.py`
- `brain/auto_handler.py`
- `brain/rule_engine.py`
- `scene/handlers/__init__.py`
- `scene/handlers/base.py`
- `scene/handlers/main_city.py`
- `scene/handlers/world_map.py`
- `scene/handlers/battle.py`
- `data/navigation_paths.json` (initial navigation definitions)
- `data/game_state.json` (empty initial state)

**Input:**
- Phase 1 + 2 code working (ADB + vision)
- Game running in emulator

**Output:**
- `GameState` correctly tracks resources, buildings from OCR
- `StatePersistence` saves/loads state to `data/game_state.json`
- `TaskQueue` manages ordered tasks
- `AutoHandler` auto-closes popups and claims visible rewards
- `RuleEngine` executes predefined task sequences (e.g., navigate to building -> tap upgrade)
- Updated `main.py` with state tracking and local decision loop (no LLM yet)

**Manual Verification:**
1. Run main loop for 2 minutes -- confirm `data/game_state.json` is created and contains realistic resource values
2. Stop and restart -- confirm state is loaded from JSON (not lost)
3. Trigger a popup in game -- confirm auto-handler closes it within one loop cycle
4. Manually add a task to queue (`"collect_resources"`) -- confirm rule engine navigates and collects
5. Check logs -- confirm state updates are recorded with timestamps

**Session prompt for this phase:**
> Read `design.md` in the project root. Phases 1-2 are already implemented. Implement Phase 3 (State & Tactical Decision). Create all listed files. Integrate with existing `vision/` and `device/` modules. Update `main.py` to include state tracking and the local decision loop (auto_handler + rule_engine, no LLM yet). Write `test_state.py` that verifies state extraction, persistence, and task queue operations.

---

### Phase 4: LLM Integration - "Make It Think Strategically"

**Goal:** Claude API integration, action validation, full execution pipeline.

**Prerequisite:** Phase 3 complete and verified.

**Files to create:**
- `brain/llm_planner.py`
- `executor/__init__.py`
- `executor/action_validator.py`
- `executor/action_runner.py`
- `executor/result_checker.py`

**Input:**
- Phase 1-3 code working (ADB + vision + state + rules)
- Valid Anthropic API key in `config.py`
- Game running in emulator

**Output:**
- `LLMPlanner` sends annotated screenshot + state summary to Claude, receives JSON plan
- `ActionValidator` rejects actions whose targets don't exist on screen
- `ActionRunner` executes validated action sequences
- `ResultChecker` confirms success via post-action screenshot
- Updated `main.py` with complete three-layer decision loop

**Manual Verification:**
1. Trigger LLM consultation manually -- confirm Claude receives annotated screenshot and returns valid JSON plan
2. Inspect the JSON response -- confirm `actions` array contains reasonable game operations
3. Let `ActionValidator` reject an intentionally wrong action (target text not on screen) -- confirm rejection
4. Run full loop for 5 minutes -- confirm: screenshot -> classify -> decide -> validate -> execute -> verify cycle completes without crashes
5. Check logs -- confirm LLM was called, response was parsed, actions were validated and executed

**Session prompt for this phase:**
> Read `design.md` in the project root. Phases 1-3 are already implemented. Implement Phase 4 (LLM Integration). Create all listed files. Integrate with existing modules. Update `main.py` to the complete three-layer decision loop. Ensure Claude API calls use grid-annotated screenshots and concise state summaries. Write `test_llm.py` that sends one screenshot to Claude and prints the parsed action plan.

---

### Phase 5: Hardening & Game-Specific Tuning - "Make It Reliable"

**Goal:** Error recovery, retry logic, game-specific navigation paths, template library expansion, logging improvements.

**Prerequisite:** Phase 4 complete and verified.

**Files to modify/create:**
- Expand `templates/buttons/`, `templates/icons/`, `templates/scenes/` with game-specific images
- Expand `data/navigation_paths.json` with all known menu paths
- Add error recovery to `main.py` (try/except around main loop, ADB reconnect)
- Add retry logic to `executor/action_runner.py` (retry failed actions up to 3 times)
- Add stuck detection to `main.py` (if same scene for N iterations, take recovery action)
- Improve `utils/logger.py` (structured JSON logs, screenshot-per-action recording)
- Add `brain/stuck_recovery.py` for stuck/loop detection and recovery

**New file:**
```python
# brain/stuck_recovery.py
class StuckRecovery:
    def __init__(self, max_same_scene: int = 10) -> None: ...

    def check(self, scene_history: list[str]) -> bool:
        """Return True if stuck (same scene repeated too many times)."""

    def recover(self, adb: ADBController) -> None:
        """Recovery actions: press back, tap center, restart app if needed."""
```

**Input:**
- Phase 1-4 code working (full pipeline)
- Extended template library
- Game running for extended testing

**Output:**
- Bot runs for 30+ minutes without crashing
- Recovers from ADB disconnection
- Recovers from stuck states (same screen loop)
- Failed actions are retried (up to 3 times)
- Complete structured logs with per-action screenshots in `logs/`

**Manual Verification:**
1. Run bot for 30 minutes -- confirm no crashes, check logs for error recovery events
2. Disconnect emulator ADB briefly -- confirm bot reconnects and resumes
3. Navigate to an unexpected screen manually -- confirm bot recovers (goes back to main city)
4. Review `logs/` directory -- confirm structured logs exist with screenshot records
5. Count LLM API calls in logs -- confirm fewer than expected (most operations handled locally)

**Session prompt for this phase:**
> Read `design.md` in the project root. Phases 1-4 are already implemented. Implement Phase 5 (Hardening). Add error recovery, retry logic, stuck detection, and improve logging. Expand template and navigation path data files. Test by running the bot for an extended period and verifying recovery behaviors.

---

## 5. Action Dict Schema Reference

All modules exchange actions as Python dicts with this schema:

```python
# Tap action
{"type": "tap", "target_text": "Upgrade", "fallback_grid": "C4", "delay": 0.5}
{"type": "tap", "x": 640, "y": 360, "delay": 0.3}

# Navigate action (follow predefined path from navigation_paths.json)
{"type": "navigate", "target": "barracks"}

# Wait action
{"type": "wait", "seconds": 2}
{"type": "wait", "condition": "popup_confirm"}

# Swipe action
{"type": "swipe", "x1": 640, "y1": 500, "x2": 640, "y2": 200, "duration_ms": 300}
```

Fields:
- `type` (required): `"tap"` | `"navigate"` | `"wait"` | `"swipe"`
- `target_text` (optional): UI text to locate via OCR/template
- `fallback_grid` (optional): Grid cell to use if text not found
- `x`, `y` (optional): Direct pixel coordinates
- `delay` (optional): Seconds to wait after this action (default 0.5)
- `seconds` (optional): For wait actions
- `condition` (optional): For conditional waits
- `target` (optional): For navigate actions, key in `navigation_paths.json`

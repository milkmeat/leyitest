"""SLGrobot - Main entry point with local decision loop.

Supports two modes:
  - Interactive CLI (default): manual game control
  - Auto mode (--auto): autonomous local decision loop (Phase 3)

The auto loop:
  screenshot -> classify scene -> update state ->
    if popup: auto-close
    if task queue has pending: rule_engine.plan(task)
    else: auto_handler.get_actions()
  -> execute actions -> persist state
"""

import sys
import time
import shlex
import logging
import argparse

import config
from device.adb_controller import ADBController
from device.input_actions import InputActions
from vision.screenshot import ScreenshotManager
from vision.template_matcher import TemplateMatcher
from vision.ocr_locator import OCRLocator
from vision.grid_overlay import GridOverlay
from vision.element_detector import ElementDetector
from scene.classifier import SceneClassifier
from scene.popup_filter import PopupFilter
from state.game_state import GameState
from state.state_tracker import StateTracker
from state.persistence import StatePersistence
from brain.task_queue import TaskQueue, Task
from brain.auto_handler import AutoHandler
from brain.rule_engine import RuleEngine
from utils.logger import GameLogger

logger = logging.getLogger(__name__)

HELP_TEXT = """\
Commands:
  tap <x>,<y>                   Tap at coordinate
  swipe <x1>,<y1> <x2>,<y2> [ms]  Swipe between points (default 300ms)
  longpress <x>,<y> [ms]       Long press (default 1000ms)
  screenshot [label]            Capture and save screenshot
  back                          Press Android back button
  home                          Press Android home button
  center                        Tap screen center
  status                        Show connection and game state
  state                         Show current game state
  scene                         Classify current scene
  task <name> [priority]        Add a task to the queue
  tasks                         Show task queue
  save_tasks                    Save task queue to data/tasks.json
  load_tasks                    Load task queue from data/tasks.json
  auto [loops]                  Run auto loop (default: infinite)
  help                          Show this help
  exit / quit                   Exit"""


def parse_coord(s: str) -> tuple[int, int]:
    """Parse 'x,y' string into (x, y) ints."""
    parts = s.split(",")
    if len(parts) != 2:
        raise ValueError(f"Invalid coordinate '{s}', expected x,y")
    return int(parts[0].strip()), int(parts[1].strip())


class GameBot:
    """Main game bot with state tracking and local decision loop."""

    def __init__(self) -> None:
        # Device layer
        self.adb = ADBController(config.ADB_HOST, config.ADB_PORT, config.NOX_ADB_PATH)
        self.input_actions = InputActions(self.adb)
        self.screenshot_mgr = ScreenshotManager(self.adb, config.SCREENSHOT_DIR)

        # Vision layer
        self.template_matcher = TemplateMatcher(config.TEMPLATE_DIR)
        self.ocr = OCRLocator()
        self.grid = GridOverlay(config.GRID_COLS, config.GRID_ROWS)
        self.detector = ElementDetector(self.template_matcher, self.ocr, self.grid)

        # Scene layer
        self.classifier = SceneClassifier(self.template_matcher)
        self.popup_filter = PopupFilter(self.template_matcher, self.adb)

        # State layer
        self.game_state = GameState()
        self.persistence = StatePersistence(config.STATE_FILE)
        self.state_tracker = StateTracker(
            self.game_state, self.ocr, self.template_matcher
        )

        # Brain layer
        self.task_queue = TaskQueue()
        self.auto_handler = AutoHandler(self.template_matcher, self.detector)
        self.rule_engine = RuleEngine(
            self.detector, self.game_state, config.NAV_PATHS_FILE
        )

    def connect(self) -> bool:
        """Connect to emulator and load persisted state."""
        if not self.adb.connect():
            print("Failed to connect to emulator.")
            return False

        img = self.adb.screenshot()
        h, w = img.shape[:2]
        print(f"Connected. Screen: {w}x{h}")

        # Load persisted state
        saved = self.persistence.load()
        if saved:
            self.game_state.from_dict(saved)
            print(f"Restored state: loop_count={self.game_state.loop_count}")
        else:
            print("Starting with fresh state")

        return True

    def auto_loop(self, max_loops: int = 0) -> None:
        """Run the autonomous local decision loop.

        Args:
            max_loops: Max iterations (0 = infinite).
        """
        loop = 0
        print(f"Starting auto loop (max_loops={max_loops or 'infinite'})...")
        print("Press Ctrl+C to stop.\n")

        try:
            while max_loops == 0 or loop < max_loops:
                loop += 1
                logger.info(f"=== Loop {loop} ===")

                # 1. Capture screenshot
                try:
                    screenshot = self.screenshot_mgr.capture()
                except Exception as e:
                    logger.error(f"Screenshot failed: {e}")
                    time.sleep(config.LOOP_INTERVAL)
                    continue

                # 2. Classify scene
                scene = self.classifier.classify(screenshot)
                logger.info(f"Scene: {scene}")

                # 3. Handle popups immediately
                if scene == "popup":
                    logger.info("Popup detected, attempting to close")
                    self.popup_filter.handle(screenshot)
                    time.sleep(0.5)
                    continue

                # 4. Skip loading screens
                if scene == "loading":
                    logger.info("Loading screen, waiting...")
                    time.sleep(config.LOOP_INTERVAL)
                    continue

                # 5. Update game state
                self.state_tracker.update(screenshot, scene)

                # 6. Decide on actions
                actions = []
                if self.task_queue.has_pending():
                    task = self.task_queue.next()
                    if task:
                        logger.info(f"Executing task: '{task.name}'")
                        if self.rule_engine.can_handle(task):
                            actions = self.rule_engine.plan(
                                task, screenshot, self.game_state
                            )
                        else:
                            logger.warning(
                                f"No rule for task '{task.name}', skipping"
                            )
                            self.task_queue.mark_failed(task)

                        if actions:
                            self.task_queue.mark_done(task)
                        elif task.status == "running":
                            self.task_queue.mark_failed(task)
                else:
                    # No pending tasks -> run auto-handler
                    actions = self.auto_handler.get_actions(
                        screenshot, self.game_state
                    )

                # 7. Execute actions
                for action in actions:
                    self._execute_action(action)
                    self.game_state.record_action(action)

                # 8. Persist state
                self.persistence.save(self.game_state)

                # 9. Log summary
                if loop % 10 == 0:
                    self._log_status()

                # Clean up completed tasks periodically
                if loop % 20 == 0:
                    self.task_queue.clear_completed()

                time.sleep(config.LOOP_INTERVAL)

        except KeyboardInterrupt:
            print("\nStopped by user.")
        finally:
            # Final state save
            self.persistence.save(self.game_state)
            print(f"Auto loop ended. {loop} iterations completed.")
            logger.info(f"Auto loop ended after {loop} iterations")

    def _execute_action(self, action: dict) -> None:
        """Execute a single action dict via ADB."""
        action_type = action.get("type", "")
        delay = action.get("delay", 0.5)
        reason = action.get("reason", "")

        logger.info(f"Execute: {action_type} reason={reason}")

        if action_type == "tap":
            x = action.get("x")
            y = action.get("y")
            target_text = action.get("target_text")

            if target_text and (x is None or y is None):
                # Locate text on screen first
                screenshot = self.screenshot_mgr.capture()
                element = self.detector.locate(screenshot, target_text)
                if element:
                    x, y = element.x, element.y
                else:
                    # Try fallback grid cell
                    fallback = action.get("fallback_grid")
                    if fallback:
                        x, y = self.grid.cell_to_pixel(fallback)
                    else:
                        logger.warning(f"Cannot locate target: '{target_text}'")
                        return

            if x is not None and y is not None:
                self.adb.tap(int(x), int(y))
            else:
                logger.warning(f"No coordinates for tap action")

        elif action_type == "swipe":
            self.adb.swipe(
                int(action["x1"]), int(action["y1"]),
                int(action["x2"]), int(action["y2"]),
                int(action.get("duration_ms", 300)),
            )

        elif action_type == "wait":
            seconds = action.get("seconds", 1)
            time.sleep(seconds)
            return  # Don't add extra delay

        elif action_type == "navigate":
            target = action.get("target", "")
            if target in self.rule_engine.nav_paths:
                for step in self.rule_engine.nav_paths[target]:
                    self._execute_action(step)
            else:
                logger.warning(f"Unknown navigation target: '{target}'")

        elif action_type == "key_event":
            keycode = action.get("keycode", 4)
            self.adb.key_event(keycode)

        else:
            logger.warning(f"Unknown action type: '{action_type}'")

        if delay > 0:
            time.sleep(delay)

    def _log_status(self) -> None:
        """Log current status summary."""
        gs = self.game_state
        logger.info(
            f"Status: scene={gs.scene}, resources={gs.resources}, "
            f"buildings={len(gs.buildings)}, loop={gs.loop_count}, "
            f"tasks_pending={self.task_queue.pending_count()}"
        )


class CLI:
    """Interactive CLI for manual game control and debugging."""

    def __init__(self, bot: GameBot) -> None:
        self.bot = bot

    def run(self) -> None:
        print("SLGrobot CLI  (type 'help' for commands, 'exit' to quit)")
        while True:
            try:
                line = input("> ").strip()
            except (EOFError, KeyboardInterrupt):
                print()
                break
            if not line:
                continue
            try:
                self.dispatch(line)
            except SystemExit:
                break
            except Exception as e:
                print(f"Error: {e}")

    def dispatch(self, line: str) -> None:
        parts = shlex.split(line)
        cmd = parts[0].lower()
        args = parts[1:]

        handler = getattr(self, f"cmd_{cmd}", None)
        if handler is None:
            print(f"Unknown command: {cmd}  (type 'help')")
            return
        handler(args)

    # -- commands --

    def cmd_tap(self, args: list[str]) -> None:
        if len(args) != 1:
            print("Usage: tap <x>,<y>")
            return
        x, y = parse_coord(args[0])
        self.bot.adb.tap(x, y)
        print(f"Tapped ({x}, {y})")

    def cmd_swipe(self, args: list[str]) -> None:
        if len(args) < 2:
            print("Usage: swipe <x1>,<y1> <x2>,<y2> [duration_ms]")
            return
        x1, y1 = parse_coord(args[0])
        x2, y2 = parse_coord(args[1])
        ms = int(args[2]) if len(args) > 2 else 300
        self.bot.adb.swipe(x1, y1, x2, y2, ms)
        print(f"Swiped ({x1},{y1})->({x2},{y2}) {ms}ms")

    def cmd_longpress(self, args: list[str]) -> None:
        if len(args) < 1:
            print("Usage: longpress <x>,<y> [duration_ms]")
            return
        x, y = parse_coord(args[0])
        ms = int(args[1]) if len(args) > 1 else 1000
        self.bot.input_actions.long_press(x, y, ms)
        print(f"Long pressed ({x}, {y}) {ms}ms")

    def cmd_screenshot(self, args: list[str]) -> None:
        label = args[0] if args else ""
        image, filepath = self.bot.screenshot_mgr.capture_and_save(label)
        h, w = image.shape[:2]
        print(f"Saved {w}x{h} -> {filepath}")

    def cmd_back(self, args: list[str]) -> None:
        self.bot.input_actions.press_back()
        print("Back")

    def cmd_home(self, args: list[str]) -> None:
        self.bot.input_actions.press_home()
        print("Home")

    def cmd_center(self, args: list[str]) -> None:
        self.bot.input_actions.tap_center()
        print(f"Tapped center ({config.SCREEN_WIDTH // 2}, {config.SCREEN_HEIGHT // 2})")

    def cmd_status(self, args: list[str]) -> None:
        alive = self.bot.adb.is_connected()
        gs = self.bot.game_state
        print(f"Connected: {alive}  Device: {self.bot.adb.device_serial}")
        print(f"Scene: {gs.scene}  Loop: {gs.loop_count}")
        print(f"Resources: {gs.resources}")
        print(f"Buildings: {len(gs.buildings)}  Marches: {len(gs.troops_marching)}")
        print(f"Tasks pending: {self.bot.task_queue.pending_count()}")

    def cmd_state(self, args: list[str]) -> None:
        gs = self.bot.game_state
        print(gs.summary_for_llm())

    def cmd_scene(self, args: list[str]) -> None:
        screenshot = self.bot.screenshot_mgr.capture()
        scene = self.bot.classifier.classify(screenshot)
        scores = self.bot.classifier.get_confidence(screenshot)
        print(f"Scene: {scene}")
        for s, score in sorted(scores.items(), key=lambda x: -x[1]):
            if score > 0:
                print(f"  {s}: {score:.3f}")

    def cmd_task(self, args: list[str]) -> None:
        if len(args) < 1:
            print("Usage: task <name> [priority]")
            print(f"Known tasks: {', '.join(sorted(self.bot.rule_engine.KNOWN_TASKS))}")
            return
        name = args[0]
        priority = int(args[1]) if len(args) > 1 else 0
        task = Task(name=name, priority=priority)
        self.bot.task_queue.add(task)
        print(f"Added task: '{name}' priority={priority}")

    def cmd_tasks(self, args: list[str]) -> None:
        status = self.bot.task_queue.get_status()
        if not status:
            print("Task queue is empty")
            return
        for t in status:
            print(f"  [{t['status']}] {t['name']} (priority={t['priority']}, retries={t['retry_count']})")

    def cmd_save_tasks(self, args: list[str]) -> None:
        filepath = args[0] if args else config.TASKS_FILE
        self.bot.task_queue.save(filepath)
        print(f"Saved {self.bot.task_queue.size()} tasks to {filepath}")

    def cmd_load_tasks(self, args: list[str]) -> None:
        filepath = args[0] if args else config.TASKS_FILE
        count = self.bot.task_queue.load(filepath)
        print(f"Loaded {count} tasks from {filepath}")

    def cmd_auto(self, args: list[str]) -> None:
        max_loops = int(args[0]) if args else 0
        self.bot.auto_loop(max_loops)

    def cmd_help(self, args: list[str]) -> None:
        print(HELP_TEXT)

    def cmd_exit(self, args: list[str]) -> None:
        raise SystemExit

    def cmd_quit(self, args: list[str]) -> None:
        raise SystemExit


def main():
    # Split sys.argv: flags (--auto, --loops) go to argparse,
    # remaining positional args are treated as a one-shot command.
    flags = []
    cmd_args = []
    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg.startswith("--"):
            flags.append(arg)
            # Consume value for --loops
            if arg == "--loops" and i + 1 < len(sys.argv):
                i += 1
                flags.append(sys.argv[i])
        else:
            # Everything from here on is the command
            cmd_args = sys.argv[i:]
            break
        i += 1

    parser = argparse.ArgumentParser(description="SLGrobot - SLG Game AI Agent")
    parser.add_argument(
        "--auto", action="store_true",
        help="Run in autonomous mode (local decision loop)"
    )
    parser.add_argument(
        "--loops", type=int, default=0,
        help="Max auto-loop iterations (0 = infinite)"
    )
    args = parser.parse_args(flags)

    GameLogger(config.LOG_DIR)
    bot = GameBot()

    if not bot.connect():
        sys.exit(1)

    cli = CLI(bot)

    if cmd_args:
        # One-shot mode: execute command and exit
        line = " ".join(cmd_args)
        try:
            cli.dispatch(line)
        except SystemExit:
            pass
    elif args.auto:
        bot.auto_loop(args.loops)
    else:
        cli.run()


if __name__ == "__main__":
    main()

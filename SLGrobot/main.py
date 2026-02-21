"""SLGrobot - Main entry point with three-layer decision loop.

Supports two modes:
  - Interactive CLI (default): manual game control
  - Auto mode (--auto): autonomous three-layer decision loop (Phase 4)

Three-layer decision loop:
  1. Strategic Layer  - Claude LLM (~30min interval) for long-term planning
  2. Tactical Layer   - Local rule engine (<500ms) decomposes tasks
  3. Execution Layer  - CV + ADB (<100ms) screenshot -> detect -> tap

Auto loop flow:
  screenshot -> classify scene ->
    popup   -> auto-close -> continue
    loading -> wait -> continue
    unknown -> LLM analyze -> execute suggestions -> continue
    other   -> update game_state ->
      has_pending tasks -> rule_engine.plan(task) -> validate -> execute -> verify
      no tasks + LLM due -> llm_planner.get_plan() -> add to queue -> continue
      no tasks           -> auto_handler.get_actions() -> execute
    -> persist state -> sleep -> repeat
"""

import os
import sys
import time
import shlex
import logging
import argparse

import cv2

import config
from game_profile import GameProfile, load_game_profile, list_games
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
from brain.llm_planner import LLMPlanner
from brain.stuck_recovery import StuckRecovery
from brain.quest_workflow import QuestWorkflow
from executor.action_validator import ActionValidator
from executor.action_runner import ActionRunner
from executor.result_checker import ResultChecker
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
  save_tasks                    Save task queue to file
  load_tasks                    Load task queue from file
  auto [loops]                  Run auto loop (default: infinite)
  llm                           Manually trigger LLM strategic consultation
  detect_finger                 Detect tutorial finger, print coords, save crop
  detect_close_x                Detect close_x button, print coords, save crop
  capture_template <category> <name> <x1>,<y1> <x2>,<y2>
                                Capture screenshot region as template
  reload_templates              Reload template library
  games                         List available games
  game [id]                     Show current game (or info about <id>)
  help                          Show this help
  exit / quit                   Exit"""


def parse_coord(s: str) -> tuple[int, int]:
    """Parse 'x,y' string into (x, y) ints."""
    parts = s.split(",")
    if len(parts) != 2:
        raise ValueError(f"Invalid coordinate '{s}', expected x,y")
    return int(parts[0].strip()), int(parts[1].strip())


class GameBot:
    """Main game bot with three-layer decision loop.

    Layers:
    1. Strategic (LLM):  llm_planner   - called every ~30min
    2. Tactical (Rules): rule_engine    - called per task
    3. Execution (ADB):  action_runner  - called per action

    Validation pipeline: validator -> runner -> checker
    """

    def __init__(self, game_profile: GameProfile | None = None) -> None:
        self.game_profile = game_profile

        # Resolve paths from profile or fall back to config defaults
        template_dir = game_profile.template_dir if game_profile else config.TEMPLATE_DIR
        nav_paths_file = game_profile.nav_paths_file if game_profile else config.NAV_PATHS_FILE
        state_file = game_profile.state_file if game_profile else config.STATE_FILE
        tasks_file = game_profile.tasks_file if game_profile else config.TASKS_FILE
        game_package = game_profile.package if game_profile else config.GAME_PACKAGE
        grid_cols = game_profile.grid_cols if game_profile else config.GRID_COLS
        grid_rows = game_profile.grid_rows if game_profile else config.GRID_ROWS

        self._tasks_file = tasks_file
        self._template_dir = template_dir

        # Device layer
        self.adb = ADBController(config.ADB_HOST, config.ADB_PORT, config.NOX_ADB_PATH)
        self.input_actions = InputActions(self.adb)
        self.screenshot_mgr = ScreenshotManager(self.adb, config.SCREENSHOT_DIR)

        # Vision layer
        self.template_matcher = TemplateMatcher(template_dir)
        self.ocr = OCRLocator()
        self.grid = GridOverlay(grid_cols, grid_rows)
        self.detector = ElementDetector(self.template_matcher, self.ocr, self.grid)

        # Scene layer
        self.classifier = SceneClassifier(self.template_matcher)
        self.popup_filter = PopupFilter(
            self.template_matcher, self.adb, self.ocr,
            game_profile=game_profile,
        )

        # State layer
        default_resources = (
            game_profile.default_resources if game_profile else None
        )
        self.game_state = GameState(default_resources=default_resources)
        self.persistence = StatePersistence(state_file)
        self.state_tracker = StateTracker(
            self.game_state, self.ocr, self.template_matcher,
            resource_keywords=(
                game_profile.resource_keywords if game_profile else None
            ),
            resource_order=(
                game_profile.resource_order if game_profile else None
            ),
        )

        # Brain layer
        self.task_queue = TaskQueue()
        self.auto_handler = AutoHandler(
            self.template_matcher, self.detector,
            game_profile=game_profile,
        )
        self.rule_engine = RuleEngine(
            self.detector, self.game_state, nav_paths_file,
            game_profile=game_profile,
        )
        self.llm_planner = LLMPlanner(
            api_key=config.LLM_API_KEY,
            model=config.LLM_MODEL,
            grid_overlay=self.grid,
            game_profile=game_profile,
        )

        # Executor layer (Phase 4)
        self.validator = ActionValidator(self.detector, self.classifier)
        self.runner = ActionRunner(
            self.adb, self.input_actions, self.detector,
            self.grid, self.screenshot_mgr
        )
        self.checker = ResultChecker(
            self.screenshot_mgr, self.classifier, self.detector
        )

        # Hardening layer (Phase 5)
        self.stuck_recovery = StuckRecovery(
            adb=self.adb, game_package=game_package,
        )
        self.game_logger = GameLogger(config.LOG_DIR)

        # Quest workflow (reset stale persisted state — workflow always starts IDLE)
        self.quest_workflow = QuestWorkflow(
            quest_bar_detector=self.state_tracker.quest_bar_detector,
            element_detector=self.detector,
            llm_planner=self.llm_planner,
            game_state=self.game_state,
            game_profile=game_profile,
        )
        self.game_state.quest_workflow_phase = "idle"
        self.game_state.quest_workflow_target = ""

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

        # Report LLM availability
        if config.LLM_API_KEY:
            print(f"LLM enabled: {config.LLM_PROVIDER}/{config.LLM_VISION_MODEL}")
        else:
            print("LLM disabled (no API key configured)")

        return True

    def auto_loop(self, max_loops: int = 0) -> None:
        """Run the autonomous three-layer decision loop with error recovery.

        Decision hierarchy:
        1. Popup/loading -> handle immediately (auto layer)
        2. Unknown scene  -> consult LLM for scene analysis
        3. Pending tasks   -> rule engine plans, executor runs with validation
        4. LLM consult due -> get strategic plan, add tasks to queue
        5. Nothing to do   -> auto-handler scans for opportunistic actions

        Hardening (Phase 5):
        - ADB reconnect on disconnection
        - Stuck detection with escalating recovery
        - Per-iteration try/except with consecutive error tracking

        Args:
            max_loops: Max iterations (0 = infinite).
        """
        loop = 0
        scene_history: list[str] = []
        consecutive_errors = 0
        consecutive_screenshot_failures = 0
        consecutive_unknown_scenes = 0
        max_consecutive_errors = 5

        print(f"Starting auto loop (max_loops={max_loops or 'infinite'})...")
        print("Press Ctrl+C to stop.\n")

        try:
            while max_loops == 0 or loop < max_loops:
                loop += 1
                logger.info(f"=== Loop {loop} ===")

                try:
                    # 0. Check ADB connection
                    if not self.adb.is_connected():
                        logger.warning("ADB disconnected, attempting reconnect...")
                        self.game_logger.log_recovery(
                            "adb_reconnect", "Connection lost, reconnecting"
                        )
                        if not self.adb.reconnect(
                            max_retries=config.ADB_RECONNECT_RETRIES
                        ):
                            logger.error("ADB reconnect failed, stopping loop")
                            break
                        consecutive_screenshot_failures = 0

                    # 1. Capture screenshot
                    try:
                        screenshot = self.screenshot_mgr.capture()
                        consecutive_screenshot_failures = 0
                    except Exception as e:
                        logger.error(f"Screenshot failed: {e}")
                        consecutive_screenshot_failures += 1
                        if consecutive_screenshot_failures >= 3:
                            logger.warning(
                                "3+ screenshot failures, attempting ADB reconnect"
                            )
                            self.game_logger.log_recovery(
                                "adb_reconnect",
                                f"Screenshot failed {consecutive_screenshot_failures} times"
                            )
                            if self.adb.reconnect(
                                max_retries=config.ADB_RECONNECT_RETRIES
                            ):
                                consecutive_screenshot_failures = 0
                        time.sleep(config.LOOP_INTERVAL)
                        continue

                    # 2. Classify scene
                    scene = self.classifier.classify(screenshot)
                    logger.info(f"Scene: {scene}")

                    # 2a. Stuck detection
                    scene_history.append(scene)
                    # Keep history bounded
                    if len(scene_history) > config.STUCK_MAX_SAME_SCENE * 2:
                        scene_history = scene_history[-config.STUCK_MAX_SAME_SCENE * 2:]

                    if self.stuck_recovery.check(scene_history):
                        action = self.stuck_recovery.recover(self.adb)
                        self.game_logger.log_recovery(
                            "stuck_recovery",
                            f"Stuck on '{scene}', recovery action: {action}",
                            screenshot
                        )
                        scene_history.clear()
                        time.sleep(config.LOOP_INTERVAL)
                        continue

                    # 2b. Reset stuck escalation if scene changed
                    if len(scene_history) >= 2 and scene_history[-1] != scene_history[-2]:
                        self.stuck_recovery.reset()

                    # 3. Handle popups immediately (skip when quest workflow
                    #    is active — workflow handles its own popups like
                    #    battle result screens with "返回领地")
                    if scene == "popup" and not self.quest_workflow.is_active():
                        # Check for claimable rewards before closing
                        reward_action = self.auto_handler._check_rewards(screenshot)
                        if reward_action:
                            logger.info("Popup: reward button found, claiming first")
                            self._execute_validated_actions(
                                [reward_action], scene, screenshot
                            )
                            time.sleep(0.5)
                            continue
                        logger.info("Popup detected, attempting to close")
                        self.popup_filter.handle(screenshot)
                        time.sleep(0.5)
                        continue

                    # 4. Story dialogue — tap the down-triangle to advance
                    if scene == "story_dialogue":
                        match = self.template_matcher.match_one(
                            screenshot, "icons/down_triangle"
                        )
                        if match:
                            logger.info(
                                f"Story dialogue: tapping triangle "
                                f"at ({match.x}, {match.y})"
                            )
                            self.adb.tap(match.x, match.y)
                        else:
                            logger.info("Story dialogue: tapping center")
                            self.adb.tap(540, 960)
                        time.sleep(0.5)
                        continue

                    # 5. Skip loading screens
                    if scene == "loading":
                        logger.info("Loading screen, waiting...")
                        time.sleep(config.LOOP_INTERVAL)
                        continue

                    # 5. Quest workflow state machine (before unknown scene
                    #    handling — workflow may navigate through non-main scenes
                    #    like expedition that get classified as "unknown")
                    if self.quest_workflow.is_active():
                        if scene == "unknown":
                            consecutive_unknown_scenes += 1
                        else:
                            consecutive_unknown_scenes = 0
                        actions = self.quest_workflow.step(screenshot, scene)
                        if actions:
                            self._execute_validated_actions(
                                actions, scene, screenshot
                            )
                        self.state_tracker.update(screenshot, scene)
                        self.persistence.save(self.game_state)
                        time.sleep(config.LOOP_INTERVAL)
                        continue

                    # 6. Handle unknown scenes with counter + BACK escape
                    if scene == "unknown":
                        consecutive_unknown_scenes += 1
                        logger.info(
                            f"Unknown scene ({consecutive_unknown_scenes} consecutive)"
                        )

                        if consecutive_unknown_scenes >= 3:
                            # Stuck in unknown scene — press BACK to escape
                            logger.warning(
                                "3+ consecutive unknown scenes, pressing BACK to escape"
                            )
                            self.adb.key_event(4)
                            self.game_logger.log_recovery(
                                "unknown_scene_escape",
                                f"Pressed BACK after {consecutive_unknown_scenes} "
                                f"consecutive unknown scenes",
                                screenshot,
                            )
                            consecutive_unknown_scenes = 0
                        elif self.popup_filter.handle(screenshot):
                            # Some popup-like screens (e.g. first-purchase
                            # reward) lack the dark border that the classifier
                            # uses for popup detection.  Try the popup filter
                            # before the more expensive LLM call.
                            logger.info(
                                "Unknown scene handled by popup filter"
                            )
                            consecutive_unknown_scenes = 0
                        elif config.LLM_API_KEY:
                            actions = self.llm_planner.analyze_unknown_scene(
                                screenshot, self.game_state
                            )
                            if actions:
                                self._execute_validated_actions(
                                    actions, scene, screenshot
                                )
                                # Check if scene changed after LLM suggestion
                                try:
                                    post = self.screenshot_mgr.capture()
                                    post_scene = self.classifier.classify(post)
                                    if post_scene != "unknown":
                                        consecutive_unknown_scenes = 0
                                except Exception:
                                    pass
                        else:
                            # No LLM — press BACK immediately
                            self.adb.key_event(4)
                            consecutive_unknown_scenes = 0

                        time.sleep(config.LOOP_INTERVAL)
                        continue
                    else:
                        consecutive_unknown_scenes = 0

                    # 7. Update game state
                    self.state_tracker.update(screenshot, scene)

                    # 7.5 Quest workflow has highest priority — start it
                    #     when quest bar is visible, before LLM tasks or
                    #     strategic consultation can take over.
                    if (not self.quest_workflow.is_active()
                            and scene == "main_city"
                            and self.game_state.quest_bar_visible
                            and self.game_state.quest_bar_current_quest):
                        logger.info(
                            "Quest bar active, starting quest workflow "
                            f"(pausing {self.task_queue.pending_count()} queued tasks)"
                        )
                        self.quest_workflow.start()
                        continue

                    # 8. Three-layer decision
                    actions = []
                    if self.task_queue.has_pending():
                        # Tactical layer: rule engine decomposes task
                        task = self.task_queue.next()
                        if task:
                            logger.info(f"Executing task: '{task.name}'")
                            if self.rule_engine.can_handle(task):
                                actions = self.rule_engine.plan(
                                    task, screenshot, self.game_state
                                )
                            elif task.params.get("actions"):
                                actions = task.params["actions"]
                            else:
                                logger.warning(
                                    f"No rule for task '{task.name}', skipping"
                                )
                                self.task_queue.mark_failed(task)

                            if actions:
                                self.task_queue.mark_done(task)
                            elif task.status == "running":
                                self.task_queue.mark_failed(task)

                    elif self.llm_planner.should_consult(self.game_state):
                        logger.info("LLM consultation due, requesting strategic plan...")
                        tasks = self.llm_planner.get_plan(screenshot, self.game_state)
                        if tasks:
                            self.task_queue.add_tasks(tasks)
                            logger.info(f"LLM added {len(tasks)} tasks to queue")
                        self.persistence.save(self.game_state)
                        time.sleep(config.LOOP_INTERVAL)
                        continue
                    else:
                        actions = self.auto_handler.get_actions(
                            screenshot, self.game_state
                        )

                    # 8. Execute actions with validation pipeline
                    self._execute_validated_actions(actions, scene, screenshot)

                    # 9. Persist state
                    self.persistence.save(self.game_state)

                    # 10. Log summary
                    if loop % 10 == 0:
                        self._log_status()

                    if loop % 20 == 0:
                        self.task_queue.clear_completed()

                    # Reset error counter on successful iteration
                    consecutive_errors = 0

                except Exception as e:
                    consecutive_errors += 1
                    logger.error(
                        f"Loop iteration error ({consecutive_errors}/"
                        f"{max_consecutive_errors}): {e}",
                        exc_info=True
                    )
                    self.game_logger.log_recovery(
                        "loop_error",
                        f"Error #{consecutive_errors}: {e}"
                    )
                    if consecutive_errors >= max_consecutive_errors:
                        logger.error(
                            f"Too many consecutive errors "
                            f"({max_consecutive_errors}), stopping"
                        )
                        break

                time.sleep(config.LOOP_INTERVAL)

        except KeyboardInterrupt:
            print("\nStopped by user.")
        finally:
            self.persistence.save(self.game_state)
            recoveries = self.stuck_recovery.recovery_count
            print(
                f"Auto loop ended. {loop} iterations, "
                f"{recoveries} recoveries."
            )
            logger.info(
                f"Auto loop ended after {loop} iterations, "
                f"{recoveries} stuck recoveries"
            )

    def _execute_validated_actions(self, actions: list[dict],
                                    pre_scene: str,
                                    pre_screenshot=None) -> int:
        """Execute actions through the validation pipeline with retry.

        Pipeline: validate -> execute (with retry) -> check result -> log

        Args:
            actions: List of action dicts.
            pre_scene: Scene classification before execution.
            pre_screenshot: Screenshot before execution (for validation).

        Returns:
            Number of successfully executed actions.
        """
        success_count = 0

        for action in actions:
            # Take a fresh screenshot for validation if needed
            if pre_screenshot is None:
                try:
                    pre_screenshot = self.screenshot_mgr.capture()
                except Exception:
                    pre_screenshot = None

            # Validate
            if pre_screenshot is not None:
                if not self.validator.validate(action, pre_screenshot):
                    logger.warning(f"Action rejected by validator: {action}")
                    continue

            before_screenshot = pre_screenshot

            # Execute with retry
            if self.runner.execute_with_retry(
                action, max_retries=config.ACTION_MAX_RETRIES
            ):
                self.game_state.record_action(action)
                success_count += 1

                # Check result
                try:
                    post_screenshot = self.screenshot_mgr.capture()
                    ok = self.checker.check(action, pre_scene, post_screenshot)
                    if not ok:
                        logger.warning(
                            f"Result check failed for action: {action.get('type')}"
                        )
                    pre_screenshot = post_screenshot
                except Exception as e:
                    logger.warning(f"Result check error: {e}")
                    post_screenshot = None

                # Log action with before/after screenshots
                self.game_logger.log_action_with_screenshots(
                    action, before_screenshot, post_screenshot
                )
            else:
                logger.warning(f"Action execution failed: {action}")

        return success_count

    def consult_llm(self) -> list[Task]:
        """Manually trigger LLM strategic consultation.

        Returns:
            List of tasks added to queue.
        """
        screenshot = self.screenshot_mgr.capture()
        tasks = self.llm_planner.get_plan(screenshot, self.game_state)
        if tasks:
            self.task_queue.add_tasks(tasks)
        return tasks

    def _log_status(self) -> None:
        """Log current status summary."""
        gs = self.game_state
        logger.info(
            f"Status: scene={gs.scene}, resources={gs.resources}, "
            f"buildings={len(gs.buildings)}, loop={gs.loop_count}, "
            f"tasks_pending={self.task_queue.pending_count()}, "
            f"last_llm={gs.last_llm_consult or 'never'}"
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
        gp = self.bot.game_profile
        if gp:
            print(f"Game: {gp.display_name} ({gp.game_id})")
        print(f"Connected: {alive}  Device: {self.bot.adb.device_serial}")
        print(f"Scene: {gs.scene}  Loop: {gs.loop_count}")
        print(f"Resources: {gs.resources}")
        print(f"Buildings: {len(gs.buildings)}  Marches: {len(gs.troops_marching)}")
        print(f"Tasks pending: {self.bot.task_queue.pending_count()}")
        print(f"Last LLM consult: {gs.last_llm_consult or 'never'}")
        if gs.quest_bar_visible:
            print(f"Quest bar: '{gs.quest_bar_current_quest}' "
                  f"red_badge={gs.quest_bar_has_red_badge} "
                  f"green_check={gs.quest_bar_has_green_check}")
        if gs.quest_workflow_phase != "idle":
            print(f"Quest workflow: phase={gs.quest_workflow_phase} "
                  f"target='{gs.quest_workflow_target}'")

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
            print(f"Known tasks: {', '.join(sorted(self.bot.rule_engine._known_tasks))}")
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
        filepath = args[0] if args else self.bot._tasks_file
        self.bot.task_queue.save(filepath)
        print(f"Saved {self.bot.task_queue.size()} tasks to {filepath}")

    def cmd_load_tasks(self, args: list[str]) -> None:
        filepath = args[0] if args else self.bot._tasks_file
        count = self.bot.task_queue.load(filepath)
        print(f"Loaded {count} tasks from {filepath}")

    def cmd_detect_finger(self, args: list[str]) -> None:
        """Detect tutorial finger on screen and save debug crop."""
        if args:
            screenshot = cv2.imread(args[0])
            if screenshot is None:
                print(f"Failed to read image: {args[0]}")
                return
        else:
            screenshot = self.bot.screenshot_mgr.capture()
        wf = self.bot.quest_workflow

        # Show raw matches for all variants (before threshold filter)
        for cache_name, _, flip_type in wf._FINGER_VARIANTS:
            raw = wf.element_detector.locate(
                screenshot, cache_name, methods=["template"]
            )
            if raw is not None:
                ncc = wf._verify_finger_ncc(screenshot, raw.x, raw.y, flip_type)
                print(f"Raw {flip_type:7s}: ccorr={raw.confidence:.3f} "
                      f"at ({raw.x}, {raw.y})  ncc={ncc:.3f}")
            else:
                print(f"Raw {flip_type:7s}: no match")
        print(f"  (threshold: ccorr>={wf._FINGER_CONFIDENCE_THRESHOLD}, "
              f"ncc>={wf._FINGER_NCC_THRESHOLD})")

        finger_match, flip_type = wf._detect_tutorial_finger(screenshot)
        if finger_match is None:
            print("No finger detected (rejected by two-stage filter).")
            return

        tip_x, tip_y = wf._fingertip_pos(
            finger_match.x, finger_match.y, flip_type)

        print(f"Finger center: ({finger_match.x}, {finger_match.y})  "
              f"confidence={finger_match.confidence:.3f}  {flip_type}")
        print(f"Fingertip:     ({tip_x}, {tip_y})")

        # Save 256x256 crop around finger center
        h, w = screenshot.shape[:2]
        cx, cy = finger_match.x, finger_match.y
        x1 = max(0, cx - 128)
        y1 = max(0, cy - 128)
        x2 = min(w, x1 + 256)
        y2 = min(h, y1 + 256)
        crop = screenshot[y1:y2, x1:x2]
        out_path = "debug_finger.png"
        cv2.imwrite(out_path, crop)
        print(f"Saved {crop.shape[1]}x{crop.shape[0]} crop -> {out_path}")

    def cmd_detect_close_x(self, args: list[str]) -> None:
        """Detect close_x button on screen and save debug crop."""
        if args:
            screenshot = cv2.imread(args[0])
            if screenshot is None:
                print(f"Failed to read image: {args[0]}")
                return
        else:
            screenshot = self.bot.screenshot_mgr.capture()

        wf = self.bot.quest_workflow
        tm = wf.element_detector.template_matcher

        # Show raw top-5 CCORR candidates with red-pixel ratios
        candidates = tm.match_one_multi(screenshot, "buttons/close_x",
                                        max_matches=5)
        entry = tm._cache.get("buttons/close_x")
        opaque, transparent = None, None
        if entry is not None:
            _, mask = entry
            if mask is not None:
                opaque = mask[:, :, 0] > 0
                transparent = ~opaque

        for i, m in enumerate(candidates):
            patch = screenshot[m.bbox[1]:m.bbox[3], m.bbox[0]:m.bbox[2]]
            hsv = cv2.cvtColor(patch, cv2.COLOR_BGR2HSV)
            red1 = cv2.inRange(hsv, (0, 80, 80), (10, 255, 255))
            red2 = cv2.inRange(hsv, (170, 80, 80), (180, 255, 255))
            red_px = red1 | red2
            if opaque is not None:
                r_op = (red_px[opaque] > 0).sum() / opaque.sum()
                r_bg = (red_px[transparent] > 0).sum() / transparent.sum()
            else:
                r_op = (red_px > 0).sum() / red_px.size
                r_bg = 0.0
            print(f"  #{i+1}: ccorr={m.confidence:.3f} "
                  f"red_x={r_op:.3f} red_bg={r_bg:.3f} at ({m.x}, {m.y})")
        print(f"  (need: red_x>={wf._CLOSE_X_RED_OPAQUE_MIN}, "
              f"red_bg<={wf._CLOSE_X_RED_BG_MAX})")

        # Run verified detection
        match = wf._find_close_x(screenshot)
        if match is None:
            print("No close_x detected (rejected by red-pixel filter).")
            return

        print(f"close_x: ({match.x}, {match.y}) conf={match.confidence:.3f}")

        # Save 128x128 crop around match center
        h, w = screenshot.shape[:2]
        cx, cy = match.x, match.y
        x1 = max(0, cx - 64)
        y1 = max(0, cy - 64)
        x2 = min(w, x1 + 128)
        y2 = min(h, y1 + 128)
        crop = screenshot[y1:y2, x1:x2]
        out_path = "debug_close_x.png"
        cv2.imwrite(out_path, crop)
        print(f"Saved {crop.shape[1]}x{crop.shape[0]} crop -> {out_path}")

    def cmd_capture_template(self, args: list[str]) -> None:
        """Capture a screenshot region and save as a template."""
        if len(args) < 4:
            print("Usage: capture_template <category> <name> <x1>,<y1> <x2>,<y2>")
            print("Example: capture_template buttons close 450,100 630,180")
            return
        category = args[0]
        name = args[1]
        try:
            x1, y1 = parse_coord(args[2])
            x2, y2 = parse_coord(args[3])
        except ValueError as e:
            print(f"Invalid coordinates: {e}")
            return

        screenshot = self.bot.screenshot_mgr.capture()
        region = screenshot[y1:y2, x1:x2]
        if region.size == 0:
            print(f"Empty region ({x1},{y1})-({x2},{y2}). Check coordinates.")
            return

        out_dir = os.path.join(self.bot._template_dir, category)
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, f"{name}.png")
        cv2.imwrite(out_path, region)
        print(f"Saved template: {out_path} ({region.shape[1]}x{region.shape[0]})")

        # Reload templates so the new one is available immediately
        self.bot.template_matcher.reload()
        print(f"Templates reloaded ({self.bot.template_matcher.count()} total)")

    def cmd_reload_templates(self, args: list[str]) -> None:
        """Reload the template library from disk."""
        self.bot.template_matcher.reload()
        count = self.bot.template_matcher.count()
        print(f"Templates reloaded: {count} templates loaded")

    def cmd_games(self, args: list[str]) -> None:
        """List available games."""
        games_dir = getattr(config, "GAMES_DIR", "games")
        available = list_games(games_dir)
        if not available:
            print(f"No games found in {games_dir}/")
            return
        active_id = (
            self.bot.game_profile.game_id if self.bot.game_profile else None
        )
        for gid in available:
            marker = " *" if gid == active_id else ""
            try:
                gp = load_game_profile(gid, games_dir)
                print(f"  {gid}{marker}  ({gp.display_name})")
            except Exception:
                print(f"  {gid}{marker}")

    def cmd_game(self, args: list[str]) -> None:
        """Show current game or info about a specific game ID."""
        games_dir = getattr(config, "GAMES_DIR", "games")
        if args:
            gid = args[0]
            try:
                gp = load_game_profile(gid, games_dir)
                print(f"Game: {gp.display_name} ({gid})")
                print(f"  Package: {gp.package}")
                print(f"  Templates: {gp.template_dir}")
                active_id = (
                    self.bot.game_profile.game_id
                    if self.bot.game_profile else None
                )
                if gid != active_id:
                    print(f"  To switch: restart with --game {gid}")
            except FileNotFoundError:
                print(f"Game '{gid}' not found. Use 'games' to list available.")
        else:
            gp = self.bot.game_profile
            if gp:
                print(f"Active game: {gp.display_name} ({gp.game_id})")
            else:
                print("No game profile loaded (using built-in defaults)")

    def cmd_auto(self, args: list[str]) -> None:
        max_loops = int(args[0]) if args else 0
        self.bot.auto_loop(max_loops)

    def cmd_llm(self, args: list[str]) -> None:
        if not config.LLM_API_KEY:
            print("Error: ANTHROPIC_API_KEY not set")
            return
        print(f"Consulting {config.LLM_MODEL}...")
        tasks = self.bot.consult_llm()
        if tasks:
            print(f"LLM generated {len(tasks)} tasks:")
            for t in tasks:
                print(f"  [{t.priority}] {t.name} params={t.params}")
        else:
            print("LLM returned no tasks")

    def cmd_help(self, args: list[str]) -> None:
        print(HELP_TEXT)

    def cmd_exit(self, args: list[str]) -> None:
        raise SystemExit

    def cmd_quit(self, args: list[str]) -> None:
        raise SystemExit


def main():
    # Split sys.argv: flags (--auto, --loops, --game) go to argparse,
    # remaining positional args are treated as a one-shot command.
    flags = []
    cmd_args = []
    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg.startswith("--"):
            flags.append(arg)
            # Consume value for --loops and --game
            if arg in ("--loops", "--game") and i + 1 < len(sys.argv):
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
        help="Run in autonomous mode (three-layer decision loop)"
    )
    parser.add_argument(
        "--loops", type=int, default=0,
        help="Max auto-loop iterations (0 = infinite)"
    )
    parser.add_argument(
        "--game", type=str,
        default=getattr(config, "ACTIVE_GAME", "frozenisland"),
        help="Game profile to load (default: %(default)s)"
    )
    args = parser.parse_args(flags)

    GameLogger(config.LOG_DIR)

    # Load game profile
    games_dir = getattr(config, "GAMES_DIR", "games")
    game_profile = None
    try:
        game_profile = load_game_profile(args.game, games_dir)
        print(f"Game: {game_profile.display_name}")
    except FileNotFoundError:
        print(f"Warning: game profile '{args.game}' not found, using defaults")

    bot = GameBot(game_profile=game_profile)

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

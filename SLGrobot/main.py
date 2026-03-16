"""SLGrobot - Main entry point with scene-driven auto loop.

Supports two modes:
  - Interactive CLI (default): manual game control
  - Auto mode (--auto): autonomous scene-driven loop

Auto loop flow:
  screenshot -> build DOM (infer scene) ->
    popup/loading    -> handle -> continue
    tutorial_finger  -> follow tap -> continue
    quest_bar green  -> claim reward -> continue
    known popup      -> auto close -> continue
    otherwise        -> auto_handler.get_actions() -> execute
  -> persist state -> sleep -> repeat
"""

import os
import re
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
from vision.building_finder import BuildingFinder, parse_city_layout
from vision.element_detector import ElementDetector
from state.game_state import GameState
from state.state_tracker import StateTracker
from state.persistence import StatePersistence
from brain.auto_handler import AutoHandler
from brain.stuck_recovery import StuckRecovery
from brain.finger_detector import FingerDetector
from brain.script_runner import ScriptRunner, load_script, list_scripts, ScriptAbortError
from vision.screen_dom import ScreenDOMBuilder
from executor.action_validator import ActionValidator
from executor.action_runner import ActionRunner
from utils.logger import GameLogger

logger = logging.getLogger(__name__)

HELP_TEXT = """\
Commands:
  tap <x>,<y>                   Tap at coordinate
  swipe <x1>,<y1> <x2>,<y2> [ms]  Swipe between points (default 300ms)
  longpress <x>,<y> [ms]       Long press (default 1000ms)
  screenshot [label]            Capture and save screenshot
  center                        Tap screen center
  status                        Show connection and game state
  state                         Show current game state
  scene                         Detect current scene (via Screen DOM)
  dom [--save]                   Build Screen DOM (YAML) of current screen
  run <name> [--dry]             Execute a YAML script (v2 DOM-aware runner)
  scripts                        List available YAML scripts
  quest <name or text>           Execute a quest script (bilingual: name or text)
  quest_rules                   List all quest scripts (name + pattern)
  quest_test <name or text>     Dry-run a quest script (show steps)
  auto [loops]                  Run auto loop (default: infinite)
  auto_test <png_file>          Simulate one auto-loop on a screenshot (dry run)
  detect_finger                 Detect tutorial finger, print coords, save crop
  detect_close_x                Detect close_x button, print coords, save crop
  find_building <name>           Find building on city map and tap it
  press_read                     Press-drag-read: show all visible building names
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
    """Main game bot with scene-driven auto loop.

    Uses AutoHandler + Quest Scripts for decision making.
    Validation pipeline: validator -> runner -> checker
    """

    def __init__(self, game_profile: GameProfile | None = None) -> None:
        self.game_profile = game_profile

        # Resolve paths from profile or fall back to config defaults
        template_dir = game_profile.template_dir if game_profile else config.TEMPLATE_DIR
        nav_paths_file = game_profile.nav_paths_file if game_profile else config.NAV_PATHS_FILE
        state_file = game_profile.state_file if game_profile else config.STATE_FILE
        game_package = game_profile.package if game_profile else config.GAME_PACKAGE
        grid_cols = game_profile.grid_cols if game_profile else config.GRID_COLS
        grid_rows = game_profile.grid_rows if game_profile else config.GRID_ROWS

        self._template_dir = template_dir

        # Device layer
        self.adb = ADBController(config.ADB_HOST, config.ADB_PORT, config.ADB_PATH)
        self.input_actions = InputActions(self.adb)
        self.screenshot_mgr = ScreenshotManager(self.adb, config.SCREENSHOT_DIR)

        # Vision layer
        self.template_matcher = TemplateMatcher(template_dir)
        ocr_corrections = game_profile.ocr_corrections if game_profile else {}
        self.ocr = OCRLocator(corrections=ocr_corrections)
        self.grid = GridOverlay(grid_cols, grid_rows)
        self.detector = ElementDetector(self.template_matcher, self.ocr, self.grid)

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
        self.auto_handler = AutoHandler(game_profile=game_profile)
        # Building finder (optional, depends on city_layout config)
        self.building_finder: BuildingFinder | None = None
        if game_profile and game_profile.city_layout:
            city_cfg = game_profile.city_layout
            layout_file = city_cfg.get("file", "city_layout.md")
            layout_path = os.path.join(game_profile.game_dir, layout_file)
            if os.path.isfile(layout_path):
                layout_data = parse_city_layout(
                    layout_path,
                    reference_building=city_cfg.get("reference_building", "城堡"),
                    pixels_per_unit=city_cfg.get("pixels_per_unit", 400),
                )
                if layout_data:
                    self.building_finder = BuildingFinder(
                        self.adb, self.ocr, city_cfg, layout_data,
                    )
                    logger.info(
                        f"BuildingFinder initialized with "
                        f"{len(layout_data)} buildings"
                    )
            else:
                logger.info(f"City layout file not found: {layout_path}")

        # Executor layer (Phase 4)
        self.validator = ActionValidator(self.detector)
        self.runner = ActionRunner(
            self.adb, self.input_actions, self.detector,
            self.grid, self.screenshot_mgr,
            building_finder=self.building_finder,
        )
        # Hardening layer (Phase 5)
        self.stuck_recovery = StuckRecovery(
            adb=self.adb, game_package=game_package,
        )
        self.game_logger = GameLogger(config.LOG_DIR)

        # Finger detector (extracted from old QuestWorkflow)
        self.finger_detector = FingerDetector(self.detector, game_profile)

        # Screen DOM builder (v2 unified vision pipeline)
        self.dom_builder = ScreenDOMBuilder(
            self.ocr, self.template_matcher, self.finger_detector,
            game_profile=game_profile,
        )

        # Quest scripts for synchronous execution
        self._quest_scripts = (
            game_profile.quest_scripts
            if game_profile and game_profile.quest_scripts
            else []
        )

        # Abort cooldown — prevent immediate restart of the same quest
        self._last_abort_time: float = 0.0
        self._last_aborted_quest: str = ""
        self._ABORT_COOLDOWN: int = 180  # seconds (3 minutes)

        # Auto-loop stateful counters
        self._auto_consecutive_unknown = 0

    def tap_blank_area(self) -> None:
        """Tap blank areas at bottom then top to dismiss overlays."""
        self.adb.tap(540, 1820)
        time.sleep(0.3)
        self.adb.tap(540, 100)

    # -- Quest helpers (synchronous execution) --

    def _find_matching_script(self, quest_name: str) -> tuple[dict | None, re.Match | None]:
        """Find quest script matching quest_name by name or regex pattern."""
        if not self._quest_scripts or not quest_name:
            return None, None
        quest_lower = quest_name.lower().strip()
        # Pass 1: match by name (exact, case-insensitive)
        for rule in self._quest_scripts:
            name = rule.get("name", "")
            if name and name.lower() == quest_lower:
                return rule, None
        # Pass 2: match by regex pattern
        for rule in self._quest_scripts:
            pattern = rule.get("pattern", "")
            if pattern:
                m = re.search(pattern, quest_name)
                if m:
                    return rule, m
        return None, None

    def _has_matching_script(self, quest_name: str) -> bool:
        """Return True if quest_name matches any quest_script pattern."""
        rule, _ = self._find_matching_script(quest_name)
        return rule is not None

    def _should_start_quest(self, quest_name: str,
                            has_green_check: bool = False) -> bool:
        """Check if we should start this quest (respects abort cooldown)."""
        if has_green_check:
            return True
        if self._last_aborted_quest and quest_name == self._last_aborted_quest:
            elapsed = time.time() - self._last_abort_time
            if elapsed < self._ABORT_COOLDOWN:
                logger.debug(
                    f"Quest cooldown active for '{quest_name}' "
                    f"({int(elapsed)}s / {self._ABORT_COOLDOWN}s)"
                )
                return False
        return True

    def _run_quest_script(self, quest_name: str, steps: list[dict],
                          regex_match: re.Match | None = None) -> bool:
        """Synchronously execute a quest script (blocks auto loop).

        Returns True if script completed successfully, False on abort/timeout.
        """
        from brain.quest_script import QuestScriptRunner

        runner = QuestScriptRunner(
            ocr_locator=self.ocr,
            template_matcher=self.template_matcher,
            adb_controller=self.adb,
            screenshot_fn=self.screenshot_mgr.capture,
        )
        runner.load(steps)

        # Extract named regex groups into runner variables
        if regex_match:
            for var_name, value in regex_match.groupdict().items():
                if value is not None:
                    runner.variables[var_name] = value

        max_iterations = len(steps) * 10
        timeout = 120.0  # seconds
        start_time = time.time()
        iteration = 0

        logger.info(f"Running quest script for '{quest_name}' ({len(steps)} steps)")

        while not runner.is_done() and iteration < max_iterations:
            if time.time() - start_time > timeout:
                logger.warning(
                    f"Quest script timeout ({timeout}s) for '{quest_name}'"
                )
                self._last_abort_time = time.time()
                self._last_aborted_quest = quest_name
                return False

            iteration += 1
            try:
                screenshot = self.screenshot_mgr.capture()
            except Exception as e:
                logger.error(f"Screenshot failed during quest script: {e}")
                self._last_abort_time = time.time()
                self._last_aborted_quest = quest_name
                return False

            actions = runner.execute_one(screenshot)
            if actions is None:
                # Step waiting (e.g. text not found), retry
                time.sleep(1.0)
                continue

            if not actions:
                # No-op step (read_text, eval)
                continue

            for action in actions:
                self.runner.execute(action)
                time.sleep(action.get("delay", 1.0))

        if runner.is_aborted():
            logger.warning(
                f"Quest script aborted for '{quest_name}': "
                f"{runner.abort_reason}"
            )
            self._last_abort_time = time.time()
            self._last_aborted_quest = quest_name
            return False

        if runner.is_done():
            logger.info(f"Quest script completed for '{quest_name}'")
            return True

        logger.warning(
            f"Quest script stopped after {iteration} iterations "
            f"for '{quest_name}'"
        )
        self._last_abort_time = time.time()
        self._last_aborted_quest = quest_name
        return False

    def _try_claim_quest_reward(self) -> bool:
        """Tap green check on quest bar to claim reward.

        Reuses the QuestBarInfo already detected by state_tracker.update()
        in the current loop iteration, avoiding a redundant screenshot and
        OCR pass.

        Returns True if reward was claimed.
        """
        info = self.state_tracker.last_quest_bar_info
        if not info or not info.visible or not info.has_green_check:
            return False

        if info.green_check_pos is not None:
            cx, cy = info.green_check_pos
            logger.info(
                f"Claiming quest reward: tapping green check at ({cx}, {cy})"
            )
        elif info.current_quest_bbox is not None:
            # Fallback: tap quest text center if green check pos unavailable
            bx1, by1, bx2, by2 = info.current_quest_bbox
            cx = (bx1 + bx2) // 2
            cy = (by1 + by2) // 2
            logger.info(
                f"Claiming quest reward: tapping quest text at ({cx}, {cy})"
            )
        else:
            return False

        self.adb.tap(cx, cy)
        time.sleep(2.0)
        return True

    def connect(self) -> bool:
        """Connect to emulator and load persisted state."""
        if not self.adb.connect():
            print("Failed to connect to emulator.")
            return False

        img = self.adb.screenshot()
        h, w = img.shape[:2]
        print(f"Connected. Screen: {w}x{h}")

        # Verify emulator resolution matches expected 1080x1920
        if w != config.SCREEN_WIDTH or h != config.SCREEN_HEIGHT:
            print(
                f"ERROR: 模拟器分辨率不匹配！"
                f"当前: {w}x{h}，要求: {config.SCREEN_WIDTH}x{config.SCREEN_HEIGHT}。"
                f"请在 Nox 模拟器设置中将分辨率调整为 {config.SCREEN_WIDTH}x{config.SCREEN_HEIGHT}（竖屏）后重试。"
            )
            return False

        # Load persisted state
        saved = self.persistence.load()
        if saved:
            self.game_state.from_dict(saved)
            print(f"Restored state: loop_count={self.game_state.loop_count}")
        else:
            print("Starting with fresh state")

        return True

    def auto_loop(self, max_loops: int = 0) -> None:
        """Run the autonomous DOM-driven decision loop with error recovery.

        Decision hierarchy:
        1. Screenshot → DOM (with inferred scene)
        2. Special-case pre-check (exit_dialog, shoot_mini_game)
        3. Priority rules via auto_handler.get_action(dom)
        4. Execute winning action

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
        self._auto_consecutive_unknown = 0
        max_consecutive_errors = 5
        # Adaptive loop_start_sleep: doubles when stuck on same scene
        _base_loop_sleep = (self.game_profile.loop_start_sleep
                            if self.game_profile else 0.7)
        _current_loop_sleep = _base_loop_sleep
        _last_scene: str | None = None
        _MAX_LOOP_SLEEP = 5.0

        print(f"Starting auto loop (max_loops={max_loops or 'infinite'})...")
        print("Press Ctrl+C to stop.\n")

        try:
            while max_loops == 0 or loop < max_loops:
                loop += 1
                self.game_logger.loop_count = loop
                _loop_t0 = time.monotonic()
                logger.info(f"=== Loop {loop} ===")

                try:
                    # 0. Brief pause at start of each loop (adaptive)
                    time.sleep(_current_loop_sleep)

                    # 0b. Check ADB connection
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

                    # 1b. Mark frame for OCR caching
                    self.ocr.set_frame(screenshot)

                    # 2. Build DOM (includes scene inference)
                    dom = self.dom_builder.build(screenshot)
                    scene = dom["screen"]["scene"]
                    logger.debug(f"Scene: {scene}")

                    # 2a. Save loop screenshot (one per loop)
                    self.game_logger.save_loop_screenshot(screenshot, scene)

                    # 2a-2. Adaptive loop sleep: double if stuck on same scene
                    #        Exception: building_upgrade reduces to 0.7s
                    if scene == _last_scene:
                        if scene == "building_upgrade":
                            new_sleep = 0.7
                        else:
                            new_sleep = min(
                                _current_loop_sleep * 2, _MAX_LOOP_SLEEP
                            )
                        if new_sleep != _current_loop_sleep:
                            _current_loop_sleep = new_sleep
                            logger.info(
                                f"Same scene '{scene}', loop_start_sleep -> "
                                f"{_current_loop_sleep:.1f}s"
                            )
                    else:
                        if _current_loop_sleep != _base_loop_sleep:
                            logger.info(
                                f"Scene changed '{_last_scene}' -> '{scene}', "
                                f"loop_start_sleep reset to {_base_loop_sleep}s"
                            )
                            _current_loop_sleep = _base_loop_sleep
                    _last_scene = scene

                    # 2b. Stuck detection
                    scene_history.append(scene)
                    if len(scene_history) > config.STUCK_MAX_SAME_SCENE * 2:
                        scene_history = scene_history[-config.STUCK_MAX_SAME_SCENE * 2:]

                    if self.stuck_recovery.check(scene_history):
                        action = self.stuck_recovery.recover(self.adb)
                        self.game_logger.log_recovery(
                            "stuck_recovery",
                            f"Stuck on '{scene}', recovery action: {action}"
                        )
                        scene_history.clear()
                        time.sleep(config.LOOP_INTERVAL)
                        continue

                    # 2b-2. Reset stuck escalation if scene changed
                    if len(scene_history) >= 2 and scene_history[-1] != scene_history[-2]:
                        self.stuck_recovery.reset()

                    # 3. Special-case pre-check (can't be expressed as rules)
                    special = self._process_scene(screenshot, scene, dom)
                    if special:
                        continue

                    # 3b. Update state on main_city
                    if scene == "main_city":
                        self.state_tracker.update(screenshot, scene)

                    # 4. Priority rules via auto_handler
                    action = self.auto_handler.get_action(dom)
                    if action:
                        action_type = action.get("type")
                        if action_type == "tap":
                            self.adb.tap(action["x"], action["y"])
                            time.sleep(action.get("delay", 0.5))
                        elif action_type == "wait":
                            time.sleep(action.get("seconds", 2))
                        # Reset adaptive sleep on finger tap
                        reason = action.get("reason", "")
                        if "finger" in reason:
                            if _current_loop_sleep != _base_loop_sleep:
                                _current_loop_sleep = _base_loop_sleep
                                logger.info(
                                    f"Finger action, loop_start_sleep "
                                    f"reset to {_base_loop_sleep}s"
                                )
                    else:
                        logger.debug("No priority rule matched, idle")

                    # 5. Persist state
                    self.persistence.save(self.game_state)

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

                logger.debug(
                    f"Loop {loop} finished in "
                    f"{time.monotonic() - _loop_t0:.2f}s"
                )
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

    def _process_scene(self, screenshot, scene: str,
                       dom: dict | None = None,
                       dry_run: bool = False) -> bool:
        """Pre-check for special scenes that can't be priority rules.

        Handles only exit_dialog (60s cooldown) and shoot_mini_game (swipe).
        All other scenes are handled by auto_handler.get_action(dom).

        Args:
            screenshot: Current frame (numpy array).
            scene: Classified scene string.
            dom: Screen DOM dict (unused in pre-check, kept for API compat).
            dry_run: If True, skip all ADB actions and sleeps.

        Returns:
            True if scene was fully handled (caller should skip to next
            iteration). False to continue to priority rules.
        """
        # Finger always takes priority in special scenes
        if dom:
            for region in ("top_bar", "center", "bottom_bar"):
                for elem in dom.get("screen", {}).get(region, []):
                    if elem.get("type") == "finger":
                        tip = elem.get("fingertip", elem.get("pos"))
                        if tip and not dry_run:
                            logger.info(
                                f"Finger detected in {scene} — "
                                f"tapping fingertip at {tip}")
                            self.adb.tap(tip[0], tip[1])
                            time.sleep(0.5)
                        return True

        # Exit dialog — game's pause/quit overlay.
        # Tap "继续" (rightmost icon) and wait 60s cooldown.
        if scene == "exit_dialog":
            logger.info(
                "Exit dialog detected — tapping '继续' and "
                "waiting 60s cooldown"
            )
            if not dry_run:
                self.adb.tap(826, 843)
                time.sleep(60)
            return True

        # Battle formation — tap "一键上阵" then "出战" (gold button).
        if scene == "battle_formation":
            logger.info(
                "Battle formation detected — tapping '一键上阵' "
                "then '出战'"
            )
            if not dry_run:
                # Find 一键上阵 button position from DOM
                deploy_pos = None
                gold_pos = None
                for region in ("top_bar", "center", "bottom_bar"):
                    for elem in dom.get("screen", {}).get(region, []):
                        if elem.get("type") != "button":
                            continue
                        if "上阵" in elem.get("text", ""):
                            deploy_pos = elem["pos"]
                        elif elem.get("color") == "gold":
                            gold_pos = elem["pos"]
                if deploy_pos:
                    self.adb.tap(deploy_pos[0], deploy_pos[1])
                    time.sleep(1.0)
                if gold_pos:
                    self.adb.tap(gold_pos[0], gold_pos[1])
                    time.sleep(1.0)
            return True

        # Shooting mini-game — swipe right to aim and wait.
        if scene == "shoot_mini_game":
            logger.info(
                "Shooting mini-game detected — swiping right "
                "150px and waiting 10s"
            )
            if not dry_run:
                self.adb.swipe(540, 1490, 690, 1490, 300)
                time.sleep(10)
            return True

        return False

    def simulate_auto_iteration(self, screenshot) -> None:
        """Simulate one auto-loop iteration on a static screenshot.

        Builds DOM (with inferred scene), matches priority rules — all in
        dry_run mode (no ADB actions, no sleeps, no persistence).
        """
        # 1b. Mark frame for OCR caching
        self.ocr.set_frame(screenshot)

        # 2. Build DOM (includes scene inference)
        dom = self.dom_builder.build(screenshot)
        scene = dom["screen"]["scene"]
        print(f"Scene: {scene}")

        yaml_str = self.dom_builder.to_yaml(dom)
        print(f"\nDOM:\n{yaml_str}")

        # 3a. Special-case pre-check
        self._auto_consecutive_unknown = 0
        special = self._process_scene(screenshot, scene, dom, dry_run=True)
        if special:
            print(f"\nResult: special handler (exit_dialog/shoot_mini_game)")
            return

        # 4. Priority rules
        action = self.auto_handler.get_action(dom)
        if action:
            print(f"\nPriority action: {action}")
        else:
            print(f"\nNo priority rule matched — idle")

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

            # Execute with retry
            if self.runner.execute_with_retry(
                action, max_retries=config.ACTION_MAX_RETRIES
            ):
                self.game_state.record_action(action)
                success_count += 1
                self.game_logger.log_action(action)
            else:
                logger.warning(f"Action execution failed: {action}")

        return success_count



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
        if gs.quest_bar_visible:
            print(f"Quest bar: '{gs.quest_bar_current_quest}' "
                  f"red_badge={gs.quest_bar_has_red_badge} "
                  f"green_check={gs.quest_bar_has_green_check}")

    def cmd_state(self, args: list[str]) -> None:
        gs = self.bot.game_state
        print(gs.summary())

    def cmd_scene(self, args: list[str]) -> None:
        """Detect current scene using Screen DOM inference."""
        screenshot = self.bot.screenshot_mgr.capture()
        dom = self.bot.dom_builder.build(screenshot)
        scene = dom["screen"]["scene"]
        print(f"Scene: {scene}")

    def cmd_dom(self, args: list[str]) -> None:
        """Capture screenshot and output YAML DOM of all interactive elements."""
        import os
        import time as _time

        screenshot = self.bot.screenshot_mgr.capture()
        t0 = _time.perf_counter()
        dom = self.bot.dom_builder.build(screenshot)
        elapsed = _time.perf_counter() - t0
        yaml_str = self.bot.dom_builder.to_yaml(dom)
        print(yaml_str)
        print(f"# DOM build time: {elapsed:.2f}s")

        if "--save" in args:
            save_dir = os.path.join("data", "dom_history")
            os.makedirs(save_dir, exist_ok=True)
            ts = _time.strftime("%Y%m%d_%H%M%S")
            img_path = os.path.join(save_dir, f"{ts}.png")
            yaml_path = os.path.join(save_dir, f"{ts}.yaml")
            import cv2 as _cv2
            _cv2.imwrite(img_path, screenshot)
            with open(yaml_path, "w", encoding="utf-8") as f:
                f.write(yaml_str)
            print(f"# Saved: {img_path}, {yaml_path}")

    def cmd_run(self, args: list[str]) -> None:
        """Execute a YAML script (v2 DOM-aware runner)."""
        if not args:
            print("Usage: run <name> [--dry]")
            return

        name = args[0]
        dry_run = "--dry" in args

        # Resolve script path
        scripts_dir = ""
        if self.bot.game_profile:
            scripts_dir = self.bot.game_profile.scripts_dir

        if not scripts_dir or not os.path.isdir(scripts_dir):
            print(f"Scripts directory not found: {scripts_dir}")
            return

        script_path = os.path.join(scripts_dir, f"{name}.yaml")
        if not os.path.isfile(script_path):
            available = list_scripts(scripts_dir)
            print(f"Script not found: {name}")
            if available:
                print(f"Available: {', '.join(available)}")
            return

        try:
            script = load_script(script_path)
        except ValueError as e:
            print(f"Invalid script: {e}")
            return

        desc = script.get("description", "")
        print(f"Script: {script['name']}")
        if desc:
            print(f"  {desc}")
        print(f"  Steps: {len(script['steps'])}")
        if dry_run:
            print("  Mode: dry-run")
        print()

        runner = ScriptRunner(
            self.bot.adb,
            self.bot.dom_builder,
            self.bot.screenshot_mgr.capture,
        )
        ok = runner.run(script, dry_run=dry_run)
        print(f"\nResult: {'OK' if ok else 'ABORTED'}")

    def cmd_scripts(self, args: list[str]) -> None:
        """List available YAML scripts."""
        scripts_dir = ""
        if self.bot.game_profile:
            scripts_dir = self.bot.game_profile.scripts_dir

        if not scripts_dir or not os.path.isdir(scripts_dir):
            print(f"No scripts directory: {scripts_dir}")
            return

        names = list_scripts(scripts_dir)
        if not names:
            print("No scripts found.")
            return

        print(f"Scripts in {scripts_dir}:")
        for name in names:
            path = os.path.join(scripts_dir, f"{name}.yaml")
            try:
                script = load_script(path)
                desc = script.get("description", "")
                steps = len(script.get("steps", []))
                print(f"  {name:<30s} {steps} steps  {desc}")
            except (ValueError, Exception) as e:
                print(f"  {name:<30s} (error: {e})")

    def cmd_auto_test(self, args: list[str]) -> None:
        """Simulate one auto-loop iteration on a static screenshot."""
        if not args:
            print("Usage: auto_test <png_file>")
            return

        png_path = args[0]
        screenshot = cv2.imread(png_path)
        if screenshot is None:
            print(f"Failed to read image: {png_path}")
            return

        # Set all loggers to DEBUG for maximum detail
        root_logger = logging.getLogger()
        old_level = root_logger.level
        old_handler_levels = []
        for h in root_logger.handlers:
            old_handler_levels.append(h.level)
            h.setLevel(logging.DEBUG)
        root_logger.setLevel(logging.DEBUG)

        try:
            self.bot.simulate_auto_iteration(screenshot)
        finally:
            root_logger.setLevel(old_level)
            for h, lvl in zip(root_logger.handlers, old_handler_levels):
                h.setLevel(lvl)

    @staticmethod
    def _match_quest_rule(rules: list[dict], quest_text: str) -> tuple[dict | None, re.Match | None]:
        """Match quest text against rules by name (bilingual) or regex pattern.

        Tries exact name match first (case-insensitive), then falls back
        to regex pattern matching.  Returns (rule, regex_match) or
        (None, None) when nothing matches.
        """
        quest_lower = quest_text.lower().strip()

        # Pass 1: match by name (exact, case-insensitive)
        for rule in rules:
            name = rule.get("name", "")
            if name and name.lower() == quest_lower:
                return rule, None

        # Pass 2: match by regex pattern
        for rule in rules:
            pattern = rule.get("pattern", "")
            if pattern:
                m = re.search(pattern, quest_text)
                if m:
                    return rule, m

        return None, None

    def cmd_quest(self, args: list[str]) -> None:
        """Execute a quest script by matching quest text against rules."""
        if not args:
            print("Usage: quest <quest text or script name>")
            print("Example: quest 派遣3名镇民")
            print("Example: quest 将驻防站升至2级")
            print("Example: quest claim_quest_reward")
            return

        quest_text = " ".join(args)
        rules = self.bot._quest_scripts
        if not rules:
            print("No quest scripts loaded.")
            return

        # Find matching rule (by name or pattern)
        matched_rule, matched_match = self._match_quest_rule(rules, quest_text)

        if matched_rule is None:
            print(f"No rule matches '{quest_text}'")
            print("Available scripts:")
            for rule in rules:
                name = rule.get("name", "")
                pattern = rule.get("pattern", "?")
                label = f"{name}  /{pattern}/" if name else f"/{pattern}/"
                print(f"  {label}  ({len(rule.get('steps', []))} steps)")
            return

        rule_name = matched_rule.get("name", "")
        pattern = matched_rule.get("pattern", "")
        steps = matched_rule.get("steps", [])
        header = f"{rule_name}  /{pattern}/" if rule_name else f"/{pattern}/"
        print(f"Matched rule: {header} ({len(steps)} steps)")

        # Create standalone runner
        from brain.quest_script import QuestScriptRunner
        runner = QuestScriptRunner(
            ocr_locator=self.bot.ocr,
            template_matcher=self.bot.template_matcher,
            adb_controller=self.bot.adb,
            screenshot_fn=self.bot.screenshot_mgr.capture,
        )
        runner.load(steps)

        # Extract named regex groups into runner variables
        if matched_match:
            for var_name, value in matched_match.groupdict().items():
                if value is not None:
                    runner.variables[var_name] = value
                    print(f"  Extracted: {var_name} = '{value}'")

        max_iterations = len(steps) * 10  # safety limit
        iteration = 0

        while not runner.is_done() and iteration < max_iterations:
            iteration += 1
            try:
                screenshot = self.bot.screenshot_mgr.capture()
            except Exception as e:
                print(f"Screenshot failed: {e}")
                break

            actions = runner.execute_one(screenshot)
            if actions is None:
                # Step waiting (e.g. text not found), retry
                print(f"  Step {runner.step_index + 1}/{len(steps)}: waiting...")
                time.sleep(1.0)
                continue

            if not actions:
                # No-op step (read_text, eval)
                cur = runner.steps[max(0, runner.step_index - 1)]
                print(f"  Step {runner.step_index}/{len(steps)}: "
                      f"{cur.get('description', 'done')}")
                continue

            # Execute actions
            for action in actions:
                delay = action.get("delay", 1.0)
                desc = action.get("reason", "")
                print(f"  Step {runner.step_index}/{len(steps)}: "
                      f"tap ({action.get('x')}, {action.get('y')}) — {desc}")
                self.bot.runner.execute(action)
                time.sleep(delay)

        if runner.is_aborted():
            print(f"Quest script ABORTED: {runner.abort_reason}")
        elif runner.is_done():
            print(f"Quest script completed ({len(steps)} steps)")
        else:
            print(f"Quest script stopped after {iteration} iterations")

    def cmd_quest_rules(self, args: list[str]) -> None:
        """List all quest action rules."""
        rules = self.bot._quest_scripts
        if not rules:
            print("No quest scripts loaded.")
            return
        print(f"{len(rules)} quest script(s):")
        for i, rule in enumerate(rules):
            name = rule.get("name", "")
            pattern = rule.get("pattern", "?")
            steps = rule.get("steps", [])
            header = f"{name}  /{pattern}/" if name else f"/{pattern}/"
            print(f"  {i + 1}. {header}  ({len(steps)} steps)")
            for j, step in enumerate(steps):
                desc = step.get("description", "")
                verb = "?"
                for v in ("tap_xy", "tap_text", "tap_icon", "swipe", "wait_text", "ensure_main_city", "ensure_world_map", "read_text", "eval", "find_building"):
                    if v in step:
                        verb = f"{v}={step[v]}"
                        break
                repeat = step.get("repeat", 1)
                repeat_str = f" x{repeat}" if repeat > 1 else ""
                print(f"      {j + 1}. {verb}{repeat_str}  {desc}")

    def cmd_quest_test(self, args: list[str]) -> None:
        """Dry-run a quest script — show steps without executing."""
        if not args:
            print("Usage: quest_test <quest text or script name>")
            return

        quest_text = " ".join(args)
        rules = self.bot._quest_scripts
        if not rules:
            print("No quest scripts loaded.")
            return

        matched_rule, _ = self._match_quest_rule(rules, quest_text)

        if matched_rule is None:
            print(f"No rule matches '{quest_text}'")
            return

        name = matched_rule.get("name", "")
        pattern = matched_rule.get("pattern", "?")
        steps = matched_rule.get("steps", [])
        header = f"{name}  /{pattern}/" if name else f"/{pattern}/"
        print(f"Matched: {header}  ({len(steps)} steps)")
        print(f"Dry run for quest text: '{quest_text}'")
        print()
        for i, step in enumerate(steps):
            desc = step.get("description", "")
            delay = step.get("delay", 1.0)
            repeat = step.get("repeat", 1)
            verb = "?"
            detail = ""
            if "tap_xy" in step:
                verb = "tap_xy"
                detail = f"({step['tap_xy'][0]}, {step['tap_xy'][1]})"
            elif "tap_text" in step:
                args_val = step["tap_text"]
                if isinstance(args_val, str):
                    args_val = [args_val]
                verb = "tap_text"
                detail = f"'{args_val[0]}'"
                if len(args_val) > 1:
                    detail += f" (#{args_val[1]})"
            elif "tap_icon" in step:
                args_val = step["tap_icon"]
                if isinstance(args_val, str):
                    args_val = [args_val]
                verb = "tap_icon"
                detail = f"'{args_val[0]}'"
                if len(args_val) > 1:
                    detail += f" (#{args_val[1]})"
            elif "swipe" in step:
                verb = "swipe"
                args_val = step["swipe"]
                detail = f"({args_val[0]},{args_val[1]})->({args_val[2]},{args_val[3]})"
                if len(args_val) > 4:
                    detail += f" {args_val[4]}ms"
            elif "wait_text" in step:
                args_val = step["wait_text"]
                if isinstance(args_val, str):
                    args_val = [args_val]
                verb = "wait_text"
                detail = f"'{args_val[0]}'"
            elif "ensure_main_city" in step:
                verb = "ensure_main_city"
                args_val = step.get("ensure_main_city", [])
                if isinstance(args_val, list) and args_val:
                    detail = f"max_retries={args_val[0]}"
                else:
                    detail = "max_retries=10"
            elif "ensure_world_map" in step:
                verb = "ensure_world_map"
                args_val = step.get("ensure_world_map", [])
                if isinstance(args_val, list) and args_val:
                    detail = f"max_retries={args_val[0]}"
                else:
                    detail = "max_retries=10"
            elif "read_text" in step:
                verb = "read_text"
                detail = f"({step['read_text'][0]}, {step['read_text'][1]}) -> ${step['read_text'][2]}"
            elif "eval" in step:
                verb = "eval"
                detail = f"${step['eval'][0]} = {step['eval'][1]}"
            elif "find_building" in step:
                verb = "find_building"
                args_val = step["find_building"]
                if isinstance(args_val, str):
                    args_val = [args_val]
                detail = f"'{args_val[0]}'"
                if len(args_val) > 1 and isinstance(args_val[1], dict):
                    detail += f" opts={args_val[1]}"

            repeat_str = f" x{repeat}" if repeat > 1 else ""
            print(f"  {i + 1}. [{verb}] {detail}  delay={delay}s{repeat_str}")
            if desc:
                print(f"     {desc}")

    def cmd_detect_finger(self, args: list[str]) -> None:
        """Detect tutorial finger on screen and save debug crop."""
        if args:
            screenshot = cv2.imread(args[0])
            if screenshot is None:
                print(f"Failed to read image: {args[0]}")
                return
        else:
            screenshot = self.bot.screenshot_mgr.capture()
        fd = self.bot.finger_detector

        # Show prescan scores
        if fd._prescan_templates:
            sh, sw = screenshot.shape[:2]
            gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
            small_w = max(1, int(sw * fd._PRESCAN_SCALE))
            small_h = max(1, int(sh * fd._PRESCAN_SCALE))
            small = cv2.resize(gray, (small_w, small_h),
                               interpolation=cv2.INTER_AREA)
            labels = ["normal", "rot117cw"]
            for i, (ps_tpl, ps_mask) in enumerate(fd._prescan_templates):
                if (ps_tpl.shape[0] > small_h
                        or ps_tpl.shape[1] > small_w):
                    print(f"Prescan[{labels[i]}]: skipped (template too large)")
                    continue
                res = cv2.matchTemplate(small, ps_tpl,
                                        cv2.TM_CCORR_NORMED,
                                        mask=ps_mask)
                _, val, _, loc = cv2.minMaxLoc(res)
                label = labels[i] if i < len(labels) else f"#{i}"
                print(f"Prescan[{label}]: {val:.3f} at {loc} "
                      f"(threshold={fd._PRESCAN_THRESHOLD})")

        # Show raw matches for all variants (before threshold filter)
        for cache_name, _, flip_type in fd._all_variants:
            raw = fd.element_detector.locate(
                screenshot, cache_name, methods=["template"]
            )
            if raw is not None:
                ncc = fd.verify_ncc(screenshot, raw.x, raw.y, flip_type)
                bcon = fd.verify_boundary_contrast(
                    screenshot, raw.x, raw.y, flip_type)
                print(f"Raw {flip_type:7s}: ccorr={raw.confidence:.3f} "
                      f"at ({raw.x}, {raw.y})  ncc={ncc:.3f}  "
                      f"boundary={bcon:.1f}")
            else:
                print(f"Raw {flip_type:7s}: no match")
        print(f"  (threshold: ccorr>={fd._FINGER_CONFIDENCE_THRESHOLD}, "
              f"ncc>={fd._FINGER_NCC_THRESHOLD}, "
              f"boundary>={fd._FINGER_BOUNDARY_THRESHOLD})")

        import time as _time
        t0 = _time.perf_counter()
        finger_match, flip_type = fd.detect(screenshot)
        elapsed = _time.perf_counter() - t0
        print(f"detect elapsed: {int(elapsed * 1000)}ms")

        if finger_match is None:
            print("No finger detected (rejected by three-stage filter).")
            return

        tip_x, tip_y = fd.fingertip_pos(
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

        from vision.template_matcher import TemplateMatcher as TM

        tm = self.bot.template_matcher

        # Show raw top-5 CCORR candidates with red-pixel ratios
        candidates = tm.match_one_multi(screenshot, "close_x",
                                        max_matches=5)
        entry = tm._cache.get("close_x")
        opaque = None
        if entry is not None:
            _, mask = entry
            if mask is not None:
                opaque = mask[:, :, 0] > 0

        # Pre-compute boundary masks for diagnostic display
        bmasks = tm._get_boundary_masks("close_x")

        best = None
        best_score = -1.0
        for i, m in enumerate(candidates):
            patch = screenshot[m.bbox[1]:m.bbox[3], m.bbox[0]:m.bbox[2]]
            # Compute per-candidate red ratios for diagnostic display
            hsv = cv2.cvtColor(patch, cv2.COLOR_BGR2HSV)
            red_px = (cv2.inRange(hsv, (0, 80, 80), (10, 255, 255))
                      | cv2.inRange(hsv, (170, 80, 80), (180, 255, 255)))
            if opaque is not None:
                r_op = float((red_px[opaque] > 0).sum()) / opaque.sum()
                bg_mask = ~opaque
                r_bg = float((red_px[bg_mask] > 0).sum()) / bg_mask.sum() if bg_mask.sum() > 0 else 0.0
            else:
                r_op = float((red_px > 0).sum()) / red_px.size
                r_bg = 0.0
            red_passed = TM.verify_red_pixel(patch, opaque,
                                             TM._RED_OPAQUE_MIN, TM._RED_BG_MAX)
            # Boundary contrast diagnostic
            bcon = -1.0
            if bmasks is not None:
                bcon = TM.compute_boundary_contrast(
                    patch, bmasks[0], bmasks[1])
            bcon_passed = bcon >= TM._BOUNDARY_CONTRAST_THRESHOLD or bmasks is None
            passed = red_passed and bcon_passed
            print(f"  #{i+1}: ccorr={m.confidence:.3f} "
                  f"red_x={r_op:.3f} red_bg={r_bg:.3f} "
                  f"boundary={bcon:.1f} at ({m.x}, {m.y})"
                  f" {'PASS' if passed else 'FAIL'}")
            if passed:
                score = r_op - r_bg
                if score > best_score:
                    best_score = score
                    best = m
        print(f"  (need: red_x>={TM._RED_OPAQUE_MIN}, "
              f"red_bg<={TM._RED_BG_MAX}, "
              f"boundary>={TM._BOUNDARY_CONTRAST_THRESHOLD})")

        match = best
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

    def cmd_find_building(self, args: list[str]) -> None:
        """Find a building on the city map and tap it."""
        if not args:
            print("Usage: find_building <building_name>")
            print("Example: find_building 兵营")
            return
        if not self.bot.building_finder:
            print("BuildingFinder not initialized. Check city_layout in game.json.")
            return
        name = " ".join(args)
        print(f"Searching for '{name}'...")
        ok = self.bot.building_finder.find_and_tap(name)
        if ok:
            print(f"Found and tapped '{name}'")
        else:
            print(f"Building '{name}' not found")

    def cmd_press_read(self, args: list[str]) -> None:
        """Press-drag-read: show all visible building names on the city map."""
        if not self.bot.building_finder:
            print("BuildingFinder not initialized. Check city_layout in game.json.")
            return
        print("Press-drag-read in progress...")
        results = self.bot.building_finder.read_all_buildings()
        if not results:
            print("No building names detected.")
            print("Make sure you are on the main city screen.")
            return
        print(f"Detected {len(results)} building(s):")
        for name, x, y in results:
            print(f"  {name:20s}  ({x}, {y})")

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
        max_loops = 0
        i = 0
        while i < len(args):
            if args[i] == "--loops" and i + 1 < len(args):
                max_loops = int(args[i + 1])
                i += 2
            else:
                max_loops = int(args[i])
                i += 1
        self.bot.auto_loop(max_loops)

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
            if arg in ("--loops", "--game", "--emulator") and i + 1 < len(sys.argv):
                i += 1
                flags.append(sys.argv[i])
        else:
            # Everything from here on is the command
            cmd_args = sys.argv[i:]
            break
        i += 1

    parser = argparse.ArgumentParser(
        description="SLGrobot - SLG Game AI Agent",
        epilog=HELP_TEXT,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
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
    parser.add_argument(
        "--emulator", type=str, default=None,
        choices=list(config.EMULATOR_PRESETS.keys()),
        help="Emulator to use (default: config.ACTIVE_EMULATOR)"
    )
    args = parser.parse_args(flags)

    # Override emulator config if --emulator flag is provided
    if args.emulator:
        preset = config.EMULATOR_PRESETS[args.emulator]
        config.ADB_PORT = preset["port"]
        config.ADB_PATH = preset["adb_path"]
        config.ACTIVE_EMULATOR = args.emulator

    GameLogger(config.LOG_DIR)

    # Detect game from emulator's foreground app if --game not explicitly provided
    game_explicit = "--game" in sys.argv
    games_dir = getattr(config, "GAMES_DIR", "games")
    game_id = args.game

    if not game_explicit:
        # Build reverse lookup: package -> game_id
        pkg_to_game = {pkg: gid for gid, pkg in config.GAME_PACKAGES.items()}
        # Connect ADB early to detect foreground app
        from device.adb_controller import ADBController
        _adb = ADBController(config.ADB_HOST, config.ADB_PORT, config.ADB_PATH)
        if _adb.connect():
            fg_pkg = _adb.get_foreground_package()
            if fg_pkg:
                if fg_pkg in pkg_to_game:
                    game_id = pkg_to_game[fg_pkg]
                    print(f"Detected game: {game_id} (package: {fg_pkg})")
                else:
                    print(f"Unknown game package: {fg_pkg}")
                    print(f"Supported: {', '.join(f'{gid} ({pkg})' for gid, pkg in config.GAME_PACKAGES.items())}")
                    sys.exit(1)

    # Load game profile
    game_profile = None
    try:
        game_profile = load_game_profile(game_id, games_dir)
        print(f"Game: {game_profile.display_name}")
    except FileNotFoundError:
        print(f"Warning: game profile '{game_id}' not found, using defaults")

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

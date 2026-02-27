"""SLGrobot - Main entry point with two-layer decision loop.

Supports two modes:
  - Interactive CLI (default): manual game control
  - Auto mode (--auto): autonomous two-layer decision loop

Two-layer decision loop:
  1. Tactical Layer   - Local rule engine (<500ms) decomposes tasks
  2. Execution Layer  - CV + ADB (<100ms) screenshot -> detect -> tap

Auto loop flow:
  screenshot -> classify scene ->
    popup   -> auto-close -> continue
    loading -> wait -> continue
    unknown -> press BACK -> continue
    other   -> update game_state ->
      has_pending tasks -> rule_engine.plan(task) -> validate -> execute -> verify
      no tasks           -> auto_handler.get_actions() -> execute
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
from vision.element_detector import ElementDetector, find_primary_button, has_red_text_near_button
from scene.classifier import SceneClassifier
from scene.popup_filter import PopupFilter
from state.game_state import GameState
from state.state_tracker import StateTracker
from state.persistence import StatePersistence
from brain.task_queue import TaskQueue, Task
from brain.auto_handler import AutoHandler
from brain.rule_engine import RuleEngine
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
  center                        Tap screen center
  status                        Show connection and game state
  state                         Show current game state
  scene                         Classify current scene
  quest <name or text>           Execute a quest script (bilingual: name or text)
  quest_rules                   List all quest scripts (name + pattern)
  quest_test <name or text>     Dry-run a quest script (show steps)
  auto [loops]                  Run auto loop (default: infinite)
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
    """Main game bot with two-layer decision loop.

    Layers:
    1. Tactical (Rules): rule_engine    - called per task
    2. Execution (ADB):  action_runner  - called per action

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
        ocr_corrections = game_profile.ocr_corrections if game_profile else {}
        self.ocr = OCRLocator(corrections=ocr_corrections)
        self.grid = GridOverlay(grid_cols, grid_rows)
        self.detector = ElementDetector(self.template_matcher, self.ocr, self.grid)

        # Scene layer
        self.classifier = SceneClassifier(self.template_matcher, game_profile=game_profile)
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
        self.validator = ActionValidator(self.detector, self.classifier)
        self.runner = ActionRunner(
            self.adb, self.input_actions, self.detector,
            self.grid, self.screenshot_mgr,
            building_finder=self.building_finder,
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
            game_state=self.game_state,
            game_profile=game_profile,
            adb_controller=self.adb,
            screenshot_fn=self.screenshot_mgr.capture,
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
        """Run the autonomous two-layer decision loop with error recovery.

        Decision hierarchy:
        1. Popup/loading -> handle immediately (auto layer)
        2. Unknown scene  -> press BACK to escape
        3. Pending tasks   -> rule engine plans, executor runs with validation
        4. Nothing to do   -> auto-handler scans for opportunistic actions

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
                self.game_logger.loop_count = loop
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

                    # 2a. Save loop screenshot (one per loop)
                    self.game_logger.save_loop_screenshot(screenshot, scene)

                    # 2b. Stuck detection
                    scene_history.append(scene)
                    # Keep history bounded
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

                    # 2b. Reset stuck escalation if scene changed
                    if len(scene_history) >= 2 and scene_history[-1] != scene_history[-2]:
                        self.stuck_recovery.reset()

                    # 2c. Tutorial finger detection — highest priority.
                    #     Runs BEFORE state update so finger can be tapped
                    #     within the ~3s it stays on screen.
                    finger, flip = self.quest_workflow._detect_tutorial_finger(
                        screenshot
                    )
                    if finger is not None:
                        tip_x, tip_y = self.quest_workflow._fingertip_pos(
                            finger.x, finger.y, flip
                        )
                        logger.info(
                            f"Tutorial finger detected at ({finger.x}, {finger.y}) "
                            f"{flip}, tapping fingertip ({tip_x}, {tip_y})"
                        )
                        self.adb.tap(tip_x, tip_y)
                        consecutive_unknown_scenes = 0
                        # Fast-start quest workflow to EXECUTE_QUEST when
                        # finger is on the quest bar — the finger tap already
                        # navigates us past the read→click phases, so skip
                        # directly to execution so quest rules are active on
                        # the next loop.
                        # Also handles the case where workflow is already active
                        # in an early phase (ENSURE_MAIN_CITY / READ_QUEST /
                        # CLICK_QUEST) — the finger tap navigates away from
                        # main_city, so the workflow must advance to
                        # EXECUTE_QUEST to avoid a back-and-forth loop.
                        if (scene == "main_city"
                                and self.game_state.quest_bar_has_tutorial_finger
                                and self.game_state.quest_bar_visible
                                and self.game_state.quest_bar_current_quest):
                            quest_text = self.game_state.quest_bar_current_quest
                            early_phases = {
                                self.quest_workflow.IDLE,
                                self.quest_workflow.ENSURE_MAIN_CITY,
                                self.quest_workflow.READ_QUEST,
                                self.quest_workflow.CLICK_QUEST,
                            }
                            if (not self.quest_workflow.is_active()
                                    or self.quest_workflow.phase in early_phases):
                                if not self.quest_workflow.is_active():
                                    self.quest_workflow.start()
                                self.quest_workflow.target_quest_name = quest_text
                                self.quest_workflow.phase = (
                                    self.quest_workflow.EXECUTE_QUEST
                                )
                                self.quest_workflow.execute_iterations = 0
                                self.quest_workflow._script_runner.reset()
                                self.quest_workflow._loaded_quest_pattern = ""
                                self.quest_workflow._exhausted_buttons = set()
                                logger.info(
                                    f"Quest workflow fast-started to EXECUTE_QUEST "
                                    f"(quest bar finger), quest='{quest_text}'"
                                )
                        # Short delay for game scene transition after tap.
                        # Too short → next screenshot still shows old scene.
                        # Too long → next finger may disappear (~3s window).
                        # 0.8s + ~1s ADB screenshot ≈ 1.8s post-tap capture.
                        time.sleep(1.5)
                        continue

                    # 2d. Update state on main_city (after finger check so
                    #     the expensive OCR doesn't delay finger detection).
                    if scene == "main_city":
                        self.state_tracker.update(screenshot, scene)

                    # 3. Exit dialog — game's pause/quit overlay.
                    #    Must be handled before popup/loading/quest workflow
                    #    since the dark background can be misclassified.
                    #    Tap "继续" (rightmost icon) and wait 60s cooldown.
                    if scene == "exit_dialog":
                        logger.info(
                            "Exit dialog detected — tapping '继续' and "
                            "waiting 60s cooldown"
                        )
                        self.adb.tap(826, 843)
                        time.sleep(60)
                        continue

                    # 3b. Hero list / Hero recruit — not part of normal
                    #     quest flow, just back out immediately.
                    if scene == "hero":
                        back = self.template_matcher.match_one(
                            screenshot, "buttons/back_arrow"
                        )
                        if back:
                            logger.info(
                                f"Hero list: tapping back arrow "
                                f"at ({back.x}, {back.y})"
                            )
                            self.adb.tap(back.x, back.y)
                        else:
                            logger.info("Hero list: no back arrow, tapping blank area")
                            self.adb.tap(500, 100)
                        time.sleep(0.5)
                        continue

                    if scene == "hero_recruit":
                        primary = find_primary_button(screenshot)
                        if primary is not None:
                            logger.info(
                                f"Hero recruit: tapping primary button "
                                f"at ({primary.x}, {primary.y})"
                            )
                            self.adb.tap(primary.x, primary.y)
                            time.sleep(0.8)
                        # Back arrow to exit
                        back = self.template_matcher.match_one(
                            screenshot, "buttons/back_arrow"
                        )
                        if back:
                            logger.info(
                                f"Hero recruit: tapping back arrow "
                                f"at ({back.x}, {back.y})"
                            )
                            self.adb.tap(back.x, back.y)
                        else:
                            logger.info("Hero recruit: no back arrow, tapping blank area")
                            self.adb.tap(500, 100)
                        time.sleep(0.5)
                        continue

                    # 3c. Hero upgrade — click primary button if no red
                    #     text (insufficient resources), otherwise back out.
                    if scene == "hero_upgrade":
                        primary = find_primary_button(screenshot)
                        if primary is not None and not has_red_text_near_button(
                            screenshot, primary
                        ):
                            logger.info(
                                f"Hero upgrade: resources OK, tapping "
                                f"primary button at ({primary.x}, {primary.y})"
                            )
                            self.adb.tap(primary.x, primary.y)
                            time.sleep(0.8)
                        else:
                            reason = (
                                "red text (insufficient resources)"
                                if primary else "no primary button"
                            )
                            logger.info(f"Hero upgrade: {reason}, backing out")
                        back = self.template_matcher.match_one(
                            screenshot, "buttons/back_arrow"
                        )
                        if back:
                            self.adb.tap(back.x, back.y)
                        else:
                            logger.info("Hero upgrade: no back arrow, tapping blank area")
                            self.adb.tap(500, 100)
                        time.sleep(0.5)
                        continue

                    # 4. Handle popups immediately (skip when quest workflow
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
                            time.sleep(0.3)
                            continue
                        logger.info("Popup detected, attempting to close")
                        self.popup_filter.handle(screenshot)
                        time.sleep(0.3)
                        continue

                    # 4. Story dialogue — try skip button first, then
                    #    down-triangle to advance one frame
                    if scene == "story_dialogue":
                        # Try OCR skip button first
                        skip_element = None
                        for skip_text in ["跳过", "skip"]:
                            skip_element = self.detector.locate(
                                screenshot, skip_text, methods=["ocr"]
                            )
                            if skip_element is not None:
                                break
                        if skip_element is not None:
                            logger.info(
                                f"Story dialogue: tapping skip "
                                f"'{skip_element.name}' "
                                f"at ({skip_element.x}, {skip_element.y})"
                            )
                            self.adb.tap(skip_element.x, skip_element.y)
                        else:
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
                        time.sleep(0.3)
                        continue

                    # 5. Skip loading screens (but check for buttons first —
                    #    reward popups with dark backgrounds get misclassified
                    #    as loading; real loading screens have no buttons).
                    if scene == "loading":
                        primary = find_primary_button(screenshot)
                        if primary is not None:
                            logger.info(
                                f"Loading screen has primary button "
                                f"at ({primary.x}, {primary.y}) — "
                                f"likely a reward popup, tapping"
                            )
                            self.adb.tap(primary.x, primary.y)
                            time.sleep(0.3)
                        else:
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

                    # 6. Handle unknown scenes with escalating escape
                    #    Level 1 (counter 1): back_arrow / popup / BACK
                    #    Level 2 (counter 2): primary button / BACK
                    #    Level 3 (counter >=3): tap blank area to reach main city
                    if scene == "unknown":
                        consecutive_unknown_scenes += 1
                        logger.info(
                            f"Unknown scene ({consecutive_unknown_scenes} consecutive)"
                        )

                        handled = False

                        # Try back arrow template (building panels have
                        # a visible back arrow in the top-left corner).
                        if not handled:
                            back = self.template_matcher.match_one(
                                screenshot, "buttons/back_arrow"
                            )
                            if back:
                                logger.info(
                                    f"Unknown scene: back arrow "
                                    f"at ({back.x}, {back.y})"
                                )
                                self.adb.tap(back.x, back.y)
                                handled = True
                                consecutive_unknown_scenes = 0

                        # Try primary button (blue/green action buttons).
                        if not handled:
                            primary = find_primary_button(screenshot)
                            if primary is not None:
                                logger.info(
                                    f"Unknown scene: primary button "
                                    f"at ({primary.x}, {primary.y})"
                                )
                                self.adb.tap(primary.x, primary.y)
                                handled = True
                                consecutive_unknown_scenes = 0

                        # Try popup filter (skips OCR if no dark overlay).
                        if not handled and self.popup_filter.handle(screenshot):
                            logger.info(
                                "Unknown scene handled by popup filter"
                            )
                            handled = True
                            consecutive_unknown_scenes = 0

                        # Escalation: tap blank area to navigate to main city
                        if not handled and consecutive_unknown_scenes >= 3:
                            logger.warning(
                                f"Unknown scene stuck ({consecutive_unknown_scenes}x),"
                                f" tapping blank area to escape"
                            )
                            self.adb.tap(500, 100)
                            self.game_logger.log_recovery(
                                "unknown_scene_escape",
                                f"Tapped blank area after "
                                f"{consecutive_unknown_scenes} "
                                f"consecutive unknown scenes"
                            )
                            consecutive_unknown_scenes = 0

                        # Fallback: tap blank area (don't reset counter
                        # to allow escalation on next iteration).
                        if not handled:
                            logger.info("Unknown scene: tapping blank area")
                            self.adb.tap(500, 100)

                        time.sleep(config.LOOP_INTERVAL)
                        continue
                    else:
                        consecutive_unknown_scenes = 0

                    # 7. Update game state (main_city already updated
                    #    in step 2c before finger detection)
                    if scene != "main_city":
                        self.state_tracker.update(screenshot, scene)

                    # 7.5 Quest workflow has highest priority — start it
                    #     when quest bar is visible.
                    if (not self.quest_workflow.is_active()
                            and scene == "main_city"
                            and self.game_state.quest_bar_visible
                            and self.game_state.quest_bar_current_quest
                            and self.quest_workflow.should_start(
                                self.game_state.quest_bar_current_quest,
                                self.game_state.quest_bar_has_green_check)):
                        logger.info(
                            "Quest bar active, starting quest workflow "
                            f"(pausing {self.task_queue.pending_count()} queued tasks), "
                            f"quest='{self.game_state.quest_bar_current_quest}'"
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
        if gs.quest_bar_visible:
            print(f"Quest bar: '{gs.quest_bar_current_quest}' "
                  f"red_badge={gs.quest_bar_has_red_badge} "
                  f"green_check={gs.quest_bar_has_green_check}")
        if gs.quest_workflow_phase != "idle":
            print(f"Quest workflow: phase={gs.quest_workflow_phase} "
                  f"target='{gs.quest_workflow_target}'")

    def cmd_state(self, args: list[str]) -> None:
        gs = self.bot.game_state
        print(gs.summary())

    def cmd_scene(self, args: list[str]) -> None:
        screenshot = self.bot.screenshot_mgr.capture()
        scene = self.bot.classifier.classify(screenshot)
        scores = self.bot.classifier.get_confidence(screenshot)
        print(f"Scene: {scene}")
        for s, score in sorted(scores.items(), key=lambda x: -x[1]):
            if score > 0:
                print(f"  {s}: {score:.3f}")

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
        rules = self.bot.quest_workflow._quest_scripts
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
        rules = self.bot.quest_workflow._quest_scripts
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
        rules = self.bot.quest_workflow._quest_scripts
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
        max_loops = int(args[0]) if args else 0
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
            if arg in ("--loops", "--game") and i + 1 < len(sys.argv):
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

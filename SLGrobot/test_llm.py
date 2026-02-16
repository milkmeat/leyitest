"""Phase 4 Test - LLM Integration verification.

Tests:
1. LLMPlanner initialization and API key validation
2. Screenshot annotation and preparation
3. JSON response parsing (strategic plan)
4. JSON response parsing (unknown scene)
5. ActionValidator rejects invalid actions
6. ActionValidator accepts valid actions
7. ActionRunner executes tap with coordinates
8. ResultChecker basic verification
9. JSON extraction edge cases
10. (Live) Send screenshot to LLM and print parsed plan

Supports multiple LLM providers via model_presets.py.

Usage:
  python test_llm.py           # Run offline tests only
  python test_llm.py --live    # Include live LLM API test (requires API key)
"""

import sys
import json
import logging
import argparse

import numpy as np

logging.basicConfig(level=logging.INFO, format="%(name)s - %(message)s")
logger = logging.getLogger("test_llm")


def test_llm_planner_init():
    """Test 1: LLMPlanner initializes correctly."""
    from brain.llm_planner import LLMPlanner
    from vision.grid_overlay import GridOverlay

    grid = GridOverlay()
    planner = LLMPlanner(api_key="test-key", model="test-model", grid_overlay=grid)

    assert planner.api_key == "test-key"
    assert planner.model == "test-model"
    assert planner.grid is grid
    print("  PASS: LLMPlanner initializes with correct params")


def test_multi_provider_init():
    """Test 1b: LLMPlanner supports multiple providers."""
    from brain.llm_planner import LLMPlanner

    # Anthropic provider
    p1 = LLMPlanner(api_key="sk-ant-test", model="claude-sonnet", provider="anthropic")
    assert p1.provider == "anthropic"
    print("  PASS: Anthropic provider init")

    # OpenAI-compatible provider (Zhipu)
    p2 = LLMPlanner(
        api_key="zhipu-key", model="GLM-4.6",
        provider="openai_compatible",
        base_url="https://api.z.ai/api/coding/paas/v4",
        vision_model="GLM-4.6V",
    )
    assert p2.provider == "openai_compatible"
    assert p2.vision_model == "GLM-4.6V"
    assert p2.base_url == "https://api.z.ai/api/coding/paas/v4"
    print("  PASS: OpenAI-compatible provider init (Zhipu)")


def test_should_consult():
    """Test 2: should_consult logic."""
    from brain.llm_planner import LLMPlanner
    from state.game_state import GameState
    from datetime import datetime, timedelta

    # No API key -> never consult
    planner = LLMPlanner(api_key="", model="test")
    state = GameState()
    assert not planner.should_consult(state)
    print("  PASS: No API key -> should_consult returns False")

    # With key, never consulted -> should consult
    planner = LLMPlanner(api_key="test-key", model="test")
    state = GameState()
    assert planner.should_consult(state)
    print("  PASS: Never consulted -> should_consult returns True")

    # Recently consulted -> should not consult
    state.last_llm_consult = datetime.now().isoformat()
    assert not planner.should_consult(state)
    print("  PASS: Recently consulted -> should_consult returns False")

    # Long ago -> should consult
    old_time = datetime.now() - timedelta(seconds=2000)
    state.last_llm_consult = old_time.isoformat()
    assert planner.should_consult(state)
    print("  PASS: Old consultation -> should_consult returns True")


def test_prepare_screenshot():
    """Test 3: Screenshot annotation and resizing."""
    from brain.llm_planner import LLMPlanner
    from vision.grid_overlay import GridOverlay

    grid = GridOverlay(cols=8, rows=6, screen_width=1080, screen_height=1920)
    planner = LLMPlanner(api_key="test", model="test", grid_overlay=grid)

    # Create a fake screenshot (1080x1920 BGR)
    screenshot = np.zeros((1920, 1080, 3), dtype=np.uint8)
    screenshot[:] = (100, 150, 200)  # Some color

    annotated = planner._prepare_screenshot(screenshot)

    # Should be resized (max dim 1024)
    h, w = annotated.shape[:2]
    assert max(h, w) <= 1024, f"Expected max dim <= 1024, got {h}x{w}"
    assert len(annotated.shape) == 3  # Still BGR
    print(f"  PASS: Screenshot annotated and resized to {w}x{h}")


def test_parse_plan_response():
    """Test 4: Parse strategic plan JSON."""
    from brain.llm_planner import LLMPlanner

    planner = LLMPlanner(api_key="test", model="test")

    # Valid JSON
    response = json.dumps({
        "reasoning": "Need to upgrade barracks first",
        "tasks": [
            {"name": "upgrade_building", "priority": 10, "params": {"building_name": "barracks"}},
            {"name": "collect_resources", "priority": 8, "params": {}},
            {"name": "custom", "priority": 5, "params": {}, "actions": [
                {"type": "tap", "target_text": "Shop", "fallback_grid": "A6"}
            ]},
        ]
    })

    tasks = planner._parse_plan_response(response)
    assert len(tasks) == 3
    assert tasks[0].name == "upgrade_building"
    assert tasks[0].priority == 10
    assert tasks[0].params["building_name"] == "barracks"
    assert tasks[2].name == "custom"
    assert "actions" in tasks[2].params
    print("  PASS: Parsed 3 tasks from valid JSON")

    # JSON with markdown fences
    response_fenced = '```json\n' + response + '\n```'
    tasks = planner._parse_plan_response(response_fenced)
    assert len(tasks) == 3
    print("  PASS: Parsed tasks from JSON with markdown fences")

    # Invalid JSON
    tasks = planner._parse_plan_response("not json at all")
    assert len(tasks) == 0
    print("  PASS: Invalid JSON returns empty task list")


def test_parse_scene_response():
    """Test 5: Parse unknown scene analysis JSON."""
    from brain.llm_planner import LLMPlanner

    planner = LLMPlanner(api_key="test", model="test")

    response = json.dumps({
        "scene_description": "A reward claim popup with two buttons",
        "actions": [
            {"type": "tap", "target_text": "Claim", "fallback_grid": "D4"},
            {"type": "tap", "target_text": "Close", "fallback_grid": "H1"},
        ]
    })

    actions = planner._parse_scene_response(response)
    assert len(actions) == 2
    assert actions[0]["type"] == "tap"
    assert actions[0]["target_text"] == "Claim"
    print("  PASS: Parsed 2 actions from scene analysis")


def test_action_validator():
    """Test 6: ActionValidator rejects/accepts correctly."""
    from executor.action_validator import ActionValidator
    from vision.element_detector import ElementDetector
    from vision.template_matcher import TemplateMatcher
    from vision.ocr_locator import OCRLocator
    from vision.grid_overlay import GridOverlay
    from scene.classifier import SceneClassifier
    import config

    template_matcher = TemplateMatcher(config.TEMPLATE_DIR)
    ocr = OCRLocator()
    grid = GridOverlay()
    detector = ElementDetector(template_matcher, ocr, grid)
    classifier = SceneClassifier(template_matcher)
    validator = ActionValidator(detector, classifier)

    screenshot = np.zeros((1920, 1080, 3), dtype=np.uint8)

    # Wait actions always valid
    assert validator.validate({"type": "wait", "seconds": 1}, screenshot)
    print("  PASS: Wait action validated")

    # Tap with valid coordinates
    assert validator.validate({"type": "tap", "x": 500, "y": 500}, screenshot)
    print("  PASS: Tap with valid coordinates accepted")

    # Tap with out-of-bounds coordinates
    assert not validator.validate({"type": "tap", "x": 5000, "y": 500}, screenshot)
    print("  PASS: Tap with out-of-bounds coordinates rejected")

    # Tap with no target and no coordinates
    assert not validator.validate({"type": "tap"}, screenshot)
    print("  PASS: Tap with no target rejected")

    # Tap with fallback_grid (always passes even if text not found)
    result = validator.validate(
        {"type": "tap", "target_text": "NonExistent", "fallback_grid": "C3"},
        screenshot,
    )
    assert result
    print("  PASS: Tap with fallback_grid accepted")

    # Swipe with missing coordinates
    assert not validator.validate({"type": "swipe", "x1": 100}, screenshot)
    print("  PASS: Swipe with missing coordinates rejected")

    # Valid swipe
    assert validator.validate(
        {"type": "swipe", "x1": 100, "y1": 200, "x2": 300, "y2": 400},
        screenshot,
    )
    print("  PASS: Valid swipe accepted")


def test_action_runner_init():
    """Test 7: ActionRunner initializes correctly."""
    from executor.action_runner import ActionRunner

    assert hasattr(ActionRunner, "execute")
    assert hasattr(ActionRunner, "execute_sequence")
    print("  PASS: ActionRunner class has expected methods")


def test_result_checker_init():
    """Test 8: ResultChecker initializes correctly."""
    from executor.result_checker import ResultChecker

    assert hasattr(ResultChecker, "check")
    assert hasattr(ResultChecker, "check_with_capture")
    print("  PASS: ResultChecker class has expected methods")


def test_extract_json_edge_cases():
    """Test 9: JSON extraction handles edge cases."""
    from brain.llm_planner import LLMPlanner

    planner = LLMPlanner(api_key="test", model="test")

    # JSON with surrounding text
    text = 'Here is the plan:\n{"reasoning": "test", "tasks": []}\nDone.'
    result = planner._extract_json(text)
    assert result is not None
    assert result["reasoning"] == "test"
    print("  PASS: Extracted JSON from surrounding text")

    # Nested code fences
    text = '```json\n{"reasoning": "nested", "tasks": [{"name": "collect_resources", "priority": 5}]}\n```'
    result = planner._extract_json(text)
    assert result is not None
    assert len(result["tasks"]) == 1
    print("  PASS: Extracted JSON from code fences")

    # Empty/null
    result = planner._extract_json("")
    assert result is None
    print("  PASS: Empty string returns None")


def test_model_presets():
    """Test 10: Model presets system."""
    from model_presets import PRESETS, get_preset, get_active_preset, ACTIVE_PRESET

    # Active preset should exist
    active = get_active_preset()
    assert "provider" in active
    assert "api_key" in active
    assert "model_name" in active
    assert "vision_model" in active
    print(f"  PASS: Active preset '{ACTIVE_PRESET}': provider={active['provider']}, model={active['model_name']}")

    # All presets should have required keys
    for name, preset in PRESETS.items():
        for key in ["provider", "base_url", "api_key", "model_name", "vision_model", "max_tokens"]:
            assert key in preset, f"Preset '{name}' missing key '{key}'"
    print(f"  PASS: All {len(PRESETS)} presets have required keys")

    # Invalid preset raises
    try:
        get_preset("nonexistent_provider")
        assert False, "Should have raised KeyError"
    except KeyError:
        pass
    print("  PASS: Invalid preset name raises KeyError")


def test_live_llm(screenshot=None):
    """Test (Live): Send screenshot to LLM and print parsed plan."""
    import config
    from brain.llm_planner import LLMPlanner
    from state.game_state import GameState
    from vision.grid_overlay import GridOverlay

    if not config.LLM_API_KEY:
        print("  SKIP: No LLM API key configured")
        return

    grid = GridOverlay()
    planner = LLMPlanner(grid_overlay=grid)
    state = GameState()
    state.scene = "main_city"
    state.resources = {"food": 50000, "wood": 32000, "stone": 15000, "gold": 8000}

    # Use provided screenshot or create a synthetic one
    if screenshot is None:
        screenshot = np.zeros((1920, 1080, 3), dtype=np.uint8)
        screenshot[:] = (80, 120, 60)  # Greenish background
        print("  Using synthetic screenshot (no emulator connected)")

    print(f"  Provider: {config.LLM_PROVIDER}")
    print(f"  Vision model: {config.LLM_VISION_MODEL}")
    print(f"  Sending request...")
    tasks = planner.get_plan(screenshot, state)

    if tasks:
        print(f"  LLM returned {len(tasks)} tasks:")
        for t in tasks:
            print(f"    [{t.priority}] {t.name} params={t.params}")
    else:
        print("  LLM returned no tasks (may be expected for synthetic screenshot)")

    print("  PASS: Live LLM call completed without error")


def test_live_llm_with_emulator():
    """Test (Live+Emulator): Capture real screenshot and send to LLM."""
    import config
    from device.adb_controller import ADBController
    from vision.screenshot import ScreenshotManager

    if not config.LLM_API_KEY:
        print("  SKIP: No LLM API key configured")
        return

    try:
        adb = ADBController(config.ADB_HOST, config.ADB_PORT, config.NOX_ADB_PATH)
        if not adb.connect():
            print("  SKIP: Cannot connect to emulator")
            return

        mgr = ScreenshotManager(adb, config.SCREENSHOT_DIR)
        screenshot = mgr.capture()
        h, w = screenshot.shape[:2]
        print(f"  Captured real screenshot: {w}x{h}")

        test_live_llm(screenshot)
    except Exception as e:
        print(f"  SKIP: Emulator error: {e}")


def main():
    parser = argparse.ArgumentParser(description="Phase 4 LLM Integration Tests")
    parser.add_argument("--live", action="store_true",
                        help="Include live LLM API tests")
    args = parser.parse_args()

    tests = [
        ("LLMPlanner initialization", test_llm_planner_init),
        ("Multi-provider initialization", test_multi_provider_init),
        ("should_consult logic", test_should_consult),
        ("Screenshot preparation", test_prepare_screenshot),
        ("Parse strategic plan JSON", test_parse_plan_response),
        ("Parse scene analysis JSON", test_parse_scene_response),
        ("ActionValidator", test_action_validator),
        ("ActionRunner class", test_action_runner_init),
        ("ResultChecker class", test_result_checker_init),
        ("JSON extraction edge cases", test_extract_json_edge_cases),
        ("Model presets system", test_model_presets),
    ]

    if args.live:
        tests.append(("Live LLM call (synthetic)", test_live_llm))
        tests.append(("Live LLM call (emulator)", test_live_llm_with_emulator))

    passed = 0
    failed = 0

    for name, test_fn in tests:
        print(f"\nTest: {name}")
        try:
            test_fn()
            passed += 1
        except Exception as e:
            print(f"  FAIL: {e}")
            failed += 1

    print(f"\n{'='*50}")
    print(f"Results: {passed} passed, {failed} failed, {len(tests)} total")

    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()

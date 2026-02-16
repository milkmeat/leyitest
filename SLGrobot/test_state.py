"""Phase 3 verification tests - State, persistence, task queue, and decision loop.

Tests:
1. GameState serialization (to_dict / from_dict round-trip)
2. StatePersistence save/load (JSON file)
3. TaskQueue operations (add, next, mark_done, mark_failed, retry)
4. StateTracker number parsing
5. RuleEngine task handling
6. AutoHandler action generation
7. Scene handlers instantiation
8. Full integration (state + persistence + task queue)
"""

import os
import sys
import json
import tempfile
import shutil

# ── Test 1: GameState serialization ──────────────────────────────────────────

def test_game_state_serialization():
    """Test GameState to_dict/from_dict round-trip."""
    from state.game_state import GameState, BuildingState, MarchState

    gs = GameState()
    gs.scene = "main_city"
    gs.resources = {"food": 50000, "wood": 32000, "stone": 15000, "gold": 8000}
    gs.buildings["castle"] = BuildingState(name="castle", level=12, upgrading=True, finish_time="2025-01-01T12:00:00")
    gs.buildings["barracks"] = BuildingState(name="barracks", level=8)
    gs.troops_marching.append(MarchState(target="node_123", action="gather", return_time="00:45:30"))
    gs.task_queue = ["upgrade_barracks", "collect_resources"]
    gs.last_actions = [{"action": {"type": "tap", "x": 100, "y": 200}}]
    gs.loop_count = 42

    # Serialize
    data = gs.to_dict()
    assert data["scene"] == "main_city"
    assert data["resources"]["food"] == 50000
    assert data["buildings"]["castle"]["level"] == 12
    assert data["buildings"]["castle"]["upgrading"] is True
    assert len(data["troops_marching"]) == 1
    assert data["troops_marching"][0]["action"] == "gather"
    assert data["loop_count"] == 42

    # Deserialize into a new GameState
    gs2 = GameState()
    gs2.from_dict(data)
    assert gs2.scene == "main_city"
    assert gs2.resources["food"] == 50000
    assert gs2.buildings["castle"].level == 12
    assert gs2.buildings["castle"].upgrading is True
    assert gs2.buildings["castle"].finish_time == "2025-01-01T12:00:00"
    assert gs2.buildings["barracks"].level == 8
    assert len(gs2.troops_marching) == 1
    assert gs2.troops_marching[0].action == "gather"
    assert gs2.loop_count == 42

    print("PASS: GameState serialization round-trip")


# ── Test 2: StatePersistence save/load ───────────────────────────────────────

def test_persistence():
    """Test save/load of GameState to JSON file."""
    from state.game_state import GameState, BuildingState
    from state.persistence import StatePersistence

    # Use temp directory
    tmpdir = tempfile.mkdtemp()
    filepath = os.path.join(tmpdir, "test_state.json")

    try:
        persistence = StatePersistence(filepath)

        # Load from non-existent file -> None
        assert persistence.load() is None

        # Save a state
        gs = GameState()
        gs.scene = "world_map"
        gs.resources = {"food": 12345, "wood": 6789}
        gs.buildings["farm"] = BuildingState(name="farm", level=5)
        gs.loop_count = 10

        persistence.save(gs)

        # File should exist
        assert os.path.exists(filepath)

        # Load back
        loaded = persistence.load()
        assert loaded is not None
        assert loaded["scene"] == "world_map"
        assert loaded["resources"]["food"] == 12345
        assert loaded["buildings"]["farm"]["level"] == 5
        assert loaded["loop_count"] == 10

        # Verify JSON is valid and human-readable
        with open(filepath, "r", encoding="utf-8") as f:
            raw = f.read()
        assert "world_map" in raw
        assert "12345" in raw

        # Save again (overwrite)
        gs.resources["food"] = 99999
        persistence.save(gs)
        loaded2 = persistence.load()
        assert loaded2["resources"]["food"] == 99999

        print("PASS: StatePersistence save/load")
    finally:
        shutil.rmtree(tmpdir)


# ── Test 3: TaskQueue operations ─────────────────────────────────────────────

def test_task_queue():
    """Test TaskQueue add, next, mark_done, mark_failed, retry logic."""
    from brain.task_queue import TaskQueue, Task

    tq = TaskQueue()
    assert tq.size() == 0
    assert not tq.has_pending()
    assert tq.next() is None

    # Add tasks with different priorities
    tq.add(Task(name="low_priority", priority=1))
    tq.add(Task(name="high_priority", priority=10))
    tq.add(Task(name="medium_priority", priority=5))

    assert tq.size() == 3
    assert tq.has_pending()
    assert tq.pending_count() == 3

    # next() should return highest priority first
    task = tq.next()
    assert task is not None
    assert task.name == "high_priority"
    assert task.status == "running"

    # Mark done
    tq.mark_done(task)
    assert task.status == "done"

    # Next should be medium
    task2 = tq.next()
    assert task2.name == "medium_priority"

    # Mark failed with retry
    tq.mark_failed(task2)
    assert task2.status == "pending"  # Should be re-queued
    assert task2.retry_count == 1

    # Can get it again
    task2_again = tq.next()
    assert task2_again.name == "medium_priority"

    # Fail it max_retries times
    for _ in range(task2_again.max_retries):
        tq.mark_failed(task2_again)

    assert task2_again.status == "failed"

    # Clear completed
    removed = tq.clear_completed()
    assert removed >= 1  # At least the done task

    # Status report
    status = tq.get_status()
    assert isinstance(status, list)

    print("PASS: TaskQueue operations")


# ── Test 4: StateTracker number parsing ──────────────────────────────────────

def test_number_parsing():
    """Test StateTracker._parse_number for various formats."""
    from state.state_tracker import StateTracker

    parse = StateTracker._parse_number

    # Plain numbers
    assert parse("12345") == 12345
    assert parse("0") == 0

    # Comma-separated
    assert parse("12,345") == 12345
    assert parse("1,234,567") == 1234567

    # Suffixed
    assert parse("500K") == 500_000
    assert parse("1.2M") == 1_200_000
    assert parse("2.5B") == 2_500_000_000
    assert parse("100k") == 100_000

    # With surrounding text
    assert parse("Food: 12,345") == 12345
    assert parse("Lv.12") == 12

    # Edge cases
    assert parse("") is None
    assert parse("abc") is None

    print("PASS: StateTracker number parsing")


# ── Test 5: RuleEngine task handling ─────────────────────────────────────────

def test_rule_engine():
    """Test RuleEngine can_handle and known tasks."""
    from brain.rule_engine import RuleEngine
    from brain.task_queue import Task
    from state.game_state import GameState

    # Create minimal mock dependencies
    class MockDetector:
        def locate(self, *args, **kwargs): return None
        def locate_all(self, *args, **kwargs): return []

    class MockMatcher:
        def match_one(self, *args, **kwargs): return None
        def match_all(self, *args, **kwargs): return []

    gs = GameState()
    engine = RuleEngine(MockDetector(), gs, "data/navigation_paths.json")

    # Known tasks should be handleable
    known = Task(name="collect_resources")
    assert engine.can_handle(known)

    unknown = Task(name="do_something_impossible")
    assert not engine.can_handle(unknown)

    # Plan should return a list (possibly empty without real screenshot)
    import numpy as np
    fake_screenshot = np.zeros((1920, 1080, 3), dtype=np.uint8)
    actions = engine.plan(known, fake_screenshot, gs)
    assert isinstance(actions, list)

    # Unknown task plan returns empty
    actions2 = engine.plan(unknown, fake_screenshot, gs)
    assert actions2 == []

    print("PASS: RuleEngine task handling")


# ── Test 6: AutoHandler action generation ────────────────────────────────────

def test_auto_handler():
    """Test AutoHandler returns valid action dicts."""
    from brain.auto_handler import AutoHandler
    from state.game_state import GameState

    class MockDetector:
        def locate(self, *args, **kwargs): return None
        def locate_all(self, *args, **kwargs): return []

    class MockMatcher:
        def match_one(self, *args, **kwargs): return None
        def match_all(self, *args, **kwargs): return []

    handler = AutoHandler(MockMatcher(), MockDetector())
    gs = GameState()
    gs.scene = "main_city"

    import numpy as np
    fake_screenshot = np.zeros((1920, 1080, 3), dtype=np.uint8)
    actions = handler.get_actions(fake_screenshot, gs)
    assert isinstance(actions, list)

    # With loading scene
    gs.scene = "loading"
    actions = handler.get_actions(fake_screenshot, gs)
    assert isinstance(actions, list)
    # Should suggest tapping center for loading
    if actions:
        assert actions[0]["type"] == "tap"
        assert "loading" in actions[0].get("reason", "")

    print("PASS: AutoHandler action generation")


# ── Test 7: Scene handlers instantiation ─────────────────────────────────────

def test_scene_handlers():
    """Test scene handlers can be instantiated and have correct interface."""
    from scene.handlers.main_city import MainCityHandler
    from scene.handlers.world_map import WorldMapHandler
    from scene.handlers.battle import BattleHandler
    from state.game_state import GameState

    class MockDetector:
        def locate(self, *args, **kwargs): return None
        def locate_all(self, *args, **kwargs): return []

    gs = GameState()
    detector = MockDetector()

    mc = MainCityHandler(detector, gs)
    wm = WorldMapHandler(detector, gs)
    bt = BattleHandler(detector, gs)

    import numpy as np
    fake = np.zeros((1920, 1080, 3), dtype=np.uint8)

    # extract_info should return dict
    mc_info = mc.extract_info(fake)
    assert isinstance(mc_info, dict)
    assert "resources" in mc_info
    assert "buttons" in mc_info

    wm_info = wm.extract_info(fake)
    assert isinstance(wm_info, dict)
    assert "resource_nodes" in wm_info

    bt_info = bt.extract_info(fake)
    assert isinstance(bt_info, dict)
    assert "result" in bt_info

    # get_available_actions should return list of strings
    mc_actions = mc.get_available_actions(fake)
    assert isinstance(mc_actions, list)
    assert "collect_resources" in mc_actions

    wm_actions = wm.get_available_actions(fake)
    assert isinstance(wm_actions, list)
    assert "navigate_main_city" in wm_actions

    bt_actions = bt.get_available_actions(fake)
    assert isinstance(bt_actions, list)

    print("PASS: Scene handlers instantiation")


# ── Test 8: Full integration ─────────────────────────────────────────────────

def test_integration():
    """Test full integration: state -> persistence -> task queue cycle."""
    from state.game_state import GameState, BuildingState
    from state.persistence import StatePersistence
    from brain.task_queue import TaskQueue, Task

    tmpdir = tempfile.mkdtemp()
    filepath = os.path.join(tmpdir, "integration_state.json")

    try:
        # 1. Create state and populate
        gs = GameState()
        gs.scene = "main_city"
        gs.resources = {"food": 10000, "wood": 5000, "stone": 3000, "gold": 1000}
        gs.buildings["castle"] = BuildingState(name="castle", level=5)

        # 2. Create task queue and add tasks
        tq = TaskQueue()
        tq.add(Task(name="collect_resources", priority=5))
        tq.add(Task(name="upgrade_building", priority=10, params={"building_name": "castle"}))

        # 3. Persist state
        persistence = StatePersistence(filepath)
        persistence.save(gs)

        # 4. Simulate restart - load from file
        gs2 = GameState()
        loaded = persistence.load()
        assert loaded is not None
        gs2.from_dict(loaded)

        # Verify loaded state
        assert gs2.scene == "main_city"
        assert gs2.resources["food"] == 10000
        assert gs2.buildings["castle"].level == 5

        # 5. Process task queue
        task = tq.next()
        assert task.name == "upgrade_building"  # Higher priority
        tq.mark_done(task)

        task2 = tq.next()
        assert task2.name == "collect_resources"
        tq.mark_done(task2)

        assert not tq.has_pending()

        # 6. Record an action
        gs2.record_action({"type": "tap", "x": 100, "y": 200, "reason": "test"})
        assert len(gs2.last_actions) == 1
        assert "timestamp" in gs2.last_actions[0]

        # 7. Save updated state
        gs2.loop_count = 5
        persistence.save(gs2)

        # 8. Verify summary for LLM
        summary = gs2.summary_for_llm()
        assert "main_city" in summary
        assert "food" in summary or "10000" in summary

        print("PASS: Full integration test")
    finally:
        shutil.rmtree(tmpdir)


# ── Run all tests ────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("Phase 3 Verification Tests")
    print("=" * 60)
    print()

    tests = [
        ("GameState serialization", test_game_state_serialization),
        ("StatePersistence save/load", test_persistence),
        ("TaskQueue operations", test_task_queue),
        ("StateTracker number parsing", test_number_parsing),
        ("RuleEngine task handling", test_rule_engine),
        ("AutoHandler actions", test_auto_handler),
        ("Scene handlers", test_scene_handlers),
        ("Full integration", test_integration),
    ]

    passed = 0
    failed = 0

    for name, test_fn in tests:
        try:
            test_fn()
            passed += 1
        except Exception as e:
            print(f"FAIL: {name} -- {e}")
            import traceback
            traceback.print_exc()
            failed += 1
        print()

    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed out of {len(tests)}")
    print("=" * 60)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

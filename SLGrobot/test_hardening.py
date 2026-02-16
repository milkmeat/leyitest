"""Phase 5 Hardening Tests - StuckRecovery, execute_with_retry, reconnect."""

import unittest
from unittest.mock import MagicMock, patch, call
import time


class TestStuckRecovery(unittest.TestCase):
    """Tests for brain.stuck_recovery.StuckRecovery."""

    def setUp(self):
        # Patch config before import so StuckRecovery reads our values
        self.config_patcher = patch.dict("sys.modules", {})
        import config
        config.STUCK_MAX_SAME_SCENE = 5
        config.SCREEN_WIDTH = 1080
        config.SCREEN_HEIGHT = 1920
        config.GAME_PACKAGE = ""

        from brain.stuck_recovery import StuckRecovery
        self.StuckRecovery = StuckRecovery

    def test_not_stuck_short_history(self):
        """Short history should never trigger stuck detection."""
        sr = self.StuckRecovery(max_same_scene=5)
        self.assertFalse(sr.check(["main", "main", "main"]))

    def test_not_stuck_varied_scenes(self):
        """Varied scenes should not trigger stuck detection."""
        sr = self.StuckRecovery(max_same_scene=5)
        history = ["main", "popup", "main", "loading", "main"]
        self.assertFalse(sr.check(history))

    def test_stuck_detected(self):
        """N identical scenes should trigger stuck detection."""
        sr = self.StuckRecovery(max_same_scene=5)
        history = ["main"] * 5
        self.assertTrue(sr.check(history))

    def test_stuck_detected_longer_history(self):
        """Stuck detected even with earlier varied scenes."""
        sr = self.StuckRecovery(max_same_scene=5)
        history = ["popup", "loading"] + ["main"] * 5
        self.assertTrue(sr.check(history))

    def test_not_stuck_one_different(self):
        """One different scene in the tail prevents stuck detection."""
        sr = self.StuckRecovery(max_same_scene=5)
        history = ["main", "main", "popup", "main", "main"]
        self.assertFalse(sr.check(history))

    def test_escalation_cycling(self):
        """Recovery should escalate through levels 1, 2, 3."""
        sr = self.StuckRecovery(max_same_scene=5)
        mock_adb = MagicMock()

        result1 = sr.recover(mock_adb)
        self.assertEqual(result1, "back")
        mock_adb.key_event.assert_called_with(4)

        result2 = sr.recover(mock_adb)
        self.assertEqual(result2, "center_tap")
        mock_adb.tap.assert_called_once_with(540, 960)

        result3 = sr.recover(mock_adb)
        self.assertEqual(result3, "restart_app")

    def test_escalation_stays_at_max(self):
        """After reaching max level, recovery stays at level 3."""
        sr = self.StuckRecovery(max_same_scene=5)
        mock_adb = MagicMock()

        sr.recover(mock_adb)  # level 1
        sr.recover(mock_adb)  # level 2
        sr.recover(mock_adb)  # level 3
        result = sr.recover(mock_adb)  # still level 3
        self.assertEqual(result, "restart_app")

    def test_reset(self):
        """reset() should bring escalation back to level 0."""
        sr = self.StuckRecovery(max_same_scene=5)
        mock_adb = MagicMock()

        sr.recover(mock_adb)  # level 1
        sr.recover(mock_adb)  # level 2
        sr.reset()

        result = sr.recover(mock_adb)  # back to level 1
        self.assertEqual(result, "back")

    def test_recovery_count(self):
        """recovery_count should track total recoveries."""
        sr = self.StuckRecovery(max_same_scene=5)
        mock_adb = MagicMock()
        self.assertEqual(sr.recovery_count, 0)

        sr.recover(mock_adb)
        self.assertEqual(sr.recovery_count, 1)

        sr.recover(mock_adb)
        self.assertEqual(sr.recovery_count, 2)

        sr.reset()
        # Reset does NOT reset the count
        self.assertEqual(sr.recovery_count, 2)

    def test_restart_app_with_package(self):
        """Level 3 with GAME_PACKAGE set should call force-stop and monkey."""
        import config
        config.GAME_PACKAGE = "com.example.game"

        sr = self.StuckRecovery(max_same_scene=5)
        mock_adb = MagicMock()

        sr.recover(mock_adb)  # level 1
        sr.recover(mock_adb)  # level 2
        sr.recover(mock_adb)  # level 3

        # Should have called _run_adb for force-stop and monkey
        force_stop_call = call(["shell", "am", "force-stop", "com.example.game"])
        monkey_call = call([
            "shell", "monkey", "-p", "com.example.game",
            "-c", "android.intent.category.LAUNCHER", "1"
        ])
        mock_adb._run_adb.assert_any_call(force_stop_call[1][0])
        mock_adb._run_adb.assert_any_call(monkey_call[1][0])

        config.GAME_PACKAGE = ""  # cleanup

    def test_restart_app_no_package_falls_back_to_home(self):
        """Level 3 without GAME_PACKAGE should press HOME key."""
        import config
        config.GAME_PACKAGE = ""

        sr = self.StuckRecovery(max_same_scene=5)
        mock_adb = MagicMock()

        sr.recover(mock_adb)  # level 1
        sr.recover(mock_adb)  # level 2
        sr.recover(mock_adb)  # level 3

        # HOME key (3) should have been called
        mock_adb.key_event.assert_any_call(3)


class TestActionRunnerRetry(unittest.TestCase):
    """Tests for executor.action_runner.ActionRunner.execute_with_retry."""

    def _make_runner(self):
        """Create an ActionRunner with mocked dependencies."""
        from executor.action_runner import ActionRunner
        runner = ActionRunner(
            adb=MagicMock(),
            input_actions=MagicMock(),
            element_detector=MagicMock(),
            grid_overlay=MagicMock(),
            screenshot_mgr=MagicMock(),
        )
        return runner

    def test_success_first_try(self):
        """Action succeeds on first attempt, no retry needed."""
        runner = self._make_runner()
        runner.execute = MagicMock(return_value=True)
        action = {"type": "tap", "x": 100, "y": 200}

        result = runner.execute_with_retry(action, max_retries=3, retry_delay=0)
        self.assertTrue(result)
        self.assertEqual(runner.execute.call_count, 1)

    def test_success_on_retry(self):
        """Action fails first, succeeds on second attempt."""
        runner = self._make_runner()
        runner.execute = MagicMock(side_effect=[False, True])
        action = {"type": "tap", "x": 100, "y": 200}

        result = runner.execute_with_retry(action, max_retries=3, retry_delay=0)
        self.assertTrue(result)
        self.assertEqual(runner.execute.call_count, 2)

    def test_exhausted_retries(self):
        """Action fails all retry attempts."""
        runner = self._make_runner()
        runner.execute = MagicMock(return_value=False)
        action = {"type": "tap", "x": 100, "y": 200}

        result = runner.execute_with_retry(action, max_retries=3, retry_delay=0)
        self.assertFalse(result)
        self.assertEqual(runner.execute.call_count, 3)

    def test_execute_sequence_with_retry(self):
        """execute_sequence with retry=True should use execute_with_retry."""
        runner = self._make_runner()
        runner.execute_with_retry = MagicMock(return_value=True)
        actions = [
            {"type": "tap", "x": 1, "y": 2},
            {"type": "tap", "x": 3, "y": 4},
        ]

        count = runner.execute_sequence(actions, retry=True, max_retries=2)
        self.assertEqual(count, 2)
        self.assertEqual(runner.execute_with_retry.call_count, 2)

    def test_execute_sequence_without_retry(self):
        """execute_sequence with retry=False uses regular execute."""
        runner = self._make_runner()
        runner.execute = MagicMock(return_value=True)
        actions = [
            {"type": "tap", "x": 1, "y": 2},
        ]

        count = runner.execute_sequence(actions, retry=False)
        self.assertEqual(count, 1)
        runner.execute.assert_called_once()


class TestADBReconnect(unittest.TestCase):
    """Tests for device.adb_controller.ADBController.reconnect."""

    def _make_controller(self):
        """Create an ADBController with a mocked connect method."""
        from device.adb_controller import ADBController
        controller = ADBController("127.0.0.1", 62001, "adb")
        return controller

    def test_success_first_try(self):
        """Reconnect succeeds on first attempt."""
        controller = self._make_controller()
        controller.connect = MagicMock(return_value=True)

        result = controller.reconnect(max_retries=3, base_delay=0.01)
        self.assertTrue(result)
        self.assertEqual(controller.connect.call_count, 1)

    def test_success_on_retry(self):
        """Reconnect fails first, succeeds on second attempt."""
        controller = self._make_controller()
        controller.connect = MagicMock(side_effect=[False, True])

        result = controller.reconnect(max_retries=3, base_delay=0.01)
        self.assertTrue(result)
        self.assertEqual(controller.connect.call_count, 2)

    def test_all_retries_fail(self):
        """Reconnect fails all attempts."""
        controller = self._make_controller()
        controller.connect = MagicMock(return_value=False)

        result = controller.reconnect(max_retries=3, base_delay=0.01)
        self.assertFalse(result)
        self.assertEqual(controller.connect.call_count, 3)

    def test_exponential_backoff_delay(self):
        """Verify that delays increase exponentially."""
        controller = self._make_controller()
        controller.connect = MagicMock(return_value=False)

        delays = []
        original_sleep = time.sleep

        def mock_sleep(seconds):
            delays.append(seconds)
            # Don't actually sleep in tests

        with patch("time.sleep", side_effect=mock_sleep):
            # Re-import to get patched time.sleep in module
            # Instead, patch at the module level
            pass

        # Use direct patching on the module where sleep is called
        with patch("device.adb_controller.time.sleep", side_effect=mock_sleep):
            controller.reconnect(max_retries=3, base_delay=1.0)

        self.assertEqual(len(delays), 3)
        self.assertAlmostEqual(delays[0], 1.0)
        self.assertAlmostEqual(delays[1], 2.0)
        self.assertAlmostEqual(delays[2], 4.0)


if __name__ == "__main__":
    unittest.main()

"""Stuck Recovery - Detect stuck loops and escalate recovery actions."""

import logging

import config

logger = logging.getLogger(__name__)


class StuckRecovery:
    """Detect when the bot is stuck on the same scene and attempt recovery.

    Escalation levels:
      1. Press BACK key
      2. Tap screen center
      3. Restart the game app (force-stop + monkey launcher)
    """

    MAX_LEVEL = 3

    def __init__(self, adb=None, max_same_scene: int = None,
                 game_package: str | None = None) -> None:
        self.adb = adb
        self.max_same_scene = max_same_scene or config.STUCK_MAX_SAME_SCENE
        self._game_package = game_package
        self._level = 0
        self._recovery_count = 0

    def check(self, scene_history: list[str]) -> bool:
        """Return True if the last N scenes are all identical (stuck).

        Args:
            scene_history: List of recent scene classification strings.

        Returns:
            True if stuck detected.
        """
        if len(scene_history) < self.max_same_scene:
            return False
        tail = scene_history[-self.max_same_scene:]
        return len(set(tail)) == 1

    def recover(self, adb=None) -> str:
        """Execute an escalating recovery action.

        Args:
            adb: ADBController instance (falls back to self.adb).

        Returns:
            Description of the recovery action taken.
        """
        controller = adb or self.adb
        self._level = min(self._level + 1, self.MAX_LEVEL)
        self._recovery_count += 1

        if self._level == 1:
            logger.warning("Stuck recovery level 1: tapping blank area")
            if controller:
                controller.tap(500, 100)
            return "tap_blank"

        if self._level == 2:
            logger.warning("Stuck recovery level 2: tapping screen center")
            if controller:
                cx = config.SCREEN_WIDTH // 2
                cy = config.SCREEN_HEIGHT // 2
                controller.tap(cx, cy)
            return "center_tap"

        # Level 3: restart app
        logger.warning("Stuck recovery level 3: restarting app")
        self._restart_app(controller)
        return "restart_app"

    def _restart_app(self, adb) -> None:
        """Force-stop and relaunch the game package."""
        package = self._game_package or getattr(config, "GAME_PACKAGE", "")
        if not package or not adb:
            logger.warning("No GAME_PACKAGE configured, falling back to HOME key")
            if adb:
                adb.key_event(3)  # KEYCODE_HOME
            return

        try:
            adb._run_adb(["shell", "am", "force-stop", package])
            logger.info(f"Force-stopped {package}")
        except Exception as e:
            logger.error(f"Force-stop failed: {e}")

        import time
        time.sleep(2)

        try:
            adb._run_adb([
                "shell", "monkey", "-p", package,
                "-c", "android.intent.category.LAUNCHER", "1"
            ])
            logger.info(f"Relaunched {package}")
        except Exception as e:
            logger.error(f"Relaunch failed: {e}")

    def reset(self) -> None:
        """Reset escalation level (call when scene changes)."""
        self._level = 0

    @property
    def recovery_count(self) -> int:
        """Total number of recovery actions taken."""
        return self._recovery_count

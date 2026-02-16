"""ADB Controller - Low-level ADB operations for Nox emulator."""

import subprocess
import time
import numpy as np
import cv2
import logging

logger = logging.getLogger(__name__)


class ADBController:
    """Low-level ADB operations: connect, screenshot, tap, swipe."""

    def __init__(self, host: str, port: int, adb_path: str = "adb") -> None:
        self.host = host
        self.port = port
        self.adb_path = adb_path
        self.device_serial = f"{host}:{port}"
        self._connected = False

    def _run_adb(self, args: list[str], timeout: int = 10) -> subprocess.CompletedProcess:
        """Run an ADB command and return the result."""
        cmd = [self.adb_path, "-s", self.device_serial] + args
        try:
            result = subprocess.run(
                cmd, capture_output=True, timeout=timeout
            )
            return result
        except subprocess.TimeoutExpired:
            logger.error(f"ADB command timed out: {' '.join(cmd)}")
            raise
        except FileNotFoundError:
            logger.error(f"ADB executable not found: {self.adb_path}")
            raise

    def connect(self) -> bool:
        """Establish ADB connection. Returns True on success."""
        try:
            result = self._run_adb(["connect", self.device_serial])
            output = result.stdout.decode("utf-8", errors="replace").strip()
            if "connected" in output or "already" in output:
                self._connected = True
                logger.info(f"Connected to emulator at {self.device_serial}")
                return True
            else:
                logger.error(f"Failed to connect: {output}")
                return False
        except Exception as e:
            logger.error(f"Connection error: {e}")
            return False

    def screenshot(self) -> np.ndarray:
        """Capture screenshot, return as BGR numpy array (OpenCV format).

        Uses 'adb exec-out screencap -p' for fast raw PNG capture.
        """
        result = self._run_adb(["exec-out", "screencap", "-p"], timeout=15)
        if result.returncode != 0:
            stderr = result.stderr.decode("utf-8", errors="replace")
            raise RuntimeError(f"Screenshot failed: {stderr}")

        png_data = result.stdout
        if not png_data:
            raise RuntimeError("Screenshot returned empty data")

        # Decode PNG bytes to numpy array
        img_array = np.frombuffer(png_data, dtype=np.uint8)
        image = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        if image is None:
            raise RuntimeError("Failed to decode screenshot image")

        return image

    def tap(self, x: int, y: int) -> None:
        """Tap at pixel coordinate (x, y)."""
        logger.debug(f"Tap at ({x}, {y})")
        result = self._run_adb(["shell", "input", "tap", str(x), str(y)])
        if result.returncode != 0:
            stderr = result.stderr.decode("utf-8", errors="replace")
            logger.error(f"Tap failed: {stderr}")

    def swipe(self, x1: int, y1: int, x2: int, y2: int, duration_ms: int = 300) -> None:
        """Swipe from (x1,y1) to (x2,y2)."""
        logger.debug(f"Swipe from ({x1},{y1}) to ({x2},{y2}) duration={duration_ms}ms")
        result = self._run_adb([
            "shell", "input", "swipe",
            str(x1), str(y1), str(x2), str(y2), str(duration_ms)
        ])
        if result.returncode != 0:
            stderr = result.stderr.decode("utf-8", errors="replace")
            logger.error(f"Swipe failed: {stderr}")

    def key_event(self, keycode: int) -> None:
        """Send a key event (e.g., BACK=4, HOME=3)."""
        logger.debug(f"Key event: {keycode}")
        self._run_adb(["shell", "input", "keyevent", str(keycode)])

    def is_connected(self) -> bool:
        """Check if ADB connection is alive."""
        try:
            result = self._run_adb(["shell", "echo", "ping"], timeout=5)
            alive = result.returncode == 0
            self._connected = alive
            return alive
        except Exception:
            self._connected = False
            return False

    def reconnect(self, max_retries: int = 3, base_delay: float = 2.0) -> bool:
        """Reconnect to the emulator with exponential backoff.

        Args:
            max_retries: Maximum number of reconnection attempts.
            base_delay: Base delay in seconds (doubles each attempt).

        Returns:
            True if reconnection succeeded, False after all retries exhausted.
        """
        for attempt in range(1, max_retries + 1):
            delay = base_delay * (2 ** (attempt - 1))
            logger.warning(
                f"ADB reconnect attempt {attempt}/{max_retries} "
                f"(delay {delay:.1f}s)"
            )
            time.sleep(delay)
            if self.connect():
                logger.info(f"ADB reconnected on attempt {attempt}")
                return True
        logger.error(f"ADB reconnect failed after {max_retries} attempts")
        return False

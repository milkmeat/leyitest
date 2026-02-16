"""Phase 1 Test Script - Verify ADB connection, screenshot, and tap."""

import sys
import time

# Initialize logging first
from utils.logger import GameLogger
game_logger = GameLogger("logs")

import config
from device.adb_controller import ADBController
from device.input_actions import InputActions
from vision.screenshot import ScreenshotManager
from utils.image_utils import crop_region, resize, to_base64, save_debug_image


def test_adb_connection():
    """Test 1: ADB connection to Nox emulator."""
    print("\n" + "=" * 50)
    print("Test 1: ADB Connection")
    print("=" * 50)

    adb = ADBController(config.ADB_HOST, config.ADB_PORT, config.NOX_ADB_PATH)
    success = adb.connect()
    print(f"  Connect result: {success}")
    assert success, "Failed to connect to emulator"

    alive = adb.is_connected()
    print(f"  Is connected: {alive}")
    assert alive, "Connection is not alive"

    print("  PASSED")
    return adb


def test_screenshot(adb: ADBController):
    """Test 2: Screenshot capture."""
    print("\n" + "=" * 50)
    print("Test 2: Screenshot Capture")
    print("=" * 50)

    image = adb.screenshot()
    h, w, c = image.shape
    print(f"  Screenshot shape: ({h}, {w}, {c})")
    assert h > 0 and w > 0, "Screenshot has zero dimensions"
    assert c == 3, "Screenshot should be 3-channel BGR"
    print(f"  Resolution: {w}x{h}")

    print("  PASSED")
    return image


def test_screenshot_manager(adb: ADBController):
    """Test 3: Screenshot manager (capture + save)."""
    print("\n" + "=" * 50)
    print("Test 3: Screenshot Manager")
    print("=" * 50)

    mgr = ScreenshotManager(adb, config.SCREENSHOT_DIR)
    image, filepath = mgr.capture_and_save("test")
    print(f"  Saved to: {filepath}")

    import os
    assert os.path.exists(filepath), f"Screenshot file not found: {filepath}"
    file_size = os.path.getsize(filepath)
    print(f"  File size: {file_size} bytes")
    assert file_size > 0, "Screenshot file is empty"

    # Test history
    recent = mgr.get_recent(1)
    assert len(recent) == 1, "History should have 1 screenshot"
    print(f"  History length: {len(recent)}")

    print("  PASSED")
    return image


def test_tap(adb: ADBController):
    """Test 4: Tap execution."""
    print("\n" + "=" * 50)
    print("Test 4: Tap Execution")
    print("=" * 50)

    cx = config.SCREEN_WIDTH // 2
    cy = config.SCREEN_HEIGHT // 2
    print(f"  Tapping at center ({cx}, {cy})...")
    adb.tap(cx, cy)
    print("  Tap sent (check emulator screen for visual feedback)")

    print("  PASSED")


def test_input_actions(adb: ADBController):
    """Test 5: Input actions (swipe, long press)."""
    print("\n" + "=" * 50)
    print("Test 5: Input Actions")
    print("=" * 50)

    actions = InputActions(adb)

    print("  Testing swipe...")
    adb.swipe(640, 500, 640, 200, 300)
    time.sleep(0.5)

    print("  Testing tap_center...")
    actions.tap_center()
    time.sleep(0.5)

    print("  PASSED")


def test_image_utils(image):
    """Test 6: Image utility functions."""
    print("\n" + "=" * 50)
    print("Test 6: Image Utilities")
    print("=" * 50)

    # Crop
    h, w = image.shape[:2]
    bbox = (0, 0, w // 2, h // 2)
    cropped = crop_region(image, bbox)
    print(f"  Cropped shape: {cropped.shape}")
    assert cropped.shape[0] == h // 2 and cropped.shape[1] == w // 2

    # Resize
    resized = resize(image, 320, 180)
    print(f"  Resized shape: {resized.shape}")
    assert resized.shape == (180, 320, 3)

    # Base64
    b64 = to_base64(image)
    print(f"  Base64 length: {len(b64)} chars")
    assert len(b64) > 0

    # Debug save
    path = save_debug_image(image, "test_utils")
    print(f"  Debug image saved to: {path}")

    print("  PASSED")


def main():
    print("SLGrobot Phase 1 - Test Suite")
    print(f"Target: {config.ADB_HOST}:{config.ADB_PORT}")
    print(f"ADB path: {config.NOX_ADB_PATH}")

    try:
        adb = test_adb_connection()
        image = test_screenshot(adb)
        test_screenshot_manager(adb)
        test_tap(adb)
        test_input_actions(adb)
        test_image_utils(image)

        print("\n" + "=" * 50)
        print("ALL TESTS PASSED")
        print("=" * 50)
    except AssertionError as e:
        print(f"\nTEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

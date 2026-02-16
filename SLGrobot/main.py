"""SLGrobot - Main Loop Entry Point (Phase 1: Infrastructure)

Minimal version: connect to emulator, capture screenshot, tap, loop.
"""

import sys
import time
import logging

import config
from device.adb_controller import ADBController
from device.input_actions import InputActions
from vision.screenshot import ScreenshotManager
from utils.logger import GameLogger

logger = logging.getLogger(__name__)


def main():
    # Initialize logging
    game_logger = GameLogger(config.LOG_DIR)

    logger.info("=" * 50)
    logger.info("SLGrobot Phase 1 - Infrastructure")
    logger.info("=" * 50)

    # 1. Initialize ADB connection
    adb = ADBController(config.ADB_HOST, config.ADB_PORT, config.NOX_ADB_PATH)
    if not adb.connect():
        logger.error("Failed to connect to emulator. Exiting.")
        sys.exit(1)

    logger.info("Connected to emulator successfully.")

    # 2. Initialize components
    input_actions = InputActions(adb)
    screenshot_mgr = ScreenshotManager(adb, config.SCREENSHOT_DIR)

    # 3. Capture and save initial screenshot
    image, filepath = screenshot_mgr.capture_and_save("startup")
    h, w, c = image.shape
    logger.info(f"Screenshot captured: {w}x{h}x{c}, saved to {filepath}")

    # 4. Main loop
    logger.info(f"Starting main loop (interval={config.LOOP_INTERVAL}s, Ctrl+C to stop)")
    loop_count = 0

    try:
        while True:
            loop_count += 1
            logger.info(f"--- Loop #{loop_count} ---")

            # Capture screenshot
            image = screenshot_mgr.capture()
            h, w, c = image.shape
            logger.info(f"Screenshot: {w}x{h}")

            # Save every 10th screenshot for debugging
            if loop_count % 10 == 1:
                screenshot_mgr.save(image, f"loop_{loop_count}")

            # Placeholder: tap screen center (will be replaced by real logic)
            if loop_count == 1:
                logger.info("Performing test tap at screen center...")
                input_actions.tap_center()

            time.sleep(config.LOOP_INTERVAL)

    except KeyboardInterrupt:
        logger.info("Stopped by user (Ctrl+C)")
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
    finally:
        logger.info(f"Exiting after {loop_count} loops.")


if __name__ == "__main__":
    main()

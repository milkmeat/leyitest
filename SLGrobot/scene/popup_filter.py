"""Popup Filter - Detect and auto-close popup dialogs."""

import time
import logging

import numpy as np

from vision.template_matcher import TemplateMatcher
from vision.ocr_locator import OCRLocator
from device.adb_controller import ADBController

logger = logging.getLogger(__name__)


class PopupFilter:
    """Detect and auto-close popup dialogs before they interfere with processing.

    Strategy:
    1. Detect popup via template match (close/X button) or overlay analysis
    2. Find close button position
    3. Tap to close
    """

    # Common close button template names to search for
    CLOSE_TEMPLATES = [
        "buttons/close",
        "buttons/close_x",
        "buttons/x",
        "buttons/cancel",
        "buttons/confirm",
        "buttons/ok",
    ]

    # OCR text patterns that dismiss popups (e.g. battle result screen)
    CLOSE_TEXTS = [
        "返回领地", "领取", "返回", "关闭", "确定", "确认",
    ]

    def __init__(self, template_matcher: TemplateMatcher,
                 adb: ADBController,
                 ocr: OCRLocator | None = None) -> None:
        self.template_matcher = template_matcher
        self.adb = adb
        self.ocr = ocr

    def is_popup(self, screenshot: np.ndarray) -> bool:
        """Check if current screen has a popup overlay.

        Detection methods:
        1. Template match for close/X buttons
        2. Border darkness analysis (popup darkens background)
        """
        # Check for close button templates
        for name in self.CLOSE_TEMPLATES:
            match = self.template_matcher.match_one(screenshot, name)
            if match is not None:
                return True

        # Check border darkness pattern
        return self._has_dark_overlay(screenshot)

    def handle(self, screenshot: np.ndarray) -> bool:
        """Detect and close popup. Returns True if popup was found and closed.

        Strategy (ordered by reliability):
        1. OCR text search for dismiss buttons (most reliable — finds actual
           text buttons like "返回领地", "确定", "关闭")
        2. Template match for close/X button images
        3. Search all button templates in the popup area
        4. Fallback: tap outside the popup area (top-left corner)
        """
        # Strategy 1: OCR text search for dismiss buttons (e.g. "返回领地")
        # Tried first because template matching can false-positive on
        # non-close elements (e.g. ">" chevron arrows).
        if self.ocr is not None:
            all_text = self.ocr.find_all_text(screenshot)
            for close_text in self.CLOSE_TEXTS:
                for r in all_text:
                    if close_text in r.text:
                        cx, cy = r.center
                        logger.info(
                            f"Popup: tapping OCR text '{close_text}' "
                            f"at ({cx}, {cy})"
                        )
                        self.adb.tap(cx, cy)
                        time.sleep(0.5)
                        return True

        # Strategy 2: Find close button template (with position validation)
        h, w = screenshot.shape[:2]
        for name in self.CLOSE_TEMPLATES:
            match = self.template_matcher.match_one(screenshot, name)
            if match is not None:
                # Close/X buttons are in the top-right corner of popups.
                # Reject matches outside the top 35% / right 55% of screen
                # to avoid false positives on game UI elements.
                if "close" in name or "x" in name:
                    if match.y > h * 0.35 or match.x < w * 0.45:
                        logger.debug(
                            f"Popup: rejected '{name}' at ({match.x}, {match.y}) — "
                            f"outside expected close button region"
                        )
                        continue
                logger.info(f"Popup: tapping close button '{name}' at ({match.x}, {match.y})")
                self.adb.tap(match.x, match.y)
                time.sleep(0.5)
                return True

        # Strategy 3: Search all button templates for anything in the popup area
        all_buttons = self.template_matcher.match_all(screenshot, "buttons")
        for match in all_buttons:
            # Prefer buttons in the upper-right quadrant of popup (typical X location)
            if match.x > w // 3 and match.y < 2 * h // 3:
                logger.info(f"Popup: tapping button '{match.template_name}' at ({match.x}, {match.y})")
                self.adb.tap(match.x, match.y)
                time.sleep(0.5)
                return True

        # Strategy 4: If we detected a dark overlay but found no buttons,
        # try tapping outside the popup area
        if self._has_dark_overlay(screenshot):
            # Tap in the dark border area (top-left) to dismiss
            tap_x, tap_y = w // 20, h // 20
            logger.info(f"Popup: tapping outside popup at ({tap_x}, {tap_y})")
            self.adb.tap(tap_x, tap_y)
            time.sleep(0.5)
            return True

        return False

    def _has_dark_overlay(self, screenshot: np.ndarray) -> bool:
        """Check if screenshot has the dark border pattern typical of popups."""
        import cv2
        h, w = screenshot.shape[:2]
        gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)

        # Sample border regions
        border_top = gray[0:h//10, :].mean()
        border_bottom = gray[9*h//10:, :].mean()
        border_left = gray[:, 0:w//10].mean()
        border_right = gray[:, 9*w//10:].mean()
        border_mean = (border_top + border_bottom + border_left + border_right) / 4

        # Sample center
        center_mean = gray[h//4:3*h//4, w//4:3*w//4].mean()

        # Popup pattern: dark borders, brighter center
        return center_mean > 50 and border_mean < center_mean * 0.5

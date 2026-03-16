"""Popup Detector — detect semi-transparent dark overlay indicating a popup dialog.

Uses border vs center brightness comparison to detect the characteristic
darkened background that appears behind popup dialogs in SLG games.
When detected, finds the popup bounds by locating the bright content area.
"""

import logging

import cv2
import numpy as np

logger = logging.getLogger(__name__)


class PopupDetector:
    """Detect popup overlay by semi-transparent dark mask analysis."""

    # Border darkness ratio: border_mean must be < center_mean * this value
    DARKNESS_RATIO = 0.5
    # Minimum center brightness to consider (avoids false positives on dark screens)
    MIN_CENTER_BRIGHTNESS = 50
    # Threshold for bright area extraction when finding popup bounds
    BRIGHT_THRESHOLD = 60
    # Minimum popup area as fraction of screen area
    MIN_POPUP_AREA_RATIO = 0.05

    def __init__(self, darkness_ratio: float = 0.0) -> None:
        """Initialize PopupDetector.

        Args:
            darkness_ratio: Per-game override for DARKNESS_RATIO.
                            0.0 means use the class default (0.5).
        """
        if darkness_ratio > 0:
            self.darkness_ratio = darkness_ratio
        else:
            self.darkness_ratio = self.DARKNESS_RATIO

    def detect(self, screenshot: np.ndarray) -> tuple[int, int, int, int] | None:
        """Detect popup overlay and return its bounds.

        Args:
            screenshot: BGR numpy array (1080x1920).

        Returns:
            (x1, y1, x2, y2) bounding rect of the popup content area,
            or None if no popup detected.
        """
        h, w = screenshot.shape[:2]
        gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)

        # Compute border strip means (10% on each edge)
        border_top = float(gray[0:h // 10, :].mean())
        border_bottom = float(gray[9 * h // 10:, :].mean())
        border_left = float(gray[:, 0:w // 10].mean())
        border_right = float(gray[:, 9 * w // 10:].mean())
        border_mean = (border_top + border_bottom + border_left + border_right) / 4

        # Compute center region mean (center 50%)
        center_region = gray[h // 4:3 * h // 4, w // 4:3 * w // 4]
        center_mean = float(center_region.mean())

        # Check popup condition
        if center_mean <= self.MIN_CENTER_BRIGHTNESS:
            return None
        if border_mean >= center_mean * self.darkness_ratio:
            return None

        logger.debug(
            f"Popup detected: border_mean={border_mean:.1f}, "
            f"center_mean={center_mean:.1f}"
        )

        # Find popup bounds: threshold bright area, find largest component
        _, bright_mask = cv2.threshold(
            gray, int(self.BRIGHT_THRESHOLD), 255, cv2.THRESH_BINARY
        )

        # Morphology to clean up noise
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 15))
        bright_mask = cv2.morphologyEx(bright_mask, cv2.MORPH_CLOSE, kernel)
        bright_mask = cv2.morphologyEx(bright_mask, cv2.MORPH_OPEN, kernel)

        contours, _ = cv2.findContours(
            bright_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        if not contours:
            # Popup detected but can't find bounds — return center estimate
            return (w // 6, h // 6, 5 * w // 6, 5 * h // 6)

        # Find largest contour that's big enough to be a popup
        min_area = h * w * self.MIN_POPUP_AREA_RATIO
        best = None
        best_area = 0
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > best_area and area >= min_area:
                best_area = area
                best = contour

        if best is None:
            return (w // 6, h // 6, 5 * w // 6, 5 * h // 6)

        x, y, bw, bh = cv2.boundingRect(best)
        logger.debug(f"Popup bounds: ({x}, {y}, {x + bw}, {y + bh})")
        return (x, y, x + bw, y + bh)

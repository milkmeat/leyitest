"""Indicator Detector — detect red dots and green check marks.

Red dots indicate unread notifications or available actions.
Green checks indicate completed tasks or claimable rewards.
Both are detected by HSV color filtering + contour shape analysis.
"""

import logging
from dataclasses import dataclass

import cv2
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class IndicatorElement:
    """A detected indicator (red dot or green check)."""
    type: str                   # "red_dot" | "green_check"
    pos: tuple[int, int]        # center (cx, cy)


class IndicatorDetector:
    """Detect red dots and green check marks by color + shape."""

    # Red dot parameters
    RED_MIN_AREA = 50
    RED_MAX_AREA = 800
    RED_MIN_CIRCULARITY = 0.6

    # Green check parameters
    GREEN_MIN_AREA = 100
    GREEN_MAX_AREA = 2000
    GREEN_MAX_CIRCULARITY = 0.7  # checks are non-circular

    def detect(self, screenshot: np.ndarray) -> list[IndicatorElement]:
        """Detect all red dots and green checks in screenshot.

        Args:
            screenshot: BGR numpy array.

        Returns:
            List of IndicatorElement with type and position.
        """
        hsv = cv2.cvtColor(screenshot, cv2.COLOR_BGR2HSV)
        results: list[IndicatorElement] = []

        results.extend(self._detect_red_dots(hsv))
        results.extend(self._detect_green_checks(hsv))

        logger.debug(
            f"Indicators detected: {len(results)} "
            f"({sum(1 for r in results if r.type == 'red_dot')} red dots, "
            f"{sum(1 for r in results if r.type == 'green_check')} green checks)"
        )
        return results

    def _detect_red_dots(self, hsv: np.ndarray) -> list[IndicatorElement]:
        """Detect small red circular dots."""
        # Red wraps around in HSV: low range (0-10) and high range (170-180)
        red_lo = cv2.inRange(hsv, (0, 100, 100), (10, 255, 255))
        red_hi = cv2.inRange(hsv, (170, 100, 100), (180, 255, 255))
        red_mask = cv2.bitwise_or(red_lo, red_hi)

        # Small morphology to clean noise
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        red_mask = cv2.morphologyEx(red_mask, cv2.MORPH_CLOSE, kernel)

        contours, _ = cv2.findContours(
            red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        results = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area < self.RED_MIN_AREA or area > self.RED_MAX_AREA:
                continue

            # Circularity = 4π·area / perimeter²
            perimeter = cv2.arcLength(contour, True)
            if perimeter == 0:
                continue
            circularity = 4 * 3.14159 * area / (perimeter * perimeter)
            if circularity < self.RED_MIN_CIRCULARITY:
                continue

            M = cv2.moments(contour)
            if M["m00"] == 0:
                continue
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            results.append(IndicatorElement(type="red_dot", pos=(cx, cy)))

        return results

    def _detect_green_checks(self, hsv: np.ndarray) -> list[IndicatorElement]:
        """Detect small green check marks (non-circular, small area)."""
        green_mask = cv2.inRange(hsv, (35, 80, 80), (85, 255, 255))

        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        green_mask = cv2.morphologyEx(green_mask, cv2.MORPH_CLOSE, kernel)

        contours, _ = cv2.findContours(
            green_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        results = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area < self.GREEN_MIN_AREA or area > self.GREEN_MAX_AREA:
                continue

            # Check marks should NOT be highly circular
            perimeter = cv2.arcLength(contour, True)
            if perimeter == 0:
                continue
            circularity = 4 * 3.14159 * area / (perimeter * perimeter)
            if circularity > self.GREEN_MAX_CIRCULARITY:
                continue  # Too circular — likely a green button, not a check

            M = cv2.moments(contour)
            if M["m00"] == 0:
                continue
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            results.append(IndicatorElement(type="green_check", pos=(cx, cy)))

        return results

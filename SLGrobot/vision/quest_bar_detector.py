"""Quest Bar Detector - Detect quest bar elements on main city screen.

Detects:
- Scroll icon (task_scroll template) in bottom 82%-92% of screen
- Red badge on scroll icon (reward available)
- Current quest text via OCR (right of scroll icon)
- Green check mark on quest text (quest completed)
- Tutorial finger icon (guided action)
"""

import logging
from dataclasses import dataclass

import cv2
import numpy as np

from .template_matcher import TemplateMatcher
from .ocr_locator import OCRLocator

logger = logging.getLogger(__name__)


@dataclass
class QuestBarInfo:
    """Detection result for the quest bar."""
    visible: bool = False
    scroll_icon_pos: tuple[int, int] | None = None
    scroll_icon_bbox: tuple[int, int, int, int] | None = None
    has_red_badge: bool = False
    current_quest_text: str = ""
    current_quest_bbox: tuple[int, int, int, int] | None = None
    has_green_check: bool = False
    has_tutorial_finger: bool = False
    tutorial_finger_pos: tuple[int, int] | None = None


class QuestBarDetector:
    """Detect quest bar elements on main city screen.

    The quest bar sits at the bottom of the main city screen (~82%-92% of
    screen height). It contains a scroll icon on the left, quest text in
    the middle, and possibly a green check or red badge indicator.
    """

    # Screen Y range for valid scroll icon position (fraction of height)
    SCROLL_Y_MIN = 0.82
    SCROLL_Y_MAX = 0.92

    # HSV thresholds for red badge detection
    RED_H_RANGES = [(0, 10), (170, 180)]
    RED_S_MIN = 120
    RED_V_MIN = 150
    RED_PIXEL_THRESHOLD = 50

    # HSV thresholds for green check detection
    # H_MIN raised from 35→50 and S_MIN from 80→100 to exclude
    # tutorial finger skin tones (yellow/orange, H~25-50, low S).
    GREEN_H_MIN = 50
    GREEN_H_MAX = 85
    GREEN_S_MIN = 100
    GREEN_V_MIN = 100
    GREEN_PIXEL_THRESHOLD = 50

    def __init__(self, template_matcher: TemplateMatcher,
                 ocr_locator: OCRLocator) -> None:
        self.template_matcher = template_matcher
        self.ocr = ocr_locator

    def detect(self, screenshot: np.ndarray) -> QuestBarInfo:
        """Detect quest bar elements in the screenshot.

        Steps:
        1. Template match icons/task_scroll to locate scroll icon
        2. Validate scroll Y position is in expected range
        3. Check for red badge in scroll icon's upper-right quadrant
        4. OCR the region right of scroll icon for quest text
        5. Check for green check mark right of quest text
        6. Check for tutorial finger icon

        Args:
            screenshot: BGR numpy array of current game screen.

        Returns:
            QuestBarInfo with detection results.
        """
        info = QuestBarInfo()
        h, w = screenshot.shape[:2]

        # 1. Find scroll icon
        match = self.template_matcher.match_one(screenshot, "icons/task_scroll")
        if match is None:
            logger.debug("Quest bar: scroll icon not found")
            return info

        # 2. Validate Y position
        y_frac = match.y / h
        if not (self.SCROLL_Y_MIN <= y_frac <= self.SCROLL_Y_MAX):
            logger.debug(
                f"Quest bar: scroll icon at y={match.y} ({y_frac:.2f}) "
                f"outside expected range [{self.SCROLL_Y_MIN}-{self.SCROLL_Y_MAX}]"
            )
            return info

        info.visible = True
        info.scroll_icon_pos = (match.x, match.y)
        info.scroll_icon_bbox = match.bbox

        # 3. Red badge detection (upper-right quadrant of scroll icon bbox)
        info.has_red_badge = self._detect_red_badge(screenshot, match.bbox)

        # 4. OCR quest text (region right of scroll icon)
        self._detect_quest_text(screenshot, match, info)

        # 5. Green check detection (right of quest text bbox)
        if info.current_quest_bbox is not None:
            info.has_green_check = self._detect_green_check(
                screenshot, info.current_quest_bbox
            )

        # 6. Tutorial finger icon
        self._detect_tutorial_finger(screenshot, info)

        logger.debug(
            f"Quest bar: visible={info.visible}, text='{info.current_quest_text}', "
            f"red_badge={info.has_red_badge}, green_check={info.has_green_check}, "
            f"finger={info.has_tutorial_finger}"
        )

        return info

    def _detect_red_badge(self, screenshot: np.ndarray,
                          scroll_bbox: tuple[int, int, int, int]) -> bool:
        """Check for red badge in the upper-right quadrant of scroll icon.

        Uses HSV color analysis to detect red pixels (H:0-10 or 170-180,
        S>120, V>150). Returns True if pixel count exceeds threshold.
        """
        x1, y1, x2, y2 = scroll_bbox
        # Upper-right quadrant
        mid_x = (x1 + x2) // 2
        mid_y = (y1 + y2) // 2
        region = screenshot[y1:mid_y, mid_x:x2]

        if region.size == 0:
            return False

        hsv = cv2.cvtColor(region, cv2.COLOR_BGR2HSV)
        red_count = 0

        for h_min, h_max in self.RED_H_RANGES:
            mask = cv2.inRange(
                hsv,
                np.array([h_min, self.RED_S_MIN, self.RED_V_MIN]),
                np.array([h_max, 255, 255])
            )
            red_count += cv2.countNonZero(mask)

        if red_count >= self.RED_PIXEL_THRESHOLD:
            logger.debug(f"Quest bar: red badge detected ({red_count} pixels)")
            return True

        return False

    def _detect_quest_text(self, screenshot: np.ndarray,
                           scroll_match, info: QuestBarInfo) -> None:
        """OCR the region right of the scroll icon to read quest text.

        The quest text region starts just right of the scroll icon and
        extends to ~90% of screen width, with similar vertical range.
        """
        h, w = screenshot.shape[:2]
        sx1, sy1, sx2, sy2 = scroll_match.bbox

        # Text region: right of scroll icon to near-right edge of screen
        text_x1 = sx2
        text_y1 = sy1
        text_x2 = min(int(w * 0.90), w)
        text_y2 = sy2

        # Expand vertically a bit
        pad_y = (sy2 - sy1) // 4
        text_y1 = max(0, text_y1 - pad_y)
        text_y2 = min(h, text_y2 + pad_y)

        if text_x2 <= text_x1 or text_y2 <= text_y1:
            return

        region = screenshot[text_y1:text_y2, text_x1:text_x2]

        try:
            results = self.ocr.find_all_text(region)
        except Exception as e:
            logger.warning(f"Quest bar OCR failed: {e}")
            return

        if not results:
            return

        # Take the highest-confidence result as quest text
        best = max(results, key=lambda r: r.confidence)
        info.current_quest_text = best.text.strip()

        # Translate bbox back to full-screenshot coordinates
        bx1, by1, bx2, by2 = best.bbox
        info.current_quest_bbox = (
            bx1 + text_x1, by1 + text_y1,
            bx2 + text_x1, by2 + text_y1
        )

    def _detect_green_check(self, screenshot: np.ndarray,
                            quest_bbox: tuple[int, int, int, int]) -> bool:
        """Check for green check mark right of quest text bbox.

        Uses HSV color analysis (H:35-85, S>80, V>100).
        Returns True if green pixel count exceeds threshold.
        """
        h, w = screenshot.shape[:2]
        qx1, qy1, qx2, qy2 = quest_bbox

        # Check region right of quest text
        check_x1 = qx2
        check_y1 = qy1
        check_x2 = min(qx2 + (qy2 - qy1) * 2, w)  # Width ~2x text height
        check_y2 = qy2

        if check_x2 <= check_x1 or check_y2 <= check_y1:
            return False

        region = screenshot[check_y1:check_y2, check_x1:check_x2]
        if region.size == 0:
            return False

        hsv = cv2.cvtColor(region, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(
            hsv,
            np.array([self.GREEN_H_MIN, self.GREEN_S_MIN, self.GREEN_V_MIN]),
            np.array([self.GREEN_H_MAX, 255, 255])
        )
        green_count = cv2.countNonZero(mask)

        if green_count >= self.GREEN_PIXEL_THRESHOLD:
            logger.debug(f"Quest bar: green check detected ({green_count} pixels)")
            return True

        return False

    def _detect_tutorial_finger(self, screenshot: np.ndarray,
                                info: QuestBarInfo) -> None:
        """Detect tutorial finger icon via template matching.

        Gracefully handles missing template (not all setups have it).
        """
        match = self.template_matcher.match_one(screenshot, "icons/tutorial_finger")
        if match is not None:
            info.has_tutorial_finger = True
            info.tutorial_finger_pos = (match.x, match.y)
            logger.debug(f"Quest bar: tutorial finger at ({match.x}, {match.y})")

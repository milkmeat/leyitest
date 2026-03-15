"""Button Detector — detect rectangular colored buttons with text.

Finds buttons by HSV color segmentation + contour analysis, then
associates OCR text results that fall inside each button's bounding rect.
Adapted from the find_primary_button / _pick_bottommost_button logic
in element_detector.py, but detects ALL buttons instead of just one.
"""

import logging
from dataclasses import dataclass

import cv2
import numpy as np

from vision.ocr_locator import OCRResult

logger = logging.getLogger(__name__)


@dataclass
class ButtonElement:
    """A detected button with text and color."""
    text: str                   # OCR text inside button (empty if none)
    pos: tuple[int, int]        # center (cx, cy)
    size: tuple[int, int]       # (width, height)
    color: str                  # "green" | "blue" | "purple" | "gold" | "red" | "gray"
    has_red_text: bool = False  # True if red text inside (e.g. insufficient resources)


class ButtonDetector:
    """Detect rectangular colored buttons by HSV + contour analysis."""

    # HSV color ranges for button detection
    COLOR_RANGES: dict[str, list[tuple]] = {
        "green":  [((35, 80, 120), (85, 255, 255))],
        "blue":   [((90, 80, 120), (115, 255, 255))],
        "purple": [((130, 80, 100), (160, 255, 255))],
        "gold":   [((10, 150, 150), (30, 255, 255))],
        "red":    [((0, 100, 80), (10, 255, 255)),
                   ((165, 100, 80), (180, 255, 255))],
    }

    # Contour filters
    MIN_AREA = 3000
    MAX_AREA = 200000
    MIN_ASPECT = 1.5       # width / height
    MAX_ASPECT = 8.0
    MIN_FILL_RATIO = 0.50  # contour area / bounding rect area
    MIN_EDGE_DENSITY = 0.04
    MAX_WIDTH_RATIO = 0.85  # reject full-width bars

    # Gray button detection threshold (mean saturation)
    GRAY_MAX_SATURATION = 45.0
    GRAY_MIN_AREA = 3000

    # Overlap merging threshold
    IOU_MERGE_THRESHOLD = 0.5

    def detect(self, screenshot: np.ndarray,
               ocr_results: list[OCRResult]) -> list[ButtonElement]:
        """Detect all buttons in screenshot and associate OCR text.

        Args:
            screenshot: BGR numpy array.
            ocr_results: Pre-computed OCR results from OCRLocator.find_all_text().

        Returns:
            List of ButtonElement with text, position, size, and color.
        """
        sh, sw = screenshot.shape[:2]
        hsv = cv2.cvtColor(screenshot, cv2.COLOR_BGR2HSV)
        gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))

        raw_buttons: list[ButtonElement] = []

        # Detect colored buttons
        for color_name, ranges in self.COLOR_RANGES.items():
            mask = np.zeros(hsv.shape[:2], dtype=np.uint8)
            for lo, hi in ranges:
                mask = cv2.bitwise_or(mask, cv2.inRange(hsv, lo, hi))
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

            buttons = self._extract_buttons(
                mask, sh, sw, edges, color_name, ocr_results
            )
            raw_buttons.extend(buttons)

        # Detect gray buttons (low saturation, but valid shape)
        gray_buttons = self._detect_gray_buttons(
            hsv, gray, edges, sh, sw, ocr_results
        )
        raw_buttons.extend(gray_buttons)

        # Merge overlapping detections
        merged = self._merge_overlapping(raw_buttons)

        # Check for red text inside non-red buttons
        self._detect_red_text(merged, hsv)

        logger.debug(f"Buttons detected: {len(merged)}")
        return merged

    def _extract_buttons(self, mask: np.ndarray,
                         sh: int, sw: int,
                         edges: np.ndarray,
                         color_name: str,
                         ocr_results: list[OCRResult],
                         ) -> list[ButtonElement]:
        """Extract button-shaped contours from a color mask."""
        contours, _ = cv2.findContours(
            mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        buttons = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area < self.MIN_AREA or area > self.MAX_AREA:
                continue

            x, y, w, h = cv2.boundingRect(contour)
            if h == 0:
                continue
            aspect = w / h
            if aspect < self.MIN_ASPECT or aspect > self.MAX_ASPECT:
                continue

            # Reject full-width bars
            if sw > 0 and w / sw > self.MAX_WIDTH_RATIO:
                continue

            # Reject sparse contours
            fill = area / (w * h)
            if fill < self.MIN_FILL_RATIO:
                continue

            # Reject regions without clear edges
            edge_roi = edges[y:y + h, x:x + w]
            density = np.count_nonzero(edge_roi) / max(edge_roi.size, 1)
            if density < self.MIN_EDGE_DENSITY:
                continue

            cx = x + w // 2
            cy = y + h // 2

            # Find OCR text inside this button
            text = self._find_text_in_rect(ocr_results, x, y, x + w, y + h)

            buttons.append(ButtonElement(
                text=text,
                pos=(cx, cy),
                size=(w, h),
                color=color_name,
            ))

        return buttons

    def _detect_gray_buttons(self, hsv: np.ndarray,
                             gray: np.ndarray,
                             edges: np.ndarray,
                             sh: int, sw: int,
                             ocr_results: list[OCRResult],
                             ) -> list[ButtonElement]:
        """Detect gray (disabled) buttons by low saturation + valid shape.

        Gray buttons have low saturation but still have clear rectangular
        edges. We use edge-based detection in low-saturation areas.
        """
        # Low saturation mask
        sat = hsv[:, :, 1]
        low_sat = (sat < self.GRAY_MAX_SATURATION).astype(np.uint8) * 255

        # Must also have reasonable brightness (not black)
        val = hsv[:, :, 2]
        bright_enough = (val > 80).astype(np.uint8) * 255
        gray_mask = cv2.bitwise_and(low_sat, bright_enough)

        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))
        gray_mask = cv2.morphologyEx(gray_mask, cv2.MORPH_CLOSE, kernel)

        return self._extract_buttons(
            gray_mask, sh, sw, edges, "gray", ocr_results
        )

    def _find_text_in_rect(self, ocr_results: list[OCRResult],
                           x1: int, y1: int, x2: int, y2: int) -> str:
        """Find OCR text whose center falls inside a bounding rect."""
        texts = []
        for ocr in ocr_results:
            cx, cy = ocr.center
            if x1 <= cx <= x2 and y1 <= cy <= y2:
                texts.append(ocr.text)
        return " ".join(texts) if texts else ""

    def _merge_overlapping(self, buttons: list[ButtonElement],
                           ) -> list[ButtonElement]:
        """Merge buttons with high IoU overlap, keeping the colored one."""
        if len(buttons) <= 1:
            return buttons

        # Sort by area descending (larger buttons first)
        buttons.sort(key=lambda b: b.size[0] * b.size[1], reverse=True)
        keep = [True] * len(buttons)

        for i in range(len(buttons)):
            if not keep[i]:
                continue
            for j in range(i + 1, len(buttons)):
                if not keep[j]:
                    continue
                if self._iou(buttons[i], buttons[j]) > self.IOU_MERGE_THRESHOLD:
                    # Keep the colored one (non-gray preferred)
                    if buttons[j].color != "gray" and buttons[i].color == "gray":
                        keep[i] = False
                    else:
                        keep[j] = False

        return [b for b, k in zip(buttons, keep) if k]

    @staticmethod
    def _iou(a: ButtonElement, b: ButtonElement) -> float:
        """Compute intersection-over-union of two button bounding rects."""
        ax1 = a.pos[0] - a.size[0] // 2
        ay1 = a.pos[1] - a.size[1] // 2
        ax2 = ax1 + a.size[0]
        ay2 = ay1 + a.size[1]
        bx1 = b.pos[0] - b.size[0] // 2
        by1 = b.pos[1] - b.size[1] // 2
        bx2 = bx1 + b.size[0]
        by2 = by1 + b.size[1]

        ix1 = max(ax1, bx1)
        iy1 = max(ay1, by1)
        ix2 = min(ax2, bx2)
        iy2 = min(ay2, by2)

        if ix1 >= ix2 or iy1 >= iy2:
            return 0.0

        intersection = (ix2 - ix1) * (iy2 - iy1)
        area_a = a.size[0] * a.size[1]
        area_b = b.size[0] * b.size[1]
        union = area_a + area_b - intersection
        return intersection / union if union > 0 else 0.0

    _RED_TEXT_RATIO = 0.01  # 1% red pixels → has red text

    def _detect_red_text(self, buttons: list[ButtonElement],
                         hsv: np.ndarray) -> None:
        """Mark buttons that contain red text (e.g. insufficient resources)."""
        for btn in buttons:
            if btn.color == "red":
                continue
            x1 = btn.pos[0] - btn.size[0] // 2
            y1 = btn.pos[1] - btn.size[1] // 2
            x2 = btn.pos[0] + btn.size[0] // 2
            y2 = btn.pos[1] + btn.size[1] // 2
            roi = hsv[y1:y2, x1:x2]
            if roi.size == 0:
                continue
            mask1 = cv2.inRange(roi, (0, 100, 100), (10, 255, 255))
            mask2 = cv2.inRange(roi, (170, 100, 100), (180, 255, 255))
            red_ratio = (np.count_nonzero(mask1) + np.count_nonzero(mask2)) / max(roi.shape[0] * roi.shape[1], 1)
            if red_ratio > self._RED_TEXT_RATIO:
                btn.has_red_text = True

"""OCR Locator - OCR text detection with bounding box positions."""

import re
import logging
from dataclasses import dataclass

import cv2
import numpy as np

logger = logging.getLogger(__name__)


def is_on_colored_button(screenshot: np.ndarray,
                         bbox: tuple[int, int, int, int]) -> bool:
    """Check if an OCR text region sits on a colored button background.

    Game buttons have saturated backgrounds (blue, green, yellow, red).
    Body text sits on low-saturation backgrounds (beige, white, brown).

    Args:
        screenshot: Full BGR screenshot.
        bbox: (x1, y1, x2, y2) bounding box of the OCR text region.

    Returns:
        True if 30%+ of the sampled region has high saturation (S>80, V>60),
        indicating a colored button background.
    """
    x1, y1, x2, y2 = bbox
    # Expand bbox slightly to sample the button background around text
    pad_y = max(5, (y2 - y1) // 3)
    pad_x = max(5, (x2 - x1) // 6)
    h, w = screenshot.shape[:2]
    ey1 = max(0, y1 - pad_y)
    ey2 = min(h, y2 + pad_y)
    ex1 = max(0, x1 - pad_x)
    ex2 = min(w, x2 + pad_x)

    region = screenshot[ey1:ey2, ex1:ex2]
    if region.size == 0:
        return False
    hsv = cv2.cvtColor(region, cv2.COLOR_BGR2HSV)
    # Saturated pixels: S > 80, V > 60
    sat_mask = cv2.inRange(hsv, (0, 80, 60), (180, 255, 255))
    sat_ratio = cv2.countNonZero(sat_mask) / sat_mask.size
    return sat_ratio > 0.3


@dataclass
class OCRResult:
    """Result of an OCR detection."""
    text: str
    confidence: float
    bbox: tuple[int, int, int, int]  # (x1, y1, x2, y2)
    center: tuple[int, int]          # (cx, cy)


class OCRLocator:
    """OCR text detection and positioning using RapidOCR (ONNX Runtime)."""

    def __init__(self, corrections: dict[str, str] | None = None) -> None:
        self._ocr = None
        self._corrections = corrections or {}
        # Frame-level cache: avoids redundant full-screen OCR within one loop
        self._frame_img: np.ndarray | None = None
        self._frame_results: list[OCRResult] | None = None

    def _get_ocr(self):
        """Lazy-load RapidOCR to avoid slow import at startup."""
        if self._ocr is None:
            try:
                from rapidocr_onnxruntime import RapidOCR
                self._ocr = RapidOCR()
                logger.info("RapidOCR initialized")
            except ImportError:
                logger.error(
                    "RapidOCR not installed. Install with: pip install rapidocr-onnxruntime"
                )
                raise
        return self._ocr

    def set_frame(self, screenshot: np.ndarray) -> None:
        """Mark a new frame for caching.

        Call this once per loop iteration with the freshly captured screenshot.
        Subsequent ``find_all_text`` calls on the **same** numpy object will
        return cached results instantly, eliminating redundant full-screen OCR.
        Region-specific calls (cropped arrays) are unaffected.
        """
        self._frame_img = screenshot
        self._frame_results = None

    def find_text(self, screenshot: np.ndarray, target_text: str) -> OCRResult | None:
        """Find specific text in screenshot. Returns position or None.

        Performs substring matching (case-insensitive).
        """
        all_results = self.find_all_text(screenshot)
        target_lower = target_text.lower()

        best: OCRResult | None = None
        for result in all_results:
            if target_lower in result.text.lower():
                if best is None or result.confidence > best.confidence:
                    best = result

        if best:
            logger.debug(f"Found text '{target_text}' -> '{best.text}' "
                         f"confidence={best.confidence:.3f} at {best.center}")
        return best

    def find_all_text(self, screenshot: np.ndarray) -> list[OCRResult]:
        """Extract all text with positions from screenshot.

        If *screenshot* is the same object passed to :meth:`set_frame`,
        cached results are returned without re-running OCR.
        """
        # Frame cache hit: exact same array object, already computed
        if (self._frame_img is not None
                and screenshot is self._frame_img
                and self._frame_results is not None):
            logger.debug(
                f"OCR frame cache hit ({len(self._frame_results)} regions)")
            return self._frame_results

        ocr = self._get_ocr()

        raw_results, _elapse = ocr(screenshot)

        results = []
        if not raw_results:
            return results

        for line in raw_results:
            # RapidOCR line format: [[[x1,y1],[x2,y2],[x3,y3],[x4,y4]], text, confidence_str]
            box_points = line[0]
            text = line[1]
            confidence = float(line[2])

            # Convert 4-point polygon to bounding box
            xs = [int(p[0]) for p in box_points]
            ys = [int(p[1]) for p in box_points]
            x1, y1 = min(xs), min(ys)
            x2, y2 = max(xs), max(ys)
            cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

            # Apply OCR error corrections
            for wrong, correct in self._corrections.items():
                if wrong in text:
                    text = text.replace(wrong, correct)

            results.append(OCRResult(
                text=text,
                confidence=confidence,
                bbox=(x1, y1, x2, y2),
                center=(cx, cy),
            ))

        logger.debug(f"OCR found {len(results)} text regions")

        # Store in frame cache if this is the current frame
        if screenshot is self._frame_img:
            self._frame_results = results

        return results

    def find_numbers_in_region(self, screenshot: np.ndarray,
                               region: tuple[int, int, int, int]) -> str:
        """Extract numeric text from a specific region (for resource values).

        Args:
            screenshot: Full screenshot image.
            region: (x1, y1, x2, y2) bounding box to crop.

        Returns:
            Extracted numeric string (digits, commas, dots, K/M/B suffixes).
            Empty string if nothing found.
        """
        x1, y1, x2, y2 = region
        cropped = screenshot[y1:y2, x1:x2]
        if cropped.size == 0:
            return ""

        all_text = self.find_all_text(cropped)
        if not all_text:
            return ""

        # Combine all text and extract numbers
        combined = " ".join(r.text for r in all_text)
        # Match patterns like "12,345", "1.2M", "500K", etc.
        numbers = re.findall(r'[\d,\.]+[KkMmBb]?', combined)
        return numbers[0] if numbers else combined.strip()

"""OCR Locator - OCR text detection with bounding box positions."""

import re
import logging
from dataclasses import dataclass

import cv2
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class OCRResult:
    """Result of an OCR detection."""
    text: str
    confidence: float
    bbox: tuple[int, int, int, int]  # (x1, y1, x2, y2)
    center: tuple[int, int]          # (cx, cy)


class OCRLocator:
    """OCR text detection and positioning using RapidOCR (ONNX Runtime)."""

    def __init__(self) -> None:
        self._ocr = None

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
        """Extract all text with positions from screenshot."""
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

            results.append(OCRResult(
                text=text,
                confidence=confidence,
                bbox=(x1, y1, x2, y2),
                center=(cx, cy),
            ))

        logger.debug(f"OCR found {len(results)} text regions")
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

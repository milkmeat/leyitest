"""Element Detector - Unified element detection entry point."""

import logging
from dataclasses import dataclass

import cv2
import numpy as np

from .template_matcher import TemplateMatcher, MatchResult
from .ocr_locator import OCRLocator, OCRResult
from .grid_overlay import GridOverlay

logger = logging.getLogger(__name__)


@dataclass
class Element:
    """A detected UI element."""
    name: str
    source: str       # "template" | "ocr" | "contour" | "grid"
    confidence: float
    x: int
    y: int
    bbox: tuple[int, int, int, int]


class ElementDetector:
    """Unified detection entry point with priority-based dispatch.

    Detection priority (unless overridden):
      1. Template matching (fastest, most reliable for known elements)
      2. OCR text search (for text-based elements)
      3. Color/contour detection (for generic shapes)
      4. Grid fallback (return grid cell center)
    """

    def __init__(self, template_matcher: TemplateMatcher,
                 ocr_locator: OCRLocator,
                 grid_overlay: GridOverlay) -> None:
        self.template_matcher = template_matcher
        self.ocr = ocr_locator
        self.grid = grid_overlay

    def locate(self, screenshot: np.ndarray, target: str,
               methods: list[str] | None = None) -> Element | None:
        """Locate a UI element by name/text.

        Args:
            screenshot: BGR numpy array.
            target: Element name (template name) or text to find.
            methods: Optional list to override detection order.
                     Values: "template", "ocr", "contour", "grid".

        Returns:
            Element with coordinates, or None if not found.
        """
        if methods is None:
            methods = ["template", "ocr", "contour"]

        for method in methods:
            result = None
            if method == "template":
                result = self._locate_by_template(screenshot, target)
            elif method == "ocr":
                result = self._locate_by_ocr(screenshot, target)
            elif method == "contour":
                result = self._locate_by_contour(screenshot, target)
            elif method == "grid":
                result = self._locate_by_grid(target)

            if result is not None:
                logger.debug(f"Located '{target}' via {method}: ({result.x}, {result.y})")
                return result

        logger.debug(f"Could not locate '{target}' with methods {methods}")
        return None

    def locate_all(self, screenshot: np.ndarray) -> list[Element]:
        """Detect all recognizable elements in screenshot.

        Combines template matches and OCR results.
        """
        elements = []

        # All template matches
        for match in self.template_matcher.match_all(screenshot):
            elements.append(Element(
                name=match.template_name,
                source="template",
                confidence=match.confidence,
                x=match.x, y=match.y,
                bbox=match.bbox,
            ))

        # All OCR text
        try:
            for ocr_result in self.ocr.find_all_text(screenshot):
                elements.append(Element(
                    name=ocr_result.text,
                    source="ocr",
                    confidence=ocr_result.confidence,
                    x=ocr_result.center[0], y=ocr_result.center[1],
                    bbox=ocr_result.bbox,
                ))
        except Exception as e:
            logger.warning(f"OCR failed in locate_all: {e}")

        return elements

    def _locate_by_template(self, screenshot: np.ndarray, target: str) -> Element | None:
        """Try to find target as a template name."""
        # Direct match by template name
        result = self.template_matcher.match_one(screenshot, target)
        if result:
            return self._match_to_element(result)

        # Try with common prefixes, but only if target has no category yet
        if "/" not in target:
            for prefix in ["buttons/", "icons/", "scenes/"]:
                result = self.template_matcher.match_one(screenshot, prefix + target)
                if result:
                    return self._match_to_element(result)

        return None

    def _locate_by_ocr(self, screenshot: np.ndarray, target: str) -> Element | None:
        """Try to find target text via OCR."""
        try:
            result = self.ocr.find_text(screenshot, target)
            if result:
                return Element(
                    name=result.text,
                    source="ocr",
                    confidence=result.confidence,
                    x=result.center[0], y=result.center[1],
                    bbox=result.bbox,
                )
        except Exception as e:
            logger.warning(f"OCR lookup failed for '{target}': {e}")
        return None

    def _locate_by_contour(self, screenshot: np.ndarray, target: str) -> Element | None:
        """Try to find target by color/contour analysis.

        This is a basic implementation that looks for prominent button-like
        rectangles. Works for common UI elements with distinct colors.
        """
        # Convert to HSV for color-based detection
        hsv = cv2.cvtColor(screenshot, cv2.COLOR_BGR2HSV)
        gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)

        # Look for bright, saturated button-like regions
        # Common game UI colors: red, green, gold buttons
        # Use edge detection + contour finding
        edges = cv2.Canny(gray, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Filter for button-sized rectangles
        min_area = 2000
        max_area = screenshot.shape[0] * screenshot.shape[1] // 4
        candidates = []

        for contour in contours:
            area = cv2.contourArea(contour)
            if area < min_area or area > max_area:
                continue

            # Approximate to polygon
            peri = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.04 * peri, True)

            # Look for roughly rectangular shapes (4-6 vertices)
            if 4 <= len(approx) <= 6:
                x, y, w, h = cv2.boundingRect(contour)
                aspect = w / h if h > 0 else 0
                # Button-like aspect ratio
                if 0.5 < aspect < 8:
                    cx, cy = x + w // 2, y + h // 2
                    candidates.append((area, cx, cy, (x, y, x + w, y + h)))

        # This method is imprecise, so we return None unless we have a strong signal
        # It's primarily a fallback and real usage will be refined per-game
        return None

    def _locate_by_grid(self, target: str) -> Element | None:
        """Interpret target as a grid cell label and return its center."""
        try:
            x, y = self.grid.cell_to_pixel(target)
            region = self.grid.get_cell_region(target)
            return Element(
                name=target,
                source="grid",
                confidence=1.0,
                x=x, y=y,
                bbox=region,
            )
        except ValueError:
            return None

    def _match_to_element(self, match: MatchResult) -> Element:
        """Convert MatchResult to Element."""
        return Element(
            name=match.template_name,
            source="template",
            confidence=match.confidence,
            x=match.x, y=match.y,
            bbox=match.bbox,
        )

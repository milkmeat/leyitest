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
        """Try to find target by color/contour analysis."""
        if target == "primary_button":
            return find_primary_button(screenshot)
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


def has_red_text_near_button(screenshot: np.ndarray,
                            button: Element,
                            above_px: int = 120,
                            min_red_pixels: int = 200) -> bool:
    """Check if there is red text near a button (above or overlapping).

    Red text typically indicates insufficient resources.  Checks a region
    from ``above_px`` pixels above the button center down to the button
    center, spanning ±200 px horizontally.

    Returns True if the number of red pixels exceeds *min_red_pixels*.
    """
    h, w = screenshot.shape[:2]
    y1 = max(0, button.y - above_px)
    y2 = min(h, button.y + 20)
    x1 = max(0, button.x - 200)
    x2 = min(w, button.x + 200)
    region = screenshot[y1:y2, x1:x2]

    hsv = cv2.cvtColor(region, cv2.COLOR_BGR2HSV)
    red_lo = cv2.inRange(hsv, (0, 100, 80), (10, 255, 255))
    red_hi = cv2.inRange(hsv, (165, 100, 80), (180, 255, 255))
    red_mask = cv2.bitwise_or(red_lo, red_hi)
    red_count = int(red_mask.sum() / 255)

    logger.debug(
        f"Red text check near ({button.x},{button.y}): "
        f"{red_count} red pixels (threshold={min_red_pixels})"
    )
    return red_count >= min_red_pixels


def find_primary_button(screenshot: np.ndarray,
                        min_area: int = 10000,
                        min_aspect: float = 1.8,
                        max_aspect: float = 8.0,
                        y_fraction: float = 0.4,
                        ) -> Element | None:
    """Detect the primary action button by HSV color filtering.

    Uses a two-tier priority system:
      Tier 1 (high): Blue / green buttons — always action buttons
                     (建造, 升级, 前往, 下一个, 训练)
      Tier 2 (low):  Gold / yellow buttons — reward / confirm buttons
                     (领取, 全部领取, 确定)

    If any Tier 1 button is found, it wins regardless of position.
    Tier 2 is only used when no Tier 1 exists.  Within each tier,
    the bottommost button is preferred.

    Args:
        screenshot: BGR numpy array.
        min_area: Minimum contour area in pixels (rejects small icons).
        min_aspect: Minimum width/height ratio (buttons are wide).
        max_aspect: Maximum width/height ratio.
        y_fraction: Button center must be below this fraction of screen height.

    Returns:
        Element with center coordinates and bbox, or None if not found.
    """
    sh, sw = screenshot.shape[:2]
    hsv = cv2.cvtColor(screenshot, cv2.COLOR_BGR2HSV)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))
    y_min = int(sh * y_fraction)

    # Tier 1: Blue + Green (high priority)
    blue_mask = cv2.inRange(hsv, (90, 80, 120), (115, 255, 255))
    green_mask = cv2.inRange(hsv, (35, 80, 120), (85, 255, 255))
    tier1_mask = cv2.bitwise_or(blue_mask, green_mask)
    tier1_mask = cv2.morphologyEx(tier1_mask, cv2.MORPH_CLOSE, kernel)

    result = _pick_bottommost_button(tier1_mask, sh, sw, y_min,
                                     min_area, min_aspect, max_aspect)
    if result is not None:
        logger.debug(
            f"Primary button (blue/green): ({result.x}, {result.y}) "
            f"bbox={result.bbox}"
        )
        return result

    # Tier 2: Gold / yellow (lower priority, only when no blue/green)
    # Higher S threshold separates gold buttons from parchment backgrounds.
    gold_mask = cv2.inRange(hsv, (10, 150, 150), (30, 255, 255))
    gold_mask = cv2.morphologyEx(gold_mask, cv2.MORPH_CLOSE, kernel)

    result = _pick_bottommost_button(gold_mask, sh, sw, y_min,
                                     min_area, min_aspect, max_aspect)
    if result is not None:
        logger.debug(
            f"Primary button (gold): ({result.x}, {result.y}) "
            f"bbox={result.bbox}"
        )
    return result


def _pick_bottommost_button(mask: np.ndarray,
                            sh: int, sw: int, y_min: int,
                            min_area: int, min_aspect: float,
                            max_aspect: float) -> Element | None:
    """Pick the bottommost button-shaped contour from a binary mask."""
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL,
                                   cv2.CHAIN_APPROX_SIMPLE)
    best = None
    best_y = -1

    for contour in contours:
        area = cv2.contourArea(contour)
        if area < min_area:
            continue

        x, y, w, h = cv2.boundingRect(contour)
        if h == 0:
            continue
        aspect = w / h
        if aspect < min_aspect or aspect > max_aspect:
            continue

        cy = y + h // 2
        if cy < y_min:
            continue

        if cy > best_y:
            best_y = cy
            best = Element(
                name="primary_button",
                source="contour",
                confidence=area / (sh * sw),
                x=x + w // 2, y=cy,
                bbox=(x, y, x + w, y + h),
            )

    return best

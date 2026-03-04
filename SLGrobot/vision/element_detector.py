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


def is_gray_button(screenshot: np.ndarray,
                   element: Element,
                   half_w: int = 80,
                   half_h: int = 25,
                   max_saturation: float = 45.0) -> bool:
    """Check if the button region around *element* is gray (disabled).

    Samples a rectangle centred on the element and computes the mean
    HSV saturation.  Gray / disabled buttons have very low saturation
    compared to active blue/green/gold buttons (S > 100).

    Args:
        screenshot: BGR numpy array.
        element: The detected UI element (text hit, template hit, etc.).
        half_w: Half-width of the sampling rectangle.
        half_h: Half-height of the sampling rectangle.
        max_saturation: If mean saturation is below this, the button is gray.

    Returns:
        True if the region looks gray (disabled).
    """
    h, w = screenshot.shape[:2]
    y1 = max(0, element.y - half_h)
    y2 = min(h, element.y + half_h)
    x1 = max(0, element.x - half_w)
    x2 = min(w, element.x + half_w)
    region = screenshot[y1:y2, x1:x2]

    if region.size == 0:
        return False

    hsv = cv2.cvtColor(region, cv2.COLOR_BGR2HSV)
    mean_sat = float(hsv[:, :, 1].mean())

    logger.debug(
        f"Gray button check at ({element.x},{element.y}): "
        f"mean_sat={mean_sat:.1f} (threshold={max_saturation})"
    )
    return mean_sat < max_saturation


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

    Uses a three-tier priority system:
      Tier 1 (high):   Blue / green buttons — always action buttons
                       (建造, 升级, 前往, 下一个, 训练)
      Tier 2 (medium): Purple buttons — special action buttons
                       (招募, 免费)
      Tier 3 (low):    Gold / yellow buttons — reward / confirm buttons
                       (领取, 全部领取, 确定)

    Higher-tier buttons win regardless of position.  Within each tier,
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
    gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))
    y_min = int(sh * y_fraction)

    # Tier 1: Blue + Green (high priority)
    blue_mask = cv2.inRange(hsv, (90, 80, 120), (115, 255, 255))
    green_mask = cv2.inRange(hsv, (35, 80, 120), (85, 255, 255))
    tier1_mask = cv2.bitwise_or(blue_mask, green_mask)
    tier1_mask = cv2.morphologyEx(tier1_mask, cv2.MORPH_CLOSE, kernel)

    result = _pick_bottommost_button(tier1_mask, sh, sw, y_min,
                                     min_area, min_aspect, max_aspect,
                                     edges=edges)
    if result is not None:
        logger.debug(
            f"Primary button (blue/green): ({result.x}, {result.y}) "
            f"bbox={result.bbox}"
        )
        return result

    # Tier 2: Purple (medium priority, only when no blue/green)
    purple_mask = cv2.inRange(hsv, (130, 80, 100), (160, 255, 255))
    purple_mask = cv2.morphologyEx(purple_mask, cv2.MORPH_CLOSE, kernel)

    result = _pick_bottommost_button(purple_mask, sh, sw, y_min,
                                     min_area, min_aspect, max_aspect,
                                     edges=edges)
    if result is not None:
        logger.debug(
            f"Primary button (purple): ({result.x}, {result.y}) "
            f"bbox={result.bbox}"
        )
        return result

    # Tier 3: Gold / yellow (lowest priority)
    # Higher S threshold separates gold buttons from parchment backgrounds.
    gold_mask = cv2.inRange(hsv, (10, 150, 150), (30, 255, 255))
    gold_mask = cv2.morphologyEx(gold_mask, cv2.MORPH_CLOSE, kernel)

    result = _pick_bottommost_button(gold_mask, sh, sw, y_min,
                                     min_area, min_aspect, max_aspect,
                                     edges=edges)
    if result is not None:
        logger.debug(
            f"Primary button (gold): ({result.x}, {result.y}) "
            f"bbox={result.bbox}"
        )
    return result


def find_purple_button(screenshot: np.ndarray,
                       min_area: int = 10000,
                       min_aspect: float = 1.8,
                       max_aspect: float = 8.0,
                       y_fraction: float = 0.4,
                       ) -> Element | None:
    """Detect a purple action button only (招募, 免费).

    Unlike :func:`find_primary_button` which checks all color tiers,
    this function only looks for purple buttons (HSV 130-160).

    Returns:
        Element with center coordinates and bbox, or None if not found.
    """
    sh, sw = screenshot.shape[:2]
    hsv = cv2.cvtColor(screenshot, cv2.COLOR_BGR2HSV)
    gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))
    y_min = int(sh * y_fraction)

    purple_mask = cv2.inRange(hsv, (130, 80, 100), (160, 255, 255))
    purple_mask = cv2.morphologyEx(purple_mask, cv2.MORPH_CLOSE, kernel)

    result = _pick_bottommost_button(purple_mask, sh, sw, y_min,
                                     min_area, min_aspect, max_aspect,
                                     edges=edges)
    if result is not None:
        logger.debug(
            f"Purple button: ({result.x}, {result.y}) bbox={result.bbox}"
        )
    return result


def _pick_bottommost_button(mask: np.ndarray,
                            sh: int, sw: int, y_min: int,
                            min_area: int, min_aspect: float,
                            max_aspect: float,
                            edges: np.ndarray | None = None,
                            min_edge_density: float = 0.04,
                            min_fill_ratio: float = 0.50,
                            max_width_ratio: float = 0.85,
                            ) -> Element | None:
    """Pick the bottommost button-shaped contour from a binary mask.

    When *edges* (Canny edge map) is provided, candidates whose bounding
    box has an edge-pixel density below *min_edge_density* are rejected.
    Real buttons have crisp borders; background gradients (e.g. sky) do not.

    *min_fill_ratio* rejects contours whose area is too small relative to
    their bounding box.  Real buttons are solid rectangles (fill ≥ 0.6);
    scattered color patches (e.g. blue sea water) have low fill ratio.

    *max_width_ratio* rejects contours wider than this fraction of the
    screen width.  Real buttons never span the full screen; navigation
    bars and toolbars do.
    """
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

        # Reject full-width bars (e.g. bottom navigation bar)
        if sw > 0 and w / sw > max_width_ratio:
            logger.debug(
                f"Rejected contour at ({x+w//2}, {cy}): "
                f"width ratio {w/sw:.3f} > {max_width_ratio}"
            )
            continue

        # Reject sparse contours (e.g. scattered sea-water pixels)
        fill = area / (w * h)
        if fill < min_fill_ratio:
            logger.debug(
                f"Rejected contour at ({x+w//2}, {cy}): "
                f"fill ratio {fill:.3f} < {min_fill_ratio}"
            )
            continue

        # Reject regions that lack clear edges (gradient backgrounds)
        if edges is not None:
            edge_roi = edges[y:y+h, x:x+w]
            density = np.count_nonzero(edge_roi) / max(edge_roi.size, 1)
            if density < min_edge_density:
                logger.debug(
                    f"Rejected contour at ({x+w//2}, {cy}): "
                    f"edge density {density:.3f} < {min_edge_density}"
                )
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

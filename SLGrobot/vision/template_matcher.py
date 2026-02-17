"""Template Matcher - Match pre-stored template images against screenshots."""

import os
import logging
from dataclasses import dataclass

import cv2
import numpy as np

import config

logger = logging.getLogger(__name__)


@dataclass
class MatchResult:
    """Result of a template match."""
    template_name: str
    confidence: float
    x: int          # center x of matched region
    y: int          # center y of matched region
    bbox: tuple[int, int, int, int]  # (x1, y1, x2, y2)


class TemplateMatcher:
    """Match pre-stored template images against screenshots using OpenCV."""

    def __init__(self, template_dir: str = None, threshold: float = None) -> None:
        self.template_dir = template_dir or config.TEMPLATE_DIR
        self.threshold = threshold or config.TEMPLATE_MATCH_THRESHOLD
        self._cache: dict[str, tuple[np.ndarray, np.ndarray | None]] = {}
        self._load_templates()

    def _load_templates(self) -> None:
        """Load all PNG templates from directory into memory cache."""
        if not os.path.isdir(self.template_dir):
            logger.warning(f"Template directory not found: {self.template_dir}")
            return

        for root, _dirs, files in os.walk(self.template_dir):
            for filename in files:
                if not filename.lower().endswith((".png", ".jpg", ".jpeg")):
                    continue
                filepath = os.path.join(root, filename)
                image = cv2.imread(filepath, cv2.IMREAD_UNCHANGED)
                if image is None:
                    logger.warning(f"Failed to load template: {filepath}")
                    continue

                # Separate alpha channel as mask if present
                mask = None
                if image.ndim == 3 and image.shape[2] == 4:
                    alpha = image[:, :, 3]
                    bgr = image[:, :, :3]
                    if alpha.min() < 255:
                        # Real transparency exists — use alpha as mask
                        mask = cv2.merge([alpha, alpha, alpha])
                    image = bgr
                elif image.ndim == 2:
                    # Grayscale — convert to BGR
                    image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

                # Key: relative path without extension, e.g. "buttons/close"
                rel_path = os.path.relpath(filepath, self.template_dir)
                name = os.path.splitext(rel_path)[0].replace("\\", "/")
                self._cache[name] = (image, mask)
                logger.debug(f"Loaded template: {name} ({image.shape[1]}x{image.shape[0]}, mask={'yes' if mask is not None else 'no'})")

        logger.info(f"Loaded {len(self._cache)} templates from {self.template_dir}")

    def reload(self) -> None:
        """Reload all templates from disk."""
        self._cache.clear()
        self._load_templates()

    def count(self) -> int:
        """Return the number of loaded templates."""
        return len(self._cache)

    def get_template_names(self) -> list[str]:
        """Return list of all loaded template names."""
        return list(self._cache.keys())

    def match_one(self, screenshot: np.ndarray, template_name: str) -> MatchResult | None:
        """Match a specific template against screenshot.

        Returns MatchResult if confidence >= threshold, else None.
        """
        entry = self._cache.get(template_name)
        if entry is None:
            logger.warning(f"Template not found in cache: {template_name}")
            return None

        template, mask = entry
        return self._match(screenshot, template_name, template, mask)

    def match_all(self, screenshot: np.ndarray, category: str = "") -> list[MatchResult]:
        """Match all templates (optionally filtered by category directory).

        Args:
            screenshot: BGR numpy array.
            category: Optional category prefix to filter, e.g. "buttons".

        Returns list of MatchResults above threshold, sorted by confidence descending.
        """
        results = []
        for name, (template, mask) in self._cache.items():
            if category and not name.startswith(category):
                continue
            result = self._match(screenshot, name, template, mask)
            if result is not None:
                results.append(result)

        results.sort(key=lambda r: r.confidence, reverse=True)
        return results

    def match_best(self, screenshot: np.ndarray, template_names: list[str]) -> MatchResult | None:
        """Find the best match among given template names.

        Returns the highest-confidence match above threshold, or None.
        """
        best: MatchResult | None = None
        for name in template_names:
            result = self.match_one(screenshot, name)
            if result is not None:
                if best is None or result.confidence > best.confidence:
                    best = result
        return best

    def match_one_multi(self, screenshot: np.ndarray, template_name: str,
                        max_matches: int = 10) -> list[MatchResult]:
        """Find multiple instances of a template in the screenshot.

        Returns list of non-overlapping matches above threshold.
        """
        entry = self._cache.get(template_name)
        if entry is None:
            logger.warning(f"Template not found in cache: {template_name}")
            return []

        template, mask = entry
        th, tw = template.shape[:2]
        method = cv2.TM_CCORR_NORMED if mask is not None else cv2.TM_CCOEFF_NORMED
        result_map = cv2.matchTemplate(screenshot, template, method, mask=mask)

        results = []
        for _ in range(max_matches):
            _, max_val, _, max_loc = cv2.minMaxLoc(result_map)
            if max_val < self.threshold:
                break

            x1, y1 = max_loc
            x2, y2 = x1 + tw, y1 + th
            cx, cy = x1 + tw // 2, y1 + th // 2

            results.append(MatchResult(
                template_name=template_name,
                confidence=float(max_val),
                x=cx, y=cy,
                bbox=(x1, y1, x2, y2),
            ))

            # Suppress the found region to find other instances
            suppress_x1 = max(0, x1 - tw // 2)
            suppress_y1 = max(0, y1 - th // 2)
            suppress_x2 = min(result_map.shape[1], x1 + tw // 2)
            suppress_y2 = min(result_map.shape[0], y1 + th // 2)
            result_map[suppress_y1:suppress_y2, suppress_x1:suppress_x2] = 0

        return results

    def _match(self, screenshot: np.ndarray, name: str, template: np.ndarray,
               mask: np.ndarray | None = None) -> MatchResult | None:
        """Run template matching and return MatchResult if above threshold."""
        th, tw = template.shape[:2]
        sh, sw = screenshot.shape[:2]

        # Template must be smaller than screenshot
        if tw > sw or th > sh:
            return None

        # Use TM_CCORR_NORMED when mask is present (OpenCV only fully supports
        # masked matching with TM_SQDIFF and TM_CCORR_NORMED, not TM_CCOEFF_NORMED)
        method = cv2.TM_CCORR_NORMED if mask is not None else cv2.TM_CCOEFF_NORMED
        result = cv2.matchTemplate(screenshot, template, method, mask=mask)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)

        if max_val < self.threshold:
            return None

        x1, y1 = max_loc
        x2, y2 = x1 + tw, y1 + th
        cx, cy = x1 + tw // 2, y1 + th // 2

        logger.debug(f"Template match: {name} confidence={max_val:.3f} at ({cx}, {cy})")
        return MatchResult(
            template_name=name,
            confidence=float(max_val),
            x=cx, y=cy,
            bbox=(x1, y1, x2, y2),
        )

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

    # Templates that should use color-invariant matching (HSV Saturation channel).
    # Useful when the same icon appears in different color variants (e.g. dark-red
    # vs light-red close button).  Normal BGR matching fails across color variants,
    # but the Saturation channel preserves shape while ignoring hue/lightness.
    COLOR_INVARIANT_TEMPLATES: set[str] = {"buttons/close_x"}

    # Templates that require strict size AND color matching.
    # After the normal CCOEFF shape match, an additional BGR pixel-level color
    # check is performed: the mean absolute difference between the template and
    # the matched region must be below STRICT_COLOR_MAX_DIFF.  This prevents
    # similarly-shaped but differently-colored icons from matching.
    STRICT_COLOR_TEMPLATES: set[str] = {"icons/upgrade_arrow"}
    STRICT_COLOR_MAX_DIFF: float = 30.0
    STRICT_COLOR_CCOEFF_THRESHOLD: float = 0.6

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
        is_strict = template_name in self.STRICT_COLOR_TEMPLATES
        effective_threshold = (
            self.STRICT_COLOR_CCOEFF_THRESHOLD if is_strict
            else self.threshold
        )

        results = []
        for _ in range(max_matches):
            _, max_val, _, max_loc = cv2.minMaxLoc(result_map)
            if max_val < effective_threshold:
                break

            x1, y1 = max_loc
            x2, y2 = x1 + tw, y1 + th
            cx, cy = x1 + tw // 2, y1 + th // 2

            # Strict color verification for selected templates
            if template_name in self.STRICT_COLOR_TEMPLATES:
                region = screenshot[y1:y2, x1:x2]
                if region.shape[:2] == template.shape[:2]:
                    diff = np.mean(np.abs(
                        region.astype(np.float32) - template.astype(np.float32)
                    ))
                    if diff > self.STRICT_COLOR_MAX_DIFF:
                        logger.debug(
                            f"Template multi-match rejected (strict color, "
                            f"diff={diff:.1f}): {template_name} at ({cx}, {cy})"
                        )
                        # Suppress and continue looking
                        result_map[max(0, y1 - th // 2):min(result_map.shape[0], y1 + th // 2),
                                   max(0, x1 - tw // 2):min(result_map.shape[1], x1 + tw // 2)] = 0
                        continue

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

        if mask is not None:
            # Two-pass matching for masked (transparent) templates:
            # Pass 1 — CCORR with mask finds the candidate location.
            # Pass 2 — CCOEFF without mask verifies (rejects false positives
            #          caused by near-white templates matching any bright area).
            result_ccorr = cv2.matchTemplate(
                screenshot, template, cv2.TM_CCORR_NORMED, mask=mask)
            _, ccorr_val, _, ccorr_loc = cv2.minMaxLoc(result_ccorr)
            if ccorr_val < self.threshold:
                return None

            result_ccoeff = cv2.matchTemplate(
                screenshot, template, cv2.TM_CCOEFF_NORMED)
            ccoeff_val = float(result_ccoeff[ccorr_loc[1], ccorr_loc[0]])
            if ccoeff_val < self.threshold:
                logger.debug(
                    f"Template match rejected (CCORR={ccorr_val:.3f}, "
                    f"CCOEFF={ccoeff_val:.3f}): {name} at "
                    f"({ccorr_loc[0] + tw // 2}, {ccorr_loc[1] + th // 2})"
                )
                return None

            x1, y1 = ccorr_loc
            max_val = ccoeff_val
        else:
            result_map = cv2.matchTemplate(
                screenshot, template, cv2.TM_CCOEFF_NORMED)
            is_strict = name in self.STRICT_COLOR_TEMPLATES
            effective_threshold = (
                self.STRICT_COLOR_CCOEFF_THRESHOLD if is_strict
                else self.threshold
            )
            _, max_val, _, max_loc = cv2.minMaxLoc(result_map)
            if max_val < effective_threshold:
                # Fallback: color-invariant matching via HSV Saturation channel
                if name in self.COLOR_INVARIANT_TEMPLATES:
                    return self._match_saturation(screenshot, name, template)
                return None
            x1, y1 = max_loc

            # Strict color templates: if color check fails, suppress and
            # keep searching for the next candidate above threshold.
            if is_strict:
                max_attempts = 20
                for _ in range(max_attempts):
                    x2, y2 = x1 + tw, y1 + th
                    cx, cy = x1 + tw // 2, y1 + th // 2
                    region = screenshot[y1:y2, x1:x2]
                    if region.shape[:2] == template.shape[:2]:
                        diff = np.mean(np.abs(
                            region.astype(np.float32) - template.astype(np.float32)
                        ))
                        if diff <= self.STRICT_COLOR_MAX_DIFF:
                            logger.debug(
                                f"Template match passed strict color check "
                                f"(diff={diff:.1f}): {name}"
                            )
                            break
                        logger.debug(
                            f"Template match rejected (strict color, "
                            f"diff={diff:.1f} > {self.STRICT_COLOR_MAX_DIFF}): "
                            f"{name} at ({cx}, {cy})"
                        )
                    # Suppress rejected region and try next candidate
                    sup_x1 = max(0, x1 - tw // 2)
                    sup_y1 = max(0, y1 - th // 2)
                    sup_x2 = min(result_map.shape[1], x1 + tw // 2)
                    sup_y2 = min(result_map.shape[0], y1 + th // 2)
                    result_map[sup_y1:sup_y2, sup_x1:sup_x2] = 0
                    _, max_val, _, max_loc = cv2.minMaxLoc(result_map)
                    if max_val < effective_threshold:
                        return None
                    x1, y1 = max_loc
                else:
                    return None  # exhausted attempts

        x2, y2 = x1 + tw, y1 + th
        cx, cy = x1 + tw // 2, y1 + th // 2

        logger.debug(f"Template match: {name} confidence={max_val:.3f} at ({cx}, {cy})")
        return MatchResult(
            template_name=name,
            confidence=float(max_val),
            x=cx, y=cy,
            bbox=(x1, y1, x2, y2),
        )

    def _match_saturation(self, screenshot: np.ndarray, name: str,
                          template: np.ndarray) -> MatchResult | None:
        """Color-invariant matching using the HSV Saturation channel.

        Converts both screenshot and template to HSV and matches on the S
        channel only.  This makes matching robust to hue/lightness differences
        (e.g. dark-red vs light-red icons) while preserving shape.
        """
        th, tw = template.shape[:2]
        scr_s = cv2.cvtColor(screenshot, cv2.COLOR_BGR2HSV)[:, :, 1]
        tmpl_s = cv2.cvtColor(template, cv2.COLOR_BGR2HSV)[:, :, 1]

        result = cv2.matchTemplate(scr_s, tmpl_s, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)

        if max_val < self.threshold:
            return None

        x1, y1 = max_loc
        x2, y2 = x1 + tw, y1 + th
        cx, cy = x1 + tw // 2, y1 + th // 2

        logger.debug(f"Template match (saturation): {name} confidence={max_val:.3f} at ({cx}, {cy})")
        return MatchResult(
            template_name=name,
            confidence=float(max_val),
            x=cx, y=cy,
            bbox=(x1, y1, x2, y2),
        )

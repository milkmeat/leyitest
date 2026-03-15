"""Finger Detector - Tutorial finger detection with three-stage validation.

Extracted from QuestWorkflow to be a standalone CV component.  Detects the
animated tutorial finger icon in various orientations (normal, flipped,
rotated) and scales using:
  Stage 1: TM_CCORR_NORMED with alpha mask (sensitive but may false-positive)
  Stage 2: Masked NCC on opaque pixels only (eliminates false positives)
  Stage 3: Boundary contrast — compares mean BGR just inside vs. just outside
           the template silhouette edge; rejects if the finger blends into a
           same-colour background (low contrast = no visible outline)
"""

import logging
import time

import cv2
import numpy as np

from vision.element_detector import Element, ElementDetector
from vision.template_matcher import TemplateMatcher

logger = logging.getLogger(__name__)


class FingerDetector:
    """Detect tutorial finger icon on game screenshots.

    The game shows the finger icon in various orientations to guide the player.
    This detector creates flipped/rotated template variants at init time,
    then runs a three-stage filter (CCORR + NCC + boundary contrast) for
    robust detection.
    """

    # Offset from template center (40, 57) to fingertip (15, 100)
    # in template-local coords (pixels) for the 80x114 tutorial_finger.png
    # (trimmed fingertip crop of the original 256x256).
    _FINGERTIP_OFFSET = (-25, 43)

    # Pre-computed fingertip offsets for rotation variants.
    # Derived by rotating _FINGERTIP_OFFSET (-25, 43) by the CW angle
    # using screen-coordinate rotation (y-down).
    _ROTATION_FINGERTIP_OFFSETS: dict[str, tuple[int, int]] = {
        "rot117cw": (-27, -42),
    }

    # All finger template variants: (cache_name, transform, flip_type)
    # transform: None=original, int=cv2.flip code, str "cwN"=CW rotation by N°
    _FINGER_VARIANTS = [
        ("tutorial_finger",           None,    "normal"),
        ("tutorial_finger_hflip",     1,       "hflip"),
        ("tutorial_finger_vflip",     0,       "vflip"),
        ("tutorial_finger_hvflip",   -1,       "hvflip"),
        ("tutorial_finger_rot117cw", "cw117",  "rot117cw"),
    ]

    # Scale factors for multi-scale detection.  The game renders the
    # tutorial finger at different sizes depending on context (e.g.
    # battle-scene Auto button uses a smaller finger than quest guide).
    # Original template (scale 1.0) is always tried first.
    _SCALE_FACTORS = [0.5, 0.7]

    # Stage-1 threshold (TM_CCORR_NORMED with mask).
    # Lowered from 0.93 to 0.85 to catch partially-visible fingers;
    # false positives are caught by stage-2 validation instead.
    _FINGER_CONFIDENCE_THRESHOLD = 0.85

    # Stage-2 threshold (masked NCC — correlation on opaque pixels only).
    # Quest-guide finger: NCC 0.98+.  False positives vary by game:
    # westgame2 ~0.20–0.40, frozenisland up to ~0.65.
    # Default 0.7; games can override via game_profile.finger_ncc_threshold
    # (e.g. frozenisland=0.68, westgame2=0.83).
    _FINGER_NCC_THRESHOLD = 0.7

    # Stage-3 threshold: minimum Euclidean distance between mean BGR of
    # inner-boundary pixels (opaque side of edge) and outer-boundary pixels
    # (transparent side of edge).  Real fingers have a visible outline
    # (distance >> 20); false positives on same-colour backgrounds have
    # distance < 20.  Games can override via game_profile.finger_boundary_threshold.
    _FINGER_BOUNDARY_THRESHOLD = 20.0
    _MIN_BOUNDARY_PIXELS = 10

    # Prescan parameters for quick rejection of no-finger frames.
    _PRESCAN_SCALE = 0.25
    _PRESCAN_THRESHOLD = 0.4

    def __init__(self, element_detector: ElementDetector,
                 game_profile=None) -> None:
        self.element_detector = element_detector
        if game_profile and game_profile.finger_ncc_threshold > 0:
            self._FINGER_NCC_THRESHOLD = game_profile.finger_ncc_threshold
        if game_profile and game_profile.finger_boundary_threshold > 0:
            self._FINGER_BOUNDARY_THRESHOLD = game_profile.finger_boundary_threshold
        # _all_variants: superset of _FINGER_VARIANTS including scaled entries.
        # Each entry: (cache_name, transform_unused, flip_type_key)
        self._all_variants: list[tuple[str, None, str]] = []
        # Maps scaled flip_type -> (base_flip_type, scale) for offset calc.
        self._variant_scales: dict[str, tuple[str, float]] = {}
        self._ensure_flipped_finger_template()

    def fingertip_pos(self, cx: int, cy: int,
                      flip_type: str) -> tuple[int, int]:
        """Compute fingertip tap position from match center and flip type."""
        # Resolve scale: if this is a scaled variant, get base flip and scale
        scale = 1.0
        base_flip = flip_type
        if flip_type in self._variant_scales:
            base_flip, scale = self._variant_scales[flip_type]

        if base_flip in self._ROTATION_FINGERTIP_OFFSETS:
            dx, dy = self._ROTATION_FINGERTIP_OFFSETS[base_flip]
            return cx + int(dx * scale), cy + int(dy * scale)
        dx, dy = self._FINGERTIP_OFFSET
        if base_flip in ("hflip", "hvflip"):
            dx = -dx
        if base_flip in ("vflip", "hvflip"):
            dy = -dy
        return cx + int(dx * scale), cy + int(dy * scale)

    def verify_ncc(self, screenshot: np.ndarray,
                   cx: int, cy: int,
                   flip_type: str) -> float:
        """Stage-2 validation: NCC on masked (opaque) pixels only.

        Computes normalized cross-correlation between template and screenshot
        crop, considering only the pixels where the template is opaque.
        This ignores background entirely, making it robust to varying
        game backgrounds around the finger.

        Returns the NCC score, or -1.0 on error / 1.0 if validation unavailable.
        """
        ncc_entry = self._finger_ncc.get(flip_type)
        if ncc_entry is None:
            return 1.0  # skip validation if unavailable

        tpl, msk = ncc_entry
        th, tw = tpl.shape[:2]
        sh, sw = screenshot.shape[:2]
        x1, y1 = cx - tw // 2, cy - th // 2
        if x1 < 0 or y1 < 0 or x1 + tw > sw or y1 + th > sh:
            return -1.0

        crop = screenshot[y1:y1 + th, x1:x1 + tw]
        return TemplateMatcher.compute_masked_ncc(tpl, crop, msk)

    def verify_boundary_contrast(
        self, screenshot: np.ndarray,
        cx: int, cy: int, flip_type: str,
    ) -> float:
        """Stage-3 validation: boundary contrast between inner and outer edge.

        Computes the Euclidean distance between the mean BGR of pixels just
        inside the template silhouette edge and just outside it in the
        screenshot.  A real finger has a visible outline (high contrast);
        a false positive blending into same-colour background has low contrast.

        Returns:
            999.0 if boundary masks are unavailable (skip this stage),
            -1.0 if the crop is out of bounds,
            otherwise the Euclidean BGR distance.
        """
        boundary_entry = self._finger_boundary.get(flip_type)
        if boundary_entry is None:
            return 999.0  # skip validation if unavailable

        inner_mask, outer_mask = boundary_entry
        th, tw = inner_mask.shape[:2]
        sh, sw = screenshot.shape[:2]
        x1, y1 = cx - tw // 2, cy - th // 2
        if x1 < 0 or y1 < 0 or x1 + tw > sw or y1 + th > sh:
            return -1.0

        crop = screenshot[y1:y1 + th, x1:x1 + tw]
        return TemplateMatcher.compute_boundary_contrast(
            crop, inner_mask, outer_mask)

    def detect_old(self, screenshot: np.ndarray) -> tuple:
        """Original detect — kept for A/B comparison via CLI.

        Checks orientation variants in priority order (normal first).
        Returns immediately on first verified match for speed.

        Stage 1: TM_CCORR_NORMED with mask (sensitive, may have false positives).
        Stage 2: Masked NCC on opaque pixels only (pattern-based,
                 eliminates false positives).
        Stage 3: Boundary contrast — rejects if silhouette edge blends
                 into same-colour background.

        Returns:
            (match, flip_type) where match is an Element or None,
            and flip_type is e.g. "normal", "vflip", "normal_s50", etc.
        """
        for cache_name, _, flip_type in self._all_variants:
            match = self.element_detector.locate(
                screenshot, cache_name, methods=["template"]
            )
            if match is None:
                continue

            # Stage-1: filter by CCORR confidence
            if match.confidence < self._FINGER_CONFIDENCE_THRESHOLD:
                logger.debug(
                    f"Finger {flip_type} rejected (stage1): "
                    f"conf={match.confidence:.3f}"
                )
                continue

            # Stage-2: masked NCC
            ncc = self.verify_ncc(
                screenshot, match.x, match.y, flip_type)
            if ncc < self._FINGER_NCC_THRESHOLD:
                logger.debug(
                    f"Finger {flip_type} rejected (stage2): ncc={ncc:.3f} "
                    f"at ({match.x}, {match.y})"
                )
                continue

            # Stage-3: boundary contrast
            bcon = self.verify_boundary_contrast(
                screenshot, match.x, match.y, flip_type)
            if bcon < self._FINGER_BOUNDARY_THRESHOLD:
                logger.debug(
                    f"Finger {flip_type} rejected (stage3): "
                    f"boundary={bcon:.1f} at ({match.x}, {match.y})"
                )
                continue

            logger.debug(
                f"Finger {flip_type} verified: conf={match.confidence:.3f}, "
                f"ncc={ncc:.3f}, boundary={bcon:.1f} at ({match.x}, {match.y})"
            )
            return match, flip_type

        return None, "normal"

    # Radius (pixels) for position exclusion — matches within this
    # distance of an excluded fingertip are skipped.
    _EXCLUDE_RADIUS = 30

    def detect(self, screenshot: np.ndarray,
               exclude_positions: list[tuple[int, int]] | None = None,
               ) -> tuple:
        """Optimized finger detection with three-layer acceleration.

        Layer 1: Prescan at 0.25x grayscale — rejects 95%+ no-finger frames
                 with just 2 small matchTemplate calls (~20ms).
        Layer 2: Last-matched variant priority — exploits temporal locality
                 (finger stays in same orientation across consecutive frames).
        Layer 3: Direct matchTemplate bypass — skips the generic
                 element_detector/template_matcher pipeline overhead.

        Args:
            exclude_positions: fingertip positions to skip (e.g. exhausted
                false positives).  Matches whose fingertip falls within
                _EXCLUDE_RADIUS of any excluded position are rejected.

        Returns:
            (match, flip_type) where match is an Element or None,
            and flip_type is e.g. "normal", "vflip", "normal_s50", etc.
        """
        t_start = time.perf_counter()

        # --- Layer 1: Prescan quick reject ---
        if self._prescan_templates:
            sh, sw = screenshot.shape[:2]
            gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
            small_w = max(1, int(sw * self._PRESCAN_SCALE))
            small_h = max(1, int(sh * self._PRESCAN_SCALE))
            small = cv2.resize(gray, (small_w, small_h),
                               interpolation=cv2.INTER_AREA)
            prescan_pass = False
            for ps_tpl, ps_mask in self._prescan_templates:
                # Skip if prescan template is larger than the small image
                if (ps_tpl.shape[0] > small_h
                        or ps_tpl.shape[1] > small_w):
                    continue
                res = cv2.matchTemplate(small, ps_tpl,
                                        cv2.TM_CCORR_NORMED,
                                        mask=ps_mask)
                _, max_val, _, _ = cv2.minMaxLoc(res)
                if max_val >= self._PRESCAN_THRESHOLD:
                    prescan_pass = True
                    break
            t_prescan = time.perf_counter()
            if not prescan_pass:
                self._last_matched_idx = None
                logger.debug(
                    f"Finger detect: prescan={int((t_prescan - t_start) * 1000)}ms, "
                    f"total={int((t_prescan - t_start) * 1000)}ms (rejected)"
                )
                return None, "normal"

        # --- Layer 2: Try last-matched variant first ---
        if self._last_matched_idx is not None:
            result = self._try_variant(screenshot, self._last_matched_idx,
                                       exclude_positions)
            if result:
                t_end = time.perf_counter()
                logger.debug(
                    f"Finger detect: total={int((t_end - t_start) * 1000)}ms "
                    f"(last-match hit)"
                )
                return result

        # --- Layer 3: Full scan with direct matchTemplate ---
        for i in range(len(self._direct_variants)):
            if i == self._last_matched_idx:
                continue
            result = self._try_variant(screenshot, i, exclude_positions)
            if result:
                self._last_matched_idx = i
                t_end = time.perf_counter()
                logger.debug(
                    f"Finger detect: total={int((t_end - t_start) * 1000)}ms "
                    f"(variant {i})"
                )
                return result

        self._last_matched_idx = None
        t_end = time.perf_counter()
        logger.debug(
            f"Finger detect: total={int((t_end - t_start) * 1000)}ms "
            f"(no match)"
        )
        return None, "normal"

    def _try_variant(self, screenshot: np.ndarray,
                     idx: int,
                     exclude_positions: list[tuple[int, int]] | None = None,
                     ) -> tuple | None:
        """Try matching a single variant by index with inline three-stage filter.

        Returns (Element, flip_type) on verified match, or None.
        """
        cache_name, tpl, mask, flip_type = self._direct_variants[idx]
        th, tw = tpl.shape[:2]
        sh, sw = screenshot.shape[:2]

        if tw > sw or th > sh:
            return None

        # Stage 1: CCORR with mask
        if mask is not None:
            result_ccorr = cv2.matchTemplate(
                screenshot, tpl, cv2.TM_CCORR_NORMED, mask=mask)
            _, ccorr_val, _, ccorr_loc = cv2.minMaxLoc(result_ccorr)
            if ccorr_val < self._FINGER_CONFIDENCE_THRESHOLD:
                return None
            x1, y1 = ccorr_loc
        else:
            result_ccoeff = cv2.matchTemplate(
                screenshot, tpl, cv2.TM_CCOEFF_NORMED)
            _, ccoeff_val, _, ccoeff_loc = cv2.minMaxLoc(result_ccoeff)
            if ccoeff_val < self._FINGER_CONFIDENCE_THRESHOLD:
                return None
            ccorr_val = ccoeff_val
            x1, y1 = ccoeff_loc

        cx = x1 + tw // 2
        cy = y1 + th // 2

        # Stage 2: Masked NCC validation
        ncc = self.verify_ncc(screenshot, cx, cy, flip_type)
        if ncc < self._FINGER_NCC_THRESHOLD:
            logger.debug(
                f"Finger {flip_type} rejected (stage2): "
                f"ccorr={ccorr_val:.3f}, ncc={ncc:.3f} at ({cx}, {cy})"
            )
            return None

        # Stage 3: Boundary contrast validation
        bcon = self.verify_boundary_contrast(screenshot, cx, cy, flip_type)
        if bcon < self._FINGER_BOUNDARY_THRESHOLD:
            logger.debug(
                f"Finger {flip_type} rejected (stage3): "
                f"boundary={bcon:.1f} at ({cx}, {cy})"
            )
            return None

        # Stage 4: Exclusion check — skip if fingertip is near an
        # exhausted position (likely a persistent false positive).
        if exclude_positions:
            tip = self.fingertip_pos(cx, cy, flip_type)
            r = self._EXCLUDE_RADIUS
            for ex in exclude_positions:
                if abs(tip[0] - ex[0]) <= r and abs(tip[1] - ex[1]) <= r:
                    logger.debug(
                        f"Finger {flip_type} excluded: fingertip "
                        f"{tip} near exhausted {ex}"
                    )
                    return None

        logger.debug(
            f"Finger {flip_type} verified: ccorr={ccorr_val:.3f}, "
            f"ncc={ncc:.3f}, boundary={bcon:.1f} at ({cx}, {cy})"
        )
        elem = Element(
            name=cache_name, source="template",
            confidence=ccorr_val, x=cx, y=cy,
            bbox=(x1, y1, x1 + tw, y1 + th)
        )
        return elem, flip_type

    def _ensure_flipped_finger_template(self) -> None:
        """Create all finger template variants (flips, rotations, scales).

        The game shows the finger icon in various orientations and sizes.
        For each variant, caches the template + mask for stage-1 matching,
        and stores BGR + boolean mask for stage-2 masked NCC.
        Scaled-down variants are also created for each orientation.
        """
        self._finger_ncc = {}
        self._finger_boundary = {}
        self._all_variants = list(self._FINGER_VARIANTS)
        self._variant_scales = {}
        try:
            tm = self.element_detector.template_matcher
            cache = tm._cache
            if not isinstance(cache, dict):
                return

            base_name = "tutorial_finger"
            entry = cache.get(base_name)
            if entry is None or not isinstance(entry, tuple):
                return

            tpl, mask = entry

            # Build boolean mask for NCC
            if mask is not None:
                base_bool_mask = mask[:, :, 0] > 128
            else:
                base_bool_mask = np.ones(tpl.shape[:2], dtype=bool)

            # Store per-variant NCC data: {flip_type: (bgr, bool_mask)}
            self._finger_ncc = {
                "normal": (tpl.copy(), base_bool_mask),
            }

            # Boundary masks for stage-3 contrast check
            self._finger_boundary = {}
            base_boundary = TemplateMatcher.compute_boundary_masks(
                base_bool_mask, self._MIN_BOUNDARY_PIXELS)
            if base_boundary is not None:
                self._finger_boundary["normal"] = base_boundary

            for cache_name, transform, flip_type in self._FINGER_VARIANTS:
                if transform is None:
                    continue  # normal — already in cache
                if cache_name in cache:
                    continue

                if isinstance(transform, str) and transform.startswith("cw"):
                    # Clockwise rotation variant (e.g. "cw135" = 135° CW)
                    angle_cw = int(transform[2:])
                    h, w = tpl.shape[:2]
                    center = (w / 2, h / 2)
                    M = cv2.getRotationMatrix2D(center, -angle_cw, 1.0)
                    cos_v = abs(M[0, 0])
                    sin_v = abs(M[0, 1])
                    new_w = int(h * sin_v + w * cos_v)
                    new_h = int(h * cos_v + w * sin_v)
                    M[0, 2] += (new_w - w) / 2
                    M[1, 2] += (new_h - h) / 2
                    var_tpl = cv2.warpAffine(tpl, M, (new_w, new_h))
                    var_mask = (cv2.warpAffine(mask, M, (new_w, new_h))
                                if mask is not None else None)
                    var_bool = cv2.warpAffine(
                        base_bool_mask.astype(np.uint8), M, (new_w, new_h)
                    ).astype(bool)
                else:
                    # Flip variant (transform is int: -1, 0, or 1)
                    var_tpl = cv2.flip(tpl, transform)
                    var_mask = (cv2.flip(mask, transform)
                                if mask is not None else None)
                    var_bool = cv2.flip(
                        base_bool_mask.astype(np.uint8), transform
                    ).astype(bool)

                cache[cache_name] = (var_tpl, var_mask)
                self._finger_ncc[flip_type] = (var_tpl.copy(), var_bool)
                var_boundary = TemplateMatcher.compute_boundary_masks(
                    var_bool, self._MIN_BOUNDARY_PIXELS)
                if var_boundary is not None:
                    self._finger_boundary[flip_type] = var_boundary

            # --- Multi-scale variants ---
            # Create scaled-down copies of every orientation variant.
            # Original-scale variants are tried first (already in
            # _all_variants); scaled variants are appended after.
            ori_variants = list(self._all_variants)  # snapshot before append
            for scale in self._SCALE_FACTORS:
                suffix = f"_s{int(scale * 100)}"
                for ori_cache, _, ori_flip in ori_variants:
                    ori_entry = cache.get(ori_cache)
                    if ori_entry is None:
                        continue
                    ori_tpl, ori_mask = ori_entry

                    new_w = max(1, int(ori_tpl.shape[1] * scale))
                    new_h = max(1, int(ori_tpl.shape[0] * scale))

                    s_tpl = cv2.resize(
                        ori_tpl, (new_w, new_h),
                        interpolation=cv2.INTER_AREA)
                    s_mask = (
                        cv2.resize(ori_mask, (new_w, new_h),
                                   interpolation=cv2.INTER_AREA)
                        if ori_mask is not None else None)

                    # Boolean mask for NCC: resize then re-threshold
                    ori_ncc = self._finger_ncc.get(ori_flip)
                    if ori_ncc is not None:
                        _, ori_bool = ori_ncc
                        s_bool = cv2.resize(
                            ori_bool.astype(np.uint8), (new_w, new_h),
                            interpolation=cv2.INTER_AREA
                        ) > 0
                    else:
                        s_bool = np.ones((new_h, new_w), dtype=bool)

                    s_cache_name = ori_cache + suffix
                    s_flip = ori_flip + suffix
                    cache[s_cache_name] = (s_tpl, s_mask)
                    self._finger_ncc[s_flip] = (s_tpl.copy(), s_bool)
                    s_boundary = TemplateMatcher.compute_boundary_masks(
                        s_bool, self._MIN_BOUNDARY_PIXELS)
                    if s_boundary is not None:
                        self._finger_boundary[s_flip] = s_boundary
                    self._all_variants.append((s_cache_name, None, s_flip))
                    self._variant_scales[s_flip] = (ori_flip, scale)

            # --- Prescan templates (0.25x grayscale) for quick rejection ---
            # normal covers normal/hflip/vflip/hvflip (mirrored silhouettes
            # are similar enough at low resolution).
            # rot117cw covers the rotated variant (very different silhouette).
            self._prescan_templates: list[tuple[np.ndarray, np.ndarray | None]] = []
            for ori_name in ["tutorial_finger",
                             "tutorial_finger_rot117cw"]:
                entry = cache.get(ori_name)
                if entry is None:
                    continue
                ori_tpl, ori_mask = entry
                gray_tpl = cv2.cvtColor(ori_tpl, cv2.COLOR_BGR2GRAY)
                ps_w = max(1, int(ori_tpl.shape[1] * self._PRESCAN_SCALE))
                ps_h = max(1, int(ori_tpl.shape[0] * self._PRESCAN_SCALE))
                ps_tpl = cv2.resize(gray_tpl, (ps_w, ps_h),
                                    interpolation=cv2.INTER_AREA)
                ps_mask = (
                    cv2.resize(ori_mask[:, :, 0], (ps_w, ps_h),
                               interpolation=cv2.INTER_AREA)
                    if ori_mask is not None else None)
                self._prescan_templates.append((ps_tpl, ps_mask))

            # --- Direct variant list for bypassing the generic pipeline ---
            # Each entry: (cache_name, tpl, mask, flip_type)
            self._direct_variants: list[
                tuple[str, np.ndarray, np.ndarray | None, str]
            ] = []
            for cache_name, _, flip_type in self._all_variants:
                v_entry = cache.get(cache_name)
                if v_entry is None:
                    continue
                v_tpl, v_mask = v_entry
                self._direct_variants.append(
                    (cache_name, v_tpl, v_mask, flip_type))

            self._last_matched_idx: int | None = None

            logger.debug(
                f"Created finger template variants: "
                f"{list(self._finger_ncc.keys())}"
            )
        except Exception:
            self._finger_ncc = {}
            self._finger_boundary = {}
            self._all_variants = list(self._FINGER_VARIANTS)
            self._prescan_templates = []
            self._direct_variants = []
            self._last_matched_idx = None

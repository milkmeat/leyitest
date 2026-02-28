"""Finger Detector - Tutorial finger detection with two-stage validation.

Extracted from QuestWorkflow to be a standalone CV component.  Detects the
animated tutorial finger icon in various orientations (normal, flipped,
rotated) and scales using:
  Stage 1: TM_CCORR_NORMED with alpha mask (sensitive but may false-positive)
  Stage 2: Masked NCC on opaque pixels only (eliminates false positives)
"""

import logging

import cv2
import numpy as np

from vision.element_detector import ElementDetector

logger = logging.getLogger(__name__)


class FingerDetector:
    """Detect tutorial finger icon on game screenshots.

    The game shows the finger icon in various orientations to guide the player.
    This detector creates flipped/rotated template variants at init time,
    then runs a two-stage filter (CCORR + NCC) for robust detection.
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
        ("icons/tutorial_finger",           None,    "normal"),
        ("icons/tutorial_finger_hflip",     1,       "hflip"),
        ("icons/tutorial_finger_vflip",     0,       "vflip"),
        ("icons/tutorial_finger_hvflip",   -1,       "hvflip"),
        ("icons/tutorial_finger_rot117cw", "cw117",  "rot117cw"),
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
    # Quest-guide finger: NCC 0.98+.  Battle-scene finger (with glow
    # overlay): NCC ~0.47–0.53.  False positives: ~0.20–0.40.
    # Threshold 0.45 catches both contexts with ≥0.05 margin over
    # false positives.
    _FINGER_NCC_THRESHOLD = 0.45

    def __init__(self, element_detector: ElementDetector,
                 game_profile=None) -> None:
        self.element_detector = element_detector
        if game_profile and game_profile.finger_ncc_threshold > 0:
            self._FINGER_NCC_THRESHOLD = game_profile.finger_ncc_threshold
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
        t = tpl[msk].astype(np.float32).flatten()
        s = crop[msk].astype(np.float32).flatten()
        t = t - t.mean()
        s = s - s.mean()
        denom = np.sqrt(np.dot(t, t) * np.dot(s, s))
        if denom < 1e-10:
            return 0.0
        return float(np.dot(t, s) / denom)

    def detect(self, screenshot: np.ndarray) -> tuple:
        """Detect tutorial finger with two-stage validation.

        Checks orientation variants in priority order (normal first).
        Returns immediately on first verified match for speed.

        Stage 1: TM_CCORR_NORMED with mask (sensitive, may have false positives).
        Stage 2: Masked NCC on opaque pixels only (pattern-based,
                 eliminates false positives).

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

            logger.debug(
                f"Finger {flip_type} verified: conf={match.confidence:.3f}, "
                f"ncc={ncc:.3f} at ({match.x}, {match.y})"
            )
            return match, flip_type

        return None, "normal"

    def _ensure_flipped_finger_template(self) -> None:
        """Create all finger template variants (flips, rotations, scales).

        The game shows the finger icon in various orientations and sizes.
        For each variant, caches the template + mask for stage-1 matching,
        and stores BGR + boolean mask for stage-2 masked NCC.
        Scaled-down variants are also created for each orientation.
        """
        self._finger_ncc = {}
        self._all_variants = list(self._FINGER_VARIANTS)
        self._variant_scales = {}
        try:
            tm = self.element_detector.template_matcher
            cache = tm._cache
            if not isinstance(cache, dict):
                return

            base_name = "icons/tutorial_finger"
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
                    self._all_variants.append((s_cache_name, None, s_flip))
                    self._variant_scales[s_flip] = (ori_flip, scale)

            logger.debug(
                f"Created finger template variants: "
                f"{list(self._finger_ncc.keys())}"
            )
        except Exception:
            self._finger_ncc = {}
            self._all_variants = list(self._FINGER_VARIANTS)

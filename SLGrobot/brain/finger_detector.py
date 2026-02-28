"""Finger Detector - Tutorial finger detection with two-stage validation.

Extracted from QuestWorkflow to be a standalone CV component.  Detects the
animated tutorial finger icon in various orientations (normal, flipped,
rotated) using:
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
        self._ensure_flipped_finger_template()

    def fingertip_pos(self, cx: int, cy: int,
                      flip_type: str) -> tuple[int, int]:
        """Compute fingertip tap position from match center and flip type."""
        if flip_type in self._ROTATION_FINGERTIP_OFFSETS:
            dx, dy = self._ROTATION_FINGERTIP_OFFSETS[flip_type]
            return cx + dx, cy + dy
        dx, dy = self._FINGERTIP_OFFSET
        if flip_type in ("hflip", "hvflip"):
            dx = -dx
        if flip_type in ("vflip", "hvflip"):
            dy = -dy
        return cx + dx, cy + dy

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
            and flip_type is one of "normal", "hflip", "vflip", "hvflip",
            "rot117cw".
        """
        for cache_name, _, flip_type in self._FINGER_VARIANTS:
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
        """Create all finger template variants (flips and rotations).

        The game shows the finger icon in various orientations.
        For each variant, caches the template + mask for stage-1 matching,
        and stores BGR + boolean mask for stage-2 masked NCC.
        """
        self._finger_ncc = {}
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

            logger.debug(
                f"Created finger template variants: "
                f"{list(self._finger_ncc.keys())}"
            )
        except Exception:
            self._finger_ncc = {}

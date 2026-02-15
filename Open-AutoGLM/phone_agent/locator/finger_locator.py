"""
Finger/hand guide locator using OpenCV template matching.

Detects the tutorial hand/finger icon on game screens and returns
the fingertip coordinate for tapping. Much faster than an AI call
(~200ms vs ~2-5s) and more reliable for this specific use case.
"""

import base64
import math
import os
from dataclasses import dataclass

import cv2
import numpy as np


@dataclass
class FingerMatchResult:
    """Result of finger template matching."""
    found: bool
    fingertip: tuple[int, int] | None = None  # absolute pixel coords (x, y)
    confidence: float = 0.0
    scale: float = 1.0
    angle: float = 0.0


class FingerLocator:
    """
    Locates the tutorial hand/finger icon on screen using a hybrid
    two-pass approach:

    Pass 1 (Detection): TM_CCORR_NORMED with alpha mask — the mask
    ensures only opaque template pixels participate in the correlation,
    giving strong responses (~0.95) even for templates with large
    transparent regions.

    Pass 2 (Verification): TM_CCOEFF_NORMED with mean-filled
    transparency at the detected location — mean-subtraction provides
    much better discrimination between true matches and false positives
    (true ~0.35+ vs false <0.25).
    """

    # Offset from template center (128, 128) to fingertip (60, 235)
    # in template-local coords (pixels) for the 256x256 hand.png.
    _FINGERTIP_OFFSET = (-65, 100)

    # Downsample factor for the search image.  Matching cost scales with
    # image area, so halving each dimension gives a ~4x speedup while
    # preserving enough detail for the finger icon.
    _SEARCH_DOWNSAMPLE = 2

    # Minimum CCOEFF score at the CCORR-detected location to confirm
    # the match is not a false positive.
    _CCOEFF_VERIFY_THRESHOLD = 0.25

    def __init__(self, template_path: str | None = None):
        self._template_path = template_path or os.path.join(
            os.path.dirname(__file__), "..", "..", "resource", "hand.png"
        )
        self._template_gray: np.ndarray | None = None      # mean-filled grayscale
        self._template_raw_gray: np.ndarray | None = None   # original grayscale
        self._template_mask: np.ndarray | None = None       # binary alpha mask (0/1)
        self._template_mask_255: np.ndarray | None = None   # binary alpha mask (0/255)

    def _load_template(self) -> None:
        """Load template image with alpha channel (lazy, once).

        Stores two grayscale versions of the template:
        - raw: original pixel values (used with alpha mask for CCORR)
        - mean-filled: transparent pixels set to opaque mean (for CCOEFF)
        """
        if self._template_gray is not None:
            return

        img = cv2.imread(self._template_path, cv2.IMREAD_UNCHANGED)
        if img is None:
            raise FileNotFoundError(f"Template not found: {self._template_path}")

        gray = cv2.cvtColor(img[:, :, :3], cv2.COLOR_BGR2GRAY)
        self._template_raw_gray = gray.copy()

        if img.shape[2] == 4:
            alpha = img[:, :, 3]
            self._template_mask = (alpha > 128).astype(np.uint8)
            self._template_mask_255 = self._template_mask * 255
            # Fill transparent pixels with the mean of opaque pixels
            opaque_mean = gray[self._template_mask > 0].mean()
            gray = gray.copy()
            gray[self._template_mask == 0] = int(opaque_mean)
        else:
            self._template_mask = None
            self._template_mask_255 = None

        self._template_gray = gray

    @staticmethod
    def _resize_and_rotate(
        img: np.ndarray, scale: float, angle: float,
        border_value: int = 0,
    ) -> np.ndarray:
        """Resize and optionally rotate an image."""
        new_w = max(1, int(img.shape[1] * scale))
        new_h = max(1, int(img.shape[0] * scale))
        resized = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)

        if angle == 0:
            return resized

        center = (new_w // 2, new_h // 2)
        rot_mat = cv2.getRotationMatrix2D(center, -angle, 1.0)

        cos_a = abs(rot_mat[0, 0])
        sin_a = abs(rot_mat[0, 1])
        rot_w = int(new_h * sin_a + new_w * cos_a)
        rot_h = int(new_h * cos_a + new_w * sin_a)

        rot_mat[0, 2] += (rot_w - new_w) / 2
        rot_mat[1, 2] += (rot_h - new_h) / 2

        return cv2.warpAffine(
            resized, rot_mat, (rot_w, rot_h),
            borderMode=cv2.BORDER_CONSTANT, borderValue=border_value,
        )

    def find_finger(
        self,
        screenshot_b64: str,
        screen_width: int,
        screen_height: int,
        confidence_threshold: float = 0.55,
    ) -> FingerMatchResult:
        """
        Find the finger/hand guide icon in a screenshot.

        Uses a hybrid two-pass approach when the template has an alpha
        channel:
        1. TM_CCORR_NORMED + mask for high-sensitivity detection
        2. TM_CCOEFF_NORMED at the detected location to reject false
           positives

        For templates without alpha, falls back to CCOEFF-only matching.

        Args:
            screenshot_b64: Base64-encoded screenshot (PNG/JPEG).
            screen_width: Device screen width in pixels.
            screen_height: Device screen height in pixels.
            confidence_threshold: Minimum confidence to consider a match.

        Returns:
            FingerMatchResult with fingertip coords if found.
        """
        self._load_template()

        # Decode screenshot
        img_bytes = base64.b64decode(screenshot_b64)
        img_arr = np.frombuffer(img_bytes, dtype=np.uint8)
        screen = cv2.imdecode(img_arr, cv2.IMREAD_COLOR)
        if screen is None:
            return FingerMatchResult(found=False)

        screen_gray = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)

        # Downsample the screen for faster matching; template scales are
        # adjusted accordingly so the found coordinates can be mapped back.
        ds = self._SEARCH_DOWNSAMPLE
        search_img = cv2.resize(
            screen_gray,
            (screen_gray.shape[1] // ds, screen_gray.shape[0] // ds),
            interpolation=cv2.INTER_AREA,
        )

        # Multi-scale parameters: base scale adapts to device resolution,
        # divided by downsample factor so the template matches the search image.
        base_scale = screen_width / 1080.0 / ds
        scale_factors = [base_scale * f for f in np.linspace(0.7, 1.4, 8)]

        # Multi-rotation: -30 to +30 degrees in 10-degree steps
        angles = list(range(-30, 31, 10))  # [-30, -20, -10, 0, 10, 20, 30]

        has_mask = self._template_mask_255 is not None

        best_confidence = 0.0
        best_location = None   # match center in search_img coordinates
        best_scale = 1.0       # effective full-resolution scale
        best_angle = 0.0
        best_topleft = None    # match top-left in search_img (for verification)

        # --- Pass 1: Detection ---
        for scale in scale_factors:
            for angle in angles:
                if has_mask:
                    # CCORR + mask: high sensitivity for masked templates
                    tmpl = self._resize_and_rotate(
                        self._template_raw_gray, scale, angle,
                        border_value=0)
                    mask = self._resize_and_rotate(
                        self._template_mask_255, scale, angle,
                        border_value=0)
                    # Re-binarize mask after resize/rotate interpolation
                    mask = (mask > 128).astype(np.uint8) * 255
                else:
                    # No alpha: mean-filled CCOEFF (original method)
                    fill_val = int(self._template_gray.mean())
                    tmpl = self._resize_and_rotate(
                        self._template_gray, scale, angle,
                        border_value=fill_val)
                    mask = None

                # Skip if template is larger than search image
                if (tmpl.shape[0] > search_img.shape[0] or
                        tmpl.shape[1] > search_img.shape[1]):
                    continue

                if mask is not None:
                    result = cv2.matchTemplate(
                        search_img, tmpl, cv2.TM_CCORR_NORMED, mask=mask)
                else:
                    result = cv2.matchTemplate(
                        search_img, tmpl, cv2.TM_CCOEFF_NORMED)

                _, max_val, _, max_loc = cv2.minMaxLoc(result)

                if max_val > best_confidence:
                    best_confidence = max_val
                    # max_loc is top-left corner of match; compute center
                    match_center_x = max_loc[0] + tmpl.shape[1] // 2
                    match_center_y = max_loc[1] + tmpl.shape[0] // 2
                    best_location = (match_center_x, match_center_y)
                    # Record the effective full-resolution scale
                    best_scale = scale * ds
                    best_angle = angle
                    best_topleft = max_loc

        if best_confidence < confidence_threshold or best_location is None:
            return FingerMatchResult(found=False, confidence=best_confidence)

        # --- Pass 2: CCOEFF Verification (only when mask was used) ---
        if has_mask:
            verify_scale = best_scale / ds
            fill_val = int(self._template_gray.mean())
            filled = self._resize_and_rotate(
                self._template_gray, verify_scale, best_angle,
                border_value=fill_val)

            if (filled.shape[0] <= search_img.shape[0] and
                    filled.shape[1] <= search_img.shape[1]):
                result_ccoeff = cv2.matchTemplate(
                    search_img, filled, cv2.TM_CCOEFF_NORMED)

                # Check CCOEFF score at the CCORR-detected location
                loc_x = min(best_topleft[0], result_ccoeff.shape[1] - 1)
                loc_y = min(best_topleft[1], result_ccoeff.shape[0] - 1)
                ccoeff_score = float(result_ccoeff[loc_y, loc_x])

                if ccoeff_score < self._CCOEFF_VERIFY_THRESHOLD:
                    return FingerMatchResult(
                        found=False, confidence=best_confidence)

        # --- Compute fingertip position ---
        # Map match center back to full-resolution coordinates
        full_center_x = best_location[0] * ds
        full_center_y = best_location[1] * ds

        # Compute fingertip position from match center + rotated/scaled offset
        offset_x, offset_y = self._FINGERTIP_OFFSET
        scaled_ox = offset_x * best_scale
        scaled_oy = offset_y * best_scale

        # Rotate the offset by best_angle
        rad = math.radians(-best_angle)
        rot_ox = scaled_ox * math.cos(rad) - scaled_oy * math.sin(rad)
        rot_oy = scaled_ox * math.sin(rad) + scaled_oy * math.cos(rad)

        fingertip_x = int(full_center_x + rot_ox)
        fingertip_y = int(full_center_y + rot_oy)

        # Clamp to screen bounds
        fingertip_x = max(0, min(screen_width - 1, fingertip_x))
        fingertip_y = max(0, min(screen_height - 1, fingertip_y))

        return FingerMatchResult(
            found=True,
            fingertip=(fingertip_x, fingertip_y),
            confidence=best_confidence,
            scale=best_scale,
            angle=best_angle,
        )

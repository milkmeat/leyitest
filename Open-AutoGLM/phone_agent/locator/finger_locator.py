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
    Locates the tutorial hand/finger icon on screen using OpenCV
    multi-scale, multi-rotation template matching.
    """

    # Offset from template center (128, 128) to fingertip (60, 235)
    # in template-local coords (pixels) for the 256x256 hand.png.
    _FINGERTIP_OFFSET = (-68, 107)

    def __init__(self, template_path: str | None = None):
        self._template_path = template_path or os.path.join(
            os.path.dirname(__file__), "..", "..", "resource", "hand.png"
        )
        self._template_gray: np.ndarray | None = None  # mean-filled grayscale
        self._template_mask: np.ndarray | None = None   # binary alpha mask

    def _load_template(self) -> None:
        """Load template image with alpha channel (lazy, once).

        Transparent pixels are filled with the mean of the opaque pixels.
        This allows using TM_CCOEFF_NORMED (which subtracts the mean from
        both template and image patch) without a mask parameter — the
        filled pixels become zero after mean subtraction and contribute
        nothing to the correlation.  This gives far better discrimination
        between true matches and false positives than TM_CCORR_NORMED
        with a mask.
        """
        if self._template_gray is not None:
            return

        img = cv2.imread(self._template_path, cv2.IMREAD_UNCHANGED)
        if img is None:
            raise FileNotFoundError(f"Template not found: {self._template_path}")

        gray = cv2.cvtColor(img[:, :, :3], cv2.COLOR_BGR2GRAY)

        if img.shape[2] == 4:
            alpha = img[:, :, 3]
            # Binary mask: opaque (>128) = 1, transparent = 0
            self._template_mask = (alpha > 128).astype(np.uint8)
            # Fill transparent pixels with the mean of opaque pixels
            opaque_mean = gray[self._template_mask > 0].mean()
            gray = gray.copy()
            gray[self._template_mask == 0] = int(opaque_mean)
        else:
            self._template_mask = None

        self._template_gray = gray

    # Downsample factor for the search image.  Matching cost scales with
    # image area, so halving each dimension gives a ~4x speedup while
    # preserving enough detail for the finger icon.
    _SEARCH_DOWNSAMPLE = 2

    def find_finger(
        self,
        screenshot_b64: str,
        screen_width: int,
        screen_height: int,
        confidence_threshold: float = 0.55,
    ) -> FingerMatchResult:
        """
        Find the finger/hand guide icon in a screenshot.

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

        best_confidence = 0.0
        best_location = None  # in search_img coordinates
        best_scale = 1.0      # scale applied to the original 256x256 template
        best_angle = 0.0

        for scale in scale_factors:
            for angle in angles:
                # Resize mean-filled template to match the downsampled search image
                new_w = max(1, int(self._template_gray.shape[1] * scale))
                new_h = max(1, int(self._template_gray.shape[0] * scale))

                resized_tmpl = cv2.resize(self._template_gray, (new_w, new_h), interpolation=cv2.INTER_AREA)

                # Rotate template
                if angle != 0:
                    center = (new_w // 2, new_h // 2)
                    rot_mat = cv2.getRotationMatrix2D(center, -angle, 1.0)

                    cos_a = abs(rot_mat[0, 0])
                    sin_a = abs(rot_mat[0, 1])
                    rot_w = int(new_h * sin_a + new_w * cos_a)
                    rot_h = int(new_h * cos_a + new_w * sin_a)

                    rot_mat[0, 2] += (rot_w - new_w) / 2
                    rot_mat[1, 2] += (rot_h - new_h) / 2

                    # Fill rotation border with template mean so it's neutral
                    # after TM_CCOEFF_NORMED's mean subtraction.
                    fill_val = int(resized_tmpl.mean())
                    resized_tmpl = cv2.warpAffine(
                        resized_tmpl, rot_mat, (rot_w, rot_h),
                        borderMode=cv2.BORDER_CONSTANT, borderValue=fill_val,
                    )

                # Skip if template is larger than search image
                if resized_tmpl.shape[0] > search_img.shape[0] or resized_tmpl.shape[1] > search_img.shape[1]:
                    continue

                # TM_CCOEFF_NORMED: subtracts mean from both template and
                # image patch before correlating.  Mean-filled transparent
                # pixels become ~0 after subtraction, contributing nothing.
                result = cv2.matchTemplate(
                    search_img, resized_tmpl, cv2.TM_CCOEFF_NORMED
                )

                _, max_val, _, max_loc = cv2.minMaxLoc(result)

                if max_val > best_confidence:
                    best_confidence = max_val
                    # max_loc is top-left corner of match; compute center
                    match_center_x = max_loc[0] + resized_tmpl.shape[1] // 2
                    match_center_y = max_loc[1] + resized_tmpl.shape[0] // 2
                    best_location = (match_center_x, match_center_y)
                    # Record the effective full-resolution scale for fingertip offset
                    best_scale = scale * ds
                    best_angle = angle

        if best_confidence < confidence_threshold or best_location is None:
            return FingerMatchResult(found=False, confidence=best_confidence)

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

"""Image Utilities - Image processing helpers."""

import os
import base64
from datetime import datetime

import cv2
import numpy as np


def crop_region(image: np.ndarray, bbox: tuple[int, int, int, int]) -> np.ndarray:
    """Crop image to bounding box region (x1, y1, x2, y2)."""
    x1, y1, x2, y2 = bbox
    return image[y1:y2, x1:x2].copy()


def resize(image: np.ndarray, width: int, height: int) -> np.ndarray:
    """Resize image to given dimensions."""
    return cv2.resize(image, (width, height), interpolation=cv2.INTER_AREA)


def to_base64(image: np.ndarray, fmt: str = ".png") -> str:
    """Convert image to base64 string (for Claude API)."""
    _, buffer = cv2.imencode(fmt, image)
    return base64.b64encode(buffer).decode("utf-8")


def save_debug_image(image: np.ndarray, label: str, output_dir: str = "logs") -> str:
    """Save image with timestamp for debugging. Returns path."""
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
    filename = f"{timestamp}_{label}.png"
    filepath = os.path.join(output_dir, filename)
    cv2.imwrite(filepath, image)
    return filepath

"""Scene Classifier - Classify current game screen into known scene types."""

import logging

import cv2
import numpy as np

from vision.template_matcher import TemplateMatcher

logger = logging.getLogger(__name__)


class SceneClassifier:
    """Classify screenshots into scene types using feature-region template matching.

    Scenes:
        main_city  - Main base/city view
        world_map  - Overworld map view
        battle     - Active battle or battle result screen
        popup      - Dialog/popup overlay
        loading    - Loading/transition screen
        unknown    - Cannot determine
    """

    SCENES = ["main_city", "world_map", "battle", "popup", "loading", "unknown"]

    # Scene-specific feature regions to check (as ratios of screen dimensions).
    # Each scene has characteristic UI elements in predictable positions.
    # Format: (x_ratio, y_ratio, w_ratio, h_ratio)
    SCENE_REGIONS = {
        "main_city": [
            (0.0, 0.0, 1.0, 0.08),   # Top resource bar
            (0.0, 0.85, 0.3, 0.15),   # Bottom-left menu buttons
        ],
        "world_map": [
            (0.0, 0.0, 0.15, 0.08),   # Top-left coordinates display
            (0.85, 0.0, 0.15, 0.08),  # Top-right minimap area
        ],
        "battle": [
            (0.3, 0.0, 0.4, 0.1),    # Top-center battle timer/info
        ],
        "popup": [
            (0.1, 0.1, 0.8, 0.8),    # Central dialog area
        ],
    }

    def __init__(self, template_matcher: TemplateMatcher) -> None:
        self.template_matcher = template_matcher

    def classify(self, screenshot: np.ndarray) -> str:
        """Classify screenshot into one of SCENES.

        Uses a combination of:
        1. Template matching for scene-specific features (scenes/ templates)
        2. Popup detection via semi-transparent overlay analysis
        3. Loading screen detection via color uniformity

        Returns scene name string.
        """
        scores = self.get_confidence(screenshot)

        # Find highest scoring scene
        best_scene = "unknown"
        best_score = 0.0

        for scene, score in scores.items():
            if score > best_score:
                best_score = score
                best_scene = scene

        logger.debug(f"Scene classified: {best_scene} (score={best_score:.3f})")
        return best_scene

    def get_confidence(self, screenshot: np.ndarray) -> dict[str, float]:
        """Return confidence scores for all scenes."""
        h, w = screenshot.shape[:2]
        scores: dict[str, float] = {}

        # 1. Check for popup (darkened/semi-transparent overlay)
        scores["popup"] = self._detect_popup_score(screenshot)

        # 2. Check for loading screen (uniform color, low detail)
        scores["loading"] = self._detect_loading_score(screenshot)

        # 3. Template-based scene detection
        scene_templates = self.template_matcher.match_all(screenshot, "scenes")
        for match in scene_templates:
            # Template names are like "scenes/main_city_resource_bar"
            for scene in self.SCENES:
                if scene in match.template_name:
                    current = scores.get(scene, 0.0)
                    scores[scene] = max(current, match.confidence)

        # 4. Heuristic detection for main_city vs world_map
        if "main_city" not in scores or scores.get("main_city", 0) < 0.5:
            scores["main_city"] = self._heuristic_main_city(screenshot)
        if "world_map" not in scores or scores.get("world_map", 0) < 0.5:
            scores["world_map"] = self._heuristic_world_map(screenshot)

        # Ensure all scenes have a score
        for scene in self.SCENES:
            if scene not in scores:
                scores[scene] = 0.0

        return scores

    def _detect_popup_score(self, screenshot: np.ndarray) -> float:
        """Detect popup overlay by analyzing border darkness.

        Popups typically darken the background around a central dialog.
        """
        h, w = screenshot.shape[:2]
        gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)

        # Check if borders are significantly darker than center
        border_top = gray[0:h//10, :].mean()
        border_bottom = gray[9*h//10:, :].mean()
        border_left = gray[:, 0:w//10].mean()
        border_right = gray[:, 9*w//10:].mean()
        border_mean = (border_top + border_bottom + border_left + border_right) / 4

        center_region = gray[h//4:3*h//4, w//4:3*w//4]
        center_mean = center_region.mean()

        # If center is much brighter than borders -> likely popup
        if center_mean > 50 and border_mean < center_mean * 0.5:
            # Also check for close/X button templates
            close_match = self.template_matcher.match_all(screenshot, "buttons")
            for m in close_match:
                if "close" in m.template_name.lower() or "x" in m.template_name.lower():
                    return max(0.9, m.confidence)
            return 0.7

        return 0.0

    def _detect_loading_score(self, screenshot: np.ndarray) -> float:
        """Detect loading screen by checking color uniformity and low detail."""
        gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)

        # Loading screens tend to have low variance (uniform color)
        std_dev = gray.std()
        if std_dev < 20:
            return 0.8

        # Check for mostly dark or mostly bright screen
        mean_val = gray.mean()
        if mean_val < 30 or mean_val > 240:
            return 0.6

        return 0.0

    def _heuristic_main_city(self, screenshot: np.ndarray) -> float:
        """Heuristic: main city has resource bar at top and is colorful."""
        h, w = screenshot.shape[:2]

        # Check top region for resource bar characteristics
        # Resource bars typically have icons + numbers in a horizontal strip
        top_strip = screenshot[0:h//12, :]
        hsv = cv2.cvtColor(top_strip, cv2.COLOR_BGR2HSV)

        # Resource bars tend to have moderate saturation and varied colors
        saturation = hsv[:, :, 1].mean()
        if saturation > 40:
            return 0.3

        return 0.1

    def _heuristic_world_map(self, screenshot: np.ndarray) -> float:
        """Heuristic: world map has large green/brown terrain areas."""
        h, w = screenshot.shape[:2]
        hsv = cv2.cvtColor(screenshot, cv2.COLOR_BGR2HSV)

        # World maps typically have a lot of green/brown terrain
        # Green hue range: 35-85
        green_mask = cv2.inRange(hsv, (35, 30, 30), (85, 255, 255))
        green_ratio = green_mask.sum() / (255.0 * h * w)

        if green_ratio > 0.3:
            return 0.4

        return 0.1

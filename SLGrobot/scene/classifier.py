"""Scene Classifier - Classify current game screen into known scene types."""

import logging

import cv2
import numpy as np

from vision.template_matcher import TemplateMatcher

logger = logging.getLogger(__name__)


class SceneClassifier:
    """Classify screenshots into scene types using template matching.

    Primary detection: bottom-right corner icon determines main_city vs world_map.
      - "世界" icon visible → main_city
      - "领地" icon visible → world_map
      - Neither → other scene (check further templates)

    Secondary detection: match scene templates for specific sub-scenes
    (hero, hero_recruit, etc.)

    Fallback: popup overlay analysis, loading screen detection.

    Scenes:
        main_city     - Main base/city view (bottom-right shows "世界")
        world_map     - Overworld map view (bottom-right shows "领地")
        hero          - Hero list/management screen
        hero_recruit  - Hero recruitment screen
        battle        - Active battle or battle result screen
        popup         - Dialog/popup overlay
        loading       - Loading/transition screen
        unknown       - Cannot determine
    """

    SCENES = [
        "main_city", "world_map", "hero", "hero_recruit", "hero_upgrade",
        "battle", "popup", "exit_dialog", "loading", "story_dialogue",
        "unknown",
    ]

    # Bottom-right corner region (ratio of screen) for main_city/world_map detection
    CORNER_REGION = (0.78, 0.85, 1.0, 1.0)  # (x1_ratio, y1_ratio, x2_ratio, y2_ratio)

    def __init__(self, template_matcher: TemplateMatcher,
                 game_profile=None) -> None:
        self.template_matcher = template_matcher
        self._scenes = (
            game_profile.scenes
            if game_profile and game_profile.scenes
            else self.SCENES
        )

    def classify(self, screenshot: np.ndarray) -> str:
        """Classify screenshot into one of SCENES.

        Returns scene name string.
        """
        scores = self.get_confidence(screenshot)

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

        # 1. Check for popup (darkened/semi-transparent overlay) — highest priority
        scores["popup"] = self._detect_popup_score(screenshot)
        if scores["popup"] >= 0.7:
            # Popup detected with high confidence, skip further checks
            for scene in self._scenes:
                if scene not in scores:
                    scores[scene] = 0.0
            return scores

        # 2. Check for exit dialog (dark background with blue play icons).
        #    Must come before loading detection — the dark background would
        #    trigger loading misclassification (mean_val < 30 → 0.6).
        scores["exit_dialog"] = self._detect_exit_dialog_score(screenshot)
        if scores["exit_dialog"] >= 0.7:
            for scene in self._scenes:
                if scene not in scores:
                    scores[scene] = 0.0
            return scores

        # 3. Check for loading screen
        scores["loading"] = self._detect_loading_score(screenshot)
        if scores["loading"] >= 0.7:
            for scene in self._scenes:
                if scene not in scores:
                    scores[scene] = 0.0
            return scores

        # 4. Story dialogue: detected by the down-triangle "continue" icon
        triangle_match = self.template_matcher.match_one(screenshot, "icons/down_triangle")
        if triangle_match and triangle_match.confidence >= 0.9:
            scores["story_dialogue"] = triangle_match.confidence
            for scene in self._scenes:
                if scene not in scores:
                    scores[scene] = 0.0
            return scores

        # 5. Primary: bottom-right corner icon → main_city or world_map
        rx1, ry1, rx2, ry2 = self.CORNER_REGION
        corner = screenshot[int(ry1*h):int(ry2*h), int(rx1*w):int(rx2*w)]

        main_city_match = self.template_matcher.match_one(corner, "scenes/main_city")
        world_map_match = self.template_matcher.match_one(corner, "scenes/world_map")

        scores["main_city"] = main_city_match.confidence if main_city_match else 0.0
        scores["world_map"] = world_map_match.confidence if world_map_match else 0.0

        if scores["main_city"] >= 0.5 or scores["world_map"] >= 0.5:
            # One of the two primary scenes detected, done
            for scene in self._scenes:
                if scene not in scores:
                    scores[scene] = 0.0
            return scores

        # 6. Secondary: check other scene templates on full screenshot
        scene_templates = self.template_matcher.match_all(screenshot, "scenes")
        for match in scene_templates:
            # Template names like "scenes/hero", "scenes/hero_recruit"
            name = match.template_name.split("/")[-1] if "/" in match.template_name else match.template_name
            if name in ("main_city", "world_map"):
                continue  # Already handled by corner detection
            if name in self._scenes:
                current = scores.get(name, 0.0)
                scores[name] = max(current, match.confidence)

        # Ensure all scenes have a score
        for scene in self._scenes:
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

    def _detect_exit_dialog_score(self, screenshot: np.ndarray) -> float:
        """Detect the game's exit/pause dialog.

        The exit dialog has a dark background with three blue square icons
        (退出 / 重新开始 / 继续).  We use template matching on the play icon
        (scenes/exit_dialog) in the center-lower region of the screen.
        """
        match = self.template_matcher.match_one(screenshot, "scenes/exit_dialog")
        if match and match.confidence >= 0.8:
            logger.debug(
                f"Exit dialog detected: conf={match.confidence:.3f} "
                f"at ({match.x}, {match.y})"
            )
            return match.confidence
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

"""Screen DOM Builder — unified screen understanding pipeline.

Takes a screenshot and produces a structured YAML DOM describing all
interactive elements on screen: text, icons, buttons, indicators, and
tutorial finger. Elements are organized into spatial regions (top_bar,
center, bottom_bar) with an optional popup overlay section.
"""

import logging
import math
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass

import cv2
import numpy as np
import yaml

from vision.ocr_locator import OCRLocator, OCRResult
from vision.template_matcher import TemplateMatcher, MatchResult
from vision.button_detector import ButtonDetector, ButtonElement
from vision.indicator_detector import IndicatorDetector, IndicatorElement
from vision.popup_detector import PopupDetector
from brain.finger_detector import FingerDetector

logger = logging.getLogger(__name__)


# Radius for associating indicators with nearby elements
INDICATOR_NEAR_RADIUS = 80


def infer_scene(dom: dict, screenshot: np.ndarray) -> str:
    """Infer scene from DOM elements and screenshot pixels.

    Called at end of build() to set dom["screen"]["scene"].
    Detection priority: popup > exit_dialog > loading > story_dialogue >
    shoot_mini_game > main_city > world_map > hero_recruit > hero_upgrade >
    hero > unknown.
    """
    screen = dom.get("screen", {})

    # 1. Popup already detected by PopupDetector
    if "popup" in screen:
        return "popup"

    # Collect icon names from all DOM elements
    icon_names = set()
    for region in ("top_bar", "center", "bottom_bar"):
        for elem in screen.get(region, []):
            if elem.get("type") == "icon":
                icon_names.add(elem["name"])
    # Also check popup children (in case popup has icons)
    popup = screen.get("popup")
    if popup:
        for elem in popup.get("children", []):
            if elem.get("type") == "icon":
                icon_names.add(elem["name"])

    # 2. Exit dialog
    if "exit_dialog" in icon_names:
        return "exit_dialog"

    # 3. Loading — pixel analysis (no DOM indicator)
    # Guard: if buttons with text exist, it's a dark popup (e.g. reward
    # screen), not a loading screen.
    gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
    if gray.std() < 20 or gray.mean() < 30 or gray.mean() > 240:
        has_buttons = any(
            elem.get("type") == "button" and elem.get("text")
            for region in ("top_bar", "center", "bottom_bar")
            for elem in screen.get(region, [])
        )
        if has_buttons:
            return "popup"
        return "loading"

    # 4. Story dialogue
    if "down_triangle" in icon_names:
        return "story_dialogue"

    # 5. Shoot mini game (westgame2)
    if "shoot_mini_game" in icon_names:
        return "shoot_mini_game"

    # 6. Building upgrade panel — "升级" button in known positions:
    #    - right-center (x>700, 800<y<1050): side panel layout
    #    - bottom-center (x<700, y>1700): bottom panel layout
    for region in ("top_bar", "center", "bottom_bar"):
        for elem in screen.get(region, []):
            if (elem.get("type") == "button"
                    and "升级" in elem.get("text", "")
                    and elem.get("size", [0, 0])[0] > 150):
                ex, ey = elem.get("pos", [0, 0])
                if ((ex > 700 and 800 < ey < 1050)
                        or (ex < 700 and ey > 1700)):
                    return "building_upgrade"

    # 7-8. Primary scenes
    if "world" in icon_names:
        return "main_city"
    if "territory" in icon_names:
        return "world_map"

    # 8-10. Secondary scenes
    for scene_name in ("hero_recruit", "hero_upgrade", "hero"):
        if scene_name in icon_names:
            return scene_name

    return "unknown"


class ScreenDOMBuilder:
    """Build a structured DOM from a screenshot.

    Pipeline:
      1. Popup detection
      2. OCR (all text)
      3. Template matching (all icons)
      4. Button detection (HSV + contour + OCR)
      5. Indicator detection (red dots, green checks)
      6. Finger detection (3-stage)
      7. Assemble into spatial regions → YAML
    """

    def __init__(self, ocr_locator: OCRLocator,
                 template_matcher: TemplateMatcher,
                 finger_detector: FingerDetector,
                 game_profile=None) -> None:
        self.ocr = ocr_locator
        self.tm = template_matcher
        self.finger_detector = finger_detector
        self.button_detector = ButtonDetector()
        self.indicator_detector = IndicatorDetector()
        self.popup_detector = PopupDetector()

        # Region boundaries (configurable via game_profile in Phase 4)
        self.top_y = 200
        self.bottom_y = 1700

    def build(self, screenshot: np.ndarray) -> dict:
        """Full pipeline: screenshot → DOM dict.

        Args:
            screenshot: BGR numpy array (1080x1920).

        Returns:
            Nested dict representing the screen DOM.
        """
        h, w = screenshot.shape[:2]

        # 1. Popup detection (fast, ~7ms)
        popup_bounds = self.popup_detector.detect(screenshot)

        # 2-6. Run heavy operations in parallel threads
        # OCR, template matching, and finger detection are independent
        # and CPU-bound (but release GIL during C library calls)
        with ThreadPoolExecutor(max_workers=3) as pool:
            fut_ocr = pool.submit(self.ocr.find_all_text, screenshot)
            fut_icons = pool.submit(self._match_all_fast, screenshot)
            fut_finger = pool.submit(self.finger_detector.detect, screenshot)

            all_texts = fut_ocr.result()
            all_icons = fut_icons.result()
            finger_result = fut_finger.result()

        finger_match, flip_type = finger_result

        # Button + indicator detection (fast, use OCR results)
        buttons = self.button_detector.detect(screenshot, all_texts)
        indicators = self.indicator_detector.detect(screenshot)

        # 7. Subtract OCR texts that are already inside buttons
        free_texts = self._subtract_button_texts(all_texts, buttons)

        # 8. Build element list
        elements = []

        # Add free text elements
        for t in free_texts:
            elements.append({
                "type": "text",
                "value": t.text,
                "pos": list(t.center),
                "size": [t.bbox[2] - t.bbox[0], t.bbox[3] - t.bbox[1]],
            })

        # Add icon elements
        for icon in all_icons:
            elements.append({
                "type": "icon",
                "name": icon.template_name,
                "pos": [icon.x, icon.y],
                "confidence": round(icon.confidence, 2),
            })

        # Add button elements
        for btn in buttons:
            elements.append({
                "type": "button",
                "text": btn.text,
                "pos": list(btn.pos),
                "size": list(btn.size),
                "color": btn.color,
            })

        # Add indicator elements
        for ind in indicators:
            elem = {
                "type": ind.type,
                "pos": list(ind.pos),
            }
            # Associate with nearest element
            near = self._find_nearest(ind.pos, elements)
            if near:
                elem["near"] = near
            elements.append(elem)

        # Add finger element
        if finger_match is not None:
            tip = self.finger_detector.fingertip_pos(
                finger_match.x, finger_match.y, flip_type
            )
            elements.append({
                "type": "finger",
                "pos": [finger_match.x, finger_match.y],
                "fingertip": list(tip),
            })

        # 9. Assign elements to regions
        dom = {
            "screen": {
                "resolution": [w, h],
                "scene": "unknown",  # set by infer_scene() below
            }
        }

        if popup_bounds:
            # Split elements: inside popup vs outside
            px1, py1, px2, py2 = popup_bounds
            popup_elements = []
            outside_elements = []
            for elem in elements:
                ex, ey = elem["pos"]
                if px1 <= ex <= px2 and py1 <= ey <= py2:
                    popup_elements.append(elem)
                else:
                    outside_elements.append(elem)

            dom["screen"]["popup"] = {
                "bounds": list(popup_bounds),
                "children": popup_elements,
            }
            # Still assign outside elements to regions
            self._assign_regions(dom, outside_elements)
        else:
            self._assign_regions(dom, elements)

        dom["screen"]["scene"] = infer_scene(dom, screenshot)
        logger.debug("DOM result:\n%s", self.to_yaml(dom))
        return dom

    def to_yaml(self, dom: dict) -> str:
        """Serialize DOM dict to YAML string.

        Uses block style for readability, but flow style for short lists
        like pos: [x, y] and size: [w, h].
        """
        return yaml.dump(
            dom,
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False,
            Dumper=_DOMDumper,
        )

    def _assign_regions(self, dom: dict, elements: list[dict]) -> None:
        """Assign elements to top_bar / center / bottom_bar by Y position."""
        top = []
        center = []
        bottom = []

        for elem in elements:
            y = elem["pos"][1]
            if y < self.top_y:
                top.append(elem)
            elif y > self.bottom_y:
                bottom.append(elem)
            else:
                center.append(elem)

        if top:
            dom["screen"]["top_bar"] = top
        if center:
            dom["screen"]["center"] = center
        if bottom:
            dom["screen"]["bottom_bar"] = bottom

    def _subtract_button_texts(self, all_texts: list[OCRResult],
                                buttons: list[ButtonElement],
                                ) -> list[OCRResult]:
        """Remove OCR results that fall inside a detected button."""
        if not buttons:
            return list(all_texts)

        free = []
        for t in all_texts:
            cx, cy = t.center
            inside = False
            for btn in buttons:
                bx1 = btn.pos[0] - btn.size[0] // 2
                by1 = btn.pos[1] - btn.size[1] // 2
                bx2 = bx1 + btn.size[0]
                by2 = by1 + btn.size[1]
                if bx1 <= cx <= bx2 and by1 <= cy <= by2:
                    inside = True
                    break
            if not inside:
                free.append(t)
        return free

    # --- Fast template matching with prescreening ---

    _MATCH_SCALE = 0.5  # match at half resolution for speed

    def _match_all_fast(self, screenshot: np.ndarray) -> list[MatchResult]:
        """Match all templates at 0.5x resolution for speed (~1s).

        Matching at half resolution is ~4x faster than full-res.
        For hits, refine position by running a small ROI match at full-res.

        Finger templates are excluded (handled separately by FingerDetector).
        """
        sh, sw = screenshot.shape[:2]
        scale = self._MATCH_SCALE
        small = cv2.resize(
            screenshot, (int(sw * scale), int(sh * scale)),
            interpolation=cv2.INTER_AREA,
        )
        small_h, small_w = small.shape[:2]

        # Build scaled template cache on first call
        if not hasattr(self, "_scaled_cache"):
            self._scaled_cache: dict[str, tuple[np.ndarray, np.ndarray | None, bool]] = {}
            for name, (template, mask) in self.tm._cache.items():
                if "tutorial_finger" in name:
                    continue
                th, tw = template.shape[:2]
                s_tw = max(1, int(tw * scale))
                s_th = max(1, int(th * scale))
                if s_tw < 4 or s_th < 4:
                    continue
                s_tpl = cv2.resize(template, (s_tw, s_th),
                                   interpolation=cv2.INTER_AREA)
                s_mask = None
                # Track whether this template needs NCC verification
                # (masked with <90% opaque pixels)
                needs_ncc = False
                if mask is not None:
                    s_mask = cv2.resize(mask, (s_tw, s_th),
                                       interpolation=cv2.INTER_AREA)
                    opaque_ratio = float((mask[:, :, 0] > 0).sum()) / (th * tw)
                    needs_ncc = opaque_ratio < 0.9
                self._scaled_cache[name] = (s_tpl, s_mask, needs_ncc)

        threshold = self.tm.threshold
        results = []

        for name, (s_tpl, s_mask, needs_ncc) in self._scaled_cache.items():
            s_th, s_tw = s_tpl.shape[:2]
            if s_tw >= small_w or s_th >= small_h:
                continue
            try:
                if s_mask is not None:
                    res = cv2.matchTemplate(
                        small, s_tpl, cv2.TM_CCORR_NORMED, mask=s_mask)
                else:
                    res = cv2.matchTemplate(
                        small, s_tpl, cv2.TM_CCOEFF_NORMED)
                _, max_val, _, max_loc = cv2.minMaxLoc(res)
                if max_val < threshold:
                    continue
            except cv2.error:
                continue

            # Hit at half-res → refine at full-res using ROI
            sx, sy = max_loc
            entry = self.tm._cache[name]
            template, mask = entry
            th, tw = template.shape[:2]

            # ROI around the hit location, with margin
            margin = max(tw, th)
            roi_x1 = max(0, int(sx / scale) - margin)
            roi_y1 = max(0, int(sy / scale) - margin)
            roi_x2 = min(sw, int(sx / scale) + tw + margin)
            roi_y2 = min(sh, int(sy / scale) + th + margin)
            roi = screenshot[roi_y1:roi_y2, roi_x1:roi_x2]

            if roi.shape[0] < th or roi.shape[1] < tw:
                # ROI too small, use half-res coordinates
                fx = int(sx / scale) + tw // 2
                fy = int(sy / scale) + th // 2
                results.append(MatchResult(
                    template_name=name,
                    confidence=float(max_val),
                    x=fx, y=fy,
                    bbox=(fx - tw // 2, fy - th // 2, fx + tw // 2, fy + th // 2),
                ))
                continue

            try:
                if mask is not None:
                    roi_res = cv2.matchTemplate(
                        roi, template, cv2.TM_CCORR_NORMED, mask=mask)
                else:
                    roi_res = cv2.matchTemplate(
                        roi, template, cv2.TM_CCOEFF_NORMED)
                _, roi_max, _, roi_loc = cv2.minMaxLoc(roi_res)
                if roi_max >= threshold:
                    rx, ry = roi_loc
                    # NCC verification for low-opacity masked templates
                    if needs_ncc:
                        crop = roi[ry:ry + th, rx:rx + tw]
                        if crop.shape[:2] != (th, tw):
                            continue
                        opaque_mask = mask[:, :, 0] > 0
                        ncc = TemplateMatcher.compute_masked_ncc(
                            template, crop, opaque_mask)
                        if ncc < TemplateMatcher._MASKED_NCC_THRESHOLD:
                            logger.debug(
                                f"_match_all_fast NCC rejected: {name} "
                                f"CCORR={roi_max:.3f} ncc={ncc:.3f}")
                            continue
                    abs_x = roi_x1 + rx + tw // 2
                    abs_y = roi_y1 + ry + th // 2
                    results.append(MatchResult(
                        template_name=name,
                        confidence=float(roi_max),
                        x=abs_x, y=abs_y,
                        bbox=(abs_x - tw // 2, abs_y - th // 2,
                              abs_x + tw // 2, abs_y + th // 2),
                    ))
            except cv2.error:
                continue

        results.sort(key=lambda r: r.confidence, reverse=True)
        logger.debug(
            f"Template matching: {len(self._scaled_cache)} templates → "
            f"{len(results)} matches (scale={scale})"
        )
        return results

    def _find_nearest(self, pos: tuple[int, int],
                      elements: list[dict]) -> str | None:
        """Find the nearest named element within INDICATOR_NEAR_RADIUS."""
        best_dist = INDICATOR_NEAR_RADIUS
        best_name = None

        for elem in elements:
            # Only associate with named elements (icons and buttons with text)
            name = elem.get("name") or elem.get("text")
            if not name:
                continue
            if elem["type"] in ("red_dot", "green_check"):
                continue  # don't associate indicators with each other

            ex, ey = elem["pos"]
            dist = math.sqrt((pos[0] - ex) ** 2 + (pos[1] - ey) ** 2)
            if dist < best_dist:
                best_dist = dist
                best_name = name

        return best_name


class _DOMDumper(yaml.SafeDumper):
    """Custom YAML dumper that uses flow style for short lists."""
    pass


def _represent_list(dumper: yaml.SafeDumper, data: list):
    """Use flow style for short lists (pos, size, bounds, resolution)."""
    # Short numeric lists → flow style [x, y]
    if len(data) <= 4 and all(isinstance(x, (int, float)) for x in data):
        return dumper.represent_sequence(
            "tag:yaml.org,2002:seq", data, flow_style=True
        )
    return dumper.represent_sequence(
        "tag:yaml.org,2002:seq", data, flow_style=False
    )


_DOMDumper.add_representer(list, _represent_list)

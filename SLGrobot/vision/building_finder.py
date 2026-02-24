"""Building Finder - Find and tap buildings on the scrollable city map.

The city map is larger than the screen and scrollable in all directions.
Building names are only visible when the player presses and slightly drags
on the screen. When the finger is released, names disappear.

Algorithm:
1. press_drag_read: press+drag to reveal names, OCR, find target
2. navigate: detect current position via visible buildings, scroll to target
3. find_and_tap: combine press_drag_read + navigate + tap

Uses a threaded approach: the ADB swipe blocks for the hold duration,
so we run it in a background thread and take a screenshot from the main
thread while the finger is still down.
"""

import logging
import re
import threading
import time

import numpy as np

from device.adb_controller import ADBController
from vision.ocr_locator import OCRLocator, OCRResult

logger = logging.getLogger(__name__)

# Default configuration values
_DEFAULTS = {
    "reference_building": "城堡",
    "pixels_per_unit": 400,
    "hold_point": [540, 960],
    "hold_duration_ms": 3000,
    "screenshot_delay_ms": 1400,
    "drag_offset": 150,
    "tap_offset_x": 150,
    "tap_offset_y": 150,
}


def parse_city_layout(md_path: str,
                      reference_building: str = "城堡",
                      pixels_per_unit: float = 400,
                      ) -> dict[str, tuple[float, float]]:
    """Parse a markdown table into {building_name: (offset_x, offset_y)}.

    The MD table uses alternating cells (chess board pattern) where
    buildings sit on "black squares", directly matching the isometric
    game view.

    Returns pixel offsets relative to the reference building.
    """
    with open(md_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Extract table rows (lines containing |)
    table_rows: list[list[str]] = []
    for line in lines:
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        # Skip separator rows (|---|---|...)
        if re.match(r"^\|[\s\-|]+\|$", stripped):
            continue
        # Split by | and strip
        cells = [c.strip() for c in stripped.split("|")]
        # Remove leading/trailing empty cells from split
        if cells and cells[0] == "":
            cells = cells[1:]
        if cells and cells[-1] == "":
            cells = cells[:-1]
        table_rows.append(cells)

    if not table_rows:
        logger.warning(f"No table rows found in {md_path}")
        return {}

    # Find all buildings and the reference position
    buildings: dict[str, tuple[int, int]] = {}
    ref_row: int | None = None
    ref_col: int | None = None

    for row_idx, row in enumerate(table_rows):
        for col_idx, cell in enumerate(row):
            name = cell.strip()
            if not name:
                continue
            # Skip header cells that are just numbers
            if re.match(r"^\d+$", name):
                continue
            buildings[name] = (row_idx, col_idx)
            if name == reference_building:
                ref_row, ref_col = row_idx, col_idx

    if ref_row is None or ref_col is None:
        logger.warning(
            f"Reference building '{reference_building}' not found in {md_path}"
        )
        # Use first building as reference
        if buildings:
            first = next(iter(buildings))
            ref_row, ref_col = buildings[first]
            logger.info(f"Using '{first}' as fallback reference")
        else:
            return {}

    # Convert to pixel offsets from reference
    result: dict[str, tuple[float, float]] = {}
    for name, (r, c) in buildings.items():
        result[name] = (
            (c - ref_col) * pixels_per_unit,   # x offset
            (r - ref_row) * pixels_per_unit,    # y offset
        )

    logger.info(
        f"Parsed city layout: {len(result)} buildings, "
        f"reference='{reference_building}' at grid ({ref_row}, {ref_col})"
    )
    return result


class BuildingFinder:
    """Find and tap buildings on the scrollable city map.

    Uses press-drag-read to reveal building names, OCR to detect them,
    and layout-based navigation to scroll to the target area.
    """

    def __init__(self,
                 adb: ADBController,
                 ocr: OCRLocator,
                 city_layout_config: dict,
                 layout_data: dict[str, tuple[float, float]],
                 ) -> None:
        """
        Args:
            adb: ADB controller for tap/swipe/screenshot.
            ocr: OCR locator for text detection.
            city_layout_config: Config dict from game.json ``city_layout``.
            layout_data: Parsed layout from :func:`parse_city_layout`.
        """
        self.adb = adb
        self.ocr = ocr
        self.layout = layout_data
        self._building_names = list(layout_data.keys())

        # Configuration with defaults
        cfg = {**_DEFAULTS, **city_layout_config}
        self.hold_point: tuple[int, int] = tuple(cfg["hold_point"])
        self.hold_duration_ms: int = int(cfg["hold_duration_ms"])
        self.screenshot_delay_ms: int = int(cfg["screenshot_delay_ms"])
        self.drag_offset: int = int(cfg["drag_offset"])
        self.tap_offset_x: int = int(cfg.get("tap_offset_x", 150))
        self.tap_offset_y: int = int(cfg.get("tap_offset_y", 150))

    # --- Public API ---

    def find_and_tap(self, target_name: str,
                     scroll: bool = True,
                     max_attempts: int = 3) -> bool:
        """Find a building by name and tap it.

        Strategy:
        1. Press-drag-read to check if target is already visible
        2. If not visible and scroll=True, use layout to navigate
        3. Press-drag-read again to find and tap
        4. Fall back to spiral search if layout navigation fails

        Args:
            target_name: Building name to find (Chinese).
            scroll: Whether to scroll the map to find the building.
            max_attempts: Maximum press-drag-read attempts.

        Returns:
            True if building was found and tapped.
        """
        logger.info(f"BuildingFinder: looking for '{target_name}'")

        # Attempt 1: check if already visible
        pos = self._press_drag_read(target_name)
        if pos is not None:
            time.sleep(0.3)
            self.adb.tap(pos[0], pos[1])
            logger.info(
                f"BuildingFinder: tapped '{target_name}' at {pos} "
                f"(visible without scrolling)"
            )
            return True

        if not scroll:
            logger.info(
                f"BuildingFinder: '{target_name}' not visible, scroll=False"
            )
            return False

        # Attempt 2: navigate using layout, then press-drag-read
        if target_name in self.layout:
            if self._navigate_to(target_name):
                time.sleep(0.5)
                pos = self._press_drag_read(target_name)
                if pos is not None:
                    time.sleep(0.3)
                    self.adb.tap(pos[0], pos[1])
                    logger.info(
                        f"BuildingFinder: tapped '{target_name}' at {pos} "
                        f"(after layout navigation)"
                    )
                    return True

        # Attempt 3: spiral search
        logger.info(
            f"BuildingFinder: '{target_name}' not found via layout, "
            f"trying spiral search"
        )
        return self._spiral_search(target_name, max_steps=max_attempts * 4)

    def read_all_buildings(self) -> list[tuple[str, int, int]]:
        """Press-drag-read and return all visible building names + positions.

        Useful for debugging and calibration.

        Returns:
            List of (name, x, y) tuples.
        """
        results = self._read_all_buildings_raw()
        out: list[tuple[str, int, int]] = []
        for r in results:
            cx, cy = r.center
            matched = self._match_building_name(r.text)
            name = matched if matched else r.text
            out.append((name, cx, cy))
        return out

    # --- Internal ---

    def _press_drag_read(self, target_name: str) -> tuple[int, int] | None:
        """Press+drag to reveal names, screenshot, OCR, find target.

        Runs the swipe in a background thread so we can take a screenshot
        while the finger is still down (names visible).

        Returns:
            (x, y) tap position if target found, None otherwise.
        """
        hx, hy = self.hold_point
        dx = self.drag_offset

        # Start press+drag in background thread
        thread = threading.Thread(
            target=self.adb.swipe,
            args=(hx, hy, hx + dx, hy + dx, self.hold_duration_ms),
            daemon=True,
        )
        thread.start()

        # Wait for names to render
        time.sleep(self.screenshot_delay_ms / 1000.0)

        # Take screenshot while finger is still down
        try:
            screenshot = self.adb.screenshot()
        except Exception as e:
            logger.warning(f"BuildingFinder: screenshot during hold failed: {e}")
            thread.join(timeout=5)
            return None

        # OCR to find all text on screen
        all_text = self.ocr.find_all_text(screenshot)

        # Wait for swipe to complete (finger releases)
        thread.join(timeout=5)

        # Compensate for map drift: after the screenshot the swipe
        # continues, shifting the map further.  The map content follows
        # the finger, so buildings move in the swipe direction.
        remaining = 1.0 - (self.screenshot_delay_ms / self.hold_duration_ms)
        drift = int(self.drag_offset * remaining)

        # Search for target building name
        target_lower = target_name.lower()
        for result in all_text:
            if target_lower in result.text.lower():
                x1, y1 = result.bbox[0], result.bbox[1]
                tap_x = x1 + self.tap_offset_x + drift
                tap_y = y1 + self.tap_offset_y + drift
                logger.info(
                    f"BuildingFinder: found '{target_name}' in OCR "
                    f"text='{result.text}' bbox={result.bbox}, "
                    f"drift={drift}, tap at ({tap_x}, {tap_y})"
                )
                return (tap_x, tap_y)

        # Also try fuzzy matching against known building names
        for result in all_text:
            matched = self._match_building_name(result.text)
            if matched and target_lower in matched.lower():
                x1, y1 = result.bbox[0], result.bbox[1]
                tap_x = x1 + self.tap_offset_x + drift
                tap_y = y1 + self.tap_offset_y + drift
                logger.info(
                    f"BuildingFinder: fuzzy matched '{target_name}' via "
                    f"'{result.text}' -> '{matched}' bbox={result.bbox}, "
                    f"drift={drift}, tap at ({tap_x}, {tap_y})"
                )
                return (tap_x, tap_y)

        logger.debug(
            f"BuildingFinder: '{target_name}' not found in "
            f"{len(all_text)} OCR results"
        )
        return None

    def _read_all_buildings_raw(self) -> list[OCRResult]:
        """Press+drag, screenshot, return all OCR results."""
        hx, hy = self.hold_point
        dx = self.drag_offset

        thread = threading.Thread(
            target=self.adb.swipe,
            args=(hx, hy, hx + dx, hy + dx, self.hold_duration_ms),
            daemon=True,
        )
        thread.start()

        time.sleep(self.screenshot_delay_ms / 1000.0)

        try:
            screenshot = self.adb.screenshot()
        except Exception as e:
            logger.warning(f"BuildingFinder: screenshot during hold failed: {e}")
            thread.join(timeout=5)
            return []

        all_text = self.ocr.find_all_text(screenshot)
        thread.join(timeout=5)

        return all_text

    def _estimate_position(self,
                           visible_buildings: list[OCRResult],
                           ) -> tuple[float, float]:
        """Estimate viewport center from visible building names.

        For each recognized building, calculate where the viewport center
        must be based on the building's screen position and its layout
        position. Average all estimates for robustness.
        """
        screen_cx, screen_cy = 540, 960  # screen center
        estimates: list[tuple[float, float]] = []

        for result in visible_buildings:
            cx, cy = result.center
            name = self._match_building_name(result.text)
            if name and name in self.layout:
                layout_x, layout_y = self.layout[name]
                # Building appears at (cx, cy) on screen.
                # Viewport center in layout coords:
                viewport_x = layout_x - (cx - screen_cx)
                viewport_y = layout_y - (cy - screen_cy)
                estimates.append((viewport_x, viewport_y))

        if not estimates:
            return (0.0, 0.0)  # assume near reference building

        avg_x = sum(e[0] for e in estimates) / len(estimates)
        avg_y = sum(e[1] for e in estimates) / len(estimates)
        logger.debug(
            f"BuildingFinder: position estimate ({avg_x:.0f}, {avg_y:.0f}) "
            f"from {len(estimates)} buildings"
        )
        return (avg_x, avg_y)

    def _navigate_to(self, target_name: str) -> bool:
        """Scroll map to bring target building into view.

        1. Read visible buildings to estimate current viewport position
        2. Calculate delta to target building
        3. Execute swipe (drag direction is opposite to desired movement)
        """
        visible = self._read_all_buildings_raw()
        current = self._estimate_position(visible)

        target = self.layout.get(target_name)
        if not target:
            logger.warning(
                f"BuildingFinder: '{target_name}' not in layout"
            )
            return False

        dx = target[0] - current[0]
        dy = target[1] - current[1]

        # Skip if delta is very small (already nearby)
        if abs(dx) < 50 and abs(dy) < 50:
            logger.debug("BuildingFinder: target already nearby, skip scroll")
            return True

        # Swipe direction is opposite: drag map left to see right
        self._scroll_by(-dx, -dy)
        logger.info(
            f"BuildingFinder: navigated toward '{target_name}' "
            f"delta=({dx:.0f}, {dy:.0f})"
        )
        return True

    def _scroll_by(self, dx: float, dy: float) -> None:
        """Execute a swipe to scroll the map by pixel delta.

        Clamps swipe to safe screen area and splits large scrolls
        into multiple swipes.
        """
        # Max pixels per single swipe (to stay in safe screen area)
        max_swipe = 400
        sx, sy = 540, 960  # swipe start (screen center)

        remaining_dx = dx
        remaining_dy = dy

        while abs(remaining_dx) > 20 or abs(remaining_dy) > 20:
            # Clamp this step
            step_dx = max(-max_swipe, min(max_swipe, remaining_dx))
            step_dy = max(-max_swipe, min(max_swipe, remaining_dy))

            ex = int(sx + step_dx)
            ey = int(sy + step_dy)

            # Clamp end point to screen bounds
            ex = max(100, min(980, ex))
            ey = max(300, min(1600, ey))

            self.adb.swipe(sx, sy, ex, ey, 400)
            time.sleep(0.3)

            remaining_dx -= step_dx
            remaining_dy -= step_dy

    def _spiral_search(self, target_name: str,
                       max_steps: int = 12) -> bool:
        """Search for building using expanding spiral swipe pattern.

        Fallback when layout navigation fails.
        """
        step_size = 300

        for dx, dy in self._spiral_pattern(step_size, max_steps):
            self._scroll_by(dx, dy)
            time.sleep(0.5)
            pos = self._press_drag_read(target_name)
            if pos is not None:
                time.sleep(0.3)
                self.adb.tap(pos[0], pos[1])
                logger.info(
                    f"BuildingFinder: tapped '{target_name}' at {pos} "
                    f"(found via spiral search)"
                )
                return True

        logger.warning(
            f"BuildingFinder: '{target_name}' not found after "
            f"{max_steps} spiral steps"
        )
        return False

    def _spiral_pattern(self, step_size: int,
                        max_steps: int) -> list[tuple[int, int]]:
        """Generate expanding spiral search swipe vectors.

        Pattern: right, down, left*2, up*2, right*3, down*3, ...
        """
        directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]  # R, D, L, U
        pattern: list[tuple[int, int]] = []
        steps_in_leg = 1
        dir_idx = 0
        turns = 0

        while len(pattern) < max_steps:
            ddx, ddy = directions[dir_idx % 4]
            for _ in range(steps_in_leg):
                if len(pattern) >= max_steps:
                    break
                pattern.append((ddx * step_size, ddy * step_size))
            dir_idx += 1
            turns += 1
            if turns % 2 == 0:
                steps_in_leg += 1

        return pattern

    def _match_building_name(self, ocr_text: str) -> str | None:
        """Fuzzy match OCR text against known building names.

        Handles partial matches and common OCR errors.
        """
        text = ocr_text.strip()
        if not text:
            return None

        # Exact match
        if text in self.layout:
            return text

        # Substring match: OCR text contains a building name
        for name in self._building_names:
            if name in text:
                return name

        # Reverse: building name contains OCR text (OCR truncation)
        if len(text) >= 2:
            for name in self._building_names:
                if text in name:
                    return name

        return None

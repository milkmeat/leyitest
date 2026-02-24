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
    "safe_zone": [100, 200, 900, 1500],
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
            # Skip header cells that are just numbers (including negative)
            if re.match(r"^-?\d+$", name):
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
        sz = cfg.get("safe_zone", [100, 200, 900, 1500])
        self.safe_zone: tuple[int, int, int, int] = (
            int(sz[0]), int(sz[1]), int(sz[2]), int(sz[3]),
        )

    # --- Public API ---

    def find_and_tap(self, target_name: str,
                     scroll: bool = True,
                     max_attempts: int = 5) -> bool:
        """Find a building by name and tap it.

        Iterative strategy:
        1. Press-drag-read — check if target is visible, also collect
           all visible buildings for position estimation.
        2. If found, tap and return.
        3. If not found and scroll=True, estimate current viewport
           position from visible buildings, calculate delta to target,
           scroll, and repeat from step 1.

        Each press-drag-read shifts the map slightly, so position is
        re-estimated every iteration.

        Args:
            target_name: Building name to find (Chinese).
            scroll: Whether to scroll the map to find the building.
            max_attempts: Maximum navigation iterations.

        Returns:
            True if building was found and tapped.
        """
        logger.info(f"BuildingFinder: looking for '{target_name}'")

        for attempt in range(max_attempts):
            # Press-drag-read: look for target AND collect visible buildings
            all_text, pos = self._press_drag_read_full(target_name)

            if pos is not None:
                time.sleep(0.3)
                self.adb.tap(pos[0], pos[1])
                logger.info(
                    f"BuildingFinder: tapped '{target_name}' at {pos} "
                    f"(attempt {attempt + 1})"
                )
                return True

            if not scroll or target_name not in self.layout:
                break

            # Log recognized buildings for debugging
            matched = []
            for r in all_text:
                name = self._match_building_name(r.text)
                if name:
                    cx, cy = r.center
                    sz = "ok" if self._in_safe_zone(cx, cy) else "OUT"
                    matched.append(f"{name}({cx},{cy})[{sz}]")
            logger.debug(
                f"BuildingFinder: visible buildings: [{', '.join(matched)}]"
            )

            # Estimate current position from visible buildings
            current = self._estimate_position(all_text)
            target = self.layout[target_name]
            dx = target[0] - current[0]
            dy = target[1] - current[1]

            if abs(dx) < 50 and abs(dy) < 50:
                logger.info(
                    f"BuildingFinder: should be nearby but not found "
                    f"(delta={dx:.0f},{dy:.0f})"
                )
                break

            logger.info(
                f"BuildingFinder: attempt {attempt + 1}, "
                f"delta=({dx:.0f}, {dy:.0f}), scrolling..."
            )
            self._scroll_by(-dx, -dy)
            time.sleep(0.5)

        logger.warning(
            f"BuildingFinder: '{target_name}' not found after "
            f"{max_attempts} attempts"
        )
        return False

    def read_all_buildings(self) -> list[tuple[str, int, int]]:
        """Press-drag-read and return all visible building names + positions.

        Useful for debugging and calibration.

        Returns:
            List of (name, x, y) tuples.
        """
        all_text, _ = self._press_drag_read_full(None)
        out: list[tuple[str, int, int]] = []
        for r in all_text:
            cx, cy = r.center
            matched = self._match_building_name(r.text)
            name = matched if matched else r.text
            out.append((name, cx, cy))
        return out

    # --- Internal ---

    def _press_drag_read_full(
        self, target_name: str | None,
    ) -> tuple[list[OCRResult], tuple[int, int] | None]:
        """Press+drag to reveal names, screenshot, OCR.

        Returns ALL OCR results (for position estimation) and the target
        tap position if found.

        Runs the swipe in a background thread so we can take a screenshot
        while the finger is still down (names visible).

        Args:
            target_name: Building name to search for, or None to just
                         read all visible text.

        Returns:
            (all_text, pos) — all_text is the full OCR result list;
            pos is (x, y) tap position if target found, else None.
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
            return ([], None)

        # OCR to find all text on screen
        all_text = self.ocr.find_all_text(screenshot)

        # Wait for swipe to complete (finger releases)
        thread.join(timeout=5)

        if target_name is None:
            return (all_text, None)

        # Compensate for map drift: after the screenshot the swipe
        # continues, shifting the map further.  The map content follows
        # the finger, so buildings move in the swipe direction.
        remaining = 1.0 - (self.screenshot_delay_ms / self.hold_duration_ms)
        drift = int(self.drag_offset * remaining)

        # Search for target building name (exact substring)
        target_lower = target_name.lower()
        for result in all_text:
            cx, cy = result.center
            if not self._in_safe_zone(cx, cy):
                continue
            if target_lower in result.text.lower():
                x1, y1 = result.bbox[0], result.bbox[1]
                tap_x = x1 + self.tap_offset_x + drift
                tap_y = y1 + self.tap_offset_y + drift
                logger.info(
                    f"BuildingFinder: found '{target_name}' in OCR "
                    f"text='{result.text}' bbox={result.bbox}, "
                    f"drift={drift}, tap at ({tap_x}, {tap_y})"
                )
                return (all_text, (tap_x, tap_y))

        # Also try fuzzy matching against known building names
        for result in all_text:
            cx, cy = result.center
            if not self._in_safe_zone(cx, cy):
                continue
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
                return (all_text, (tap_x, tap_y))

        logger.debug(
            f"BuildingFinder: '{target_name}' not found in "
            f"{len(all_text)} OCR results"
        )
        return (all_text, None)

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
            if not self._in_safe_zone(cx, cy):
                continue
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

    def _in_safe_zone(self, x: float, y: float) -> bool:
        """Check if coordinates are inside the safe zone (not UI elements)."""
        x1, y1, x2, y2 = self.safe_zone
        return x1 <= x <= x2 and y1 <= y <= y2

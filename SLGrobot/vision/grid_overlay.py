"""Grid Overlay - Draw labeled grid on screenshots for LLM communication."""

import logging

import cv2
import numpy as np

import config

logger = logging.getLogger(__name__)


class GridOverlay:
    """Overlay a labeled grid (A1, B3, C4...) on screenshots for LLM communication.

    Grid uses column letters (A-H) and row numbers (1-6).
    Cell "A1" is top-left, "H6" is bottom-right.
    """

    def __init__(self, cols: int = None, rows: int = None,
                 screen_width: int = None, screen_height: int = None) -> None:
        self.cols = cols or config.GRID_COLS
        self.rows = rows or config.GRID_ROWS
        self.screen_width = screen_width or config.SCREEN_WIDTH
        self.screen_height = screen_height or config.SCREEN_HEIGHT

        self.cell_width = self.screen_width // self.cols
        self.cell_height = self.screen_height // self.rows

    def annotate(self, screenshot: np.ndarray) -> np.ndarray:
        """Draw labeled grid on screenshot. Returns annotated copy."""
        annotated = screenshot.copy()
        h, w = annotated.shape[:2]

        # Recompute cell size based on actual image dimensions
        cell_w = w // self.cols
        cell_h = h // self.rows

        # Grid line style
        line_color = (0, 255, 0)  # Green
        line_thickness = 1
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.5
        font_color = (0, 255, 0)
        font_thickness = 1

        # Draw vertical lines
        for c in range(1, self.cols):
            x = c * cell_w
            cv2.line(annotated, (x, 0), (x, h), line_color, line_thickness)

        # Draw horizontal lines
        for r in range(1, self.rows):
            y = r * cell_h
            cv2.line(annotated, (0, y), (w, y), line_color, line_thickness)

        # Draw cell labels
        for r in range(self.rows):
            for c in range(self.cols):
                label = self._cell_label(c, r)
                text_x = c * cell_w + 4
                text_y = r * cell_h + 18

                # Draw background rectangle for readability
                (tw, th), _ = cv2.getTextSize(label, font, font_scale, font_thickness)
                cv2.rectangle(annotated,
                              (text_x - 1, text_y - th - 2),
                              (text_x + tw + 1, text_y + 2),
                              (0, 0, 0), -1)

                cv2.putText(annotated, label,
                            (text_x, text_y),
                            font, font_scale, font_color, font_thickness)

        return annotated

    def cell_to_pixel(self, cell: str) -> tuple[int, int]:
        """Convert grid cell label (e.g., 'B3') to pixel center (x, y).

        Args:
            cell: Cell label like "A1", "B3", "H6".

        Returns:
            (x, y) pixel coordinates of cell center.
        """
        col, row = self._parse_cell(cell)
        x = col * self.cell_width + self.cell_width // 2
        y = row * self.cell_height + self.cell_height // 2
        return (x, y)

    def pixel_to_cell(self, x: int, y: int) -> str:
        """Convert pixel coordinate to grid cell label.

        Args:
            x, y: Pixel coordinates.

        Returns:
            Cell label like "B3".
        """
        col = min(x // self.cell_width, self.cols - 1)
        row = min(y // self.cell_height, self.rows - 1)
        return self._cell_label(col, row)

    def get_cell_region(self, cell: str) -> tuple[int, int, int, int]:
        """Return bounding box (x1, y1, x2, y2) for a grid cell."""
        col, row = self._parse_cell(cell)
        x1 = col * self.cell_width
        y1 = row * self.cell_height
        x2 = x1 + self.cell_width
        y2 = y1 + self.cell_height
        return (x1, y1, x2, y2)

    def get_all_cells(self) -> list[str]:
        """Return list of all cell labels."""
        cells = []
        for r in range(self.rows):
            for c in range(self.cols):
                cells.append(self._cell_label(c, r))
        return cells

    def _cell_label(self, col: int, row: int) -> str:
        """Convert (col, row) indices to label like 'A1'."""
        letter = chr(ord('A') + col)
        number = row + 1
        return f"{letter}{number}"

    def _parse_cell(self, cell: str) -> tuple[int, int]:
        """Parse cell label like 'B3' into (col, row) indices."""
        cell = cell.strip().upper()
        if len(cell) < 2:
            raise ValueError(f"Invalid cell label: {cell}")

        letter = cell[0]
        number = cell[1:]

        col = ord(letter) - ord('A')
        row = int(number) - 1

        if col < 0 or col >= self.cols:
            raise ValueError(f"Column '{letter}' out of range (A-{chr(ord('A') + self.cols - 1)})")
        if row < 0 or row >= self.rows:
            raise ValueError(f"Row '{number}' out of range (1-{self.rows})")

        return (col, row)

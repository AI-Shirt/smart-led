"""Virtual 12x10 display. (0,0) is the top-left pixel, x grows right, y grows down."""

from __future__ import annotations

from .const import HEIGHT, WIDTH
from .font import GLYPH_HEIGHT, GLYPH_WIDTH, glyph

RGB = tuple[int, int, int]
BLACK: RGB = (0, 0, 0)


class Canvas:
    """Pixel buffer for one display."""

    def __init__(self, width: int = WIDTH, height: int = HEIGHT) -> None:
        self.width = width
        self.height = height
        self.pixels: list[RGB] = [BLACK] * (width * height)

    def set(self, x: int, y: int, color: RGB) -> None:
        if 0 <= x < self.width and 0 <= y < self.height:
            self.pixels[y * self.width + x] = color

    def get(self, x: int, y: int) -> RGB:
        return self.pixels[y * self.width + x]

    def fill_rect(self, x0: int, y0: int, w: int, h: int, color: RGB) -> None:
        for y in range(y0, y0 + h):
            for x in range(x0, x0 + w):
                self.set(x, y, color)

    def clear(self) -> None:
        self.pixels = [BLACK] * (self.width * self.height)

    def draw_char(self, char: str, x0: int, y0: int, color: RGB) -> None:
        """Draw one character with its top-left corner at (x0, y0). Unlit pixels are cleared."""
        rows = glyph(char)
        for dy in range(GLYPH_HEIGHT):
            for dx in range(GLYPH_WIDTH):
                self.set(x0 + dx, y0 + dy, color if rows[dy][dx] == "1" else BLACK)

    def to_hex(self) -> str:
        """Frame for the ESP: RRGGBB per pixel, row by row from the top-left."""
        return "".join(f"{r:02X}{g:02X}{b:02X}" for r, g, b in self.pixels)

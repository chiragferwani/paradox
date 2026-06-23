"""Pixel data extractor for Paradox.

Extracts detailed pixel information at each walk step.
"""

from dataclasses import dataclass

import numpy as np


@dataclass
class PixelData:
    """Container for extracted pixel data at a coordinate."""

    x: int
    y: int
    r: int
    g: int
    b: int
    hex_color: str
    brightness: float
    contrast: float

    def to_bytes(self) -> bytes:
        """Serialize pixel data to bytes for hashing."""
        return (
            self.x.to_bytes(4, byteorder="big")
            + self.y.to_bytes(4, byteorder="big")
            + bytes([self.r, self.g, self.b])
            + self.hex_color.encode("utf-8")
            + int(self.brightness * 1000).to_bytes(4, byteorder="big", signed=True)
            + int(self.contrast * 1000).to_bytes(4, byteorder="big", signed=True)
        )


def _compute_brightness(r: int, g: int, b: int) -> float:
    """Compute perceived brightness using luminance formula."""
    return (0.299 * r + 0.587 * g + 0.114 * b) / 255.0


def _compute_local_contrast(
    pixels: np.ndarray, x: int, y: int, width: int, height: int
) -> float:
    """Compute local contrast as standard deviation of neighbourhood brightness."""
    x_min = max(0, x - 1)
    x_max = min(width, x + 2)
    y_min = max(0, y - 1)
    y_max = min(height, y + 2)

    patch = pixels[y_min:y_max, x_min:x_max].astype(np.float64)
    brightness_map = (
        0.299 * patch[:, :, 0] + 0.587 * patch[:, :, 1] + 0.114 * patch[:, :, 2]
    )
    return float(np.std(brightness_map) / 255.0)


def extract_pixel_data(
    pixels: np.ndarray,
    x: int,
    y: int,
    width: int,
    height: int,
) -> PixelData:
    """Extract full pixel data at the given coordinate.

    Args:
        pixels: HxWx3 numpy array of RGB pixel data.
        x: X coordinate.
        y: Y coordinate.
        width: Image width.
        height: Image height.

    Returns:
        PixelData with RGB, hex, brightness, and contrast.
    """
    r, g, b = int(pixels[y, x, 0]), int(pixels[y, x, 1]), int(pixels[y, x, 2])
    hex_color = f"#{r:02x}{g:02x}{b:02x}"
    brightness = _compute_brightness(r, g, b)
    contrast = _compute_local_contrast(pixels, x, y, width, height)

    return PixelData(
        x=x,
        y=y,
        r=r,
        g=g,
        b=b,
        hex_color=hex_color,
        brightness=brightness,
        contrast=contrast,
    )

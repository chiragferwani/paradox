"""Local image source module for Paradox.

Handles loading and validating user-provided images from the local filesystem.
"""

import hashlib
from pathlib import Path
from dataclasses import dataclass
from typing import Tuple

import numpy as np
from PIL import Image

SUPPORTED_FORMATS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff", ".tif"}


@dataclass
class ImageData:
    """Container for loaded image data and metadata."""

    path: str
    pixels: np.ndarray  # HxWx3 RGB array
    width: int
    height: int
    image_hash: str
    format: str

    @property
    def dimensions(self) -> Tuple[int, int]:
        """Return (width, height) tuple."""
        return (self.width, self.height)


def _compute_image_hash(pixel_data: np.ndarray) -> str:
    """Compute a SHA3-256 hash of the raw pixel data for deterministic identification."""
    return hashlib.sha3_256(pixel_data.tobytes()).hexdigest()


def use_image(path: str) -> ImageData:
    """Load and validate a local image file.

    Args:
        path: Path to the image file.

    Returns:
        ImageData containing the loaded pixels and metadata.

    Raises:
        FileNotFoundError: If the image file does not exist.
        ValueError: If the image format is not supported.
    """
    filepath = Path(path).resolve()

    if not filepath.exists():
        raise FileNotFoundError(f"Image not found: {filepath}")

    suffix = filepath.suffix.lower()
    if suffix not in SUPPORTED_FORMATS:
        raise ValueError(
            f"Unsupported image format '{suffix}'. "
            f"Supported formats: {', '.join(sorted(SUPPORTED_FORMATS))}"
        )

    img = Image.open(filepath).convert("RGB")
    pixels = np.array(img, dtype=np.uint8)
    width, height = img.size
    image_hash = _compute_image_hash(pixels)

    return ImageData(
        path=str(filepath),
        pixels=pixels,
        width=width,
        height=height,
        image_hash=image_hash,
        format=suffix.lstrip("."),
    )

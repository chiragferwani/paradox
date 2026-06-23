"""Coordinate engine for Paradox.

Maps seed bytes to image coordinates for deterministic traversal.
"""

from typing import List, Tuple


def seed_to_coordinate(
    seed: bytes,
    width: int,
    height: int,
    offset: int = 0,
) -> Tuple[int, int]:
    """Convert seed bytes to an (x, y) image coordinate.

    Uses bytes from the seed at the given offset to deterministically
    compute pixel coordinates within the image dimensions.

    Args:
        seed: The current seed bytes (at least 64 bytes from SHA3-512).
        width: Image width in pixels.
        height: Image height in pixels.
        offset: Byte offset into the seed to read from.

    Returns:
        (x, y) coordinate tuple.
    """
    x_bytes = seed[offset:offset + 4]
    y_bytes = seed[offset + 4:offset + 8]

    x = int.from_bytes(x_bytes, byteorder="big") % width
    y = int.from_bytes(y_bytes, byteorder="big") % height

    return (x, y)


def get_neighbours(
    x: int,
    y: int,
    width: int,
    height: int,
    radius: int = 1,
) -> List[Tuple[int, int]]:
    """Get the coordinates of neighbouring pixels.

    Args:
        x: Center x coordinate.
        y: Center y coordinate.
        width: Image width.
        height: Image height.
        radius: Neighbourhood radius (default 1 = 3x3 grid).

    Returns:
        List of (x, y) tuples for valid neighbours (excluding center).
    """
    neighbours = []
    for dx in range(-radius, radius + 1):
        for dy in range(-radius, radius + 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = x + dx, y + dy
            if 0 <= nx < width and 0 <= ny < height:
                neighbours.append((nx, ny))
    return neighbours

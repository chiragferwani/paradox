"""Recursive walk engine for Paradox.

Performs deterministic traversals through image pixel data,
collecting entropy at each step.
"""

import hashlib
from dataclasses import dataclass, field
from typing import List, Tuple

import numpy as np

from paradox.walk.coordinate_engine import seed_to_coordinate, get_neighbours
from paradox.hashchain.engine import evolve_seed
from paradox.entropy.extractor import extract_pixel_data, PixelData


@dataclass
class WalkStep:
    """Record of a single step in the recursive walk."""

    step_index: int
    coordinate: Tuple[int, int]
    pixel_data: PixelData
    seed_snapshot: bytes


@dataclass
class WalkResult:
    """Complete result of a recursive walk layer."""

    layer: int
    steps: List[WalkStep]
    final_seed: bytes
    coordinates_visited: List[Tuple[int, int]]
    entropy_collected: List[bytes]


def perform_walk(
    pixels: np.ndarray,
    initial_seed: bytes,
    width: int,
    height: int,
    num_steps: int,
    layer: int = 0,
    record_steps: bool = False,
) -> WalkResult:
    """Perform a single-layer recursive walk through the image.

    At each step:
    1. Convert current seed to (x, y) coordinate
    2. Read pixel data at that coordinate
    3. Gather neighbour pixel data
    4. Evolve the seed using the hash chain engine
    5. Collect entropy

    Args:
        pixels: HxWx3 numpy array of RGB pixel data.
        initial_seed: Starting seed for this walk layer.
        width: Image width.
        height: Image height.
        num_steps: Number of steps to perform.
        layer: Layer index (for metadata).
        record_steps: If True, store detailed step records (uses more memory).

    Returns:
        WalkResult with collected entropy and final seed.
    """
    current_seed = initial_seed
    steps_list: List[WalkStep] = []
    coordinates: List[Tuple[int, int]] = []
    entropy_pool: List[bytes] = []

    for i in range(num_steps):
        # 1. Map seed to coordinate
        coord = seed_to_coordinate(current_seed, width, height)
        x, y = coord
        coordinates.append(coord)

        # 2. Extract pixel data
        pixel_data = extract_pixel_data(pixels, x, y, width, height)

        # 3. Get neighbour data
        neighbour_coords = get_neighbours(x, y, width, height)
        neighbour_bytes = b""
        for nx, ny in neighbour_coords:
            r, g, b = pixels[ny, nx]
            neighbour_bytes += bytes([r, g, b])

        # 4. Evolve seed
        current_seed = evolve_seed(
            current_seed,
            pixel_data.to_bytes(),
            coord,
            neighbour_bytes,
        )

        # 5. Collect entropy
        entropy_chunk = hashlib.sha3_256(
            current_seed + pixel_data.to_bytes()
        ).digest()
        entropy_pool.append(entropy_chunk)

        # Record step if requested
        if record_steps:
            steps_list.append(
                WalkStep(
                    step_index=i,
                    coordinate=coord,
                    pixel_data=pixel_data,
                    seed_snapshot=current_seed[:16],
                )
            )

    return WalkResult(
        layer=layer,
        steps=steps_list,
        final_seed=current_seed,
        coordinates_visited=coordinates,
        entropy_collected=entropy_pool,
    )


def debug_walk(
    pixels: np.ndarray,
    initial_seed: bytes,
    width: int,
    height: int,
    num_steps: int = 100,
) -> WalkResult:
    """Perform a walk with full step recording for debugging.

    Args:
        pixels: HxWx3 numpy array.
        initial_seed: Starting seed.
        width: Image width.
        height: Image height.
        num_steps: Number of steps (default 100).

    Returns:
        WalkResult with all steps recorded.
    """
    return perform_walk(
        pixels, initial_seed, width, height, num_steps,
        layer=0, record_steps=True,
    )

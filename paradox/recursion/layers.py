"""Multi-layer recursion engine for Paradox.

Manages the multi-layer recursive walk process, which is Paradox's
defining feature. Each layer feeds its final seed into the next layer.
"""

from dataclasses import dataclass
from enum import Enum
from typing import List

import numpy as np

from paradox.walk.recursive_walk import perform_walk, WalkResult
from paradox.entropy.collector import EntropyPool


class SecurityLevel(Enum):
    """Pre-defined security levels controlling walk depth and breadth."""

    LOW = ("low", 1000, 2)
    MEDIUM = ("medium", 10000, 4)
    HIGH = ("high", 100000, 8)
    EXTREME = ("extreme", 1000000, 16)

    def __init__(self, level_name: str, steps: int, layers: int):
        self.level_name = level_name
        self.steps = steps
        self.layers = layers

    @classmethod
    def from_string(cls, name: str) -> "SecurityLevel":
        """Get security level from string name."""
        name_upper = name.upper()
        try:
            return cls[name_upper]
        except KeyError:
            valid = ", ".join(level.level_name for level in cls)
            raise ValueError(
                f"Unknown security level '{name}'. Valid levels: {valid}"
            )


@dataclass
class RecursionResult:
    """Result of the full multi-layer recursion process."""

    layer_results: List[WalkResult]
    entropy_pool: EntropyPool
    final_seed: bytes
    security_level: SecurityLevel
    total_steps: int


def execute_recursion(
    pixels: np.ndarray,
    initial_seed: bytes,
    width: int,
    height: int,
    security_level: str = "high",
    record_steps: bool = False,
) -> RecursionResult:
    """Execute the full multi-layer recursive walk.

    Layer 1: Seed0 -> Walk -> SeedA
    Layer 2: SeedA -> Walk -> SeedB
    Layer 3: SeedB -> Walk -> SeedC
    ... continue until layer count reached.

    Args:
        pixels: HxWx3 numpy array of RGB pixel data.
        initial_seed: The initial seed (Seed0) from seed generation.
        width: Image width.
        height: Image height.
        security_level: Security level name ('low', 'medium', 'high', 'extreme').
        record_steps: If True, record all walk steps (high memory usage).

    Returns:
        RecursionResult with all layer results and aggregated entropy.
    """
    level = SecurityLevel.from_string(security_level)
    entropy_pool = EntropyPool()
    layer_results: List[WalkResult] = []
    current_seed = initial_seed

    for layer_idx in range(level.layers):
        result = perform_walk(
            pixels=pixels,
            initial_seed=current_seed,
            width=width,
            height=height,
            num_steps=level.steps,
            layer=layer_idx,
            record_steps=record_steps,
        )

        layer_results.append(result)
        entropy_pool.add_layer_entropy(layer_idx, result.entropy_collected)
        current_seed = result.final_seed

    return RecursionResult(
        layer_results=layer_results,
        entropy_pool=entropy_pool,
        final_seed=current_seed,
        security_level=level,
        total_steps=level.steps * level.layers,
    )

"""Entropy collector for Paradox.

Aggregates entropy from multiple recursive layers into a master entropy pool.
"""

import hashlib
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class EntropyPool:
    """Master entropy pool collecting entropy from all recursive layers."""

    layer_entropy: Dict[int, List[bytes]] = field(default_factory=dict)
    _master_pool: Optional[bytes] = field(default=None, repr=False)

    def add_layer_entropy(self, layer: int, entropy_chunks: List[bytes]) -> None:
        """Add entropy collected from a recursive walk layer.

        Args:
            layer: Layer index.
            entropy_chunks: List of entropy byte chunks from the walk.
        """
        self.layer_entropy[layer] = entropy_chunks
        self._master_pool = None  # Invalidate cache

    def get_master_pool(self) -> bytes:
        """Compute the master entropy pool by aggregating all layers.

        Returns:
            SHA3-512 hash of all aggregated layer entropy.
        """
        if self._master_pool is not None:
            return self._master_pool

        hasher = hashlib.sha3_512()

        for layer_idx in sorted(self.layer_entropy.keys()):
            layer_chunks = self.layer_entropy[layer_idx]
            layer_hash = hashlib.sha3_512()
            for chunk in layer_chunks:
                layer_hash.update(chunk)
            hasher.update(layer_hash.digest())

        self._master_pool = hasher.digest()
        return self._master_pool

    def get_extended_pool(self, length: int = 128) -> bytes:
        """Generate an extended entropy pool of arbitrary length.

        Uses iterative hashing to stretch the master pool.

        Args:
            length: Desired output length in bytes.

        Returns:
            Extended entropy bytes.
        """
        master = self.get_master_pool()
        result = b""
        counter = 0

        while len(result) < length:
            block = hashlib.sha3_256(
                master + counter.to_bytes(4, byteorder="big")
            ).digest()
            result += block
            counter += 1

        return result[:length]

    @property
    def total_chunks(self) -> int:
        """Total number of entropy chunks across all layers."""
        return sum(len(chunks) for chunks in self.layer_entropy.values())

    @property
    def num_layers(self) -> int:
        """Number of layers with entropy."""
        return len(self.layer_entropy)


def export_entropy(pool: EntropyPool) -> dict:
    """Export entropy pool data for analysis.

    Args:
        pool: The entropy pool to export.

    Returns:
        Dictionary with entropy pool statistics and data.
    """
    return {
        "num_layers": pool.num_layers,
        "total_chunks": pool.total_chunks,
        "master_pool_hex": pool.get_master_pool().hex(),
        "layer_chunk_counts": {
            layer: len(chunks) for layer, chunks in pool.layer_entropy.items()
        },
    }

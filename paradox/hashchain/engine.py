"""Hash chain engine for Paradox.

Creates evolving cryptographic state through iterative hashing
of seed, pixel data, coordinates, and neighbour data.
"""

import hashlib
from typing import Tuple


def evolve_seed(
    current_seed: bytes,
    pixel_data: bytes,
    coordinate: Tuple[int, int],
    neighbour_data: bytes,
) -> bytes:
    """Evolve the seed to the next state using SHA3-512.

    Formula:
        Seed(n+1) = SHA3-512(Seed(n) + PixelData + Coordinates + Neighbours)

    Args:
        current_seed: The current 64-byte seed.
        pixel_data: Serialized pixel data bytes.
        coordinate: (x, y) coordinate tuple.
        neighbour_data: Concatenated neighbour pixel bytes.

    Returns:
        New 64-byte evolved seed.
    """
    coord_bytes = (
        coordinate[0].to_bytes(4, byteorder="big")
        + coordinate[1].to_bytes(4, byteorder="big")
    )

    material = current_seed + pixel_data + coord_bytes + neighbour_data
    return hashlib.sha3_512(material).digest()


def compute_chain_hash(chain: list) -> bytes:
    """Compute a summary hash of an entire hash chain.

    Args:
        chain: List of seed bytes from the chain.

    Returns:
        SHA3-512 hash of the concatenated chain.
    """
    combined = b"".join(chain)
    return hashlib.sha3_512(combined).digest()

"""Seed generator for Paradox.

Generates the initial cryptographic seed from image hash, nonce,
timestamp, and version using SHA3-512.
"""

import hashlib
import os
import time
from typing import Optional


def generate_initial_seed(
    image_hash: str,
    nonce: Optional[bytes] = None,
    timestamp: Optional[float] = None,
    version: str = "1.0",
) -> bytes:
    """Generate the initial seed (Seed0) for the recursive walk engine.

    Formula:
        Seed0 = SHA3-512(ImageHash + Nonce + Timestamp + Version)

    Args:
        image_hash: SHA3-256 hash of the image pixel data.
        nonce: Random nonce bytes. If None, generates 32 random bytes.
        timestamp: Unix timestamp. If None, uses current time.
        version: Protocol version string.

    Returns:
        64-byte initial seed.
    """
    if nonce is None:
        nonce = os.urandom(32)
    if timestamp is None:
        timestamp = time.time()

    material = (
        image_hash.encode("utf-8")
        + nonce
        + str(timestamp).encode("utf-8")
        + version.encode("utf-8")
    )

    return hashlib.sha3_512(material).digest()


def generate_deterministic_seed(
    image_hash: str,
    nonce: bytes,
    timestamp: float,
    version: str = "1.0",
) -> bytes:
    """Generate a deterministic seed for reproducible key derivation.

    Same as generate_initial_seed but all parameters are required
    to ensure deterministic output for decryption.

    Args:
        image_hash: SHA3-256 hash of the image pixel data.
        nonce: Exact nonce bytes used during encryption.
        timestamp: Exact timestamp used during encryption.
        version: Protocol version string.

    Returns:
        64-byte initial seed (deterministic).
    """
    material = (
        image_hash.encode("utf-8")
        + nonce
        + str(timestamp).encode("utf-8")
        + version.encode("utf-8")
    )

    return hashlib.sha3_512(material).digest()

"""Key derivation functions for Paradox.

Supports HKDF-SHA256 (recommended) and BLAKE3 KDF.
"""

import os
import time
from typing import Optional

import blake3
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes

from paradox.image_source.local import ImageData
from paradox.seed.generator import generate_initial_seed
from paradox.recursion.layers import execute_recursion
from paradox.entropy.collector import EntropyPool


def _derive_key_hkdf(
    entropy_pool: EntropyPool,
    key_length: int,
    salt: Optional[bytes] = None,
    info: bytes = b"paradox-rve-kde-v1.0",
) -> bytes:
    """Derive a key using HKDF-SHA256.

    Args:
        entropy_pool: The master entropy pool from recursion.
        key_length: Desired key length in bytes (16, 32, or 64).
        salt: Optional salt for HKDF. If None, uses a zero-filled salt.
        info: Context info for HKDF.

    Returns:
        Derived key bytes.
    """
    master_entropy = entropy_pool.get_extended_pool(length=128)

    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=key_length,
        salt=salt,
        info=info,
    )
    return hkdf.derive(master_entropy)


def _derive_key_blake3(
    entropy_pool: EntropyPool,
    key_length: int,
    context: str = "paradox-rve-kde-v1.0",
) -> bytes:
    """Derive a key using BLAKE3 KDF.

    Args:
        entropy_pool: The master entropy pool from recursion.
        key_length: Desired key length in bytes.
        context: BLAKE3 derive_key context string.

    Returns:
        Derived key bytes.
    """
    master_entropy = entropy_pool.get_extended_pool(length=128)
    return blake3.blake3(master_entropy, derive_key_context=context).digest(length=key_length)


def _run_full_pipeline(
    image: ImageData,
    security_level: str = "high",
    nonce: Optional[bytes] = None,
    timestamp: Optional[float] = None,
) -> tuple:
    """Run the full pipeline from image to entropy pool.

    Returns:
        Tuple of (RecursionResult, nonce, timestamp)
    """
    if nonce is None:
        nonce = os.urandom(32)
    if timestamp is None:
        timestamp = time.time()

    seed = generate_initial_seed(
        image_hash=image.image_hash,
        nonce=nonce,
        timestamp=timestamp,
    )

    result = execute_recursion(
        pixels=image.pixels,
        initial_seed=seed,
        width=image.width,
        height=image.height,
        security_level=security_level,
    )

    return result, nonce, timestamp


def generate_key(
    image: ImageData,
    key_length: int = 32,
    security_level: str = "high",
    kdf: str = "hkdf",
    nonce: Optional[bytes] = None,
    timestamp: Optional[float] = None,
) -> tuple:
    """Generate a cryptographic key from image data.

    This is the primary key generation API.

    Args:
        image: ImageData from use_image() or get_random_image().
        key_length: Key length in bytes (16, 32, or 64).
        security_level: Security level ('low', 'medium', 'high', 'extreme').
        kdf: KDF algorithm ('hkdf' or 'blake3').
        nonce: Optional nonce for deterministic derivation.
        timestamp: Optional timestamp for deterministic derivation.

    Returns:
        Tuple of (key_bytes, metadata_dict) where metadata contains
        the nonce, timestamp, and other parameters needed for re-derivation.
    """
    result, used_nonce, used_timestamp = _run_full_pipeline(
        image, security_level, nonce, timestamp
    )

    if kdf == "hkdf":
        key = _derive_key_hkdf(result.entropy_pool, key_length)
    elif kdf == "blake3":
        key = _derive_key_blake3(result.entropy_pool, key_length)
    else:
        raise ValueError(f"Unknown KDF: {kdf}. Use 'hkdf' or 'blake3'.")

    metadata = {
        "version": "1.0",
        "nonce": used_nonce.hex(),
        "timestamp": used_timestamp,
        "security_level": security_level,
        "kdf": kdf,
        "key_length": key_length,
        "image_hash": image.image_hash,
        "layers": result.security_level.layers,
        "steps_per_layer": result.security_level.steps,
        "total_steps": result.total_steps,
    }

    return key, metadata


def generate_key128(
    image: ImageData,
    security_level: str = "high",
    **kwargs,
) -> tuple:
    """Generate a 128-bit (16-byte) key."""
    return generate_key(image, key_length=16, security_level=security_level, **kwargs)


def generate_key256(
    image: ImageData,
    security_level: str = "high",
    **kwargs,
) -> tuple:
    """Generate a 256-bit (32-byte) key."""
    return generate_key(image, key_length=32, security_level=security_level, **kwargs)


def generate_key512(
    image: ImageData,
    security_level: str = "high",
    **kwargs,
) -> tuple:
    """Generate a 512-bit (64-byte) key."""
    return generate_key(image, key_length=64, security_level=security_level, **kwargs)

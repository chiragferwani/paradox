"""AES-256-GCM encryption engine for Paradox."""

import os
from typing import Tuple

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def encrypt(
    plaintext: bytes,
    key: bytes,
    associated_data: bytes = b"",
) -> Tuple[bytes, bytes]:
    """Encrypt data using AES-256-GCM.

    Args:
        plaintext: Data to encrypt.
        key: 32-byte encryption key.
        associated_data: Optional associated data for authentication.

    Returns:
        Tuple of (ciphertext, nonce) where ciphertext includes the GCM tag.
    """
    if len(key) != 32:
        raise ValueError(f"AES-256-GCM requires a 32-byte key, got {len(key)} bytes")

    aes_nonce = os.urandom(12)  # 96-bit nonce for GCM
    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(aes_nonce, plaintext, associated_data or None)
    return ciphertext, aes_nonce


def decrypt(
    ciphertext: bytes,
    key: bytes,
    nonce: bytes,
    associated_data: bytes = b"",
) -> bytes:
    """Decrypt data using AES-256-GCM.

    Args:
        ciphertext: Encrypted data (includes GCM tag).
        key: 32-byte encryption key.
        nonce: 12-byte nonce used during encryption.
        associated_data: Optional associated data used during encryption.

    Returns:
        Decrypted plaintext bytes.

    Raises:
        cryptography.exceptions.InvalidTag: If authentication fails.
    """
    if len(key) != 32:
        raise ValueError(f"AES-256-GCM requires a 32-byte key, got {len(key)} bytes")

    aesgcm = AESGCM(key)
    return aesgcm.decrypt(nonce, ciphertext, associated_data or None)

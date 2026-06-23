"""ChaCha20-Poly1305 encryption engine for Paradox."""

import os
from typing import Tuple

from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305


def encrypt(
    plaintext: bytes,
    key: bytes,
    associated_data: bytes = b"",
) -> Tuple[bytes, bytes]:
    """Encrypt data using ChaCha20-Poly1305.

    Args:
        plaintext: Data to encrypt.
        key: 32-byte encryption key.
        associated_data: Optional associated data for authentication.

    Returns:
        Tuple of (ciphertext, nonce) where ciphertext includes the Poly1305 tag.
    """
    if len(key) != 32:
        raise ValueError(f"ChaCha20-Poly1305 requires a 32-byte key, got {len(key)} bytes")

    chacha_nonce = os.urandom(12)
    chacha = ChaCha20Poly1305(key)
    ciphertext = chacha.encrypt(chacha_nonce, plaintext, associated_data or None)
    return ciphertext, chacha_nonce


def decrypt(
    ciphertext: bytes,
    key: bytes,
    nonce: bytes,
    associated_data: bytes = b"",
) -> bytes:
    """Decrypt data using ChaCha20-Poly1305.

    Args:
        ciphertext: Encrypted data (includes Poly1305 tag).
        key: 32-byte encryption key.
        nonce: 12-byte nonce used during encryption.
        associated_data: Optional associated data used during encryption.

    Returns:
        Decrypted plaintext bytes.
    """
    if len(key) != 32:
        raise ValueError(f"ChaCha20-Poly1305 requires a 32-byte key, got {len(key)} bytes")

    chacha = ChaCha20Poly1305(key)
    return chacha.decrypt(nonce, ciphertext, associated_data or None)

"""High-level encryption/decryption interface for Paradox.

Provides the public-facing encrypt/decrypt APIs that tie together
key derivation, encryption, and metadata management.
"""

from pathlib import Path

from paradox.image_source.local import ImageData
from paradox.kdf.hkdf import generate_key
from paradox.crypto import aes, chacha
from paradox.metadata.serializer import serialize_metadata, deserialize_metadata


def encrypt(
    plaintext: bytes,
    image: ImageData,
    security_level: str = "high",
    algorithm: str = "AES-256-GCM",
    kdf: str = "hkdf",
) -> bytes:
    """Encrypt raw bytes using image-derived key.

    Args:
        plaintext: Data to encrypt.
        image: ImageData from use_image() or get_random_image().
        security_level: Security level for key derivation.
        algorithm: Encryption algorithm ('AES-256-GCM' or 'ChaCha20-Poly1305').
        kdf: KDF algorithm ('hkdf' or 'blake3').

    Returns:
        Encrypted bundle (metadata + ciphertext) as bytes.
    """
    key, meta = generate_key(
        image, key_length=32, security_level=security_level, kdf=kdf
    )
    meta["algorithm"] = algorithm

    if algorithm == "AES-256-GCM":
        ciphertext, enc_nonce = aes.encrypt(plaintext, key)
    elif algorithm == "ChaCha20-Poly1305":
        ciphertext, enc_nonce = chacha.encrypt(plaintext, key)
    else:
        raise ValueError(f"Unsupported algorithm: {algorithm}")

    meta["encryption_nonce"] = enc_nonce.hex()

    # Bundle: metadata_json + separator + ciphertext
    meta_bytes = serialize_metadata(meta)
    separator = b"\x00PARADOX\x00"
    return meta_bytes + separator + ciphertext


def decrypt(
    encrypted_bundle: bytes,
    image: ImageData,
) -> bytes:
    """Decrypt raw bytes using image-derived key.

    Args:
        encrypted_bundle: The encrypted bundle from encrypt().
        image: The same ImageData used during encryption.

    Returns:
        Decrypted plaintext bytes.
    """
    separator = b"\x00PARADOX\x00"
    parts = encrypted_bundle.split(separator, 1)
    if len(parts) != 2:
        raise ValueError("Invalid encrypted bundle format")

    meta_bytes, ciphertext = parts
    meta = deserialize_metadata(meta_bytes)

    # Re-derive the same key
    kdf_nonce = bytes.fromhex(meta["nonce"])
    timestamp = meta["timestamp"]
    security_level = meta["security_level"]
    kdf = meta.get("kdf", "hkdf")
    algorithm = meta["algorithm"]
    enc_nonce = bytes.fromhex(meta["encryption_nonce"])

    key, _ = generate_key(
        image,
        key_length=32,
        security_level=security_level,
        kdf=kdf,
        nonce=kdf_nonce,
        timestamp=timestamp,
    )

    if algorithm == "AES-256-GCM":
        return aes.decrypt(ciphertext, key, enc_nonce)
    elif algorithm == "ChaCha20-Poly1305":
        return chacha.decrypt(ciphertext, key, enc_nonce)
    else:
        raise ValueError(f"Unsupported algorithm: {algorithm}")


def encrypt_text(
    text: str,
    image: ImageData,
    security_level: str = "high",
    algorithm: str = "AES-256-GCM",
    kdf: str = "hkdf",
) -> bytes:
    """Encrypt a text string.

    Args:
        text: The string to encrypt.
        image: ImageData from use_image() or get_random_image().
        security_level: Security level for key derivation.
        algorithm: Encryption algorithm.
        kdf: KDF algorithm.

    Returns:
        Encrypted bundle as bytes.
    """
    return encrypt(text.encode("utf-8"), image, security_level, algorithm, kdf)


def decrypt_text(
    encrypted_bundle: bytes,
    image: ImageData,
) -> str:
    """Decrypt an encrypted text string.

    Args:
        encrypted_bundle: The encrypted bundle from encrypt_text().
        image: The same ImageData used during encryption.

    Returns:
        Decrypted text string.
    """
    return decrypt(encrypted_bundle, image).decode("utf-8")


def encrypt_file(
    input_path: str,
    output_path: str,
    image: ImageData,
    security_level: str = "high",
    algorithm: str = "AES-256-GCM",
    kdf: str = "hkdf",
) -> str:
    """Encrypt a file.

    Args:
        input_path: Path to the file to encrypt.
        output_path: Path to write the encrypted file.
        image: ImageData from use_image() or get_random_image().
        security_level: Security level for key derivation.
        algorithm: Encryption algorithm.
        kdf: KDF algorithm.

    Returns:
        Path to the encrypted output file.
    """
    plaintext = Path(input_path).read_bytes()
    encrypted = encrypt(plaintext, image, security_level, algorithm, kdf)
    Path(output_path).write_bytes(encrypted)
    return output_path


def decrypt_file(
    input_path: str,
    output_path: str,
    image: ImageData,
) -> str:
    """Decrypt a file.

    Args:
        input_path: Path to the encrypted file.
        output_path: Path to write the decrypted file.
        image: The same ImageData used during encryption.

    Returns:
        Path to the decrypted output file.
    """
    encrypted = Path(input_path).read_bytes()
    decrypted = decrypt(encrypted, image)
    Path(output_path).write_bytes(decrypted)
    return output_path

# Paradox API Reference Manual
**Recursive Visual Entropy Key Derivation Engine (RVE-KDE) Public API Documentation**

> [!WARNING]
> Paradox is an experimental research-oriented key derivation framework and should not be considered a replacement for established cryptographic standards such as Argon2, PBKDF2, HKDF, or BLAKE3.

---

## 1. Image Sources API

### `useImage(path: str) -> ImageData`
Loads a local image file from the specified path and validates its type and dimensions.
*   **Args**:
    *   `path` (str): Absolute or relative filesystem path to a valid PNG, JPG, JPEG, WEBP, BMP, or TIFF file.
*   **Returns**:
    *   `ImageData`: A dataclass containing the loaded image (`pixels` as a HxWx3 NumPy array, `path` as str, and `image_hash` as str).

### `getRandomImage() -> ImageData`
Downloads a random high-resolution image from Unsplash/Picsum Photos APIs, caches it locally in the temp directory, and returns its metadata.
*   **Returns**:
    *   `ImageData`: Metadata of the fetched image.

---

## 2. Key Derivation API

### `generate_key(image: ImageData, key_length: int = 32, security_level: str = "high", kdf: str = "hkdf", nonce: Optional[bytes] = None, timestamp: Optional[float] = None) -> Tuple[bytes, dict]`
Main interface for deriving symmetric cryptographic keys from loaded image content.
*   **Args**:
    *   `image` (ImageData): Loaded image data from `useImage` or `getRandomImage`.
    *   `key_length` (int): Byte size of the output key (must be 16, 32, or 64 bytes).
    *   `security_level` (str): Configures the walk path depth and breadth ('low', 'medium', 'high', 'extreme').
    *   `kdf` (str): Internal post-processing KDF compression ('hkdf' or 'blake3').
    *   `nonce` (bytes): Optional 32-byte salt nonce. If omitted, generated using `os.urandom(32)`.
    *   `timestamp` (float): Optional epoch timestamp. If omitted, defaults to `time.time()`.
*   **Returns**:
    *   `Tuple[bytes, dict]`: A tuple of `(key_bytes, metadata_dict)`.

### Helper Variants:
*   `generate_key128(image, security_level, **kwargs)`: Returns 16-byte key.
*   `generate_key256(image, security_level, **kwargs)`: Returns 32-byte key.
*   `generate_key512(image, security_level, **kwargs)`: Returns 64-byte key.

---

## 3. High-Level Cryptographic Wrapper API

### `encrypt_text(text: str, image: ImageData, security_level: str = "high", algorithm: str = "AES-256-GCM") -> str`
Encrypts plaintext text and bundles the required key reconstruction parameters into an output string.
*   **Args**:
    *   `text` (str): Plaintext message string.
    *   `image` (ImageData): Image source to derive key from.
    *   `security_level` (str): Configured walk depth ('low', 'medium', 'high').
    *   `algorithm` (str): Symmetric encryption cipher ('AES-256-GCM' or 'ChaCha20-Poly1305').
*   **Returns**:
    *   `str`: A JSON-serialized header base64 envelope embedding ciphertext, tag, nonce, and KDF metadata.

### `decrypt_text(envelope: str, image: ImageData) -> str`
Decrypts a serialized envelope string and returns the original plaintext.
*   **Args**:
    *   `envelope` (str): Serialized JSON base64 string.
    *   `image` (ImageData): Corresponding image source.
*   **Returns**:
    *   `str`: Original decrypted plaintext message.

### File Cryptography:
*   `encrypt_file(src_path: str, dest_path: str, image: ImageData, security_level: str)`: Encrypts a binary file to disk.
*   `decrypt_file(src_path: str, dest_path: str, image: ImageData)`: Decrypts a binary file to disk.

---

## 4. Visual Analysis & Diagnostics

### `visualize_walk(layer_results: List[WalkResult], width: int, height: int, output_path: str, show_layers: bool = True)`
Generates Matplotlib-based path traversal, spatial density, and recursion coverage plots.
*   **Args**:
    *   `layer_results`: Evolved recursion walker outputs.
    *   `width`/`height`: Image dimensions.
    *   `output_path`: File path to save the generated PNG plot.

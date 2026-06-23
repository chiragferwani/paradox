"""Tests for the Paradox package.

Uses a small synthetic test image to verify the full pipeline:
image loading, seed generation, recursive walk, key derivation,
encryption, and decryption.
"""

import os
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

# Ensure we can import the package
import paradox
from paradox.image_source.local import use_image
from paradox.seed.generator import generate_initial_seed, generate_deterministic_seed
from paradox.walk.coordinate_engine import seed_to_coordinate, get_neighbours
from paradox.hashchain.engine import evolve_seed
from paradox.entropy.extractor import extract_pixel_data
from paradox.entropy.collector import EntropyPool, export_entropy
from paradox.recursion.layers import SecurityLevel, execute_recursion
from paradox.kdf.hkdf import generate_key, generate_key128, generate_key512
from paradox.crypto import aes, chacha
from paradox.crypto.interface import (
    encrypt, decrypt, encrypt_text, decrypt_text,
    encrypt_file, decrypt_file,
)
from paradox.metadata.serializer import (
    serialize_metadata, deserialize_metadata,
    export_metadata, import_metadata,
)
from paradox.analysis.image_analyzer import analyze_image


# --- Fixtures ---

@pytest.fixture
def test_image_path(tmp_path):
    """Create a small deterministic test image."""
    rng = np.random.RandomState(42)
    pixels = rng.randint(0, 256, (64, 64, 3), dtype=np.uint8)
    img = Image.fromarray(pixels, "RGB")
    path = tmp_path / "test_image.png"
    img.save(str(path))
    return str(path)


@pytest.fixture
def test_image(test_image_path):
    """Load the test image as ImageData."""
    return use_image(test_image_path)


@pytest.fixture
def fixed_nonce():
    """Fixed nonce for deterministic tests."""
    return bytes(range(32))


@pytest.fixture
def fixed_timestamp():
    """Fixed timestamp for deterministic tests."""
    return 1700000000.0


# --- Image Source Tests ---

class TestImageSource:
    def test_use_image_loads_correctly(self, test_image):
        assert test_image.width == 64
        assert test_image.height == 64
        assert test_image.pixels.shape == (64, 64, 3)
        assert len(test_image.image_hash) == 64  # SHA3-256 hex
        assert test_image.format == "png"

    def test_use_image_deterministic_hash(self, test_image_path):
        img1 = use_image(test_image_path)
        img2 = use_image(test_image_path)
        assert img1.image_hash == img2.image_hash

    def test_use_image_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            use_image("/nonexistent/path/image.png")

    def test_use_image_unsupported_format(self, tmp_path):
        bad_file = tmp_path / "test.xyz"
        bad_file.write_text("not an image")
        with pytest.raises(ValueError, match="Unsupported image format"):
            use_image(str(bad_file))

    def test_image_data_dimensions(self, test_image):
        assert test_image.dimensions == (64, 64)


# --- Seed Generator Tests ---

class TestSeedGenerator:
    def test_seed_length(self, test_image, fixed_nonce, fixed_timestamp):
        seed = generate_initial_seed(
            test_image.image_hash, fixed_nonce, fixed_timestamp
        )
        assert len(seed) == 64  # SHA3-512 output

    def test_seed_deterministic(self, test_image, fixed_nonce, fixed_timestamp):
        seed1 = generate_initial_seed(
            test_image.image_hash, fixed_nonce, fixed_timestamp
        )
        seed2 = generate_initial_seed(
            test_image.image_hash, fixed_nonce, fixed_timestamp
        )
        assert seed1 == seed2

    def test_different_nonce_different_seed(self, test_image, fixed_timestamp):
        seed1 = generate_initial_seed(
            test_image.image_hash, b"\x00" * 32, fixed_timestamp
        )
        seed2 = generate_initial_seed(
            test_image.image_hash, b"\x01" * 32, fixed_timestamp
        )
        assert seed1 != seed2

    def test_deterministic_seed(self, test_image, fixed_nonce, fixed_timestamp):
        seed1 = generate_initial_seed(
            test_image.image_hash, fixed_nonce, fixed_timestamp
        )
        seed2 = generate_deterministic_seed(
            test_image.image_hash, fixed_nonce, fixed_timestamp
        )
        assert seed1 == seed2


# --- Coordinate Engine Tests ---

class TestCoordinateEngine:
    def test_seed_to_coordinate_in_bounds(self):
        seed = os.urandom(64)
        x, y = seed_to_coordinate(seed, 100, 100)
        assert 0 <= x < 100
        assert 0 <= y < 100

    def test_seed_to_coordinate_deterministic(self):
        seed = b"\x42" * 64
        coord1 = seed_to_coordinate(seed, 200, 200)
        coord2 = seed_to_coordinate(seed, 200, 200)
        assert coord1 == coord2

    def test_get_neighbours_center(self):
        neighbours = get_neighbours(5, 5, 10, 10)
        assert len(neighbours) == 8  # 3x3 - 1 center

    def test_get_neighbours_corner(self):
        neighbours = get_neighbours(0, 0, 10, 10)
        assert len(neighbours) == 3  # Only right, below, diagonal

    def test_get_neighbours_edge(self):
        neighbours = get_neighbours(0, 5, 10, 10)
        assert len(neighbours) == 5


# --- Hash Chain Tests ---

class TestHashChain:
    def test_evolve_seed_length(self):
        seed = os.urandom(64)
        new_seed = evolve_seed(seed, b"pixel_data", (10, 20), b"neighbours")
        assert len(new_seed) == 64

    def test_evolve_seed_deterministic(self):
        seed = b"\x42" * 64
        result1 = evolve_seed(seed, b"data", (1, 2), b"nbr")
        result2 = evolve_seed(seed, b"data", (1, 2), b"nbr")
        assert result1 == result2

    def test_evolve_seed_differs_with_different_input(self):
        seed = b"\x42" * 64
        result1 = evolve_seed(seed, b"data1", (1, 2), b"nbr")
        result2 = evolve_seed(seed, b"data2", (1, 2), b"nbr")
        assert result1 != result2


# --- Pixel Extractor Tests ---

class TestPixelExtractor:
    def test_extract_pixel_data(self, test_image):
        px = extract_pixel_data(test_image.pixels, 10, 10, 64, 64)
        assert 0 <= px.r <= 255
        assert 0 <= px.g <= 255
        assert 0 <= px.b <= 255
        assert px.hex_color.startswith("#")
        assert 0.0 <= px.brightness <= 1.0
        assert px.contrast >= 0.0

    def test_pixel_data_to_bytes(self, test_image):
        px = extract_pixel_data(test_image.pixels, 10, 10, 64, 64)
        data = px.to_bytes()
        assert isinstance(data, bytes)
        assert len(data) > 0


# --- Entropy Collector Tests ---

class TestEntropyCollector:
    def test_entropy_pool_basic(self):
        pool = EntropyPool()
        pool.add_layer_entropy(0, [b"chunk1", b"chunk2"])
        pool.add_layer_entropy(1, [b"chunk3"])

        assert pool.num_layers == 2
        assert pool.total_chunks == 3

        master = pool.get_master_pool()
        assert len(master) == 64  # SHA3-512

    def test_entropy_pool_deterministic(self):
        pool1 = EntropyPool()
        pool1.add_layer_entropy(0, [b"a", b"b"])
        pool1.add_layer_entropy(1, [b"c"])

        pool2 = EntropyPool()
        pool2.add_layer_entropy(0, [b"a", b"b"])
        pool2.add_layer_entropy(1, [b"c"])

        assert pool1.get_master_pool() == pool2.get_master_pool()

    def test_extended_pool(self):
        pool = EntropyPool()
        pool.add_layer_entropy(0, [b"data"])
        extended = pool.get_extended_pool(length=256)
        assert len(extended) == 256

    def test_export_entropy(self):
        pool = EntropyPool()
        pool.add_layer_entropy(0, [b"chunk1", b"chunk2"])
        result = export_entropy(pool)
        assert result["num_layers"] == 1
        assert result["total_chunks"] == 2
        assert "master_pool_hex" in result


# --- Security Level Tests ---

class TestSecurityLevel:
    def test_security_levels(self):
        low = SecurityLevel.from_string("low")
        assert low.steps == 1000
        assert low.layers == 2

        high = SecurityLevel.from_string("high")
        assert high.steps == 100000
        assert high.layers == 8

    def test_invalid_security_level(self):
        with pytest.raises(ValueError, match="Unknown security level"):
            SecurityLevel.from_string("invalid")


# --- Recursive Walk Tests ---

class TestRecursiveWalk:
    def test_walk_produces_results(self, test_image, fixed_nonce, fixed_timestamp):
        seed = generate_initial_seed(
            test_image.image_hash, fixed_nonce, fixed_timestamp
        )
        result = execute_recursion(
            test_image.pixels, seed,
            test_image.width, test_image.height,
            security_level="low",
        )
        assert len(result.layer_results) == 2  # LOW = 2 layers
        assert result.total_steps == 2000  # 1000 steps * 2 layers
        assert len(result.entropy_pool.get_master_pool()) == 64

    def test_walk_deterministic(self, test_image, fixed_nonce, fixed_timestamp):
        seed = generate_initial_seed(
            test_image.image_hash, fixed_nonce, fixed_timestamp
        )
        result1 = execute_recursion(
            test_image.pixels, seed,
            test_image.width, test_image.height,
            security_level="low",
        )
        result2 = execute_recursion(
            test_image.pixels, seed,
            test_image.width, test_image.height,
            security_level="low",
        )
        assert result1.final_seed == result2.final_seed
        assert (
            result1.entropy_pool.get_master_pool()
            == result2.entropy_pool.get_master_pool()
        )


# --- Key Derivation Tests ---

class TestKeyDerivation:
    def test_generate_key_256(self, test_image, fixed_nonce, fixed_timestamp):
        key, meta = generate_key(
            test_image, key_length=32, security_level="low",
            nonce=fixed_nonce, timestamp=fixed_timestamp,
        )
        assert len(key) == 32
        assert meta["version"] == "1.0"
        assert meta["security_level"] == "low"
        assert meta["key_length"] == 32

    def test_generate_key_deterministic(self, test_image, fixed_nonce, fixed_timestamp):
        key1, _ = generate_key(
            test_image, security_level="low",
            nonce=fixed_nonce, timestamp=fixed_timestamp,
        )
        key2, _ = generate_key(
            test_image, security_level="low",
            nonce=fixed_nonce, timestamp=fixed_timestamp,
        )
        assert key1 == key2

    def test_generate_key128(self, test_image, fixed_nonce, fixed_timestamp):
        key, _ = generate_key128(
            test_image, security_level="low",
            nonce=fixed_nonce, timestamp=fixed_timestamp,
        )
        assert len(key) == 16

    def test_generate_key512(self, test_image, fixed_nonce, fixed_timestamp):
        key, _ = generate_key512(
            test_image, security_level="low",
            nonce=fixed_nonce, timestamp=fixed_timestamp,
        )
        assert len(key) == 64

    def test_blake3_kdf(self, test_image, fixed_nonce, fixed_timestamp):
        key, meta = generate_key(
            test_image, security_level="low", kdf="blake3",
            nonce=fixed_nonce, timestamp=fixed_timestamp,
        )
        assert len(key) == 32
        assert meta["kdf"] == "blake3"


# --- Crypto Engine Tests ---

class TestCryptoEngines:
    def test_aes_encrypt_decrypt(self):
        key = os.urandom(32)
        plaintext = b"Hello, Paradox!"
        ciphertext, nonce = aes.encrypt(plaintext, key)
        decrypted = aes.decrypt(ciphertext, key, nonce)
        assert decrypted == plaintext

    def test_chacha_encrypt_decrypt(self):
        key = os.urandom(32)
        plaintext = b"Hello, Paradox!"
        ciphertext, nonce = chacha.encrypt(plaintext, key)
        decrypted = chacha.decrypt(ciphertext, key, nonce)
        assert decrypted == plaintext

    def test_aes_wrong_key_fails(self):
        key1 = os.urandom(32)
        key2 = os.urandom(32)
        ciphertext, nonce = aes.encrypt(b"secret", key1)
        with pytest.raises(Exception):
            aes.decrypt(ciphertext, key2, nonce)

    def test_invalid_key_length(self):
        with pytest.raises(ValueError, match="32-byte key"):
            aes.encrypt(b"data", b"short_key")


# --- High-Level Interface Tests ---

class TestHighLevelInterface:
    def test_encrypt_decrypt_text(self, test_image):
        encrypted = encrypt_text(
            "Hello World", test_image, security_level="low"
        )
        decrypted = decrypt_text(encrypted, test_image)
        assert decrypted == "Hello World"

    def test_encrypt_decrypt_bytes(self, test_image):
        data = b"\x00\x01\x02\xff" * 100
        encrypted = encrypt(data, test_image, security_level="low")
        decrypted = decrypt(encrypted, test_image)
        assert decrypted == data

    def test_encrypt_decrypt_chacha(self, test_image):
        encrypted = encrypt_text(
            "ChaCha test", test_image,
            security_level="low",
            algorithm="ChaCha20-Poly1305",
        )
        decrypted = decrypt_text(encrypted, test_image)
        assert decrypted == "ChaCha test"

    def test_encrypt_decrypt_file(self, test_image, tmp_path):
        # Create input file
        input_file = tmp_path / "input.txt"
        input_file.write_text("File encryption test content")

        encrypted_file = str(tmp_path / "encrypted.bin")
        decrypted_file = str(tmp_path / "decrypted.txt")

        encrypt_file(str(input_file), encrypted_file, test_image, security_level="low")
        decrypt_file(encrypted_file, decrypted_file, test_image)

        assert Path(decrypted_file).read_text() == "File encryption test content"


# --- Metadata Tests ---

class TestMetadata:
    def test_serialize_deserialize(self):
        meta = {"version": "1.0", "nonce": "abc123", "layers": 8}
        data = serialize_metadata(meta)
        restored = deserialize_metadata(data)
        assert restored == meta

    def test_export_import(self, tmp_path):
        meta = {"version": "1.0", "test": True}
        path = str(tmp_path / "meta.json")
        export_metadata(meta, path)
        restored = import_metadata(path)
        assert restored == meta


# --- Image Analyzer Tests ---

class TestImageAnalyzer:
    def test_analyze_image(self, test_image):
        results = analyze_image(test_image)
        assert results["dimensions"]["width"] == 64
        assert results["dimensions"]["height"] == 64
        assert "entropy" in results
        assert "red" in results["entropy"]
        assert "average" in results["entropy"]
        assert results["entropy_quality"] in ("excellent", "good", "moderate", "low")
        assert results["unique_colors"] > 0


# --- Package API Tests ---

class TestPackageAPI:
    def test_version(self):
        assert paradox.__version__ == "1.0.0"

    def test_camel_case_aliases(self, test_image_path):
        img = paradox.useImage(test_image_path)
        assert img.width == 64

    def test_all_apis_importable(self):
        """Verify all specified public APIs are accessible."""
        assert callable(paradox.useImage)
        assert callable(paradox.getRandomImage)
        assert callable(paradox.analyze_image)
        assert callable(paradox.visualize_walk)
        assert callable(paradox.generate_key)
        assert callable(paradox.generate_key128)
        assert callable(paradox.generate_key256)
        assert callable(paradox.generate_key512)
        assert callable(paradox.encrypt)
        assert callable(paradox.decrypt)
        assert callable(paradox.encrypt_text)
        assert callable(paradox.decrypt_text)
        assert callable(paradox.encrypt_file)
        assert callable(paradox.decrypt_file)
        assert callable(paradox.export_metadata)
        assert callable(paradox.import_metadata)
        assert callable(paradox.export_entropy)
        assert callable(paradox.debug_walk)

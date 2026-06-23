"""Shared utilities for the Paradox benchmarking suite."""

import sys
import time
import hashlib
import tempfile
import tracemalloc
from pathlib import Path
from contextlib import contextmanager
from typing import Tuple, Optional, Dict, List

import numpy as np
from PIL import Image
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from paradox.image_source.local import use_image, ImageData
from paradox.kdf.hkdf import generate_key

# ---------------------------------------------------------------------------
# Image helpers
# ---------------------------------------------------------------------------

_IMG_CACHE = Path(tempfile.gettempdir()) / "paradox_bench_images"


def create_test_image(width: int = 64, height: int = 64, seed: int = 42) -> str:
    """Create a deterministic synthetic test image, return its path."""
    _IMG_CACHE.mkdir(parents=True, exist_ok=True)
    path = _IMG_CACHE / f"bench_{width}x{height}_s{seed}.png"
    if not path.exists():
        rng = np.random.RandomState(seed)
        pixels = rng.randint(0, 256, (height, width, 3), dtype=np.uint8)
        Image.fromarray(pixels, "RGB").save(str(path))
    return str(path)


def load_test_image(width: int = 64, height: int = 64, seed: int = 42) -> ImageData:
    """Create and load a test image as ImageData."""
    return use_image(create_test_image(width, height, seed))


def create_modified_image(
    image: ImageData,
    x: int = 0,
    y: int = 0,
    channel: int = 0,
    delta: int = 1,
) -> ImageData:
    """Return a copy of *image* with a single pixel value changed."""
    modified = image.pixels.copy()
    old_val = int(modified[y, x, channel])
    modified[y, x, channel] = (old_val + delta) % 256
    _IMG_CACHE.mkdir(parents=True, exist_ok=True)
    h = hashlib.sha256(modified.tobytes()).hexdigest()[:12]
    path = _IMG_CACHE / f"mod_{h}.png"
    if not path.exists():
        Image.fromarray(modified, "RGB").save(str(path))
    return use_image(str(path))


# ---------------------------------------------------------------------------
# Key generation wrapper
# ---------------------------------------------------------------------------


def gen_key(
    image: ImageData,
    nonce: Optional[bytes] = None,
    timestamp: Optional[float] = None,
    security_level: str = "low",
    key_length: int = 32,
    kdf: str = "hkdf",
) -> Tuple[bytes, dict]:
    """Thin wrapper around paradox.kdf.hkdf.generate_key."""
    return generate_key(
        image,
        key_length=key_length,
        security_level=security_level,
        kdf=kdf,
        nonce=nonce,
        timestamp=timestamp,
    )


def _parallel_gen_key_worker(args) -> bytes:
    path, nonce, timestamp, security_level, key_length, kdf = args
    from paradox.image_source.local import use_image
    from paradox.kdf.hkdf import generate_key

    image = use_image(path)
    key, _ = generate_key(
        image,
        key_length=key_length,
        security_level=security_level,
        kdf=kdf,
        nonce=nonce,
        timestamp=timestamp,
    )
    return key


def gen_keys_parallel(
    image_path: str,
    nonces: List[bytes],
    timestamp: Optional[float] = None,
    security_level: str = "low",
    key_length: int = 32,
    kdf: str = "hkdf",
    max_workers: Optional[int] = None,
) -> List[bytes]:
    """Generate multiple keys in parallel using multiprocessing."""
    import concurrent.futures

    tasks = [
        (image_path, nonce, timestamp, security_level, key_length, kdf)
        for nonce in nonces
    ]
    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(_parallel_gen_key_worker, tasks))
    return results


# ---------------------------------------------------------------------------
# Analytical helpers
# ---------------------------------------------------------------------------


def bit_difference(a: bytes, b: bytes) -> Tuple[int, float]:
    """Return (differing_bits, percentage)."""
    total = len(a) * 8
    diff = sum(bin(x ^ y).count("1") for x, y in zip(a, b))
    return diff, diff / total * 100.0


def shannon_entropy(data: bytes) -> float:
    """Shannon entropy of a byte sequence (bits, max 8.0)."""
    if not data:
        return 0.0
    counts = np.bincount(list(data), minlength=256).astype(np.float64)
    probs = counts / len(data)
    probs = probs[probs > 0]
    return float(-np.sum(probs * np.log2(probs)))


def bit_distribution(data: bytes) -> Tuple[int, int]:
    """Return (zero_bits, one_bits)."""
    ones = sum(bin(b).count("1") for b in data)
    return len(data) * 8 - ones, ones


def chi_square_bytes(data: bytes) -> float:
    """Chi-square statistic vs. uniform byte distribution."""
    observed = np.bincount(list(data), minlength=256).astype(np.float64)
    expected = len(data) / 256.0
    return float(np.sum((observed - expected) ** 2 / expected))


# ---------------------------------------------------------------------------
# Timing / memory context managers
# ---------------------------------------------------------------------------


@contextmanager
def timer():
    result: Dict[str, float] = {"elapsed": 0.0}
    t0 = time.perf_counter()
    try:
        yield result
    finally:
        result["elapsed"] = time.perf_counter() - t0


@contextmanager
def memory_tracker():
    result: Dict[str, float] = {"peak_mb": 0.0, "current_mb": 0.0}
    tracemalloc.start()
    try:
        yield result
    finally:
        cur, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        result["current_mb"] = cur / 1_048_576
        result["peak_mb"] = peak / 1_048_576


# ---------------------------------------------------------------------------
# Console helpers
# ---------------------------------------------------------------------------


def progress(current: int, total: int, prefix: str = "", width: int = 40) -> None:
    pct = current / total if total else 1
    filled = int(width * pct)
    bar = "█" * filled + "░" * (width - filled)
    sys.stdout.write(f"\r  {prefix} [{bar}] {current}/{total}")
    sys.stdout.flush()
    if current >= total:
        sys.stdout.write("\n")


def header(title: str) -> None:
    print(f"\n{'=' * 64}")
    print(f"  {title}")
    print(f"{'=' * 64}\n")


# ---------------------------------------------------------------------------
# Plot style
# ---------------------------------------------------------------------------


def apply_plot_style() -> None:
    """Apply a consistent plot style for all charts."""
    try:
        plt.style.use("seaborn-v0_8-darkgrid")
    except OSError:
        try:
            plt.style.use("ggplot")
        except OSError:
            pass
    plt.rcParams.update(
        {
            "figure.figsize": (10, 6),
            "font.size": 11,
            "axes.titlesize": 14,
            "axes.labelsize": 12,
            "savefig.dpi": 150,
            "savefig.bbox": "tight",
        }
    )

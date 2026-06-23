"""Phase 7 — Performance Benchmarking.

Measure key generation, encryption, and decryption times
across different image sizes.
"""

import os
from pathlib import Path
from typing import Any, Dict, List

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from paradox.image_source.local import use_image
from paradox.crypto.interface import encrypt_text, decrypt_text

from paradox_benchmarks.utils import (
    create_test_image,
    load_test_image,
    gen_key,
    timer,
    header,
    apply_plot_style,
)


def run(output_dir: Path, config: Dict[str, Any]) -> Dict[str, Any]:
    header("PHASE 7: PERFORMANCE BENCHMARKING")

    sizes = config.get("phase7_sizes", [256, 512, 1024])
    iterations = config.get("phase7_iterations", 3)
    test_text = "Paradox benchmark payload — " * 20  # ~600 bytes

    rows: List[Dict[str, Any]] = []

    for size in sizes:
        print(f"\n  Image {size}×{size}  ({iterations} iterations) …")

        # Image load time
        load_times = []
        for _ in range(iterations):
            path = create_test_image(size, size, seed=42)
            with timer() as t:
                img = use_image(path)
            load_times.append(t["elapsed"])

        img = load_test_image(size, size, seed=42)

        # Key generation time
        keygen_times = []
        for _ in range(iterations):
            with timer() as t:
                k, _ = gen_key(img, nonce=os.urandom(32), security_level="low")
            keygen_times.append(t["elapsed"])

        # Encryption time
        enc_times = []
        encrypted_bundle = None
        for _ in range(iterations):
            with timer() as t:
                encrypted_bundle = encrypt_text(test_text, img, security_level="low")
            enc_times.append(t["elapsed"])

        # Decryption time
        dec_times = []
        for _ in range(iterations):
            with timer() as t:
                _ = decrypt_text(encrypted_bundle, img)
            dec_times.append(t["elapsed"])

        row = {
            "size": f"{size}x{size}",
            "pixels": size * size,
            "image_load_ms": round(np.mean(load_times) * 1000, 2),
            "keygen_ms": round(np.mean(keygen_times) * 1000, 2),
            "encrypt_ms": round(np.mean(enc_times) * 1000, 2),
            "decrypt_ms": round(np.mean(dec_times) * 1000, 2),
            "total_ms": round(
                (np.mean(load_times) + np.mean(keygen_times) + np.mean(enc_times))
                * 1000,
                2,
            ),
        }
        rows.append(row)

        print(
            f"    Load: {row['image_load_ms']:.0f} ms  |  "
            f"KeyGen: {row['keygen_ms']:.0f} ms  |  "
            f"Encrypt: {row['encrypt_ms']:.0f} ms  |  "
            f"Decrypt: {row['decrypt_ms']:.0f} ms"
        )

    # Print table
    print(
        f"\n  {'Size':<12} {'Load (ms)':>10} {'KeyGen (ms)':>12} {'Enc (ms)':>10} {'Dec (ms)':>10} {'Total (ms)':>12}"
    )
    print(f"  {'-'*66}")
    for r in rows:
        print(
            f"  {r['size']:<12} {r['image_load_ms']:>10.1f} {r['keygen_ms']:>12.1f} "
            f"{r['encrypt_ms']:>10.1f} {r['decrypt_ms']:>10.1f} {r['total_ms']:>12.1f}"
        )

    # ---- Charts ----
    chart_dir = output_dir / "performance"
    chart_dir.mkdir(parents=True, exist_ok=True)
    apply_plot_style()

    labels = [r["size"] for r in rows]
    x = np.arange(len(labels))
    width = 0.2

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(
        x - 1.5 * width,
        [r["image_load_ms"] for r in rows],
        width,
        label="Image Load",
        color="#4e79a7",
        alpha=0.85,
    )
    ax.bar(
        x - 0.5 * width,
        [r["keygen_ms"] for r in rows],
        width,
        label="Key Gen",
        color="#59a14f",
        alpha=0.85,
    )
    ax.bar(
        x + 0.5 * width,
        [r["encrypt_ms"] for r in rows],
        width,
        label="Encrypt",
        color="#e15759",
        alpha=0.85,
    )
    ax.bar(
        x + 1.5 * width,
        [r["decrypt_ms"] for r in rows],
        width,
        label="Decrypt",
        color="#f28e2b",
        alpha=0.85,
    )
    ax.set_xlabel("Image Size")
    ax.set_ylabel("Time (ms)")
    ax.set_title("Performance by Image Size (LOW security)")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()
    p1 = chart_dir / "performance_by_size.png"
    fig.savefig(str(p1))
    plt.close(fig)

    # Line plot
    fig, ax = plt.subplots(figsize=(10, 6))
    pixels = [r["pixels"] for r in rows]
    ax.plot(pixels, [r["keygen_ms"] for r in rows], "o-", label="Key Gen", linewidth=2)
    ax.plot(pixels, [r["encrypt_ms"] for r in rows], "s-", label="Encrypt", linewidth=2)
    ax.plot(pixels, [r["decrypt_ms"] for r in rows], "^-", label="Decrypt", linewidth=2)
    ax.set_xlabel("Total Pixels")
    ax.set_ylabel("Time (ms)")
    ax.set_title("Timing vs Image Size")
    ax.legend()
    ax.grid(True, alpha=0.3)
    p2 = chart_dir / "timing_vs_size.png"
    fig.savefig(str(p2))
    plt.close(fig)

    results = {"sizes": rows, "charts": [str(p1), str(p2)]}
    print(f"\n  Charts saved → {chart_dir}/")
    return results

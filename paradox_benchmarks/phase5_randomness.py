"""Phase 5 — Randomness Analysis.

Byte frequency, bit frequency, histogram, and chi-square test
over a large pool of generated key material.
"""

import os
from pathlib import Path
from typing import Any, Dict

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats as sp_stats

from paradox_benchmarks.utils import (
    load_test_image, gen_key, shannon_entropy, chi_square_bytes,
    bit_distribution, header, progress, apply_plot_style,
)


def run(output_dir: Path, config: Dict[str, Any]) -> Dict[str, Any]:
    header("PHASE 5: RANDOMNESS ANALYSIS")

    n_keys = config.get("phase5_keys", 1000)
    img = load_test_image(64, 64, seed=42)
    fixed_ts = 1_700_000_000.0

    all_bytes = bytearray()

    print(f"  Generating {n_keys:,} keys ({n_keys * 32:,} bytes of key material) …")
    if n_keys >= 500:
        from paradox_benchmarks.utils import gen_keys_parallel
        nonces = [os.urandom(32) for _ in range(n_keys)]
        all_keys = gen_keys_parallel(img.path, nonces, timestamp=fixed_ts, security_level="low")
        for k in all_keys:
            all_bytes.extend(k)
    else:
        for i in range(n_keys):
            k, _ = gen_key(img, nonce=os.urandom(32), timestamp=fixed_ts, security_level="low")
            all_bytes.extend(k)
            if (i + 1) % max(1, n_keys // 40) == 0 or i == n_keys - 1:
                progress(i + 1, n_keys, "Keys")

    data = bytes(all_bytes)
    total_bytes = len(data)
    total_bits = total_bytes * 8

    # Byte frequency
    byte_freq = np.bincount(list(data), minlength=256)
    expected_freq = total_bytes / 256.0

    # Bit frequency
    zeros, ones = bit_distribution(data)

    # Shannon entropy
    entropy = shannon_entropy(data)

    # Chi-square test (bytes vs uniform)
    chi2 = chi_square_bytes(data)
    # Degrees of freedom = 255; p-value
    chi2_p = 1.0 - float(sp_stats.chi2.cdf(chi2, df=255))

    stats = {
        "total_keys": n_keys,
        "total_bytes": total_bytes,
        "total_bits": total_bits,
        "shannon_entropy": round(entropy, 6),
        "max_entropy": 8.0,
        "entropy_ratio": round(entropy / 8.0, 6),
        "zero_bits": zeros,
        "one_bits": ones,
        "zero_pct": round(zeros / total_bits * 100, 4),
        "one_pct": round(ones / total_bits * 100, 4),
        "chi_square": round(chi2, 4),
        "chi_square_p_value": round(chi2_p, 6),
        "chi_square_dof": 255,
        "expected_byte_freq": round(expected_freq, 2),
        "byte_freq_std": round(float(np.std(byte_freq)), 4),
        "byte_freq_min": int(np.min(byte_freq)),
        "byte_freq_max": int(np.max(byte_freq)),
    }

    # Interpret chi-square: p > 0.01 means we cannot reject uniformity
    stats["chi_square_uniform"] = chi2_p > 0.01
    stats["quality"] = (
        "excellent" if chi2_p > 0.05 and entropy > 7.95
        else "good" if chi2_p > 0.01 and entropy > 7.9
        else "acceptable" if chi2_p > 0.001
        else "poor"
    )

    print(f"\n  Randomness Results ({total_bytes:,} bytes):")
    print(f"    Shannon entropy   : {entropy:.6f} / 8.0")
    print(f"    Bit distribution  : {stats['zero_pct']:.2f}% zeros, {stats['one_pct']:.2f}% ones")
    print(f"    Chi-square        : {chi2:.2f}  (p={chi2_p:.6f}, df=255)")
    print(f"    Uniform (p>0.01)  : {'YES ✓' if stats['chi_square_uniform'] else 'NO ✗'}")
    print(f"    Quality           : {stats['quality']}")

    # ---- Charts ----
    chart_dir = output_dir / "randomness"
    chart_dir.mkdir(parents=True, exist_ok=True)
    apply_plot_style()

    # Byte frequency histogram
    fig, ax = plt.subplots(figsize=(14, 5))
    ax.bar(range(256), byte_freq, color="#4e79a7", alpha=0.8, width=1.0)
    ax.axhline(expected_freq, color="red", linestyle="--", linewidth=1.5,
               label=f"Expected ({expected_freq:.1f})")
    ax.set_xlabel("Byte Value (0–255)")
    ax.set_ylabel("Frequency")
    ax.set_title(f"Byte Frequency Distribution ({total_bytes:,} bytes)")
    ax.legend()
    p1 = chart_dir / "byte_frequency.png"
    fig.savefig(str(p1))
    plt.close(fig)

    # Byte frequency deviation
    fig, ax = plt.subplots(figsize=(14, 5))
    deviation = (byte_freq - expected_freq) / expected_freq * 100
    colors = ["#e15759" if abs(d) > 15 else "#59a14f" for d in deviation]
    ax.bar(range(256), deviation, color=colors, alpha=0.8, width=1.0)
    ax.axhline(0, color="black", linewidth=0.5)
    ax.set_xlabel("Byte Value (0–255)")
    ax.set_ylabel("Deviation from Expected (%)")
    ax.set_title("Byte Frequency Deviation from Uniform")
    p2 = chart_dir / "byte_deviation.png"
    fig.savefig(str(p2))
    plt.close(fig)

    # Bit frequency bar
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.bar(["0-bits", "1-bits"], [zeros, ones], color=["#4e79a7", "#e15759"], alpha=0.85)
    ax.axhline(total_bits / 2, color="green", linestyle="--", label="Ideal (50%)")
    ax.set_ylabel("Count")
    ax.set_title(f"Bit Frequency ({total_bits:,} bits)")
    ax.legend()
    p3 = chart_dir / "bit_frequency.png"
    fig.savefig(str(p3))
    plt.close(fig)

    stats["charts"] = [str(p1), str(p2), str(p3)]
    print(f"  Charts saved → {chart_dir}/")
    return stats

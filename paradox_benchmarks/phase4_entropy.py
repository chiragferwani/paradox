"""Phase 4 — Entropy Analysis.

Shannon entropy and bit distribution of generated keys.
"""

import os
from pathlib import Path
from typing import Any, Dict, List

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from paradox_benchmarks.utils import (
    load_test_image,
    gen_key,
    shannon_entropy,
    bit_distribution,
    header,
    progress,
    apply_plot_style,
)


def run(output_dir: Path, config: Dict[str, Any]) -> Dict[str, Any]:
    header("PHASE 4: ENTROPY ANALYSIS")

    n_keys = config.get("phase4_keys", 50)
    img = load_test_image(64, 64, seed=42)
    fixed_ts = 1_700_000_000.0

    entropies: List[float] = []
    total_zeros = 0
    total_ones = 0
    all_key_bytes = bytearray()

    print(f"  Generating {n_keys} keys for entropy analysis …")
    for i in range(n_keys):
        k, _ = gen_key(
            img, nonce=os.urandom(32), timestamp=fixed_ts, security_level="low"
        )
        entropies.append(shannon_entropy(k))
        z, o = bit_distribution(k)
        total_zeros += z
        total_ones += o
        all_key_bytes.extend(k)
        if (i + 1) % max(1, n_keys // 20) == 0 or i == n_keys - 1:
            progress(i + 1, n_keys, "Keys")

    arr = np.array(entropies)
    total_bits = total_zeros + total_ones
    combined_entropy = shannon_entropy(bytes(all_key_bytes))

    stats = {
        "num_keys": n_keys,
        "per_key_entropy_mean": round(float(np.mean(arr)), 4),
        "per_key_entropy_std": round(float(np.std(arr)), 4),
        "per_key_entropy_min": round(float(np.min(arr)), 4),
        "per_key_entropy_max": round(float(np.max(arr)), 4),
        "combined_entropy": round(combined_entropy, 4),
        "max_possible_entropy": 8.0,
        "zero_bits": total_zeros,
        "one_bits": total_ones,
        "zero_pct": round(total_zeros / total_bits * 100, 4),
        "one_pct": round(total_ones / total_bits * 100, 4),
    }

    quality = (
        "excellent"
        if combined_entropy >= 7.9
        else (
            "good"
            if combined_entropy >= 7.5
            else "moderate" if combined_entropy >= 7.0 else "poor"
        )
    )
    stats["quality"] = quality

    print("\n  Entropy Analysis Results:")
    print(f"    Combined Shannon entropy : {combined_entropy:.4f} / 8.0 bits")
    print(f"    Per-key mean entropy     : {stats['per_key_entropy_mean']:.4f}")
    print(
        f"    Bit distribution         : {stats['zero_pct']:.2f}% zeros, {stats['one_pct']:.2f}% ones"
    )
    print(f"    Quality                  : {quality}")

    # ---- Charts ----
    chart_dir = output_dir / "entropy"
    chart_dir.mkdir(parents=True, exist_ok=True)
    apply_plot_style()

    # Per-key entropy bar chart
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.bar(range(len(entropies)), entropies, color="#59a14f", alpha=0.8, width=1.0)
    ax.axhline(8.0, color="red", linestyle="--", label="Max (8.0)")
    ax.axhline(
        np.mean(arr), color="orange", linestyle="-", label=f"Mean ({np.mean(arr):.3f})"
    )
    ax.set_xlabel("Key Index")
    ax.set_ylabel("Shannon Entropy (bits)")
    ax.set_title(f"Per-Key Shannon Entropy (n={n_keys})")
    ax.set_ylim(0, 8.5)
    ax.legend()
    p1 = chart_dir / "per_key_entropy.png"
    fig.savefig(str(p1))
    plt.close(fig)

    # Bit distribution pie chart
    fig, ax = plt.subplots(figsize=(7, 7))
    ax.pie(
        [total_zeros, total_ones],
        labels=[
            f"0-bits ({stats['zero_pct']:.2f}%)",
            f"1-bits ({stats['one_pct']:.2f}%)",
        ],
        colors=["#4e79a7", "#e15759"],
        autopct="%1.2f%%",
        startangle=90,
        textprops={"fontsize": 12},
    )
    ax.set_title(f"Bit Distribution Across {n_keys} Keys")
    p2 = chart_dir / "bit_distribution.png"
    fig.savefig(str(p2))
    plt.close(fig)

    stats["charts"] = [str(p1), str(p2)]
    print(f"  Charts saved → {chart_dir}/")
    return stats

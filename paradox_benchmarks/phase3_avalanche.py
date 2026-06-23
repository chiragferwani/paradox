"""Phase 3 — Avalanche Effect Test.

Modify a single pixel and measure how many key bits change.
Ideal: ~50 % bit difference.
"""

import os
from pathlib import Path
from typing import Any, Dict, List

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from paradox_benchmarks.utils import (
    load_test_image, create_modified_image, gen_key,
    bit_difference, header, progress, apply_plot_style,
)


def run(output_dir: Path, config: Dict[str, Any]) -> Dict[str, Any]:
    header("PHASE 3: AVALANCHE EFFECT")

    n_runs = config.get("phase3_runs", 100)
    img = load_test_image(64, 64, seed=42)
    fixed_nonce = bytes(range(32))
    fixed_ts = 1_700_000_000.0

    orig_key, _ = gen_key(img, nonce=fixed_nonce, timestamp=fixed_ts)

    diffs: List[float] = []
    rng = np.random.RandomState(0)

    print(f"  Running {n_runs} avalanche tests …")
    for i in range(n_runs):
        # Pick a random pixel and channel to modify
        rx = rng.randint(0, img.width)
        ry = rng.randint(0, img.height)
        rc = rng.randint(0, 3)
        mod_img = create_modified_image(img, x=rx, y=ry, channel=rc, delta=1)
        mod_key, _ = gen_key(mod_img, nonce=fixed_nonce, timestamp=fixed_ts)
        _, pct = bit_difference(orig_key, mod_key)
        diffs.append(pct)
        if (i + 1) % max(1, n_runs // 20) == 0 or i == n_runs - 1:
            progress(i + 1, n_runs, "Runs")

    arr = np.array(diffs)
    stats = {
        "runs": n_runs,
        "mean_pct": round(float(np.mean(arr)), 4),
        "median_pct": round(float(np.median(arr)), 4),
        "std_pct": round(float(np.std(arr)), 4),
        "min_pct": round(float(np.min(arr)), 4),
        "max_pct": round(float(np.max(arr)), 4),
    }

    ideal_deviation = abs(stats["mean_pct"] - 50.0)
    stats["deviation_from_ideal"] = round(ideal_deviation, 4)
    stats["quality"] = (
        "excellent" if ideal_deviation < 3
        else "good" if ideal_deviation < 5
        else "acceptable" if ideal_deviation < 10
        else "poor"
    )

    print(f"\n  Avalanche Statistics:")
    print(f"    Mean bit diff  : {stats['mean_pct']:.2f} %")
    print(f"    Std deviation  : {stats['std_pct']:.2f} %")
    print(f"    Min / Max      : {stats['min_pct']:.2f} % / {stats['max_pct']:.2f} %")
    print(f"    Quality        : {stats['quality']}")

    # ---- Charts ----
    chart_dir = output_dir / "avalanche"
    chart_dir.mkdir(parents=True, exist_ok=True)

    apply_plot_style()

    # Histogram
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hist(diffs, bins=30, color="#4e79a7", edgecolor="white", alpha=0.85)
    ax.axvline(50, color="red", linestyle="--", linewidth=2, label="Ideal (50 %)")
    ax.axvline(stats["mean_pct"], color="lime", linestyle="-", linewidth=2,
               label=f"Mean ({stats['mean_pct']:.2f} %)")
    ax.set_xlabel("Bit Difference (%)")
    ax.set_ylabel("Frequency")
    ax.set_title(f"Avalanche Effect Distribution (n={n_runs})")
    ax.legend()
    hist_path = chart_dir / "avalanche_histogram.png"
    fig.savefig(str(hist_path))
    plt.close(fig)

    # Box plot
    fig, ax = plt.subplots(figsize=(8, 5))
    bp = ax.boxplot(diffs, vert=True, patch_artist=True,
                    boxprops=dict(facecolor="#4e79a7", alpha=0.7))
    ax.axhline(50, color="red", linestyle="--", linewidth=1.5, label="Ideal (50 %)")
    ax.set_ylabel("Bit Difference (%)")
    ax.set_title("Avalanche Effect Box Plot")
    ax.legend()
    box_path = chart_dir / "avalanche_boxplot.png"
    fig.savefig(str(box_path))
    plt.close(fig)

    stats["charts"] = [str(hist_path), str(box_path)]
    print(f"  Charts saved → {chart_dir}/")
    return stats

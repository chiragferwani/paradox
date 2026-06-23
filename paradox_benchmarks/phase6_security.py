"""Phase 6 — Security Level Analysis.

Compare LOW / MEDIUM / HIGH / EXTREME on execution time,
memory usage, key generation speed, and entropy score.
"""

import os
import time
from pathlib import Path
from typing import Any, Dict, List

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from paradox_benchmarks.utils import (
    load_test_image, gen_key, shannon_entropy, timer, memory_tracker,
    header, apply_plot_style,
)


_LEVELS = ["low", "medium", "high", "extreme"]


def run(output_dir: Path, config: Dict[str, Any]) -> Dict[str, Any]:
    header("PHASE 6: SECURITY LEVEL ANALYSIS")

    levels_to_test = config.get("phase6_levels", ["low", "medium", "high"])
    img = load_test_image(64, 64, seed=42)
    nonce = bytes(range(32))
    ts = 1_700_000_000.0

    rows: List[Dict[str, Any]] = []

    for lvl in levels_to_test:
        print(f"  Testing security level: {lvl.upper()} …", end=" ", flush=True)

        with memory_tracker() as mem:
            with timer() as t:
                key, meta = gen_key(img, nonce=nonce, timestamp=ts, security_level=lvl)

        ent = shannon_entropy(key)
        steps = meta["total_steps"]
        layers = meta["layers"]

        row = {
            "level": lvl.upper(),
            "steps_per_layer": meta["steps_per_layer"],
            "layers": layers,
            "total_steps": steps,
            "time_s": round(t["elapsed"], 4),
            "peak_memory_mb": round(mem["peak_mb"], 2),
            "keys_per_sec": round(1.0 / t["elapsed"], 4) if t["elapsed"] > 0 else float("inf"),
            "entropy": round(ent, 4),
            "key_hex": key.hex(),
        }
        rows.append(row)
        print(f"  {t['elapsed']:.2f}s  |  {mem['peak_mb']:.1f} MB  |  entropy {ent:.4f}")

    # Print comparison table
    print(f"\n  {'Level':<10} {'Steps':>12} {'Layers':>7} {'Time (s)':>10} {'Mem (MB)':>10} {'Keys/s':>10} {'Entropy':>8}")
    print(f"  {'-'*67}")
    for r in rows:
        print(
            f"  {r['level']:<10} {r['total_steps']:>12,} {r['layers']:>7} "
            f"{r['time_s']:>10.3f} {r['peak_memory_mb']:>10.2f} "
            f"{r['keys_per_sec']:>10.3f} {r['entropy']:>8.4f}"
        )

    # ---- Charts ----
    chart_dir = output_dir / "performance"
    chart_dir.mkdir(parents=True, exist_ok=True)
    apply_plot_style()

    labels = [r["level"] for r in rows]
    times = [r["time_s"] for r in rows]
    mems = [r["peak_memory_mb"] for r in rows]
    entropies = [r["entropy"] for r in rows]

    fig, axes = plt.subplots(1, 3, figsize=(16, 5))

    axes[0].bar(labels, times, color="#4e79a7", alpha=0.85)
    axes[0].set_ylabel("Time (seconds)")
    axes[0].set_title("Key Generation Time")
    for i, v in enumerate(times):
        axes[0].text(i, v + max(times) * 0.02, f"{v:.2f}s", ha="center", fontsize=9)

    axes[1].bar(labels, mems, color="#e15759", alpha=0.85)
    axes[1].set_ylabel("Peak Memory (MB)")
    axes[1].set_title("Memory Usage")
    for i, v in enumerate(mems):
        axes[1].text(i, v + max(mems) * 0.02, f"{v:.1f}", ha="center", fontsize=9)

    axes[2].bar(labels, entropies, color="#59a14f", alpha=0.85)
    axes[2].set_ylabel("Shannon Entropy (bits)")
    axes[2].set_title("Key Entropy")
    axes[2].set_ylim(0, 8.5)
    for i, v in enumerate(entropies):
        axes[2].text(i, v + 0.1, f"{v:.3f}", ha="center", fontsize=9)

    fig.suptitle("Security Level Comparison", fontsize=15, fontweight="bold")
    plt.tight_layout()
    p1 = chart_dir / "security_level_comparison.png"
    fig.savefig(str(p1))
    plt.close(fig)

    results = {"levels": rows, "charts": [str(p1)]}
    print(f"\n  Chart saved → {p1}")
    return results

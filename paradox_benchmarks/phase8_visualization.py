"""Phase 8 — Visualization.

Generates walk traversal plots, heatmaps, entropy density maps,
and layer visualizations using Paradox internals.
"""

import os
from pathlib import Path
from typing import Any, Dict

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.cm as cm

from paradox.image_source.local import use_image
from paradox.seed.generator import generate_initial_seed
from paradox.recursion.layers import execute_recursion
from paradox.visualize.walk_visualizer import visualize_walk

from paradox_benchmarks.utils import (
    load_test_image, header, apply_plot_style,
)


def run(output_dir: Path, config: Dict[str, Any]) -> Dict[str, Any]:
    header("PHASE 8: VISUALIZATION")

    chart_dir = output_dir / "visualizations"
    chart_dir.mkdir(parents=True, exist_ok=True)
    apply_plot_style()

    img = load_test_image(128, 128, seed=42)
    nonce = bytes(range(32))
    ts = 1_700_000_000.0

    seed = generate_initial_seed(
        image_hash=img.image_hash, nonce=nonce, timestamp=ts,
    )

    # Use LOW for speed (1000 steps × 2 layers)
    print("  Executing recursive walk (LOW security, 128×128) …")
    result = execute_recursion(
        pixels=img.pixels, initial_seed=seed,
        width=img.width, height=img.height,
        security_level="low", record_steps=True,
    )

    charts: list = []

    # 1. Built-in visualizer (traversal + heatmap + entropy density)
    print("  Generating walk visualization …")
    p = str(chart_dir / "walk_visualization.png")
    visualize_walk(
        result.layer_results, img.width, img.height,
        output_path=p, show_layers=True,
    )
    charts.append(p)
    print(f"    → {p}")

    # 2. Custom per-layer traversal paths
    print("  Generating per-layer traversal paths …")
    colors = cm.Set1(np.linspace(0, 1, len(result.layer_results)))
    fig, axes = plt.subplots(1, len(result.layer_results), figsize=(7 * len(result.layer_results), 6))
    if len(result.layer_results) == 1:
        axes = [axes]
    for idx, lr in enumerate(result.layer_results):
        ax = axes[idx]
        coords = lr.coordinates_visited
        sample = coords[:min(500, len(coords))]
        xs = [c[0] for c in sample]
        ys = [c[1] for c in sample]
        ax.plot(xs, ys, linewidth=0.4, alpha=0.6, color=colors[idx])
        if xs:
            ax.scatter(xs[0], ys[0], c="lime", s=60, zorder=5, edgecolors="black", label="Start")
            ax.scatter(xs[-1], ys[-1], c="red", s=60, zorder=5, edgecolors="black", label="End")
        ax.set_xlim(0, img.width)
        ax.set_ylim(img.height, 0)
        ax.set_aspect("equal")
        ax.set_facecolor("black")
        ax.set_title(f"Layer {idx} ({len(coords)} steps)")
        ax.legend(fontsize=8)
    fig.suptitle("Per-Layer Walk Traversal", fontsize=14, fontweight="bold")
    plt.tight_layout()
    p2 = str(chart_dir / "per_layer_traversal.png")
    fig.savefig(p2)
    plt.close(fig)
    charts.append(p2)
    print(f"    → {p2}")

    # 3. Combined pixel heatmap (high-res)
    print("  Generating pixel visit heatmap …")
    heatmap = np.zeros((img.height, img.width))
    for lr in result.layer_results:
        for x, y in lr.coordinates_visited:
            heatmap[y, x] += 1

    fig, ax = plt.subplots(figsize=(8, 8))
    im = ax.imshow(heatmap, cmap="inferno", interpolation="bilinear")
    plt.colorbar(im, ax=ax, label="Visit Count")
    ax.set_title("Pixel Visit Heatmap (All Layers)")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    p3 = str(chart_dir / "pixel_heatmap.png")
    fig.savefig(p3)
    plt.close(fig)
    charts.append(p3)
    print(f"    → {p3}")

    # 4. Entropy density map
    print("  Generating entropy density map …")
    bin_size = 8
    bx = max(1, img.width // bin_size)
    by = max(1, img.height // bin_size)
    density = np.zeros((by, bx))
    for lr in result.layer_results:
        for x, y in lr.coordinates_visited:
            density[min(y // bin_size, by - 1), min(x // bin_size, bx - 1)] += 1

    total = density.sum()
    if total > 0:
        prob = density / total
        with np.errstate(divide="ignore", invalid="ignore"):
            ent_map = -prob * np.log2(prob + 1e-12)
    else:
        ent_map = density

    fig, ax = plt.subplots(figsize=(8, 8))
    im = ax.imshow(ent_map, cmap="viridis", interpolation="bilinear")
    plt.colorbar(im, ax=ax, label="Spatial Entropy")
    ax.set_title("Entropy Density Map")
    p4 = str(chart_dir / "entropy_density.png")
    fig.savefig(p4)
    plt.close(fig)
    charts.append(p4)
    print(f"    → {p4}")

    # 5. Coverage analysis
    print("  Computing coverage statistics …")
    total_pixels = img.width * img.height
    visited = np.count_nonzero(heatmap)
    coverage_pct = visited / total_pixels * 100
    total_visits = int(heatmap.sum())
    max_visits = int(heatmap.max())

    coverage = {
        "total_pixels": total_pixels,
        "unique_visited": int(visited),
        "coverage_pct": round(coverage_pct, 2),
        "total_visits": total_visits,
        "max_visits_per_pixel": max_visits,
        "mean_visits": round(total_visits / max(visited, 1), 2),
    }
    print(f"    Coverage: {coverage_pct:.1f}% ({visited}/{total_pixels} pixels visited)")
    print(f"    Max visits per pixel: {max_visits}")

    print(f"\n  All visualizations saved → {chart_dir}/")
    return {"charts": charts, "coverage": coverage}

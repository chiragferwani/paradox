#!/usr/bin/env python3
"""
Generate additional research-quality visualizations for the Paradox RVE-KDE paper.
Reads data from comparison_metrics.json and paper_metrics.json.
Saves all plots to comparison_visualizations/.
"""

import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.gridspec import GridSpec
from pathlib import Path

# ──────────────────────────────────────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────────────────────────────────────
REPO_ROOT   = Path(__file__).resolve().parent
OUT_DIR     = REPO_ROOT / "comparison_visualizations"
METRICS_F   = REPO_ROOT / "comparison_metrics.json"
PAPER_F     = REPO_ROOT / "paper_metrics.json"
OUT_DIR.mkdir(exist_ok=True)

# Publication-ready style
plt.rcParams.update({
    "figure.dpi": 150,
    "savefig.dpi": 300,
    "font.family": "DejaVu Sans",
    "axes.titlesize": 14,
    "axes.labelsize": 12,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "legend.fontsize": 10,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.alpha": 0.35,
    "grid.linestyle": "--",
})

PALETTE = {
    "paradox": "#4C72B0",
    "pbkdf2":  "#DD8452",
    "hkdf":    "#C44E52",
    "argon2id":"#55A868",
    "blake3":  "#8172B2",
}
LABEL = {
    "paradox": "Paradox (RVE-KDE)",
    "pbkdf2":  "PBKDF2-SHA256",
    "hkdf":    "HKDF-SHA256",
    "argon2id":"Argon2id",
    "blake3":  "BLAKE3-KDF",
}
KDF_ORDER = ["paradox", "pbkdf2", "hkdf", "argon2id", "blake3"]

# Load data
with open(METRICS_F) as f:
    M = json.load(f)
with open(PAPER_F) as f:
    PM = json.load(f)


# ──────────────────────────────────────────────────────────────────────────────
# 1. Entropy Comparison Across Key Sizes  (grouped bar chart)
# ──────────────────────────────────────────────────────────────────────────────
def plot_entropy_comparison():
    key_sizes = ["128", "256", "512"]
    x = np.arange(len(key_sizes))
    width = 0.15
    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.set_facecolor("#f0f2f7")
    fig.patch.set_facecolor("#f0f2f7")

    for i, kdf in enumerate(KDF_ORDER):
        vals = [M["entropy_results"][kdf][k]["entropy"] for k in key_sizes]
        bars = ax.bar(x + i * width - 2 * width, vals, width,
                      label=LABEL[kdf], color=PALETTE[kdf], alpha=0.88,
                      edgecolor="white", linewidth=0.6)

    ax.set_xlabel("Key Size (bits)")
    ax.set_ylabel("Shannon Entropy (bits/byte)")
    ax.set_title("Shannon Entropy Comparison Across Key Sizes")
    ax.set_xticks(x)
    ax.set_xticklabels(["128-bit", "256-bit", "512-bit"])
    ax.set_ylim(7.82, 7.99)
    ax.axhline(8.0, color="red", linestyle="--", linewidth=1.2, label="Theoretical Max (8.0)", alpha=0.7)
    ax.legend(framealpha=0.85, ncol=2)
    fig.tight_layout()
    out = OUT_DIR / "entropy_comparison.png"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    print(f"  ✓ {out.name}")


# ──────────────────────────────────────────────────────────────────────────────
# 2. Chi-Square p-value Heatmap  (KDF × Key-Size)
# ──────────────────────────────────────────────────────────────────────────────
def plot_chi2_heatmap():
    key_sizes = ["128", "256", "512"]
    data = np.array([
        [M["entropy_results"][kdf][k]["p_value"] for k in key_sizes]
        for kdf in KDF_ORDER
    ])

    cmap = LinearSegmentedColormap.from_list(
        "pval", ["#d73027", "#fee090", "#91cf60", "#1a9850"])
    fig, ax = plt.subplots(figsize=(7, 4.5))
    fig.patch.set_facecolor("#f0f2f7")
    ax.set_facecolor("#f0f2f7")

    im = ax.imshow(data, cmap=cmap, vmin=0.0, vmax=1.0, aspect="auto")
    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label("Chi-Square p-value", fontsize=10)

    ax.set_xticks(range(len(key_sizes)))
    ax.set_xticklabels(["128-bit", "256-bit", "512-bit"])
    ax.set_yticks(range(len(KDF_ORDER)))
    ax.set_yticklabels([LABEL[k] for k in KDF_ORDER])
    ax.set_title("Chi-Square Uniformity Test p-values\n(p > 0.01 = PASS)", pad=12)

    # Annotate cells
    for i in range(len(KDF_ORDER)):
        for j in range(len(key_sizes)):
            txt = f"{data[i, j]:.3f}"
            col = "black" if data[i, j] > 0.4 else "white"
            ax.text(j, i, txt, ha="center", va="center", fontsize=9,
                    color=col, fontweight="bold")

    # PASS threshold line annotation
    ax.axhline(-0.5, color="gray", linewidth=0.5)

    fig.tight_layout()
    out = OUT_DIR / "chi2_pvalue_heatmap.png"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    print(f"  ✓ {out.name}")


# ──────────────────────────────────────────────────────────────────────────────
# 3. Memory Footprint Comparison  (grouped bar chart, log scale)
# ──────────────────────────────────────────────────────────────────────────────
def plot_memory_comparison():
    levels = ["low", "medium", "high"]
    x = np.arange(len(levels))
    width = 0.15
    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.set_facecolor("#f0f2f7")
    fig.patch.set_facecolor("#f0f2f7")

    for i, kdf in enumerate(KDF_ORDER):
        vals = [max(M["memory_results"][lvl][kdf]["peak_memory_mb"], 1e-4)
                for lvl in levels]
        ax.bar(x + i * width - 2 * width, vals, width,
               label=LABEL[kdf], color=PALETTE[kdf], alpha=0.88,
               edgecolor="white", linewidth=0.6)

    ax.set_yscale("log")
    ax.set_xlabel("Configured Security Level")
    ax.set_ylabel("Peak Memory Usage (MB, Log Scale)")
    ax.set_title("Peak Memory Footprint Comparison Across Security Levels")
    ax.set_xticks(x)
    ax.set_xticklabels(["LOW", "MEDIUM", "HIGH"])
    ax.legend(framealpha=0.85, ncol=2)
    fig.tight_layout()
    out = OUT_DIR / "memory_footprint_comparison.png"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    print(f"  ✓ {out.name}")


# ──────────────────────────────────────────────────────────────────────────────
# 4. Throughput Comparison  (grouped bar chart)
# ──────────────────────────────────────────────────────────────────────────────
def plot_throughput_comparison():
    levels = ["low", "medium", "high"]
    x = np.arange(len(levels))
    width = 0.15
    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.set_facecolor("#f0f2f7")
    fig.patch.set_facecolor("#f0f2f7")

    for i, kdf in enumerate(KDF_ORDER):
        vals = [M["performance_results"][lvl][kdf]["keys_per_sec"] for lvl in levels]
        ax.bar(x + i * width - 2 * width, vals, width,
               label=LABEL[kdf], color=PALETTE[kdf], alpha=0.88,
               edgecolor="white", linewidth=0.6)

    ax.set_yscale("log")
    ax.set_xlabel("Configured Security Level")
    ax.set_ylabel("Throughput (keys/sec, Log Scale)")
    ax.set_title("Key Generation Throughput Comparison Across Security Levels")
    ax.set_xticks(x)
    ax.set_xticklabels(["LOW", "MEDIUM", "HIGH"])
    ax.legend(framealpha=0.85, ncol=2)
    fig.tight_layout()
    out = OUT_DIR / "throughput_comparison.png"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    print(f"  ✓ {out.name}")


# ──────────────────────────────────────────────────────────────────────────────
# 5. Avalanche Effect Radar / Spider Chart  (per-KDF mean vs std)
# ──────────────────────────────────────────────────────────────────────────────
def plot_avalanche_radar():
    """Radar chart: 5 KDFs × {mean, std, min_dev, max_dev} axes."""
    cats = ["Mean (%)", "Std Dev (%)", "Min (%)  ", "  Max (%)"]
    N = len(cats)
    angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(7, 7), subplot_kw=dict(polar=True))
    fig.patch.set_facecolor("#f0f2f7")
    ax.set_facecolor("#e8ebf5")

    # Normalise each axis to [0,1] over all KDFs
    raw = {kdf: [
        M["avalanche_results"][kdf]["mean"],
        M["avalanche_results"][kdf]["std"],
        M["avalanche_results"][kdf]["min"],
        M["avalanche_results"][kdf]["max"],
    ] for kdf in KDF_ORDER}

    mins_  = [min(raw[k][i] for k in KDF_ORDER) for i in range(N)]
    maxs_  = [max(raw[k][i] for k in KDF_ORDER) for i in range(N)]

    for kdf in KDF_ORDER:
        vals = [(raw[kdf][i] - mins_[i]) / max(maxs_[i] - mins_[i], 1e-9)
                for i in range(N)]
        vals += vals[:1]
        ax.plot(angles, vals, "o-", linewidth=1.8,
                label=LABEL[kdf], color=PALETTE[kdf])
        ax.fill(angles, vals, alpha=0.12, color=PALETTE[kdf])

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(cats, size=10)
    ax.set_yticklabels([])
    ax.set_title("Avalanche Effect Profile Comparison\n(normalised per axis)", pad=20)
    ax.legend(loc="upper right", bbox_to_anchor=(1.35, 1.1), framealpha=0.85)
    fig.tight_layout()
    out = OUT_DIR / "avalanche_radar.png"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    print(f"  ✓ {out.name}")


# ──────────────────────────────────────────────────────────────────────────────
# 6. Image Sensitivity Analysis  (Paradox-only horizontal bar)
# ──────────────────────────────────────────────────────────────────────────────
def plot_sensitivity_analysis():
    sens = M["paradox_sensitivity_results"]
    labels = [
        "Single Pixel\nModification",
        "Single Channel\nModification",
        "Image Rotation\n(90°)",
        "Image Crop\n(5%)",
        "Image Resize\n(±10%)",
    ]
    values = [
        sens["single_pixel_pct"],
        sens["single_channel_pct"],
        sens["image_rotation_pct"],
        sens["image_crop_pct"],
        sens["image_resize_pct"],
    ]
    colors = ["#4C72B0" if abs(v - 50) < 5 else "#C44E52" for v in values]

    fig, ax = plt.subplots(figsize=(9, 5))
    fig.patch.set_facecolor("#f0f2f7")
    ax.set_facecolor("#f0f2f7")

    bars = ax.barh(labels, values, color=colors, alpha=0.88,
                   edgecolor="white", linewidth=0.7, height=0.55)
    ax.axvline(50.0, color="red", linestyle="--", linewidth=1.4,
               label="Ideal (50.0%)", alpha=0.8)
    ax.axvspan(45, 55, alpha=0.07, color="green", label="±5% acceptance band")

    for bar, val in zip(bars, values):
        ax.text(val + 0.3, bar.get_y() + bar.get_height() / 2,
                f"{val:.2f}%", va="center", fontsize=10, fontweight="bold")

    ax.set_xlim(40, 65)
    ax.set_xlabel("Bit Difference After Perturbation (%)")
    ax.set_title("Paradox (RVE-KDE) — Image Sensitivity Analysis\n"
                 "Key Bit-Change % for Various Image Perturbations")
    ax.legend(framealpha=0.85)
    fig.tight_layout()
    out = OUT_DIR / "image_sensitivity_analysis.png"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    print(f"  ✓ {out.name}")


# ──────────────────────────────────────────────────────────────────────────────
# 7. Multi-panel Summary Dashboard
# ──────────────────────────────────────────────────────────────────────────────
def plot_summary_dashboard():
    fig = plt.figure(figsize=(16, 10))
    fig.patch.set_facecolor("#f0f2f7")
    gs = GridSpec(2, 3, figure=fig, hspace=0.42, wspace=0.38)

    bg = "#f0f2f7"

    # ── Panel A: Entropy 256-bit keys ──────────────────────────────────────
    ax_a = fig.add_subplot(gs[0, 0])
    ax_a.set_facecolor(bg)
    vals_e = [M["entropy_results"][k]["256"]["entropy"] for k in KDF_ORDER]
    bars_a = ax_a.bar([LABEL[k] for k in KDF_ORDER], vals_e,
                      color=[PALETTE[k] for k in KDF_ORDER], alpha=0.88,
                      edgecolor="white", linewidth=0.6)
    ax_a.axhline(8.0, color="red", linestyle="--", linewidth=1.1, alpha=0.7)
    ax_a.set_ylim(7.82, 7.99)
    ax_a.set_title("(A) Shannon Entropy\n(256-bit keys)", fontsize=11)
    ax_a.set_ylabel("bits/byte")
    ax_a.set_xticklabels([LABEL[k].replace(" ", "\n") for k in KDF_ORDER],
                          fontsize=7.5)
    for bar, v in zip(bars_a, vals_e):
        ax_a.text(bar.get_x() + bar.get_width() / 2, v + 0.0005,
                  f"{v:.4f}", ha="center", va="bottom", fontsize=7)

    # ── Panel B: Avalanche Mean ─────────────────────────────────────────────
    ax_b = fig.add_subplot(gs[0, 1])
    ax_b.set_facecolor(bg)
    means = [M["avalanche_results"][k]["mean"] for k in KDF_ORDER]
    stds  = [M["avalanche_results"][k]["std"]  for k in KDF_ORDER]
    ax_b.bar([LABEL[k] for k in KDF_ORDER], means, yerr=stds,
             color=[PALETTE[k] for k in KDF_ORDER], alpha=0.88,
             capsize=4, edgecolor="white", linewidth=0.6,
             error_kw={"elinewidth": 1.3, "ecolor": "#333"})
    ax_b.axhline(50.0, color="red", linestyle="--", linewidth=1.1, alpha=0.7)
    ax_b.set_ylim(45, 55)
    ax_b.set_title("(B) Avalanche Effect\nMean ± Std (%)", fontsize=11)
    ax_b.set_ylabel("Bit Difference (%)")
    ax_b.set_xticklabels([LABEL[k].replace(" ", "\n") for k in KDF_ORDER],
                          fontsize=7.5)

    # ── Panel C: Latency LOW (ms) ───────────────────────────────────────────
    ax_c = fig.add_subplot(gs[0, 2])
    ax_c.set_facecolor(bg)
    lats_low = [M["performance_results"]["low"][k]["latency_s"] * 1000
                for k in KDF_ORDER]
    ax_c.bar([LABEL[k] for k in KDF_ORDER], lats_low,
             color=[PALETTE[k] for k in KDF_ORDER], alpha=0.88,
             edgecolor="white", linewidth=0.6)
    ax_c.set_yscale("log")
    ax_c.set_title("(C) Keygen Latency\n(LOW security, ms log scale)", fontsize=11)
    ax_c.set_ylabel("Latency (ms)")
    ax_c.set_xticklabels([LABEL[k].replace(" ", "\n") for k in KDF_ORDER],
                          fontsize=7.5)

    # ── Panel D: Memory at HIGH level ───────────────────────────────────────
    ax_d = fig.add_subplot(gs[1, 0])
    ax_d.set_facecolor(bg)
    mems = [max(M["memory_results"]["high"][k]["peak_memory_mb"], 1e-4)
            for k in KDF_ORDER]
    ax_d.bar([LABEL[k] for k in KDF_ORDER], mems,
             color=[PALETTE[k] for k in KDF_ORDER], alpha=0.88,
             edgecolor="white", linewidth=0.6)
    ax_d.set_yscale("log")
    ax_d.set_title("(D) Peak Memory\n(HIGH security, MB log scale)", fontsize=11)
    ax_d.set_ylabel("Memory (MB)")
    ax_d.set_xticklabels([LABEL[k].replace(" ", "\n") for k in KDF_ORDER],
                          fontsize=7.5)

    # ── Panel E: Chi-Square p-value (256-bit) ───────────────────────────────
    ax_e = fig.add_subplot(gs[1, 1])
    ax_e.set_facecolor(bg)
    pvals = [M["entropy_results"][k]["256"]["p_value"] for k in KDF_ORDER]
    bars_e = ax_e.bar([LABEL[k] for k in KDF_ORDER], pvals,
                      color=[PALETTE[k] for k in KDF_ORDER], alpha=0.88,
                      edgecolor="white", linewidth=0.6)
    ax_e.axhline(0.01, color="red", linestyle="--", linewidth=1.1, alpha=0.7,
                 label="Reject Threshold (p=0.01)")
    ax_e.set_ylim(0, 1)
    ax_e.set_title("(E) Chi-Square p-value\n(256-bit, higher = more uniform)", fontsize=11)
    ax_e.set_ylabel("p-value")
    ax_e.set_xticklabels([LABEL[k].replace(" ", "\n") for k in KDF_ORDER],
                          fontsize=7.5)
    ax_e.legend(fontsize=8, framealpha=0.85)

    # ── Panel F: Image Sensitivity ──────────────────────────────────────────
    ax_f = fig.add_subplot(gs[1, 2])
    ax_f.set_facecolor(bg)
    sens = M["paradox_sensitivity_results"]
    s_labels = ["Pixel", "Channel", "Rotate", "Crop", "Resize"]
    s_values = [sens["single_pixel_pct"], sens["single_channel_pct"],
                sens["image_rotation_pct"], sens["image_crop_pct"],
                sens["image_resize_pct"]]
    s_colors = ["#4C72B0" if abs(v - 50) < 5 else "#C44E52" for v in s_values]
    ax_f.bar(s_labels, s_values, color=s_colors, alpha=0.88,
             edgecolor="white", linewidth=0.6)
    ax_f.axhline(50.0, color="red", linestyle="--", linewidth=1.1, alpha=0.7)
    ax_f.set_ylim(40, 65)
    ax_f.set_title("(F) Paradox Image Sensitivity\n(% bit-change per perturbation)", fontsize=11)
    ax_f.set_ylabel("Bit Difference (%)")

    fig.suptitle("Paradox (RVE-KDE) — Cryptographic Performance Summary Dashboard",
                 fontsize=15, fontweight="bold", y=1.01)

    out = OUT_DIR / "summary_dashboard.png"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    print(f"  ✓ {out.name}")


# ──────────────────────────────────────────────────────────────────────────────
# 8. Latency vs Security Level (line chart, linear)
# ──────────────────────────────────────────────────────────────────────────────
def plot_latency_linear():
    levels = ["low", "medium", "high"]
    level_labels = ["LOW", "MEDIUM", "HIGH"]
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.5), sharey=False)
    for ax in axes:
        ax.set_facecolor("#f0f2f7")
    fig.patch.set_facecolor("#f0f2f7")

    # Left: log scale (all KDFs)
    ax1 = axes[0]
    for kdf in KDF_ORDER:
        lats = [M["performance_results"][lvl][kdf]["latency_s"] * 1000
                for lvl in levels]
        ax1.plot(level_labels, lats, "o-", label=LABEL[kdf],
                 color=PALETTE[kdf], linewidth=2, markersize=6)
    ax1.set_yscale("log")
    ax1.set_ylabel("Latency (ms, Log Scale)")
    ax1.set_title("(a) All KDFs — Log Scale")
    ax1.legend(framealpha=0.85)

    # Right: linear scale without Paradox (to show traditional KDF differences)
    ax2 = axes[1]
    for kdf in KDF_ORDER:
        if kdf == "paradox":
            continue
        lats = [M["performance_results"][lvl][kdf]["latency_s"] * 1000
                for lvl in levels]
        ax2.plot(level_labels, lats, "o-", label=LABEL[kdf],
                 color=PALETTE[kdf], linewidth=2, markersize=6)
    ax2.set_ylabel("Latency (ms, Linear Scale)")
    ax2.set_title("(b) Traditional KDFs Only — Linear Scale")
    ax2.legend(framealpha=0.85)

    fig.suptitle("Key Generation Latency vs. Security Level", fontsize=14,
                 fontweight="bold")
    fig.tight_layout()
    out = OUT_DIR / "latency_linear_comparison.png"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    print(f"  ✓ {out.name}")


# ──────────────────────────────────────────────────────────────────────────────
# 9. Entropy vs Key Size  (line chart, all KDFs)
# ──────────────────────────────────────────────────────────────────────────────
def plot_entropy_vs_keysize():
    key_sizes = ["128", "256", "512"]
    key_x = [128, 256, 512]

    fig, ax = plt.subplots(figsize=(9, 5.5))
    ax.set_facecolor("#f0f2f7")
    fig.patch.set_facecolor("#f0f2f7")

    for kdf in KDF_ORDER:
        vals = [M["entropy_results"][kdf][k]["entropy"] for k in key_sizes]
        ax.plot(key_x, vals, "o-", label=LABEL[kdf],
                color=PALETTE[kdf], linewidth=2, markersize=7)

    ax.axhline(8.0, color="red", linestyle="--", linewidth=1.3,
               label="Theoretical Max (8.0 bits/byte)", alpha=0.7)
    ax.set_xticks(key_x)
    ax.set_xticklabels(["128-bit", "256-bit", "512-bit"])
    ax.set_ylabel("Shannon Entropy (bits/byte)")
    ax.set_xlabel("Derived Key Size")
    ax.set_title("Shannon Entropy vs. Derived Key Size\nAcross All KDF Systems")
    ax.set_ylim(7.82, 8.02)
    ax.legend(framealpha=0.85)
    fig.tight_layout()
    out = OUT_DIR / "entropy_vs_keysize.png"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    print(f"  ✓ {out.name}")


# ──────────────────────────────────────────────────────────────────────────────
# 10. Collision Elapsed Time Comparison  (horizontal bar)
# ──────────────────────────────────────────────────────────────────────────────
def plot_collision_time():
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.set_facecolor("#f0f2f7")
    fig.patch.set_facecolor("#f0f2f7")

    times = [M["collision_results"][k]["elapsed_s"] for k in KDF_ORDER]
    labels_c = [LABEL[k] for k in KDF_ORDER]
    colors_c  = [PALETTE[k] for k in KDF_ORDER]

    bars = ax.barh(labels_c, times, color=colors_c, alpha=0.88,
                   edgecolor="white", linewidth=0.6, height=0.55)
    for bar, t in zip(bars, times):
        ax.text(t + 0.3, bar.get_y() + bar.get_height() / 2,
                f"{t:.3f}s", va="center", fontsize=10, fontweight="bold")

    ax.set_xscale("log")
    ax.set_xlabel("Time to Generate 1,000 Keys (s, Log Scale)")
    ax.set_title("Collision-Test Elapsed Time\n(1,000 unique keys per KDF, 0 collisions observed)")
    fig.tight_layout()
    out = OUT_DIR / "collision_time_comparison.png"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    print(f"  ✓ {out.name}")


# ──────────────────────────────────────────────────────────────────────────────
# 11. Bit Distribution Comparison  (zero% vs one%)
# ──────────────────────────────────────────────────────────────────────────────
def plot_bit_distribution():
    key_sizes = ["128", "256", "512"]
    fig, axes = plt.subplots(1, 3, figsize=(14, 5), sharey=True)
    fig.patch.set_facecolor("#f0f2f7")

    for ax, ks in zip(axes, key_sizes):
        ax.set_facecolor("#f0f2f7")
        zeros = [M["entropy_results"][k][ks]["zero_pct"] for k in KDF_ORDER]
        ones  = [M["entropy_results"][k][ks]["one_pct"]  for k in KDF_ORDER]
        x = np.arange(len(KDF_ORDER))
        w = 0.35
        ax.bar(x - w/2, zeros, w, label="0-bits (%)", color="#4C72B0", alpha=0.82, edgecolor="white")
        ax.bar(x + w/2, ones,  w, label="1-bits (%)", color="#DD8452", alpha=0.82, edgecolor="white")
        ax.axhline(50.0, color="red", linestyle="--", linewidth=1.1, alpha=0.7)
        ax.set_ylim(48, 52)
        ax.set_xticks(x)
        ax.set_xticklabels([LABEL[k].replace(" ", "\n") for k in KDF_ORDER], fontsize=7)
        ax.set_title(f"{ks}-bit keys")
        if ax == axes[0]:
            ax.set_ylabel("Bit Proportion (%)")
            ax.legend(framealpha=0.85)

    fig.suptitle("Bit Distribution (0-bit vs 1-bit Ratio) Across KDF Systems",
                 fontsize=13, fontweight="bold")
    fig.tight_layout()
    out = OUT_DIR / "bit_distribution_comparison.png"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    print(f"  ✓ {out.name}")


# ──────────────────────────────────────────────────────────────────────────────
# 12. Avalanche Mean Bar + Error Bars  (focused, publication-ready)
# ──────────────────────────────────────────────────────────────────────────────
def plot_avalanche_mean_error():
    fig, ax = plt.subplots(figsize=(9, 5.5))
    ax.set_facecolor("#f0f2f7")
    fig.patch.set_facecolor("#f0f2f7")

    means = [M["avalanche_results"][k]["mean"] for k in KDF_ORDER]
    stds  = [M["avalanche_results"][k]["std"]  for k in KDF_ORDER]
    mins_ = [M["avalanche_results"][k]["min"]  for k in KDF_ORDER]
    maxs_ = [M["avalanche_results"][k]["max"]  for k in KDF_ORDER]

    x = np.arange(len(KDF_ORDER))
    bars = ax.bar(x, means, color=[PALETTE[k] for k in KDF_ORDER],
                  alpha=0.88, edgecolor="white", linewidth=0.8, width=0.55,
                  yerr=stds, capsize=6,
                  error_kw={"elinewidth": 1.6, "ecolor": "#222"})

    # Min-Max whiskers
    for xi, mn, mx in zip(x, mins_, maxs_):
        ax.plot([xi, xi], [mn, mx], color="#444", linewidth=1, zorder=3)
        ax.plot([xi - 0.1, xi + 0.1], [mn, mn], color="#444", linewidth=1, zorder=3)
        ax.plot([xi - 0.1, xi + 0.1], [mx, mx], color="#444", linewidth=1, zorder=3)

    ax.axhline(50.0, color="red", linestyle="--", linewidth=1.5,
               label="Ideal Avalanche (50.0%)", alpha=0.85)
    ax.axhspan(47.5, 52.5, alpha=0.07, color="green", label="±2.5% acceptance band")

    ax.set_xticks(x)
    ax.set_xticklabels([LABEL[k] for k in KDF_ORDER], rotation=10)
    ax.set_ylabel("Bit Difference After 1-bit Input Perturbation (%)")
    ax.set_title("Avalanche Effect Analysis — Mean, Std, Min & Max\n"
                 "1-bit input change → % changed output bits (ideal: 50%)")
    ax.set_ylim(38, 65)
    ax.legend(framealpha=0.85)
    fig.tight_layout()
    out = OUT_DIR / "avalanche_mean_error.png"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    print(f"  ✓ {out.name}")


# ──────────────────────────────────────────────────────────────────────────────
# 13. Cryptographic Quality Scorecard  (table-style heatmap)
# ──────────────────────────────────────────────────────────────────────────────
def plot_quality_scorecard():
    """
    Binary PASS/FAIL + quality score heatmap across multiple criteria.
    """
    criteria = [
        "Shannon Entropy\n≥ 7.95",
        "Chi-Sq Uniformity\np > 0.01",
        "Avalanche ≈ 50%\n(|mean−50| < 1%)",
        "Zero Collisions\n(1k keys)",
        "Mem-Hardness\n> 1 MB @ LOW",
    ]

    # Compute binary scores [0=fail, 1=pass] for each (kdf, criterion)
    scores = []
    for kdf in KDF_ORDER:
        row = []
        # Entropy (256-bit)
        row.append(1.0 if M["entropy_results"][kdf]["256"]["entropy"] >= 7.95 else 0.5)
        # Chi-sq
        row.append(1.0 if M["entropy_results"][kdf]["256"]["p_value"] > 0.01 else 0.0)
        # Avalanche
        row.append(1.0 if abs(M["avalanche_results"][kdf]["mean"] - 50.0) < 1.0 else 0.5)
        # Zero collisions
        row.append(1.0 if M["collision_results"][kdf]["collision_count"] == 0 else 0.0)
        # Mem hardness
        row.append(1.0 if M["memory_results"]["low"][kdf]["peak_memory_mb"] > 1.0 else 0.0)
        scores.append(row)

    data = np.array(scores)
    cmap = LinearSegmentedColormap.from_list("scorecard", ["#d73027", "#fee090", "#1a9850"])

    fig, ax = plt.subplots(figsize=(10, 5))
    fig.patch.set_facecolor("#f0f2f7")
    ax.set_facecolor("#f0f2f7")

    im = ax.imshow(data.T, cmap=cmap, vmin=0.0, vmax=1.0, aspect="auto")

    ax.set_xticks(range(len(KDF_ORDER)))
    ax.set_xticklabels([LABEL[k] for k in KDF_ORDER], rotation=10, fontsize=10)
    ax.set_yticks(range(len(criteria)))
    ax.set_yticklabels(criteria, fontsize=9)
    ax.set_title("Cryptographic Quality Scorecard\n"
                 "(Green = PASS, Yellow = PARTIAL, Red = FAIL)", pad=14)

    labels_map = {0.0: "FAIL", 0.5: "PARTIAL", 1.0: "PASS"}
    for i in range(len(KDF_ORDER)):
        for j in range(len(criteria)):
            txt = labels_map.get(data[i, j], f"{data[i,j]:.1f}")
            col = "white" if data[i, j] < 0.4 else "black"
            ax.text(i, j, txt, ha="center", va="center",
                    fontsize=10, fontweight="bold", color=col)

    cbar = fig.colorbar(im, ax=ax, fraction=0.025, pad=0.04)
    cbar.set_ticks([0, 0.5, 1.0])
    cbar.set_ticklabels(["FAIL", "PARTIAL", "PASS"])
    fig.tight_layout()
    out = OUT_DIR / "quality_scorecard.png"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    print(f"  ✓ {out.name}")


# ──────────────────────────────────────────────────────────────────────────────
# Run all
# ──────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Generating research visualizations for Paradox (RVE-KDE)…\n")
    plot_entropy_comparison()
    plot_chi2_heatmap()
    plot_memory_comparison()
    plot_throughput_comparison()
    plot_avalanche_radar()
    plot_sensitivity_analysis()
    plot_summary_dashboard()
    plot_latency_linear()
    plot_entropy_vs_keysize()
    plot_collision_time()
    plot_bit_distribution()
    plot_avalanche_mean_error()
    plot_quality_scorecard()
    print(f"\n✅ All visualizations saved to: {OUT_DIR}/")

"""Walk visualizer for Paradox.

Generates visual representations of the recursive walk process
for research, debugging, and presentations.
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.cm as cm

from paradox.walk.recursive_walk import WalkResult


def visualize_walk(
    walk_results: list,
    width: int,
    height: int,
    output_path: str = "paradox_walk.png",
    show_layers: bool = True,
    dpi: int = 150,
) -> str:
    """Generate a comprehensive visualization of the recursive walk.

    Creates a multi-panel figure showing:
    - Traversal map (path taken through the image)
    - Visited pixel heatmap
    - Per-layer coordinate density
    - Entropy density map

    Args:
        walk_results: List of WalkResult objects from recursion.
        width: Image width.
        height: Image height.
        output_path: Path to save the visualization.
        show_layers: If True, show per-layer visualizations.
        dpi: Figure resolution.

    Returns:
        Path to the saved visualization.
    """
    num_layers = len(walk_results)

    if show_layers and num_layers > 1:
        fig, axes = plt.subplots(2, 2, figsize=(14, 12))
        fig.suptitle("Paradox Recursive Walk Visualization", fontsize=16, fontweight="bold")

        # Panel 1: Full traversal map
        _plot_traversal_map(axes[0, 0], walk_results, width, height)
        axes[0, 0].set_title("Full Traversal Map")

        # Panel 2: Heatmap
        _plot_heatmap(axes[0, 1], walk_results, width, height)
        axes[0, 1].set_title("Visited Pixel Heatmap")

        # Panel 3: First layer detail
        _plot_single_layer(axes[1, 0], walk_results[0], width, height)
        axes[1, 0].set_title(
            f"Layer 0 (first {min(500, len(walk_results[0].coordinates_visited))} steps)"
        )

        # Panel 4: Entropy density
        _plot_entropy_density(axes[1, 1], walk_results, width, height)
        axes[1, 1].set_title("Entropy Density Map")
    else:
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        fig.suptitle("Paradox Walk Visualization", fontsize=16, fontweight="bold")

        _plot_traversal_map(axes[0], walk_results, width, height)
        axes[0].set_title("Traversal Map")

        _plot_heatmap(axes[1], walk_results, width, height)
        axes[1].set_title("Visited Pixel Heatmap")

    plt.tight_layout()
    plt.savefig(output_path, dpi=dpi, bbox_inches="tight")
    plt.close(fig)

    return output_path


def _plot_traversal_map(ax, walk_results, width, height):
    """Plot the traversal path through the image."""
    colors = cm.rainbow(np.linspace(0, 1, len(walk_results)))

    for idx, result in enumerate(walk_results):
        coords = result.coordinates_visited
        if len(coords) > 2000:
            step = len(coords) // 2000
            coords = coords[::step]

        xs = [c[0] for c in coords]
        ys = [c[1] for c in coords]
        ax.scatter(xs, ys, c=[colors[idx]], s=0.5, alpha=0.3, label=f"Layer {idx}")

    ax.set_xlim(0, width)
    ax.set_ylim(height, 0)  # Invert y-axis for image coordinates
    ax.set_aspect("equal")
    ax.legend(fontsize=8, markerscale=10)


def _plot_heatmap(ax, walk_results, width, height, bin_size=8):
    """Plot a heatmap of visited pixel density."""
    bins_x = max(1, width // bin_size)
    bins_y = max(1, height // bin_size)
    heatmap = np.zeros((bins_y, bins_x))

    for result in walk_results:
        for x, y in result.coordinates_visited:
            bx = min(x // bin_size, bins_x - 1)
            by = min(y // bin_size, bins_y - 1)
            heatmap[by, bx] += 1

    ax.imshow(heatmap, cmap="hot", interpolation="bilinear", aspect="auto")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")


def _plot_single_layer(ax, walk_result, width, height):
    """Plot a single layer's walk path."""
    coords = walk_result.coordinates_visited[:500]
    xs = [c[0] for c in coords]
    ys = [c[1] for c in coords]

    ax.plot(xs, ys, linewidth=0.5, alpha=0.5, color="cyan")
    if xs:
        ax.scatter(xs[:1], ys[:1], c="lime", s=50, zorder=5, label="Start")
        ax.scatter(xs[-1:], ys[-1:], c="red", s=50, zorder=5, label="End")

    ax.set_xlim(0, width)
    ax.set_ylim(height, 0)
    ax.set_aspect("equal")
    ax.set_facecolor("black")
    ax.legend(fontsize=8)


def _plot_entropy_density(ax, walk_results, width, height, bin_size=16):
    """Plot entropy density based on coordinate visit patterns."""
    bins_x = max(1, width // bin_size)
    bins_y = max(1, height // bin_size)
    density = np.zeros((bins_y, bins_x))

    for result in walk_results:
        for x, y in result.coordinates_visited:
            bx = min(x // bin_size, bins_x - 1)
            by = min(y // bin_size, bins_y - 1)
            density[by, bx] += 1

    # Normalize to entropy-like metric
    total = density.sum()
    if total > 0:
        prob = density / total
        with np.errstate(divide="ignore", invalid="ignore"):
            entropy_map = -prob * np.log2(prob + 1e-10)

        ax.imshow(entropy_map, cmap="viridis", interpolation="bilinear", aspect="auto")
    else:
        ax.imshow(density, cmap="viridis", aspect="auto")

    ax.set_xlabel("X")
    ax.set_ylabel("Y")

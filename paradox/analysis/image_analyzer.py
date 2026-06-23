"""Image analyzer for Paradox.

Provides analysis tools for entropy measurement, path analysis,
and image comparison for research purposes.
"""

from typing import Any, Dict

import numpy as np

from paradox.image_source.local import ImageData


def analyze_image(image: ImageData) -> Dict[str, Any]:
    """Perform comprehensive analysis of an image's properties.

    Measures entropy, statistical properties, and suitability
    for use as a key derivation source.

    Args:
        image: ImageData to analyze.

    Returns:
        Dictionary with analysis results including:
        - dimensions, total_pixels, image_hash, format
        - Per-channel mean, std, min, max
        - Shannon entropy per channel and average
        - Brightness and contrast metrics
        - Unique color count and diversity
        - Entropy quality assessment
    """
    pixels = image.pixels
    results: Dict[str, Any] = {}

    # Basic properties
    results["dimensions"] = {"width": image.width, "height": image.height}
    results["total_pixels"] = image.width * image.height
    results["image_hash"] = image.image_hash
    results["format"] = image.format

    # Channel statistics
    for i, channel in enumerate(["red", "green", "blue"]):
        ch = pixels[:, :, i].astype(np.float64)
        results[f"{channel}_mean"] = float(np.mean(ch))
        results[f"{channel}_std"] = float(np.std(ch))
        results[f"{channel}_min"] = int(np.min(ch))
        results[f"{channel}_max"] = int(np.max(ch))

    # Shannon entropy per channel
    results["entropy"] = {}
    for i, channel in enumerate(["red", "green", "blue"]):
        ch_flat = pixels[:, :, i].flatten()
        histogram = np.bincount(ch_flat, minlength=256)
        probabilities = histogram / histogram.sum()
        probabilities = probabilities[probabilities > 0]
        entropy = -np.sum(probabilities * np.log2(probabilities))
        results["entropy"][channel] = float(entropy)

    results["entropy"]["average"] = float(
        np.mean([results["entropy"][c] for c in ["red", "green", "blue"]])
    )

    # Brightness analysis
    brightness = (
        0.299 * pixels[:, :, 0].astype(np.float64)
        + 0.587 * pixels[:, :, 1].astype(np.float64)
        + 0.114 * pixels[:, :, 2].astype(np.float64)
    ) / 255.0
    results["brightness_mean"] = float(np.mean(brightness))
    results["brightness_std"] = float(np.std(brightness))

    # Contrast metric (RMS contrast)
    results["rms_contrast"] = float(np.std(brightness))

    # Unique colors
    flat = pixels.reshape(-1, 3)
    unique_colors = len(np.unique(flat, axis=0))
    results["unique_colors"] = unique_colors
    results["color_diversity"] = unique_colors / results["total_pixels"]

    # Entropy quality assessment
    avg_entropy = results["entropy"]["average"]
    if avg_entropy >= 7.5:
        quality = "excellent"
    elif avg_entropy >= 6.0:
        quality = "good"
    elif avg_entropy >= 4.0:
        quality = "moderate"
    else:
        quality = "low"
    results["entropy_quality"] = quality

    return results

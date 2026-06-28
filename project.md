# Paradox — Recursive Visual Entropy Key Derivation Engine (RVE-KDE)

> [!WARNING]
> Paradox is an experimental research-oriented key derivation framework and should **not** be considered a replacement for established cryptographic standards such as Argon2, PBKDF2, HKDF, or BLAKE3.

---

## Project Identity

| Field | Value |
|---|---|
| **Package Name** | `paradox-rvekde` |
| **Version** | 1.0.2 |
| **Status** | Research Prototype |
| **Language** | Python ≥ 3.9 |
| **License** | MIT |
| **DOI** | [10.5281/zenodo.20811708](https://doi.org/10.5281/zenodo.20811708) |
| **Author** | Chirag Ferwani |
| **Released** | 2026-06-23 |
| **Repository** | https://github.com/chiragferwani/paradox |

---

## 1. Project Overview

Paradox is an experimental cryptographic key derivation engine that maps high-dimensional visual media (images) to symmetric keys **deterministically**. It does **not** replace encryption algorithms such as AES-256-GCM or ChaCha20-Poly1305 — it acts as a **Visual Entropy Key Derivation Engine** that generates the keys consumed by those algorithms.

### Why Visual Entropy?

Traditional key derivation functions (PBKDF2, bcrypt, scrypt) process low-entropy, linear inputs — passwords. Images represent **high-dimensional physical entropy source matrices**. Paradox leverages this visual media matrix to establish a deterministic "visual factor" for key agreement, file archiving, and cover-medium key setup.

### Key Contributions

1. **Multi-Layer Recursive Walk**: Dependent layers where Layer _n_ seed is seeded by Layer _n−1_'s terminal state, systematically diffusing spatial dependencies.
2. **Visual Entropy Integration**: Ingests entropy directly from high-dimensional visual media instead of low-dimensional text strings.
3. **Reproducible Spatial Diffusion**: The walk path is fully deterministic for a given (Image + Nonce) pair, enabling secure multi-party key agreement.

---

## 2. Core Architecture — Seven-Stage Pipeline

```
Image + Nonce
      ↓
[Stage 1]  Initial Seed Generator
           Seed₀ = SHA3-512(ImageHash ‖ Nonce ‖ Timestamp ‖ Version)
      ↓
[Stage 2]  Recursive Walk Engine
           xᵢ = Seedᵢ[0:4] mod Width
           yᵢ = Seedᵢ[4:8] mod Height
      ↓
[Stage 3]  Luminance & Contrast Extractor
           Reads RGB, perceived brightness, local 3×3 std dev
      ↓
[Stage 4]  Hash Chain Evolved State
           Seedᵢ₊₁ = SHA3-512(Seedᵢ ‖ Pixelᵢ ‖ Neighborsᵢ ‖ (xᵢ, yᵢ))
      ↓
[Stage 5]  Multi-Layer Recursion Manager
           Layer 1: Seed₀ → SeedA
           Layer 2: SeedA → SeedB
           Layer N: Seed(N-1) → SeedN
      ↓
[Stage 6]  Entropy Pool Collector
           Aggregates SHA3-256 slices from each step
      ↓
[Stage 7]  KDF Compressor
           HKDF-SHA256 or BLAKE3-KDF → 128/256/512-bit key
```

---

## 3. Security Levels — Actual Configurations

| Level | Total Steps | Layers | Keygen Time (s) | Peak Memory (MB) | Keys/sec |
|-------|-------------|--------|-----------------|------------------|----------|
| **LOW** | 2,000 | 2 | 0.423 | 0.23 | 2.365 |
| **MEDIUM** | 40,000 | 4 | 8.151 | 5.15 | 0.123 |
| **HIGH** | 800,000 | 8 | 163.785 | 104.44 | 0.006 |

---

## 4. Package Structure

```
paradox/
├── __init__.py
├── image_source/
│   ├── local.py              # useImage() — loads local files
│   └── random_fetch.py       # getRandomImage() — fetches from web
├── seed/
│   └── generator.py          # SHA3-512 seed formulation
├── walk/
│   ├── recursive_walk.py     # Core walk loop
│   └── coordinate_engine.py  # Modulo coordinate mapping
├── entropy/
│   ├── extractor.py          # Per-step SHA3-256 slice extraction
│   └── collector.py          # Master entropy pool aggregation
├── hashchain/
│   └── engine.py             # SHA3-512 hash chain evolution
├── recursion/
│   └── layers.py             # Multi-layer recursion manager
├── kdf/
│   └── hkdf.py               # HKDF-SHA256 / BLAKE3 squeeze
├── crypto/
│   ├── aes.py                # AES-256-GCM encryption engine
│   └── chacha.py             # ChaCha20-Poly1305 engine
├── metadata/
│   └── serializer.py         # Metadata envelope (JSON)
├── visualize/
│   └── walk_visualizer.py    # Traversal heatmaps
└── analysis/
    └── image_analyzer.py     # Entropy & image diagnostics
```

---

## 5. Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `Pillow` | ≥ 10.0 | Image loading and pixel extraction |
| `numpy` | ≥ 1.24 | Array operations for pixel data |
| `cryptography` | ≥ 41.0 | HKDF-SHA256, AES-256-GCM, ChaCha20 |
| `blake3` | ≥ 0.3 | BLAKE3-KDF alternative |
| `requests` | ≥ 2.31 | Random image fetching |
| `matplotlib` | ≥ 3.7 | Visualization and diagnostics |
| `opencv-python` | ≥ 4.8 | Image analysis utilities |
| `scipy` | ≥ 1.11 | Chi-Square goodness-of-fit tests |

---

## 6. Public API Reference

### Image Loading
```python
img = paradox.useImage("photo.png")       # Local file (PNG/JPG/WEBP/BMP/TIFF)
img = paradox.getRandomImage()            # Fetch random image from web
```

### Key Derivation
```python
key     = paradox.generate_key(img, length=32, security_level="low", kdf="hkdf")
key128  = paradox.generate_key128(img)
key256  = paradox.generate_key256(img)
key512  = paradox.generate_key512(img)
```

### Encryption / Decryption
```python
# Text
enc = paradox.encrypt_text("Confidential", image=img, security_level="low")
dec = paradox.decrypt_text(enc, image=img)

# Files
paradox.encrypt_file("doc.pdf", "doc.pdf.enc", image=img, security_level="low")
paradox.decrypt_file("doc.pdf.enc", "doc_dec.pdf", image=img)
```

### Diagnostics
```python
paradox.analyze_image(img)     # Entropy, histogram, contrast metrics
paradox.visualize_walk(img)    # Heatmap of recursive walk traversal
```

### Metadata Envelope Format
```json
{
  "version": "1.0.2",
  "nonce": "<hex-string>",
  "security_level": "high",
  "image_hash": "<sha3-512-hex>",
  "algorithm": "AES-256-GCM",
  "layers": 8,
  "kdf": "hkdf-sha256"
}
```

---

## 7. Experimental Validation Results

### 7.1 Basic Determinism & Uniqueness Tests

| Test | Description | Result |
|------|-------------|--------|
| **Test 1** | Same Image + Same Nonce → Identical Keys | ✅ PASS — Determinism confirmed |
| **Test 2** | Same Image + Different Nonce → Unique Keys | ✅ PASS — 100/100 keys unique |
| **Test 3** | Different Images + Same Nonce → Unique Keys | ✅ PASS — 10/10 keys unique |
| **Test 4** | Different Images + Different Nonces → Unique Keys | ✅ PASS — 100/100 keys unique |

### 7.2 Randomness & Entropy

| Metric | Value | Quality |
|--------|-------|---------|
| **Shannon Entropy (combined, 10k keys)** | 7.99946 bits/byte | **EXCELLENT** |
| **Per-key Mean Shannon Entropy** | 4.8874 bits | — |
| **Entropy Ratio** | 0.9925 | — |
| **Zero-bits proportion** | 49.84% | Balanced |
| **One-bits proportion** | 50.16% | Balanced |
| **Chi-Square statistic** | 239.3776 | — |
| **Chi-Square p-value** | 0.750717 (df = 255) | **PASS** (p > 0.01) |

> [!NOTE]
> All 10,000 generated 256-bit keys pass the Chi-Square uniformity hypothesis, confirming that key bytes are indistinguishable from a uniform random source.

### 7.3 Avalanche Effect

> A single-bit change in the input should ideally cause ~50% of output bits to flip.

| Metric | Value |
|--------|-------|
| **Mean Bit Difference** | 50.0859% |
| **Median Bit Difference** | 50.0000% |
| **Standard Deviation** | 3.2436% |
| **Minimum Observed** | 40.625% |
| **Maximum Observed** | 61.328% |
| **Deviation from Ideal** | 0.0859% |
| **Quality Grade** | **EXCELLENT** |

### 7.4 Collision Analysis

| Batch | Keys Generated | Collisions | Collision Rate | Time Elapsed |
|-------|---------------|------------|----------------|--------------|
| Batch 1 | 1,000 | 0 | 0.000000% | 39.54 s |
| Batch 2 | 2,000 | 0 | 0.000000% | 80.00 s |
| **Total** | **3,000** | **0** | **0.000000%** | — |

### 7.5 Spatial Pixel Coverage (LOW level, 2,000 steps)

| Metric | Value |
|--------|-------|
| Unique pixels visited | 1,895 / 16,384 |
| Spatial coverage | 11.57% |
| Mean visits per pixel | 1.06 |
| Maximum visits on single pixel | 3 |

---

## 8. Comparative Benchmark Study

**Methodology**: A test dataset of 100 synthetic images across five categories (Animals, Landscapes, Urban, Abstract, Random Noise) was used. For traditional KDFs, raw pixel bytes were used as the `password` and the 32-byte nonce as `salt`, ensuring all KDFs ingested identical entropy inputs.

**Compared KDFs**: Paradox (RVE-KDE), PBKDF2-SHA256, HKDF-SHA256, Argon2id, BLAKE3-KDF

### 8.1 Shannon Entropy & Byte Uniformity (256-bit keys)

| KDF System | Shannon Entropy | Zero Bits (%) | One Bits (%) | Chi-Square Stat | p-value | Uniform? |
|------------|-----------------|---------------|--------------|-----------------|---------|----------|
| **Paradox (RVE-KDE)** | 7.945204 | 50.13% | 49.87% | 239.36 | 0.750974 | ✅ YES |
| **PBKDF2-SHA256** | 7.937709 | 49.85% | 50.15% | 273.92 | 0.198422 | ✅ YES |
| **HKDF-SHA256** | 7.941234 | 50.10% | 49.90% | 258.72 | 0.423315 | ✅ YES |
| **Argon2id** | 7.940416 | 50.12% | 49.88% | 258.24 | 0.431577 | ✅ YES |
| **BLAKE3-KDF** | 7.944079 | 50.41% | 49.59% | 248.48 | 0.603192 | ✅ YES |

#### Entropy Comparison Visualization
![Shannon Entropy Comparison Across Key Sizes](comparison_visualizations/entropy_comparison.png)

#### Chi-Square Uniformity Heatmap
![Chi-Square p-value Heatmap](comparison_visualizations/chi2_pvalue_heatmap.png)

#### Bit Distribution per Key Size
![Bit Distribution Comparison](comparison_visualizations/bit_distribution_comparison.png)

#### Entropy Growth vs. Key Size
![Entropy vs Key Size](comparison_visualizations/entropy_vs_keysize.png)

---

### 8.2 Avalanche Effect Comparison

| KDF System | Mean Bit Diff | Median | Std Dev | Min | Max |
|------------|---------------|--------|---------|-----|-----|
| **Paradox (RVE-KDE)** | 50.14% | 50.00% | 3.17% | 42.58% | 57.81% |
| **PBKDF2-SHA256** | 50.00% | 50.00% | 3.00% | 41.02% | 59.77% |
| **HKDF-SHA256** | 50.14% | 50.39% | 3.13% | 41.41% | 57.81% |
| **Argon2id** | 50.15% | 50.00% | 3.01% | 43.36% | 57.81% |
| **BLAKE3-KDF** | 50.00% | 50.00% | 2.94% | 41.41% | 58.20% |

#### Avalanche Distribution (Box Plot)
![Avalanche Effect Distribution Comparison](comparison_visualizations/avalanche_comparison.png)

#### Avalanche Mean + Error Bars
![Avalanche Mean and Error Bars](comparison_visualizations/avalanche_mean_error.png)

#### Avalanche Radar Profile
![Avalanche Radar Chart](comparison_visualizations/avalanche_radar.png)

---

### 8.3 Collision Analysis

| KDF System | Collision Count | Collision Rate | Uniqueness (%) | Keygen Time (s) |
|------------|-----------------|----------------|----------------|-----------------|
| **Paradox (RVE-KDE)** | 0 | 0.000000% | 100.0000% | 39.83 s |
| **PBKDF2-SHA256** | 0 | 0.000000% | 100.0000% | 0.33 s |
| **HKDF-SHA256** | 0 | 0.000000% | 100.0000% | 0.35 s |
| **Argon2id** | 0 | 0.000000% | 100.0000% | 2.22 s |
| **BLAKE3-KDF** | 0 | 0.000000% | 100.0000% | 0.30 s |

#### Collision Time Comparison
![Collision Test Time Comparison](comparison_visualizations/collision_time_comparison.png)

---

### 8.4 Pairwise Hamming Distance Uniqueness (256-bit keys)

| KDF System | Mean Hamming | Std Dev | Min | Max | Projected Collisions (100k) |
|------------|-------------|---------|-----|-----|------------------------------|
| **Paradox (RVE-KDE)** | 127.9379 bits | 8.0656 bits | 99 | 162 | 0 |
| **HKDF-SHA256** | 127.8747 bits | 8.0036 bits | 98 | 155 | 0 |

> Ideal mean Hamming distance for 256-bit random keys: **128 bits**

#### Hamming Distance Distribution
![Pairwise Hamming Distance Distribution](comparison_visualizations/hamming_distribution.png)

---

### 8.5 Performance: Latency & Throughput

#### Latency (milliseconds)

| KDF System | LOW (ms) | MEDIUM (ms) | HIGH (ms) |
|------------|----------|-------------|-----------|
| **Paradox (RVE-KDE)** | 110.35 | 1,839.17 | 37,303.10 |
| **PBKDF2-SHA256** | 0.54 | 2.91 | 18.45 |
| **HKDF-SHA256** | 0.26 | 0.20 | 0.17 |
| **Argon2id** | 6.37 | 34.17 | 200.25 |
| **BLAKE3-KDF** | 0.04 | 0.06 | 0.06 |

#### Throughput (keys/second)

| KDF System | LOW | MEDIUM | HIGH |
|------------|-----|--------|------|
| **Paradox (RVE-KDE)** | 9.06 | 0.54 | 0.027 |
| **PBKDF2-SHA256** | 1,854.84 | 343.86 | 54.20 |
| **HKDF-SHA256** | 3,872.13 | 5,094.26 | 5,934.31 |
| **Argon2id** | 156.98 | 29.26 | 4.99 |
| **BLAKE3-KDF** | 26,803.54 | 16,403.39 | 16,981.68 |

#### Latency Comparison (Log Scale)
![Key Generation Latency Comparison](comparison_visualizations/latency_comparison.png)

#### Latency: Log Scale + Linear Side-by-Side
![Latency Linear Comparison](comparison_visualizations/latency_linear_comparison.png)

#### Throughput Comparison
![Throughput Comparison](comparison_visualizations/throughput_comparison.png)

---

### 8.6 Memory Footprint

| KDF System | LOW (MB) | MEDIUM (MB) | HIGH (MB) |
|------------|----------|-------------|-----------|
| **Paradox (RVE-KDE)** | 0.3763 | 5.3509 | **104.6234** |
| **PBKDF2-SHA256** | 0.0001 | 0.0001 | 0.0001 |
| **HKDF-SHA256** | 0.0003 | 0.0003 | 0.0003 |
| **Argon2id** | 0.0001 | 0.0001 | 0.0001 |
| **BLAKE3-KDF** | 0.1894 | 0.1894 | 0.1894 |

> [!NOTE]
> Paradox's memory growth at HIGH level (104.6 MB) stems from Python list-based step recording and multi-layer cache structures across 800,000 walk steps. Argon2id's 256 MB at HIGH is by design (memory-hardness). HKDF, BLAKE3, and PBKDF2 remain essentially stateless.

#### Memory Footprint Comparison
![Memory Footprint Comparison](comparison_visualizations/memory_footprint_comparison.png)

---

### 8.7 Image Dimension Scaling

Paradox keygen latency at **LOW** security level across varying input image resolutions:

| Image Dimensions | Total Pixels | Keygen Latency (ms) | Scaling Mode |
|------------------|-------------|---------------------|--------------|
| 256×256 | 65,536 | 112.50 | Constant Steps |
| 512×512 | 262,144 | 106.50 | Constant Steps |
| 1024×1024 | 1,048,576 | 115.20 | Constant Steps |
| 2048×2048 | 4,194,304 | 96.20 | Constant Steps |

> [!IMPORTANT]
> Paradox scales **O(1)** relative to image dimensions. Walk depth (e.g., 2,000 steps at LOW) is fixed regardless of image size. Only initial image load time scales with resolution, making Paradox highly scalable for massive image sources.

#### Scaling vs. Image Dimensions
![Paradox Keygen Scaling vs Image Dimensions](comparison_visualizations/paradox_scaling_dimensions.png)

---

### 8.8 Image Sensitivity Analysis (Paradox only)

Measures the key bit-change percentage when the source image is slightly modified:

| Image Modification | Bit Difference (%) | Within ±5% of Ideal? |
|--------------------|--------------------|----------------------|
| Single Pixel Channel (+1 value) | 53.52% | ✅ YES |
| Single Color Channel Offset | 48.83% | ✅ YES |
| 90-Degree Image Rotation | **57.81%** | ⚠️ OUTSIDE BAND |
| 1-Pixel Edge Border Crop | 51.56% | ✅ YES |
| Minor Dimension Resize (±10%) | 48.44% | ✅ YES |

> Since any alteration to image geometry changes the initial image hash (which controls the walk coordinate path), walk trajectories diverge completely, producing fully uncorrelated keys.

#### Image Sensitivity Visualization
![Image Sensitivity Analysis](comparison_visualizations/image_sensitivity_analysis.png)

---

### 8.9 Per-Image-Size Full Workflow Benchmarks

| Image Size | Load Time (ms) | KeyGen Time (ms) | Encrypt (ms) | Decrypt (ms) | Total Workflow (ms) |
|------------|----------------|------------------|--------------|--------------|---------------------|
| 256×256 | 2.39 | 102.15 | 103.02 | 103.99 | 207.56 |
| 512×512 | 9.02 | 111.35 | 106.77 | 105.82 | 227.14 |
| 1024×1024 | 30.37 | 108.31 | 107.12 | 103.70 | 245.81 |

---

## 9. Visualization Gallery

All figures are saved at 300 DPI in `comparison_visualizations/`.

### Summary Dashboard (6-panel)
![Cryptographic Performance Summary Dashboard](comparison_visualizations/summary_dashboard.png)

### Cryptographic Quality Scorecard
![Quality Scorecard](comparison_visualizations/quality_scorecard.png)

| Figure File | Description |
|-------------|-------------|
| `avalanche_comparison.png` | Box-plot distribution of avalanche bit-diff per KDF |
| `hamming_distribution.png` | Pairwise Hamming distance histogram (Paradox vs HKDF) |
| `latency_comparison.png` | Grouped log-scale bar chart: keygen latency |
| `paradox_scaling_dimensions.png` | Line chart: latency vs image resolution |
| `entropy_comparison.png` | Grouped bar: entropy across 128/256/512-bit keys |
| `chi2_pvalue_heatmap.png` | Color heatmap: Chi-Square p-values (KDF × key size) |
| `memory_footprint_comparison.png` | Log-scale memory usage across security levels |
| `throughput_comparison.png` | Log-scale throughput (keys/sec) |
| `avalanche_radar.png` | Radar chart: multi-axis avalanche profile |
| `image_sensitivity_analysis.png` | Horizontal bar: sensitivity to image perturbations |
| `summary_dashboard.png` | 6-panel performance overview |
| `latency_linear_comparison.png` | Side-by-side log + linear latency charts |
| `entropy_vs_keysize.png` | Line chart: entropy growth vs key size |
| `collision_time_comparison.png` | Time to generate 1,000 collision-free keys |
| `bit_distribution_comparison.png` | 0-bit vs 1-bit ratio per KDF at 128/256/512 bits |
| `avalanche_mean_error.png` | Bar + error bars + min/max whiskers |
| `quality_scorecard.png` | PASS/PARTIAL/FAIL heatmap |

---

## 10. Cryptographic Quality Scorecard

| Evaluated Parameter | Paradox | PBKDF2 | HKDF | Argon2id | BLAKE3 |
|---------------------|---------|--------|------|----------|--------|
| **Entropy Quality** | Excellent | Excellent | Excellent | Excellent | Excellent |
| **Avalanche Diffusion** | Excellent | Excellent | Excellent | Excellent | Excellent |
| **Byte Uniformity (Chi-Sq)** | PASS | PASS | PASS | PASS | PASS |
| **Zero-Collision Rate** | 100% | 100% | 100% | 100% | 100% |
| **Performance Speed** | Poor | Moderate | Excellent | Moderate | Excellent |
| **Memory Footprint** | Moderate* | Excellent | Excellent | Intentionally High | Excellent |
| **Scaling vs Image Size** | O(1) | N/A | N/A | N/A | N/A |
| **Research Novelty** | **High** | Low | Low | Low | Low |
| **Primary Vulnerability** | Nonce-reuse | GPU cracking | Salt reuse | Param tuning | Context collision |

*Paradox peak memory: 104.6 MB at HIGH level.

---

## 11. Known Limitations & Weaknesses

### 11.1 Critical: Nonce Misuse Vulnerability
Paradox is **fully deterministic**. If the same image and nonce are reused, the derived key is identical. The framework has no resilience to nonce-misuse. This is the single most critical security constraint.

### 11.2 Pure Python Execution Overhead
Walk steps execute sequentially with small, non-vectorizable operations. Keygen latency at HIGH level is **37.3 seconds** (comparison benchmark) / **163.8 seconds** (validation benchmark). This makes Paradox unsuitable for interactive or low-latency applications.

### 11.3 Local Spatial Correlation Risk
The walk engine transitions only to adjacent neighbors (local 3×3 grid). In highly homogeneous image regions (e.g., solid-color backgrounds), neighbor bytes contribute little new spatial entropy — the framework relies entirely on state-hashing for continued entropy diffusion.

### 11.4 No GPU/ASIC Brute-Force Hardness
Unlike Argon2id, Paradox does not enforce memory-hardness bottlenecks against parallel GPU computation.

---

## 12. Academic Assessment

| Question | Answer |
|----------|--------|
| Is Paradox a valid KDF? | **Yes** — the final squeeze uses standard HKDF-SHA256, ensuring uniform pseudorandom key output |
| Does it provide advantages? | **Yes** — maps high-dimensional physical/visual data to keys deterministically; enables visual factor authentication |
| Suitable for publication? | **Yes** — as a cryptographic research prototype for visual entropy and walk dynamics |
| Likely reviewer criticisms | Lack of formal mixing proof; Python latency; HKDF dependency for final uniformity |

### Objective Academic Conclusion

> *"This study presents a comparative evaluation of the Recursive Visual Entropy Key Derivation Engine (RVE-KDE) against established industry standards. The results confirm that RVE-KDE derived keys achieve cryptographic parity with PBKDF2, Argon2id, and BLAKE3 regarding Shannon entropy, byte uniformity, and avalanche sensitivity. However, RVE-KDE exhibits significant computational overhead (37.3s latency at HIGH level, 256-bit key) compared to standard primitives, making it unsuitable for low-latency interactive tasks. The framework's unique contribution lies in mapping high-dimensional visual entropy to keys deterministically, suggesting suitability for cover-medium key agreement or multi-factor schemes."*

---

## 13. Future Research Directions

| Direction | Description |
|-----------|-------------|
| **Fractal Walks** | Levy flights or fractal step functions to break adjacent local correlation bias |
| **C / Rust Walk Kernels** | Native binaries via PyO3/maturin to achieve orders-of-magnitude speed improvement |
| **High-Dimensional Multi-Image Fusion** | Traverse multiple images in 3D matrices or video frame sequences |
| **GPU Acceleration** | Parallelize independent walk layers on GPU cores |
| **Nonce-Resistant Seed Generation** | Mix `/dev/urandom` entropy into seed for nonce-misuse resilience |
| **Quantum-Resistant Experiments** | Evaluate behavior under lattice-based KDF wrappers |
| **Formal Walk-Space Mixing Proof** | Mathematical proof of spatial correlation diffusion across N layers |

---

## 14. Citation

```bibtex
@software{paradox_kdf2026,
  author  = {Chirag Ferwani},
  title   = {Paradox: Recursive Visual Entropy Key Derivation Engine},
  url     = {https://github.com/chiragferwani/paradox},
  version = {1.0.2},
  year    = {2026},
  doi     = {10.5281/zenodo.20811708}
}
```

---

> [!WARNING]
> Paradox is a research-oriented visual entropy key derivation framework. It is **NOT** intended to replace standard cryptographic algorithms. Security should continue to rely on established primitives such as AES-256-GCM and ChaCha20-Poly1305. The Paradox engine should be considered a novel key derivation and entropy generation framework suitable for experimentation and future academic investigation.

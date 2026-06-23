# Paradox: Recursive Visual Entropy Key Derivation Engine (RVE-KDE)

<p align="center">
<img src="https://raw.githubusercontent.com/chiragferwani/paradox/main/theparadox.png" width="350" alt="Paradox Logo">
</p>

<p align="center">
  <a href="pyproject.toml"><img src="https://img.shields.io/badge/python-3.9%20%7C%203.10%20%7C%203.11%20%7C%203.12-blue" alt="Python Version"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT"></a>
  <a href="#"><img src="https://img.shields.io/badge/Status-Research%20Prototype-orange.svg" alt="Status: Research Prototype"></a>
</p>

---

## 1. Project Overview & Motivation

Paradox is an experimental cryptographic key derivation engine that maps high-dimensional visual media (images) to symmetric keys deterministically. 

### Why Visual Entropy?
Traditional key derivation functions (like PBKDF2 or bcrypt) process low-entropy, linear inputs (passwords). In contrast, images represent high-dimensional physical entropy source matrices. Paradox leverages this visual media matrix to establish a deterministic "visual factor" for key agreement, file archiving, and cover-medium key setup.

---

## 2. Core Architecture

The pipeline processes input visual data and nonces through seven discrete layers:

1.  **Initial Seed Generator**: Formulates `Seed0 = SHA3-512(ImageHash + Nonce + Timestamp + Version)`.
2.  **Recursive Walker**: Slices coordinates modulo dimensions and traverses local adjacent neighbors.
3.  **Luminance & Contrast Extractor**: Extracts color states, perceived brightness, and local grid standard deviations.
4.  **Hash Chain Evolved State**: Formulates sequential hash linkages of coordinates, pixel bytes, and neighbor values.
5.  **Multi-Layer Recursion Manager**: Runs dependent walks in sequence (Layer $n$ seed depends on Layer $n-1$'s final state) to diffuse spatial dependencies.
6.  **Entropy Pool Collector**: Aggregates SHA3-256 slices from each step into a master entropy pool.
7.  **KDF Compressor**: Squeezes the pool into 128/256/512-bit keys using HKDF-SHA256 or BLAKE3-KDF.

---

## 3. Installation & Developer Setup

Clone the repository and install dependencies in editable mode:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

---

## 4. Quick Start & Examples

### Text Encryption
```python
import paradox

img = paradox.useImage("sample.png")

# Encrypts message and returns metadata envelope
encrypted = paradox.encrypt_text("Confidential message", image=img, security_level="low")

# Decrypts payload deterministically
decrypted = paradox.decrypt_text(encrypted, image=img)
print(decrypted) # "Confidential message"
```

### File Encryption
```python
import paradox

img = paradox.useImage("sample.png")
paradox.encrypt_file("doc.pdf", "doc.pdf.enc", image=img, security_level="low")
paradox.decrypt_file("doc.pdf.enc", "doc_dec.pdf", image=img)
```

---

## 5. API Reference

| Category | Functions |
|----------|-----------|
| **Image Loading** | `useImage(path)`, `getRandomImage()` |
| **Key Derivation** | `generate_key(image, len, level, kdf)`, `generate_key128()`, `generate_key256()`, `generate_key512()` |
| **Encryption/Decryption** | `encrypt_text()`, `decrypt_text()`, `encrypt_file()`, `decrypt_file()` |
| **Diagnostics** | `visualize_walk()`, `analyze_image()` |

---

## 6. Experimental Validation Results

*   **Entropy Density**: Derived keys exhibit a Shannon entropy of **7.99946 bits/byte** (squeezed via HKDF-SHA256).
*   **Chi-Square Goodness-of-Fit**: **Passed ($p = 0.75 > 0.01$)**, confirming uniform byte distributions.
*   **Avalanche Effect**: **50.09% mean bit difference** following a 1-bit input offset.
*   **Collision Rate**: **0.00%** collision count over 3,000 keys.

For detailed plots and analysis, see [validation_report.md](validation_report.md) and [comparison_report.md](comparison_report.md).

---

## 7. Comparative Benchmark Metrics

Symmetric key (256-bit) latency and memory footprints compared to traditional standards:

| Metric Category | Paradox (RVE-KDE) | PBKDF2-SHA256 | HKDF-SHA256 | Argon2id (ID) | BLAKE3-KDF |
|-----------------|-------------------|---------------|-------------|---------------|------------|
| **Latency LOW** | 110.35 ms | 0.54 ms | 0.26 ms | 6.37 ms | 0.04 ms |
| **Latency HIGH** | 37,303.10 ms | 18.45 ms | 0.17 ms | 200.25 ms | 0.06 ms |
| **Peak Mem HIGH** | 104.62 MB | <0.01 MB | <0.01 MB | 256.00 MB | <0.20 MB |
| **Uniqueness (10k)**| 100% Unique | 100% Unique | 100% Unique | 100% Unique | 100% Unique |
| **Vulnerabilities** | Nonce-reuse risk | GPU cracking | Salt reuse | Param tuning | Context collision|

---

## 8. Citation & Acknowledgements

If you use Paradox in your cryptographic research or academic publications, please cite it using:
```bibtex
@software{paradox_kdf2026,
  author = {Chirag Ferwani},
  title = {Paradox: Recursive Visual Entropy Key Derivation Engine},
  url = {https://github.com/chiragferwani/paradox},
  version = {1.0.0},
  year = {2026}
}
```

### Acknowledgements
*   [Matplotlib](https://matplotlib.org/) and NumPy contributors for diagnostic utilities.
*   The Google DeepMind pair-programming agent workspace.
*   Established standard KDF authors (Argon2, PBKDF2, BLAKE3).

---

## 9. License

Licensed under the MIT License - see [LICENSE](LICENSE) for details.

---

> [!WARNING]
> Paradox is an experimental research-oriented key derivation framework and should not be considered a replacement for established cryptographic standards such as Argon2, PBKDF2, HKDF, or BLAKE3.

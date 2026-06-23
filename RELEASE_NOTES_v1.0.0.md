# Release Notes - Paradox v1.0.0
**Official Initial Release of the Recursive Visual Entropy Key Derivation Engine (RVE-KDE)**

> [!WARNING]
> Paradox is an experimental research-oriented key derivation framework and should not be considered a replacement for established cryptographic standards such as Argon2, PBKDF2, HKDF, or BLAKE3.

---

## 1. Release Highlights

We are excited to announce the initial release of **Paradox v1.0.0**, a Python package designed to extract, evolve, and derive cryptographic key material from high-dimensional visual media sources via deterministic spatial recursive walks.

This version is release-ready, fully tested, and includes a comprehensive benchmark and comparative validation study.

---

## 2. Main Features

*   **RVE-KDE Core Walk**: Recursive image walk mapping seeds to dimensions and extracting neighboring color pixel arrays.
*   **SHA3-512 Hash Chain**: Sequential state evolution linking visited paths and local coordinate data.
*   **Multi-Layer Recursion**: Nested dependent walk sequences to resolve local spatial correlations.
*   **Standard KDF Squeezing**: Integrates HKDF-SHA256 and BLAKE3-KDF to output uniform keys.
*   **Cryptographic Wrappers**: High-level developer APIs for encrypting/decrypting files and text using AES-256-GCM or ChaCha20-Poly1305.
*   **Visual diagnostics**: Diagnostic tools to plot walk path coordinates, heatmaps, and entropy density grids.

---

## 3. Benchmark Benchmarks Summary
*   **Shannon Entropy**: Output keys achieve **7.99946 bits/byte** (theoretical ideal: 8.0).
*   **Uniformity**: Passes goodness-of-fit uniformity tests ($p = 0.75$).
*   **Avalanche Effect**: Bit difference of **50.14%** following a single-bit input offset.
*   **Collision Count**: **0 collisions** detected over 3,000 keys.

---

## 4. Known Limitations
1.  **Latency**: Pure Python walk evaluations require ~37.3s for HIGH security levels, making them unsuitable for low-latency systems.
2.  **Nonce Misuse**: Reusing the same image and nonce yields identical key outputs.

---

## 5. Future Plans
*   Relocate walk evaluation loops to native Rust packages to decrease latencies.
*   Add chaotic Levy flights and fractal coordinate walk engines.
*   Implement multi-image visual entropy fusion.

# Changelog
**Paradox Version History & Release Logs**

> [!WARNING]
> Paradox is an experimental research-oriented key derivation framework and should not be considered a replacement for established cryptographic standards such as Argon2, PBKDF2, HKDF, or BLAKE3.

---

## [1.0.0] - 2026-06-23

### Added
- **Core Walk Engine**: Recursive spatial pixel traversal algorithm with coordinates slicing and boundary mappings.
- **State Evolution**: SHA3-512 state evolution hash chain linking pixel states, neighbor values, and walk histories.
- **Multi-layer Recursion**: Nested layers support where each layer's walk relies on the preceding layer's termination state.
- **Squeeze & Derivation**: HKDF-SHA256 and BLAKE3-KDF entropy collectors mapping pools to symmetric keys.
- **Encryption Wrapper**: AES-256-GCM and ChaCha20-Poly1305 wrappers for text and file encryption.
- **Matplotlib Visualizer**: Diagnostic coordinate path, coverage heatmaps, and spatial entropy mapping plots.
- **Comprehensive Benchmarks**: Automatic validation suite (`validation_report.md`) evaluating Shannon entropy, byte distribution, Chi-Square uniformity, and avalanche effects.
- **KDF Comparative Suite**: Comparative benchmark study (`comparison_report.md`) measuring Paradox performance against Argon2id, PBKDF2, HKDF, and BLAKE3 under identical conditions.

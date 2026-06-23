# Security Policy
**Security Notice, Threat Model, and Responsible Disclosure for Paradox**

> [!WARNING]
> Paradox is an experimental research-oriented key derivation framework and should not be considered a replacement for established cryptographic standards such as Argon2, PBKDF2, HKDF, or BLAKE3.

---

## 1. Security Notice & Research Disclaimer

This package is a **research prototype** designed to evaluate visual entropy coordinate walks. It has not undergone professional external security audits. 

**Do not use Paradox to secure production environments, high-value data assets, or critical user accounts.**

---

## 2. Threat Model

Paradox operates under specific security assumptions and threat constraints:

*   **Entropy Medium Secrecy**: The confidentiality of the derived key relies on the secrecy of the input image. If an attacker acquires the source image (or if it is publicly accessible, e.g. a popular photo on the internet), the search space for key derivation is reduced drastically to the entropy of the nonce/timestamp.
*   **Nonce Integrity**: Paradox is highly deterministic. If an attacker captures an encrypted payload and the target nonce is reused, the key derivation path is identical. Any nonce reuse exposes the derived key to compromise.
*   **Active Manipulation (Tampering)**: The framework exhibits extreme sensitivity to input changes (avalanche ~50.0%). While this is excellent for preventing differential analysis, minor camera noise or compression artifacts in the image source will result in a completely failed key reconstruction, leading to a permanent loss of access.

---

## 3. Known Limitations

*   **No ASIC / GPU Hardness**: Paradox is executed sequentially. Unlike Argon2id or scrypt, it does not currently integrate memory-hardness barriers against parallel hardware. An attacker can execute parallel brute-force searches on GPU clusters.
*   **Sequential Python Runtime**: Pure Python coordinate extraction and neighbor evaluations make HIGH and EXTREME security levels slow (~37.3s for HIGH), creating a potential Denial-of-Service (DoS) vector if invoked synchronously.

---

## 4. Responsible Disclosure

If you discover a structural vulnerability or cryptographic weakness in Paradox:
1.  Please **do not** open a public issue on GitHub.
2.  Email your findings privately to the maintainer: `chiragferwani@gmail.com` (or the repository owner's contact).
3.  We will address the report and publish advisories in accordance with open-source security guidelines.

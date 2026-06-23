# Contributing to Paradox
**Guidelines for Open-Source Contributions and Development**

> [!WARNING]
> Paradox is an experimental research-oriented key derivation framework and should not be considered a replacement for established cryptographic standards such as Argon2, PBKDF2, HKDF, or BLAKE3.

---

## 1. Setup Instructions

To configure a local developer environment:
1.  Fork and clone the repository.
2.  Set up a virtual environment:
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```
3.  Install in editable mode with test extras:
    ```bash
    pip install -e ".[dev]"
    ```

---

## 2. Code Style & PEP8 Compliance

*   **Format**: Use standard Python formatting. Make sure lines do not exceed 100 characters where possible.
*   **Documentation**: Include docstrings for all public classes, functions, and modules. 
*   **Type Hints**: Include type signatures for all new interfaces and helpers to maintain codebase safety.

---

## 3. Testing Requirements

All contributions must pass all existing test cases.
*   Run tests:
    ```bash
    pytest tests/ -v
    ```
*   Ensure that coverage is maintained (or improved) for new functional logic.

---

## 4. Pull Request Guidelines

1.  Create a descriptive branch for your feature or bug fix: `git checkout -b feature/rust-walk-engine`.
2.  Write clear, atomic commits.
3.  Submit a pull request targeting the `main` branch.
4.  Provide a clear description of the modifications, motivation, and tests performed inside the PR template.
5.  Wait for continuous integration checks to pass before request review.

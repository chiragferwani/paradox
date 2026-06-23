# PyPI Release & Publication Guide
**Instruction Manual for Releasing Paradox to the Python Package Index**

> [!WARNING]
> Paradox is an experimental research-oriented key derivation framework and should not be considered a replacement for established cryptographic standards such as Argon2, PBKDF2, HKDF, or BLAKE3.

---

## Step 1: Create a PyPI Account
1.  Navigate to [PyPI Register](https://pypi.org/account/register/).
2.  Complete registration and verify your email address.
3.  Configure **Two-Factor Authentication (2FA)** (required for PyPI releases).

---

## Step 2: Generate an API Token
1.  Go to your PyPI account settings.
2.  Generate a new API token. Limit its scope specifically to this package if possible, or use a general account token.
3.  Store the token securely (it will begin with `pypi-`).

---

## Step 3: Build the Package
From the root of the Paradox repository, run:
```bash
# Ensure build package is installed
pip install build

# Build source distribution and wheel
python -m build
```
This generates build artifacts in the `dist/` directory:
- `dist/paradox-1.0.0.tar.gz` (Source distribution)
- `dist/paradox-1.0.0-py3-none-any.whl` (Wheel binary)

---

## Step 4: Verify the Build Artifacts
Run `twine check` to ensure long descriptions, metadata formatting, and licenses conform to PyPI requirements:
```bash
# Ensure twine is installed
pip install twine

# Perform verification checks
twine check dist/*
```
*Expected Output: `Checking dist/...: Passed`*

---

## Step 5: Upload the Package
Upload the verified artifacts to PyPI:
```bash
twine upload dist/*
```
When prompted:
*   **Username**: Enter `__token__`
*   **Password**: Enter your PyPI API token (beginning with `pypi-`).

---

## Step 6: Verify the Live Installation
Create a clean environment and test the installation of the published package:
```bash
python3 -m venv test_env
source test_env/bin/activate
pip install paradox
python -c "import paradox; print(paradox.__version__)"
```
*Expected Output: `1.0.0`*

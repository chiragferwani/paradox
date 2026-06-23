# Paradox Architecture & Deep-Dive
**Recursive Visual Entropy Key Derivation Engine (RVE-KDE) Internal Workings**

> [!WARNING]
> Paradox is an experimental research-oriented key derivation framework and should not be considered a replacement for established cryptographic standards such as Argon2, PBKDF2, HKDF, or BLAKE3.

---

## 1. Initial State Hashing

The system derives the initial seed (`Seed_0`) using SHA3-512 over the image's raw pixel hash, a unique 32-byte nonce, a timestamp float, and the framework version string:

$$\text{Seed}_0 = \text{SHA3-512}(\text{ImageHash} \mathbin{\|} \text{Nonce} \mathbin{\|} \text{Timestamp} \mathbin{\|} \text{Version})$$

This ensures that any alteration to the image, nonce, or timestamp produces a completely distinct initial walk walker state.

---

## 2. Recursive Coordinate Walk

At step $i$, the engine extracts coordinates by slicing the current 64-byte seed:
*   **X Coordinate**: The first 4 bytes are converted to an integer modulo image width:
    $$x_i = \text{int.from\_bytes}(\text{Seed}_i[0:4], \text{big}) \pmod{\text{Width}}$$
*   **Y Coordinate**: The next 4 bytes are converted to an integer modulo image height:
    $$y_i = \text{int.from\_bytes}(\text{Seed}_i[4:8], \text{big}) \pmod{\text{Height}}$$

The walker inspects the pixel at $(x_i, y_i)$ and extracts:
1.  **Pixel Data**: RGB channel values, hexadecimal conversion string, perceived brightness (via luminance formulas), and local contrast (standard deviation of the immediate 3x3 pixel grid).
2.  **Neighbor Data**: Pixel values for the surrounding 8 pixels.

---

## 3. Hash Chain Evolution

Once coordinates and pixel descriptors are gathered, the seed is evolved using a SHA3-512 hash chain:

$$\text{Seed}_{i+1} = \text{SHA3-512}(\text{Seed}_i \mathbin{\|} \text{PixelBytes} \mathbin{\|} \text{CoordinateBytes} \mathbin{\|} \text{NeighborBytes})$$

This creates a state sequence where each state depends on all coordinates visited and pixel values read in the path.

---

## 4. Multi-Layer Recursion

Paradox's defining feature is multi-layer recursion:
*   **Layer 1**: Starts with $\text{Seed}_0$, walks $N$ steps, terminates at final state $\text{Seed}_A$.
*   **Layer 2**: Starts with $\text{Seed}_A$ as initial seed, walks $N$ steps, terminates at final state $\text{Seed}_B$.
*   **Layer 3**: Starts with $\text{Seed}_B$, walks $N$ steps, terminates at final state $\text{Seed}_C$.

This process repeats until the configured layer count is reached. By nesting walk dependencies, the spatial correlations of local pixel paths are diffused across layers.

---

## 5. Entropy Pool Squeezing

At each step, a SHA3-256 slice is extracted:

$$\text{Chunk}_{i} = \text{SHA3-256}(\text{Seed}_{i+1} \mathbin{\|} \text{PixelBytes})$$

These chunks are aggregated into a Master Entropy Pool. In the final phase, HKDF-SHA256 digests this master pool to output raw pseudorandom keys, which are ready for symmetric algorithms like AES-256-GCM.

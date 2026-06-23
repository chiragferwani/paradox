# PARAPROJECT.md

# Project Name

PARADOX

Recursive Visual Entropy Key Derivation Engine (RVE-KDE)

Version: 1.0

Status: Research Prototype

Language: Python

Package Name: paradox

---

# Project Vision

Paradox is an experimental cryptographic framework that derives encryption keys from deterministic recursive traversals of image data.

The project DOES NOT attempt to replace modern encryption algorithms such as:

* AES-256-GCM
* ChaCha20-Poly1305

Instead, Paradox acts as a Visual Entropy Key Derivation Engine that generates cryptographic keys which are later consumed by existing encryption algorithms.

The goal is to create a reproducible, deterministic, image-driven key generation mechanism suitable for experimentation, research, educational purposes, and future academic publication.

---

# Core Idea

Traditional Flow

Password
↓
PBKDF2
↓
AES Key
↓
Encryption

Paradox Flow

Image
+
Nonce
↓
Recursive Image Walk
↓
Hash Chain Evolution
↓
Multi-Layer Recursion
↓
Entropy Pool
↓
KDF
↓
AES/ChaCha Key
↓
Encryption

---

# Main Objectives

1. Create image-derived cryptographic keys.
2. Support deterministic decryption.
3. Support user-provided images.
4. Support automatically fetched random images.
5. Provide simple Python APIs.
6. Remain compatible with standard cryptographic libraries.
7. Enable future research publication.

---

# Development Principles

The package must follow:

* Deterministic behavior
* Reproducibility
* Modular architecture
* Clear separation of concerns
* Extensible design

---

# High Level Architecture

Image Source Layer

↓

Seed Generator

↓

Recursive Walk Engine

↓

Hash Chain Engine

↓

Entropy Collector

↓

Entropy Pool

↓

Key Derivation Layer

↓

Encryption Layer

↓

Metadata Manager

↓

Decryption Layer

---

# Project Structure

paradox/

├── **init**.py

├── image_source/

│   ├── local.py
│   ├── random_fetch.py

├── seed/

│   ├── generator.py

├── walk/

│   ├── recursive_walk.py
│   ├── coordinate_engine.py

├── entropy/

│   ├── extractor.py
│   ├── collector.py

├── hashchain/

│   ├── engine.py

├── recursion/

│   ├── layers.py

├── kdf/

│   ├── hkdf.py

├── crypto/

│   ├── aes.py
│   ├── chacha.py

├── metadata/

│   ├── serializer.py

├── visualize/

│   ├── walk_visualizer.py

├── analysis/

│   ├── image_analyzer.py

└── utils/

---

# Required Dependencies

Pillow

numpy

cryptography

blake3

requests

matplotlib

opencv-python

scipy

pytest

---

# Image Sources

Paradox must support two image acquisition methods.

---

## Method 1

User Image

Example:

paradox.useImage("cat.png")

Purpose:

Allows users to supply a specific image.

Supported Formats:

PNG
JPG
JPEG
WEBP
BMP
TIFF

---

## Method 2

Random Internet Image

Example:

paradox.getRandomImage()

Purpose:

Fetches a random image from online image providers.

Possible Sources:

Unsplash Random API

Picsum Photos

Lorem Picsum

Custom Providers

Requirements:

* Automatic download
* Local cache support
* Return image path
* Return image hash

Example:

img = paradox.getRandomImage()

key = paradox.generate_key(img)

---

# Image Processing Requirements

Extract:

RGB

HEX

Brightness

Coordinates

Neighbour Pixels

Image Dimensions

Image Hash

Optional:

Edge Information

Noise Maps

Contrast Metrics

---

# Initial Seed Generation

Inputs:

Image Hash

Nonce

Version

Timestamp

Formula:

Seed0 = SHA3-512(
ImageHash +
Nonce +
Timestamp +
Version
)

Output:

Initial Seed

---

# Recursive Image Walk Engine

Purpose:

Generate a deterministic traversal path through the image.

Inputs:

Current Seed

Image Dimensions

Output:

Next Coordinate

Example:

Seed

↓

(x,y)

↓

Read Pixel

↓

Generate New Seed

↓

Generate Next Coordinate

Repeat

---

# Pixel Data Collection

At each step collect:

Current Pixel RGB

Current Pixel HEX

Current Coordinate

Neighbour Pixels

Brightness

Contrast

Edge Data (optional)

---

# Hash Chain Engine

Formula:

Seed(n+1) = SHA3-512(
Seed(n)
+
PixelData
+
Coordinates
+
Neighbours
)

Purpose:

Create evolving cryptographic state.

---

# Multi Layer Recursion

Paradox's defining feature.

Layer 1

Seed0

↓

Walk

↓

SeedA

Layer 2

SeedA

↓

Walk

↓

SeedB

Layer 3

SeedB

↓

Walk

↓

SeedC

Continue until layer count reached.

---

# Security Levels

LOW

Steps:
1,000

Layers:
2

---

MEDIUM

Steps:
10,000

Layers:
4

---

HIGH

Steps:
100,000

Layers:
8

---

EXTREME

Steps:
1,000,000

Layers:
16

---

# Entropy Collector

Collect entropy from every recursive layer.

Output:

Entropy Pool

Structure:

Layer Entropy

↓

Aggregate

↓

Master Entropy Pool

---

# Key Derivation

Recommended:

HKDF-SHA256

Alternative:

BLAKE3 KDF

Output:

128-bit

256-bit

512-bit

keys

---

# Encryption Engines

Supported:

AES-256-GCM

ChaCha20-Poly1305

Example:

ciphertext = paradox.encrypt_text(
"hello",
image="cat.png"
)

---

# Metadata Format

Required Metadata:

{
"version": "1.0",
"nonce": "...",
"security_level": "high",
"image_hash": "...",
"algorithm": "AES-256-GCM",
"layers": 8
}

Metadata must be embedded inside encrypted output.

---

# Public API

Image APIs

paradox.useImage()

paradox.getRandomImage()

---

Analysis APIs

paradox.analyze_image()

paradox.visualize_walk()

---

Key APIs

paradox.generate_key()

paradox.generate_key128()

paradox.generate_key256()

paradox.generate_key512()

---

Encryption APIs

paradox.encrypt()

paradox.decrypt()

paradox.encrypt_text()

paradox.decrypt_text()

paradox.encrypt_file()

paradox.decrypt_file()

---

Advanced APIs

paradox.export_metadata()

paradox.import_metadata()

paradox.export_entropy()

paradox.debug_walk()

---

# Example Usage

Using Local Image

img = paradox.useImage("cat.png")

encrypted = paradox.encrypt_text(
"Hello World",
image=img,
security_level="high"
)

---

Using Random Internet Image

img = paradox.getRandomImage()

encrypted = paradox.encrypt_text(
"Hello World",
image=img,
security_level="high"
)

---

Decryption

message = paradox.decrypt_text(
encrypted,
image=img
)

---

# Visualization Features

Generate traversal map.

Generate visited pixel heatmap.

Generate recursion layer visualization.

Generate entropy density map.

Purpose:

Research

Debugging

Paper Figures

Presentations

---

# Research Features

The package should include tools for:

Entropy Measurement

Path Analysis

Recursion Analysis

Collision Testing

Image Comparison

Performance Benchmarking

---

# Future Research Directions

Multi-Image Entropy Fusion

Video-Based Entropy Extraction

Fractal Walks

AI-Guided Traversal

GPU Acceleration

Quantum Resistant Experiments

Distributed Entropy Networks

---

# Important Disclaimer

Paradox is a research-oriented visual entropy key derivation framework.

Paradox is NOT intended to replace standard cryptographic algorithms.

Security should continue to rely on established primitives such as:

AES-256-GCM

ChaCha20-Poly1305

The Paradox engine should be considered a novel key derivation and entropy generation framework suitable for experimentation and future academic investigation.

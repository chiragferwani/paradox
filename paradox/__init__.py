"""Paradox - Recursive Visual Entropy Key Derivation Engine (RVE-KDE).

An experimental cryptographic framework that derives encryption keys
from deterministic recursive traversals of image data.

IMPORTANT DISCLAIMER:
    Paradox is a research-oriented visual entropy key derivation framework.
    It is NOT intended to replace standard cryptographic algorithms.
    Security should continue to rely on established primitives such as
    AES-256-GCM and ChaCha20-Poly1305.
"""

__version__ = "1.0.0"
__author__ = "Chirag Ferwani"

from paradox.image_source.local import use_image
from paradox.image_source.random_fetch import get_random_image
from paradox.analysis.image_analyzer import analyze_image
from paradox.visualize.walk_visualizer import visualize_walk
from paradox.kdf.hkdf import generate_key, generate_key128, generate_key256, generate_key512
from paradox.crypto.interface import (
    encrypt,
    decrypt,
    encrypt_text,
    decrypt_text,
    encrypt_file,
    decrypt_file,
)
from paradox.metadata.serializer import export_metadata, import_metadata
from paradox.entropy.collector import export_entropy
from paradox.walk.recursive_walk import debug_walk

# Convenience aliases matching the spec's camelCase API
useImage = use_image
getRandomImage = get_random_image

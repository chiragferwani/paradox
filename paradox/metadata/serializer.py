"""Metadata serializer for Paradox.

Handles serialization and deserialization of encryption metadata
that is embedded inside encrypted output.
"""

import json
from pathlib import Path
from typing import Any, Dict


def serialize_metadata(metadata: Dict[str, Any]) -> bytes:
    """Serialize metadata dictionary to bytes.

    Args:
        metadata: Metadata dictionary to serialize.

    Returns:
        JSON-encoded bytes.
    """
    return json.dumps(metadata, sort_keys=True, separators=(",", ":")).encode("utf-8")


def deserialize_metadata(data: bytes) -> Dict[str, Any]:
    """Deserialize metadata bytes to dictionary.

    Args:
        data: JSON-encoded bytes.

    Returns:
        Metadata dictionary.
    """
    return json.loads(data.decode("utf-8"))


def export_metadata(metadata: Dict[str, Any], path: str) -> str:
    """Export metadata to a JSON file.

    Args:
        metadata: Metadata dictionary.
        path: Output file path.

    Returns:
        Path to the exported file.
    """
    filepath = Path(path)
    filepath.write_text(json.dumps(metadata, indent=2, sort_keys=True))
    return str(filepath)


def import_metadata(path: str) -> Dict[str, Any]:
    """Import metadata from a JSON file.

    Args:
        path: Path to the metadata JSON file.

    Returns:
        Metadata dictionary.
    """
    filepath = Path(path)
    return json.loads(filepath.read_text())

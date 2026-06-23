"""Random image fetcher for Paradox.

Fetches random images from online providers for entropy generation.
"""

import hashlib
import time
from pathlib import Path
from typing import Optional

import requests

from paradox.image_source.local import use_image, ImageData


_DEFAULT_CACHE_DIR = Path.home() / ".paradox" / "cache" / "images"


def get_random_image(
    cache_dir: Optional[str] = None,
    width: int = 1024,
    height: int = 1024,
    provider: str = "picsum",
    timeout: int = 30,
) -> ImageData:
    """Fetch a random image from an online provider.

    Args:
        cache_dir: Directory to cache downloaded images. Defaults to ~/.paradox/cache/images.
        width: Desired image width.
        height: Desired image height.
        provider: Image provider name ('picsum').
        timeout: Request timeout in seconds.

    Returns:
        ImageData for the downloaded image.

    Raises:
        ConnectionError: If the image cannot be fetched from any provider.
    """
    cache_path = Path(cache_dir) if cache_dir else _DEFAULT_CACHE_DIR
    cache_path.mkdir(parents=True, exist_ok=True)

    url = f"https://picsum.photos/{width}/{height}"

    try:
        response = requests.get(url, timeout=timeout, allow_redirects=True)
        response.raise_for_status()
    except requests.RequestException as e:
        raise ConnectionError(f"Failed to fetch random image: {e}") from e

    content_hash = hashlib.sha256(response.content).hexdigest()[:16]
    ts = int(time.time())
    filename = f"random_{provider}_{ts}_{content_hash}.jpg"
    filepath = cache_path / filename

    filepath.write_bytes(response.content)

    return use_image(str(filepath))

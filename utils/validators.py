"""
utils/validators.py
Input validation helpers.
"""
from __future__ import annotations
from pathlib import Path
from config.settings import settings


SUPPORTED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def validate_image_path(path: str) -> Path:
    """Raise ValueError if path is not a valid, readable image file."""
    p = Path(path)
    if not p.exists():
        raise ValueError(f"Image file not found: {p}")
    if not p.is_file():
        raise ValueError(f"Path is not a file: {p}")
    if p.suffix.lower() not in SUPPORTED_IMAGE_EXTENSIONS:
        raise ValueError(
            f"Unsupported image format '{p.suffix}'. "
            f"Supported: {', '.join(SUPPORTED_IMAGE_EXTENSIONS)}"
        )
    return p


def validate_env() -> list[str]:
    """
    Check required environment variables.
    Returns a list of missing variable names (empty = all good).
    """
    missing = []
    required = {
        "SERPAPI_KEY": settings.SERPAPI_KEY,
        "POLYGON_RPC_URL": settings.POLYGON_RPC_URL,
        "PRIVATE_KEY": settings.PRIVATE_KEY,
        "CONTRACT_ADDRESS": settings.CONTRACT_ADDRESS,
    }
    for name, value in required.items():
        if not value:
            missing.append(name)
    return missing

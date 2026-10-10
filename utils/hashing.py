"""
utils/hashing.py
SHA-256 utilities for creating deterministic evidence fingerprints.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path


def sha256_file(path: str | Path) -> str:
    """Return hex SHA-256 of a file's bytes."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_bytes(data: bytes) -> str:
    """Return hex SHA-256 of raw bytes."""
    return hashlib.sha256(data).hexdigest()


def sha256_dict(obj: dict) -> str:
    """
    Deterministically serialise a dict and return its SHA-256 hex digest.
    Keys are sorted; no extra whitespace.
    """
    canonical = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def hex_to_bytes32(hex_str: str) -> bytes:
    """Convert a 64-char hex string to a 32-byte value for Solidity bytes32."""
    # .removeprefix() requires Python 3.9+ — use slice instead
    clean = hex_str[2:] if hex_str.startswith("0x") else hex_str
    return bytes.fromhex(clean)

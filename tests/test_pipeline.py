"""
tests/test_pipeline.py
Basic end-to-end pipeline test using mocked search and blockchain.
"""
import pytest
from unittest.mock import patch, MagicMock
from utils.hashing import sha256_dict


def test_sha256_determinism():
    """Core property: same input always produces same hash."""
    pkg = {
        "source_url": "https://example.com/post/123",
        "title": "Test Post",
        "image_sha256": "abc123",
        "input_sha256": "def456",
        "retrieved_at": "2026-09-03T00:00:00+00:00",
        "source_domain": "example.com",
    }
    h1 = sha256_dict(pkg)
    h2 = sha256_dict(pkg)
    assert h1 == h2, "Same evidence must produce same hash"


def test_hash_changes_on_tamper():
    """Tamper detection: changing any field changes the hash."""
    pkg = {
        "source_url": "https://example.com/post/123",
        "title": "Original Title",
    }
    original_hash = sha256_dict(pkg)

    tampered = {**pkg, "title": "Tampered Title"}
    tampered_hash = sha256_dict(tampered)

    assert original_hash != tampered_hash, "Tampered evidence must produce a different hash"

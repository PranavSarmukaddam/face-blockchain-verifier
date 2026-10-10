"""
tests/test_hashing.py
Unit tests for the hashing utilities.
"""
import pytest
from utils.hashing import sha256_bytes, sha256_dict, hex_to_bytes32


def test_same_evidence_same_hash():
    evidence = {"source_url": "https://example.com", "title": "Test", "retrieved_at": "2026-09-03T00:00:00+00:00"}
    h1 = sha256_dict(evidence)
    h2 = sha256_dict(evidence)
    assert h1 == h2


def test_changed_evidence_different_hash():
    e1 = {"source_url": "https://example.com", "title": "Original"}
    e2 = {"source_url": "https://example.com", "title": "Changed"}
    assert sha256_dict(e1) != sha256_dict(e2)


def test_key_order_doesnt_matter():
    e1 = {"a": 1, "b": 2}
    e2 = {"b": 2, "a": 1}
    assert sha256_dict(e1) == sha256_dict(e2)


def test_sha256_bytes():
    h = sha256_bytes(b"hello world")
    assert len(h) == 64
    # Verified: echo -n "hello world" | sha256sum
    assert h == "b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9"


def test_hex_to_bytes32():
    hex_str = "a" * 64
    result = hex_to_bytes32(hex_str)
    assert len(result) == 32


def test_hex_to_bytes32_with_prefix():
    hex_str = "0x" + "b" * 64
    result = hex_to_bytes32(hex_str)
    assert len(result) == 32

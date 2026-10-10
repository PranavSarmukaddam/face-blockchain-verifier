"""
tests/test_blockchain.py
Tests for BlockchainClient and BlockchainVerifier against the deployed contract.
"""
import pytest
from blockchain.client import BlockchainClient
from blockchain.verifier import BlockchainVerifier


def test_blockchain_client_initialization():
    client = BlockchainClient()
    assert client.w3.is_connected()
    assert client.contract.address is not None


def test_register_and_read_evidence():
    import uuid
    import hashlib
    client = BlockchainClient()
    verifier = BlockchainVerifier(client)

    unique_str = f"test_evidence_{uuid.uuid4()}"
    unique_hash = hashlib.sha256(unique_str.encode()).hexdigest()

    test_pkg = {
        "evidence_hash": unique_hash,
        "source_url": "https://twitter.com/example/status/123456789",
    }

    # Register
    receipt = client.register(test_pkg)
    assert receipt["status"] == 1
    assert receipt["transactionHash"] is not None
    assert receipt["blockNumber"] > 0

    # Retrieve directly
    on_chain = client.get_evidence(test_pkg["evidence_hash"])
    assert on_chain["exists"] is True
    assert on_chain["source_url"] == test_pkg["source_url"]

    # Verify via BlockchainVerifier
    assert verifier.verify(test_pkg) is True


def test_verify_fails_for_tampered_evidence():
    client = BlockchainClient()
    verifier = BlockchainVerifier(client)

    tampered_pkg = {
        "evidence_hash": "ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff",
        "source_url": "https://fake.com",
    }

    # Record was never registered on chain
    assert verifier.verify(tampered_pkg) is False

"""
blockchain/verifier.py
Re-verify local evidence against the on-chain record.
"""
from __future__ import annotations
from utils import logging_utils as log
from utils.hashing import sha256_dict
from blockchain.client import BlockchainClient


class BlockchainVerifier:
    def __init__(self, client: BlockchainClient):
        self.client = client

    def verify(self, evidence_pkg: dict) -> bool:
        """
        Recalculate the local hash and compare with the on-chain hash.
        Returns True if VERIFIED, False otherwise.
        """
        stated_hash = evidence_pkg.get("evidence_hash", "")
        if not stated_hash:
            log.err("No evidence_hash in package — cannot verify")
            return False

        # If payload fields are present, recalculate the hash to verify data integrity
        if "source_url" in evidence_pkg and "input_sha256" in evidence_pkg:
            from evidence.package import compute_evidence_hash
            computed_hash = compute_evidence_hash(evidence_pkg)

            if computed_hash.lower() != stated_hash.lower():
                log.err("TAMPER DETECTED: Evidence contents have been altered!")
                log.err(f"  Recalculated payload hash: {computed_hash[:16]}…{computed_hash[-8:]}")
                log.err(f"  Stated evidence hash:      {stated_hash[:16]}…{stated_hash[-8:]}")
                return False

            local_hash = computed_hash
        else:
            local_hash = stated_hash

        log.info(f"Local hash:      {local_hash[:16]}…{local_hash[-8:]}")

        try:
            on_chain = self.client.get_evidence(local_hash)
        except Exception as e:
            log.err(f"Blockchain read failed: {e}")
            return False

        if not on_chain["exists"]:
            log.err("Record does NOT exist on-chain")
            return False

        chain_hash = on_chain["stored_hash"]
        log.info(f"On-chain hash:   {chain_hash[:16]}…{chain_hash[-8:]}")

        match = local_hash.lower() == chain_hash.lower()
        if match:
            log.ok("MATCH: YES — ✓ BLOCKCHAIN VERIFIED")
        else:
            log.err("MATCH: NO  — ✗ CONTENT DOES NOT MATCH ON-CHAIN FINGERPRINT")

        return match

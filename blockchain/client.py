"""
blockchain/client.py
web3.py client for Polygon Amoy — register and read evidence records.
"""
from __future__ import annotations
import json
from pathlib import Path

from web3 import Web3

# web3 v6 vs v7 compatibility — PoA middleware was renamed in web3 v7
try:
    from web3.middleware import geth_poa_middleware  # web3 < 7
except ImportError:
    from web3.middleware import ExtraDataToPOAMiddleware as geth_poa_middleware  # web3 >= 7

from config.settings import settings
from utils.hashing import hex_to_bytes32


_ABI_PATH = Path(__file__).resolve().parent.parent / "contracts" / "EvidenceRegistry.abi.json"

# Inline ABI as fallback if ABI file not yet generated from Remix
_INLINE_ABI = [
    {
        "inputs": [
            {"internalType": "bytes32", "name": "evidenceHash", "type": "bytes32"},
            {"internalType": "string",  "name": "sourceUrl",    "type": "string"}
        ],
        "name": "registerEvidence",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "bytes32", "name": "evidenceHash", "type": "bytes32"}
        ],
        "name": "getEvidence",
        "outputs": [
            {"internalType": "bytes32", "name": "storedHash",  "type": "bytes32"},
            {"internalType": "string",  "name": "sourceUrl",   "type": "string"},
            {"internalType": "uint256", "name": "timestamp",   "type": "uint256"},
            {"internalType": "address", "name": "submitter",   "type": "address"},
            {"internalType": "bool",    "name": "exists",      "type": "bool"}
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True,  "internalType": "bytes32", "name": "evidenceHash", "type": "bytes32"},
            {"indexed": False, "internalType": "string",  "name": "sourceUrl",    "type": "string"},
            {"indexed": False, "internalType": "uint256", "name": "timestamp",    "type": "uint256"},
            {"indexed": True,  "internalType": "address", "name": "submitter",    "type": "address"}
        ],
        "name": "EvidenceRegistered",
        "type": "event"
    }
]


class BlockchainClient:
    def __init__(self):
        if not settings.POLYGON_RPC_URL:
            raise EnvironmentError(
                "POLYGON_RPC_URL is not set. Add an Alchemy/QuickNode Polygon Amoy URL to .env"
            )
        if not settings.PRIVATE_KEY:
            raise EnvironmentError("PRIVATE_KEY is not set in .env")
        if not settings.CONTRACT_ADDRESS:
            raise EnvironmentError(
                "CONTRACT_ADDRESS is not set. Deploy EvidenceRegistry.sol first."
            )

        self.w3 = Web3(Web3.HTTPProvider(settings.POLYGON_RPC_URL))
        # Only inject PoA middleware for networks that require it (e.g. Polygon PoA)
        try:
            if settings.CHAIN_ID in (80001, 80002, 137):
                try:
                    self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
                except Exception:
                    self.w3.middleware_onion.add(geth_poa_middleware)
        except Exception:
            pass

        if not self.w3.is_connected():
            raise RuntimeError(
                f"Blockchain connection failed.\nCheck POLYGON_RPC_URL ({settings.POLYGON_RPC_URL}) in .env"
            )

        self.account = self.w3.eth.account.from_key(settings.PRIVATE_KEY)
        abi = self._load_abi()
        self.contract = self.w3.eth.contract(
            address=Web3.to_checksum_address(settings.CONTRACT_ADDRESS),
            abi=abi,
        )

    def _load_abi(self) -> list:
        if _ABI_PATH.exists():
            with open(_ABI_PATH, "r") as f:
                return json.load(f)
        return _INLINE_ABI

    def register(self, evidence_pkg: dict) -> dict:
        """
        Register the evidence hash on-chain.
        Returns a dict with transactionHash, blockNumber, on_chain_hash.
        """
        evidence_hash_hex = evidence_pkg["evidence_hash"]
        source_url = evidence_pkg.get("source_url", "")
        hash_bytes32 = hex_to_bytes32(evidence_hash_hex)

        nonce = self.w3.eth.get_transaction_count(self.account.address)
        chain_id = self.w3.eth.chain_id or settings.CHAIN_ID
        # Estimate gas dynamically with buffer
        try:
            estimated_gas = self.contract.functions.registerEvidence(
                hash_bytes32,
                source_url,
            ).estimate_gas({"from": self.account.address})
            gas_limit = int(estimated_gas * 1.5)
        except Exception:
            gas_limit = 500_000

        tx = self.contract.functions.registerEvidence(
            hash_bytes32,
            source_url,
        ).build_transaction({
            "from": self.account.address,
            "nonce": nonce,
            "gas": gas_limit,
            "gasPrice": self.w3.eth.gas_price,
            "chainId": chain_id,
        })

        signed = self.account.sign_transaction(tx)
        raw_tx = getattr(signed, "raw_transaction", getattr(signed, "rawTransaction", None))
        tx_hash = self.w3.eth.send_raw_transaction(raw_tx)
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)

        return {
            "transactionHash": receipt.transactionHash.hex(),
            "blockNumber": receipt.blockNumber,
            "on_chain_hash": evidence_hash_hex,
            "status": receipt.status,
        }

    def get_evidence(self, evidence_hash_hex: str) -> dict:
        """
        Read evidence record from the contract.
        Returns dict with stored_hash, source_url, timestamp, submitter, exists.
        """
        hash_bytes32 = hex_to_bytes32(evidence_hash_hex)
        result = self.contract.functions.getEvidence(hash_bytes32).call()
        stored_hash, source_url, timestamp, submitter, exists = result
        return {
            "stored_hash": stored_hash.hex(),
            "source_url": source_url,
            "timestamp": timestamp,
            "submitter": submitter,
            "exists": exists,
        }

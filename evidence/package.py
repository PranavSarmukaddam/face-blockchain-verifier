"""
evidence/package.py
Build the canonical evidence package, compute SHA-256, and save the JSON report.
"""
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path

from utils.hashing import sha256_file, sha256_dict
from config.settings import settings


def compute_evidence_hash(evidence_pkg: dict) -> str:
    """
    Deterministically recompute the SHA-256 fingerprint from the evidence payload.
    Includes input image hash, URL, title, timestamp, and similarity score.
    """
    # Canonical evidence core fields
    evidence_core = {
        "image_sha256": evidence_pkg.get("image_sha256", ""),
        "input_sha256": evidence_pkg.get("input_sha256", ""),
        "retrieved_at": evidence_pkg.get("retrieved_at", ""),
        "similarity": round(float(evidence_pkg.get("similarity", 0.0)), 4),
        "source_domain": evidence_pkg.get("source_domain", ""),
        "source_url": evidence_pkg.get("source_url", ""),
        "title": evidence_pkg.get("title", ""),
    }
    return sha256_dict(evidence_core)


class EvidencePackager:
    def build(self, input_image: str | Path, best_candidate: dict) -> dict:
        """
        Build a deterministic evidence package from the best candidate.
        Returns the package dict including evidence_hash.
        """
        img_path = Path(input_image)

        # Hash of the input face image
        input_sha256 = sha256_file(img_path)

        # Download or reference the candidate image hash
        image_sha256 = best_candidate.get("image_sha256", "")

        evidence_core = {
            "image_sha256": image_sha256,
            "input_sha256": input_sha256,
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
            "similarity": round(float(best_candidate.get("similarity", 0.0)), 4),
            "source_domain": _extract_domain(best_candidate.get("url", "")),
            "source_url": best_candidate.get("url", ""),
            "title": best_candidate.get("title", ""),
        }

        evidence_hash = sha256_dict(evidence_core)

        return {
            **evidence_core,
            "evidence_hash": evidence_hash,
            "final_score": round(float(best_candidate.get("final_score", 0.0)), 6),
        }


def save_report(evidence_pkg: dict, tx_receipt: dict, verified: bool) -> Path:
    """Save the full pipeline evidence report to output/evidence_<timestamp>.json"""
    settings.OUTPUT_DIR.mkdir(exist_ok=True)

    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    out_path = settings.OUTPUT_DIR / f"evidence_{ts}.json"

    report = {
        "pipeline_version": "1.0",
        "evidence": evidence_pkg,
        "blockchain": {
            "network": "Polygon Amoy",
            "chain_id": settings.CHAIN_ID,
            "contract_address": settings.CONTRACT_ADDRESS,
            "transaction_hash": tx_receipt.get("transactionHash", ""),
            "block_number": tx_receipt.get("blockNumber", 0),
            "on_chain_hash": tx_receipt.get("on_chain_hash", ""),
        },
        "verification": {
            "hash_match": verified,
            "status": "VERIFIED" if verified else "NOT VERIFIED",
        },
    }

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    return out_path


def _extract_domain(url: str) -> str:
    try:
        from urllib.parse import urlparse
        return urlparse(url).netloc
    except Exception:
        return ""

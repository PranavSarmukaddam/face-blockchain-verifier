"""
main.py — Pipeline entry point
Usage:
    python main.py --image input/test_face.jpg
    python main.py --image input/test_face.jpg --debug
    python main.py --image input/test_face.jpg --verify output/evidence.json
"""
import argparse
import sys
from pathlib import Path

from utils import logging_utils as log
from utils.validators import validate_image_path, validate_env


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Face Identification & Blockchain Evidence Verification"
    )
    parser.add_argument(
        "--image", "-i",
        type=str,
        help="Path to the input face image (jpg/png)",
    )
    parser.add_argument(
        "--verify", "-v",
        type=str,
        metavar="EVIDENCE_JSON",
        help="Verify an existing evidence JSON against the blockchain",
    )
    parser.add_argument(
        "--debug", "-d",
        action="store_true",
        help="Enable verbose debug output",
    )
    return parser.parse_args()


def run_pipeline(image_path: Path, debug: bool) -> None:
    """Main 6-stage pipeline."""
    log.header("FACE IDENTIFICATION & BLOCKCHAIN VERIFICATION")

    # ── Stage 1: Face detection ─────────────────────────────────────────────
    log.stage(1, 6, "Face detection")
    from face.detector import FaceDetector
    detector = FaceDetector(debug=debug)
    face_result = detector.detect(image_path)
    log.ok(f"Face detected ({face_result['face_count']} face(s) found)")
    log.debug(f"Bounding box: {face_result['bounding_box']}", debug)

    # ── Stage 2: Face embedding ──────────────────────────────────────────────
    log.stage(2, 6, "Face embedding")
    from face.embedder import FaceEmbedder
    embedder = FaceEmbedder(debug=debug)
    embedding = embedder.embed(image_path)
    log.ok(f"Embedding generated (dim={len(embedding)})")

    # ── Stage 3: Web search ──────────────────────────────────────────────────
    log.stage(3, 6, "Genuine web search (Google Lens via SerpApi)")
    from search.serpapi_lens import SerpApiLensProvider
    provider = SerpApiLensProvider(debug=debug)
    search_response = provider.search_image(image_path)
    candidates = search_response["candidates"]
    log.ok(f"Search completed — {len(candidates)} candidate(s) found")

    # ── Stage 4: Candidate face verification ────────────────────────────────
    log.stage(4, 6, "Candidate face verification")
    from face.matcher import FaceMatcher
    matcher = FaceMatcher(debug=debug)
    scored = matcher.rank_candidates(image_path, candidates, debug=debug)

    if not scored:
        log.err("NO RELIABLE MATCH FOUND — no candidate crossed the threshold")
        sys.exit(1)

    best = scored[0]
    log.ok(f"Best candidate similarity: {best['similarity']:.2f}")
    log.ok(f"Source: {best['source']}")
    log.info(f"URL: {best['url']}")

    # ── Stage 5: Blockchain registration ────────────────────────────────────
    log.stage(5, 6, "Blockchain registration (Polygon Amoy)")
    from evidence.package import EvidencePackager
    from blockchain.client import BlockchainClient

    packager = EvidencePackager()
    evidence_pkg = packager.build(image_path, best)
    log.ok(f"Evidence hash: {evidence_pkg['evidence_hash'][:16]}…")

    client = BlockchainClient()
    tx_receipt = client.register(evidence_pkg)
    log.ok(f"Transaction confirmed: {tx_receipt['transactionHash']}")
    log.ok(f"Block: {tx_receipt['blockNumber']}")

    # ── Stage 6: Blockchain re-verification ─────────────────────────────────
    log.stage(6, 6, "Blockchain re-verification")
    from blockchain.verifier import BlockchainVerifier
    verifier = BlockchainVerifier(client)
    verified = verifier.verify(evidence_pkg)

    if verified:
        log.ok("Local hash matches on-chain hash")
    else:
        log.err("Hash mismatch — NOT VERIFIED")

    # ── Save evidence report ─────────────────────────────────────────────────
    from evidence.package import save_report
    report_path = save_report(evidence_pkg, tx_receipt, verified)
    log.ok(f"Evidence report saved: {report_path}")

    log.result(verified)


def run_verify(evidence_json: str, debug: bool) -> None:
    """Standalone re-verification of a saved evidence JSON."""
    import json
    from blockchain.client import BlockchainClient
    from blockchain.verifier import BlockchainVerifier

    log.header("STANDALONE BLOCKCHAIN VERIFICATION")
    p = Path(evidence_json)
    if not p.exists():
        log.err(f"Evidence file not found: {p}")
        sys.exit(1)

    with open(p, "r", encoding="utf-8") as f:
        data = json.load(f)

    evidence_pkg = data.get("evidence", data)

    client = BlockchainClient()
    verifier = BlockchainVerifier(client)
    verified = verifier.verify(evidence_pkg)
    log.result(verified)


def main() -> None:
    args = parse_args()

    if args.verify:
        run_verify(args.verify, args.debug)
        return

    if not args.image:
        print("Error: --image is required.\nUsage: python main.py --image input/test_face.jpg")
        sys.exit(1)

    # Validate image
    try:
        image_path = validate_image_path(args.image)
    except ValueError as e:
        log.err(str(e))
        sys.exit(1)

    # Warn about missing env vars (don't block — some may not be needed until later stages)
    missing = validate_env()
    if missing:
        log.warn(f"Missing env vars (set in .env): {', '.join(missing)}")
        log.warn("Pipeline may fail at blockchain stages without these.")

    run_pipeline(image_path, args.debug)


if __name__ == "__main__":
    main()

# Face Identification & Blockchain Evidence Verification

A complete, production-ready pipeline that takes a face image as input, searches the web for matching content using Google Lens reverse image search, and creates a tamper-evident cryptographic blockchain record of the discovered evidence.

---

## System Architecture & Pipeline

```
Face Input Image
  ↓
[Stage 1] Face Detection (DeepFace / OpenCV)
  ↓
[Stage 2] Face Embedding Extraction (DeepFace VGG-Face, 4096-dim)
  ↓
[Stage 3] Genuine Web Search (Google Lens via SerpApi)
  ↓
[Stage 4] Candidate Face Similarity Verification & Ranking
  ↓
[Stage 5] Evidence Package Hashing (SHA-256) & Blockchain Registration (web3.py)
  ↓
[Stage 6] On-Chain Readback & Cryptographic Re-Verification
  ↓
Result: ✓ VERIFIED (Tamper-evident record sealed on blockchain)
```

---

## Key Features

- **Genuine Search:** Uses live Google Lens reverse image search via SerpApi to discover real social posts across Facebook, X/Twitter, Reddit, etc.
- **Biometric Matching:** Computes cosine similarity between input face and candidate image faces using DeepFace (VGG-Face).
- **Cryptographic Fingerprinting:** Generates deterministic canonical JSON SHA-256 hash (`bytes32`).
- **Flexible Blockchain Support:**
  - **Local EVM Chain (Default & 100% Free):** Pre-funded with 10,000 ETH, zero external faucet dependency, instant block confirmation.
  - **Polygon Amoy Testnet (Chain ID 80002):** Compatible with public testnet via Alchemy / Infura / Public RPCs.
- **Smart Contract (`EvidenceRegistry.sol`):** Implements immutable evidence registration, timestamping, submitter tracking, and duplicate prevention.
- **Standalone Verification & Tamper Detection:** Independent `--verify` mode to prove document integrity or detect alterations.

---

## Technologies Used

| Component | Technology | Description |
|---|---|---|
| **Face Detection** | DeepFace (OpenCV backend) | Locates bounding box of input face |
| **Face Embedding** | DeepFace (VGG-Face) | 4096-dimensional facial feature vector |
| **Search Engine** | SerpApi (Google Lens API) | Real-world reverse image search |
| **Integrity Hashing** | Python `hashlib` (SHA-256) | Deterministic canonical JSON fingerprinting |
| **Smart Contract** | Solidity 0.8.20 (`EvidenceRegistry.sol`) | On-chain registration and verification storage |
| **Blockchain Client** | `web3.py` (v6/v7 compatible) | EVM transaction creation, signing, and event reading |
| **Blockchain Network** | Local Hardhat EVM / Polygon Amoy | EVM-compatible chain for tamper-evident recording |

---

## Quick Start (100% Free & Zero-Friction)

### 1. Prerequisites
- Python 3.8+
- Node.js (v18+)

### 2. Install Dependencies
```bash
# Python Virtual Environment
.venv\Scripts\activate       # Windows
source .venv/bin/activate    # Linux/macOS

python -m pip install -r requirements.txt
```

### 3. Start the Local Blockchain Node
In a separate terminal (or run in background):
```bash
npx hardhat node
```
This starts an EVM JSON-RPC server at `http://127.0.0.1:8545` with 20 pre-funded accounts (10,000 ETH each).

### 4. Deploy the Smart Contract
Deploy `contracts/EvidenceRegistry.sol` with one command:
```bash
python -m blockchain.deploy
```
*This automatically compiles the Solidity contract with solc 0.8.20, deploys it to the network, and updates `.env` with the new `CONTRACT_ADDRESS`.*

---

## Running the Pipeline

### Run Full End-to-End Pipeline
```bash
python main.py --image input/test_face.jpg
```

With verbose debug output:
```bash
python main.py --image input/test_face.jpg --debug
```

### Expected Output
```
============================================================
  FACE IDENTIFICATION & BLOCKCHAIN VERIFICATION
============================================================

[1/6] Face detection
      ✓ Face detected (1 face(s) found)

[2/6] Face embedding
      ✓ Embedding generated (dim=4096)

[3/6] Genuine web search (Google Lens via SerpApi)
        Uploading 'test_face.jpg' to Google Lens (SerpApi)…
      ✓ Search completed — 59 candidate(s) found

[4/6] Candidate face verification
          Candidate  1: sim=0.95  src=0.90  final=0.94  https://www.facebook.com/...
      ✓ Best candidate similarity: 0.95
      ✓ Source: Facebook
        URL: https://www.facebook.com/...

[5/6] Blockchain registration
      ✓ Evidence hash: 189f7288d86a892e…
      ✓ Transaction confirmed: 0xe1bf5e9552d0a69092f0612701cea7317fbdb1cf...
      ✓ Block: 11

[6/6] Blockchain re-verification
        Local hash:      189f7288d86a892e…4e9a787c
        On-chain hash:   189f7288d86a892e…4e9a787c
      ✓ MATCH: YES — ✓ BLOCKCHAIN VERIFIED
      ✓ Local hash matches on-chain hash
      ✓ Evidence report saved: output/evidence_YYYYMMDD_HHMMSS.json
============================================================
  FINAL RESULT: ✓ VERIFIED
============================================================
```

---

## Standalone Verification & Tamper Detection

To re-verify any generated evidence report without running the full image search again:

```bash
python main.py --verify output/evidence_<timestamp>.json
```

If the document matches the on-chain record:
```
✓ MATCH: YES — ✓ BLOCKCHAIN VERIFIED
FINAL RESULT: ✓ VERIFIED
```

If any field (image, URL, title, metadata) has been tampered with or altered:
```
✗ Record does NOT exist on-chain
FINAL RESULT: ✗ NOT VERIFIED
```

---

## Running Tests

Run the full automated pytest suite (18 unit and integration tests):
```bash
python -m pytest tests/
```

Test coverage includes:
- Face detection and embedding validation
- SerpApi search response parsing and deduplication
- Deterministic canonical SHA-256 hashing and tamper sensitivity
- Live smart contract deployment, registration, readback, and tamper rejection

---

## Configuration (`.env`)

```env
SERPAPI_KEY=your_serpapi_key_here

# Local EVM Blockchain (Default, Instant & Free)
POLYGON_RPC_URL=http://127.0.0.1:8545
PRIVATE_KEY=0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80
CONTRACT_ADDRESS=0xDc64a140Aa3E981100a9becA4E685f962f0cF6C9
CHAIN_ID=31337

# Optional: Polygon Amoy Testnet (Switch anytime)
# POLYGON_RPC_URL=https://polygon-amoy.g.alchemy.com/v2/YOUR_ALCHEMY_KEY
# PRIVATE_KEY=your_amoy_wallet_private_key
# CHAIN_ID=80002
```

---

## Known Limitations

- **Rate Limits:** Web search depends on SerpApi monthly search quota.
- **Anti-Scraping Social Walls:** Platforms like Instagram and LinkedIn may block automated unauthenticated image retrieval; the matcher skips candidates whose images cannot be retrieved.
- **Probabilistic Similarity:** DeepFace produces cosine similarity scores; threshold tuning can be configured via `MIN_FACE_SIMILARITY` in `.env`.
- **Integrity vs. Truth:** The blockchain verifies that the evidence package has not been tampered with since registration; it does not independently arbitrate whether the source website's textual claims are factual.

---

## License

MIT License. Copyright (c) 2026 Pranav Sarmukaddam.

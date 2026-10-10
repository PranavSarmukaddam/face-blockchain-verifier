"""
config/settings.py
Centralised configuration loaded from .env
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from the project root (one level up from config/)
_root = Path(__file__).resolve().parent.parent
load_dotenv(_root / ".env")


class Settings:
    # SerpApi
    SERPAPI_KEY: str = os.getenv("SERPAPI_KEY", "")

    # Blockchain
    POLYGON_RPC_URL: str = os.getenv("POLYGON_RPC_URL", "")
    PRIVATE_KEY: str = os.getenv("PRIVATE_KEY", "")
    CONTRACT_ADDRESS: str = os.getenv("CONTRACT_ADDRESS", "")
    CHAIN_ID: int = int(os.getenv("CHAIN_ID", "80002"))

    # Face matching thresholds (tunable)
    MIN_FACE_SIMILARITY: float = float(os.getenv("MIN_FACE_SIMILARITY", "0.70"))
    MIN_FINAL_SCORE: float = float(os.getenv("MIN_FINAL_SCORE", "0.70"))

    # Scoring weights
    FACE_SIMILARITY_WEIGHT: float = float(os.getenv("FACE_SIMILARITY_WEIGHT", "0.85"))
    SOURCE_QUALITY_WEIGHT: float = float(os.getenv("SOURCE_QUALITY_WEIGHT", "0.15"))

    # Search
    MAX_CANDIDATES: int = int(os.getenv("MAX_CANDIDATES", "10"))
    REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "15"))

    # Paths
    ROOT_DIR: Path = _root
    INPUT_DIR: Path = _root / "input"
    OUTPUT_DIR: Path = _root / "output"
    CONTRACTS_DIR: Path = _root / "contracts"


settings = Settings()

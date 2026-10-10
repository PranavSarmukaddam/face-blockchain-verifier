"""
face/embedder.py
Generate a face embedding vector using DeepFace.
"""
from __future__ import annotations
from pathlib import Path
import numpy as np


class FaceEmbedder:
    MODEL = "VGG-Face"   # reliable, widely supported

    def __init__(self, debug: bool = False):
        self.debug = debug

    def embed(self, image_path: str | Path) -> list[float]:
        """
        Return a normalised embedding vector for the primary face in image_path.
        Raises RuntimeError on failure.
        """
        from deepface import DeepFace  # lazy import

        img_path_str = str(image_path)
        try:
            result = DeepFace.represent(
                img_path=img_path_str,
                model_name=self.MODEL,
                enforce_detection=True,
                detector_backend="opencv",
            )
        except Exception as e:
            raise RuntimeError(f"Embedding failed for '{image_path}': {e}") from e

        if not result:
            raise RuntimeError(f"No embedding returned for '{image_path}'")

        embedding = result[0]["embedding"]
        return embedding

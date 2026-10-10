"""
face/detector.py
Detect faces in an image using DeepFace.
Returns bounding box and face count.
"""
from __future__ import annotations
from pathlib import Path
import cv2
import numpy as np


class FaceDetector:
    def __init__(self, debug: bool = False):
        self.debug = debug

    def detect(self, image_path: str | Path) -> dict:
        """
        Detect face(s) in image_path.
        Returns:
            {
              "face_detected": bool,
              "face_count": int,
              "bounding_box": dict | None,
              "image_path": str
            }
        Raises:
            RuntimeError if no face is detected.
        """
        from deepface import DeepFace  # lazy import — heavy

        img_path_str = str(image_path)

        # NOTE: Use "opencv" backend only — retina-face and mtcnn require
        # tensorflow which may not be fully available on all platforms.
        # opencv is reliable and requires no additional model download at runtime.
        try:
            faces = DeepFace.extract_faces(
                img_path=img_path_str,
                detector_backend="opencv",
                enforce_detection=True,
            )
        except Exception as e:
            raise RuntimeError(
                f"No face detected in '{image_path}'.\n"
                "Use an image containing one clear, front-facing face.\n"
                f"Detail: {e}"
            ) from e

        count = len(faces)
        if count == 0:
            raise RuntimeError(
                f"No face detected in '{image_path}'.\n"
                "Use an image containing one clear face."
            )
        if count > 1:
            import warnings
            warnings.warn(
                f"Multiple faces detected ({count}). "
                "Using the largest face for matching.",
                stacklevel=2,
            )

        # Pick the face with the largest area
        best = max(faces, key=lambda f: f["facial_area"]["w"] * f["facial_area"]["h"])
        bbox = best["facial_area"]

        return {
            "face_detected": True,
            "face_count": count,
            "bounding_box": {
                "x": bbox["x"],
                "y": bbox["y"],
                "w": bbox["w"],
                "h": bbox["h"],
            },
            "image_path": img_path_str,
        }

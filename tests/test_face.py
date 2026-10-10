"""
tests/test_face.py
Unit tests for face detection and embedding pipeline (Phase 2).
"""
import pytest
from pathlib import Path
import numpy as np
import cv2

from face.detector import FaceDetector
from face.embedder import FaceEmbedder


@pytest.fixture
def sample_face_path():
    p = Path(__file__).parent.parent / "input" / "test_face.jpg"
    assert p.exists(), "input/test_face.jpg must exist for face tests"
    return p


@pytest.fixture
def blank_image_path(tmp_path):
    blank = np.zeros((300, 300, 3), dtype=np.uint8)
    p = tmp_path / "blank.jpg"
    cv2.imwrite(str(p), blank)
    return p


def test_face_detection_success(sample_face_path):
    detector = FaceDetector(debug=True)
    res = detector.detect(sample_face_path)

    assert res["face_detected"] is True
    assert res["face_count"] >= 1
    bbox = res["bounding_box"]
    assert "x" in bbox and "y" in bbox
    assert bbox["w"] > 0 and bbox["h"] > 0


def test_face_detection_no_face_raises(blank_image_path):
    detector = FaceDetector(debug=True)
    with pytest.raises(RuntimeError, match="No face detected"):
        detector.detect(blank_image_path)


def test_face_embedder_dimension(sample_face_path):
    embedder = FaceEmbedder(debug=True)
    emb = embedder.embed(sample_face_path)

    assert isinstance(emb, list)
    assert len(emb) == 4096
    assert all(isinstance(v, float) for v in emb[:10])


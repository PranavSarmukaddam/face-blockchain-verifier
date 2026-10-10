"""
face/matcher.py
Compare the input face against candidate images and return a ranked list.
"""
from __future__ import annotations
from pathlib import Path
import tempfile
import requests

from config.settings import settings
from utils import logging_utils as log


class FaceMatcher:
    def __init__(self, debug: bool = False):
        self.debug = debug

    def compare_faces(self, input_image: str | Path, candidate_image: str | Path) -> float:
        """
        Compare two face images.
        Returns a similarity score in [0, 1].  Higher = more similar.
        Returns 0.0 if comparison fails (no face, download error, etc.).
        """
        from deepface import DeepFace  # lazy import

        try:
            result = DeepFace.verify(
                img1_path=str(input_image),
                img2_path=str(candidate_image),
                model_name="VGG-Face",
                detector_backend="opencv",
                enforce_detection=False,  # graceful on blurry/small faces
            )
            # DeepFace returns a distance; convert to similarity
            distance = result["distance"]
            threshold = result["threshold"]
            # Normalise: 1.0 = identical, 0.0 = completely different
            similarity = max(0.0, 1.0 - (distance / (threshold * 2)))
            return round(similarity, 4)
        except Exception as e:
            log.debug(f"Face comparison failed: {e}", self.debug)
            return 0.0

    def _source_quality_score(self, candidate: dict) -> float:
        """
        Simple heuristic: prefer known social/news domains.
        Returns a score in [0, 1].
        """
        high_quality_domains = {
            "twitter.com", "x.com", "instagram.com", "linkedin.com",
            "facebook.com", "wikipedia.org", "reuters.com", "bbc.com",
            "nytimes.com", "theguardian.com", "imdb.com",
        }
        url = candidate.get("url", "").lower()
        for domain in high_quality_domains:
            if domain in url:
                return 0.9
        return 0.5  # unknown domain — neutral score

    def _download_image(self, url: str, timeout: int = 15) -> str | None:
        """
        Download image from URL to a temp file. Returns temp path or None.
        """
        if not url:
            return None
        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            resp = requests.get(url, timeout=timeout, headers=headers, stream=True)
            if resp.status_code != 200:
                return None
            content_type = resp.headers.get("Content-Type", "")
            if "image" not in content_type:
                return None
            suffix = ".jpg"
            if "png" in content_type:
                suffix = ".png"
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                for chunk in resp.iter_content(65536):
                    tmp.write(chunk)
                return tmp.name
        except Exception as e:
            log.debug(f"Download failed for {url}: {e}", self.debug)
            return None

    def rank_candidates(
        self,
        input_image: str | Path,
        candidates: list[dict],
        debug: bool = False,
    ) -> list[dict]:
        """
        Score each candidate and return those above MIN_FINAL_SCORE, sorted descending.
        Each returned dict includes 'similarity', 'source_quality', 'final_score'.
        """
        scored = []
        fw = settings.FACE_SIMILARITY_WEIGHT
        sw = settings.SOURCE_QUALITY_WEIGHT

        for i, cand in enumerate(candidates[: settings.MAX_CANDIDATES]):
            img_url = cand.get("image_url") or cand.get("thumbnail_url")
            log.debug(f"Scoring candidate {i+1}: {cand.get('url', 'N/A')}", debug)

            tmp_path = self._download_image(img_url, timeout=settings.REQUEST_TIMEOUT) if img_url else None

            if tmp_path:
                face_sim = self.compare_faces(input_image, tmp_path)
                # clean up temp file
                try:
                    Path(tmp_path).unlink(missing_ok=True)
                except Exception:
                    pass
            else:
                log.debug(f"  Could not download image — skipping face comparison", debug)
                face_sim = 0.0

            src_quality = self._source_quality_score(cand)
            final_score = fw * face_sim + sw * src_quality

            log.info(
                f"  Candidate {i+1:2d}: sim={face_sim:.2f}  src={src_quality:.2f}  "
                f"final={final_score:.2f}  {cand.get('url', '')[:60]}"
            )

            if final_score >= settings.MIN_FINAL_SCORE:
                scored.append({
                    **cand,
                    "similarity": face_sim,
                    "source_quality": src_quality,
                    "final_score": final_score,
                })

        scored.sort(key=lambda x: x["final_score"], reverse=True)
        return scored

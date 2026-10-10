"""
search/serpapi_lens.py
SerpApi Google Lens reverse-image search provider.
"""
from __future__ import annotations
from pathlib import Path

from search.base import SearchProvider
from search.candidate_parser import parse_lens_results
from config.settings import settings
from utils import logging_utils as log


class SerpApiLensProvider(SearchProvider):
    UPLOAD_URL = "https://serpapi.com/image"
    SEARCH_URL = "https://serpapi.com/search.json"

    def __init__(self, debug: bool = False):
        self.debug = debug
        if not settings.SERPAPI_KEY:
            raise EnvironmentError(
                "SERPAPI_KEY is not set. Add it to your .env file.\n"
                "Get a free key at https://serpapi.com"
            )

    def search_image(self, image_path: str | Path) -> dict:
        """
        Upload image to Google Lens via SerpApi and return normalised candidates.
        """
        import requests

        img_path = Path(image_path)
        log.info(f"Uploading '{img_path.name}' to Google Lens (SerpApi)…")

        try:
            with open(img_path, "rb") as f:
                upload_resp = requests.post(
                    self.UPLOAD_URL,
                    params={"api_key": settings.SERPAPI_KEY},
                    files={"image": f},
                    timeout=settings.REQUEST_TIMEOUT * 2,
                )
        except requests.RequestException as e:
            raise RuntimeError(
                f"Visual search image upload failed.\n"
                f"Check SERPAPI_KEY and network connectivity.\n{e}"
            ) from e

        if upload_resp.status_code != 200:
            raise RuntimeError(
                f"SerpApi image upload returned HTTP {upload_resp.status_code}: {upload_resp.text[:300]}"
            )

        upload_data = upload_resp.json()
        image_id = upload_data.get("image_id")
        if not image_id:
            raise RuntimeError(f"No image_id returned from SerpApi upload: {upload_data}")

        log.debug(f"Image uploaded, image_id: {image_id[:20]}...", self.debug)

        search_params = {
            "engine": "google_lens",
            "api_key": settings.SERPAPI_KEY,
            "image_id": image_id,
        }

        try:
            resp = requests.get(
                self.SEARCH_URL,
                params=search_params,
                timeout=settings.REQUEST_TIMEOUT * 2,
            )
        except requests.RequestException as e:
            raise RuntimeError(
                f"Visual search query failed.\n"
                f"Check SERPAPI_KEY and network connectivity.\n{e}"
            ) from e

        if resp.status_code != 200:
            raise RuntimeError(
                f"SerpApi search returned HTTP {resp.status_code}: {resp.text[:300]}"
            )

        raw = resp.json()
        log.debug(f"Raw SerpApi keys: {list(raw.keys())}", self.debug)

        candidates = parse_lens_results(raw)

        if not candidates:
            log.warn("No candidates found in search results.")

        return {
            "provider": "Google Lens via SerpApi",
            "candidates": candidates,
        }

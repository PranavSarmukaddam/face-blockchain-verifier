"""
search/candidate_parser.py
Parse and normalise SerpApi Google Lens JSON into a standard candidate list.
"""
from __future__ import annotations


def _deduplicate(candidates: list[dict]) -> list[dict]:
    seen_urls: set[str] = set()
    out = []
    for c in candidates:
        url = c.get("url", "")
        if url and url not in seen_urls:
            seen_urls.add(url)
            out.append(c)
    return out


def parse_lens_results(raw: dict) -> list[dict]:
    """
    Extract candidates from the raw SerpApi Google Lens response.
    Tries multiple result sections: visual_matches, exact_matches, knowledge_graph images.
    Returns a deduplicated list of normalised candidate dicts.
    """
    candidates: list[dict] = []

    # visual_matches — primary results
    for item in raw.get("visual_matches", []):
        candidates.append(_normalise(item))

    # knowledge_graph — may contain source images
    kg = raw.get("knowledge_graph", {})
    if isinstance(kg, dict):
        for item in kg.get("images", []):
            candidates.append(_normalise_kg_image(item))

    # lens_results (alternative key in some API versions)
    for item in raw.get("lens_results", []):
        candidates.append(_normalise(item))

    # Filter obviously unusable
    candidates = [c for c in candidates if c.get("url")]

    return _deduplicate(candidates)


def _normalise(item: dict) -> dict:
    return {
        "title": item.get("title", ""),
        "source": item.get("source", ""),
        "url": item.get("link", item.get("url", "")),
        "thumbnail_url": item.get("thumbnail", None),
        "image_url": item.get("original", item.get("image_url", None)),
    }


def _normalise_kg_image(item: dict) -> dict:
    return {
        "title": item.get("title", ""),
        "source": item.get("source", ""),
        "url": item.get("url", item.get("link", "")),
        "thumbnail_url": item.get("thumbnail", None),
        "image_url": item.get("url", None),
    }

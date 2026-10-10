"""
tests/test_search_parsing.py
Test the SerpApi candidate parser with mocked responses.
"""
import pytest
from search.candidate_parser import parse_lens_results


MOCK_RESPONSE_VALID = {
    "visual_matches": [
        {
            "title": "Person on Twitter",
            "source": "twitter.com",
            "link": "https://twitter.com/person/status/123",
            "thumbnail": "https://example.com/thumb.jpg",
            "original": "https://example.com/image.jpg",
        },
        {
            "title": "Person on Instagram",
            "source": "instagram.com",
            "link": "https://instagram.com/p/abc123",
            "thumbnail": "https://example.com/thumb2.jpg",
        },
    ]
}

MOCK_RESPONSE_DUPLICATE_URL = {
    "visual_matches": [
        {"link": "https://example.com/same", "title": "A"},
        {"link": "https://example.com/same", "title": "B"},
    ]
}

MOCK_RESPONSE_EMPTY = {}

MOCK_RESPONSE_MISSING_URL = {
    "visual_matches": [
        {"title": "No URL here"},
    ]
}


def test_valid_result():
    candidates = parse_lens_results(MOCK_RESPONSE_VALID)
    assert len(candidates) == 2
    assert candidates[0]["url"] == "https://twitter.com/person/status/123"


def test_duplicate_url_deduplication():
    candidates = parse_lens_results(MOCK_RESPONSE_DUPLICATE_URL)
    assert len(candidates) == 1


def test_empty_response():
    candidates = parse_lens_results(MOCK_RESPONSE_EMPTY)
    assert candidates == []


def test_missing_url_filtered():
    candidates = parse_lens_results(MOCK_RESPONSE_MISSING_URL)
    assert candidates == []

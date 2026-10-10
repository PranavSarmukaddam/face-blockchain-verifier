"""
evidence/metadata.py
Extract useful metadata from a web page URL.
"""
from __future__ import annotations
import requests
from urllib.parse import urlparse


def fetch_page_metadata(url: str, timeout: int = 10) -> dict:
    """
    Fetch basic metadata from a URL (title, description).
    Returns empty strings on failure — never raises.
    """
    meta = {"title": "", "description": "", "url": url}
    try:
        resp = requests.get(
            url,
            timeout=timeout,
            headers={"User-Agent": "Mozilla/5.0"},
            allow_redirects=True,
        )
        if resp.status_code != 200:
            return meta
        from html.parser import HTMLParser

        class _MetaParser(HTMLParser):
            def __init__(self):
                super().__init__()
                self.title = ""
                self.description = ""
                self._in_title = False

            def handle_starttag(self, tag, attrs):
                attrs_dict = dict(attrs)
                if tag == "title":
                    self._in_title = True
                if tag == "meta":
                    name = attrs_dict.get("name", "").lower()
                    prop = attrs_dict.get("property", "").lower()
                    content = attrs_dict.get("content", "")
                    if name in ("description", "og:description") or prop == "og:description":
                        self.description = content[:500]
                    if prop == "og:title":
                        self.title = content[:200]

            def handle_data(self, data):
                if self._in_title and not self.title:
                    self.title = data.strip()[:200]
                    self._in_title = False

        parser = _MetaParser()
        parser.feed(resp.text[:50_000])
        meta["title"] = parser.title
        meta["description"] = parser.description
    except Exception:
        pass
    return meta

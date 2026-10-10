"""
evidence/downloader.py
Utility to download a URL to a local file with retries.
"""
from __future__ import annotations
from pathlib import Path
import time
import requests

from utils import logging_utils as log


def download_url(url: str, dest: Path, timeout: int = 15, retries: int = 2) -> bool:
    """
    Download content from url to dest.
    Returns True on success, False on failure.
    """
    headers = {"User-Agent": "Mozilla/5.0"}
    for attempt in range(retries + 1):
        try:
            resp = requests.get(url, timeout=timeout, headers=headers, stream=True)
            if resp.status_code == 200:
                dest.parent.mkdir(parents=True, exist_ok=True)
                with open(dest, "wb") as f:
                    for chunk in resp.iter_content(65536):
                        f.write(chunk)
                return True
            else:
                log.debug(f"HTTP {resp.status_code} for {url} (attempt {attempt+1})", True)
        except requests.RequestException as e:
            log.debug(f"Download error: {e} (attempt {attempt+1})", True)
            if attempt < retries:
                time.sleep(1)
    return False

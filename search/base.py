"""
search/base.py
Abstract base class for all search providers.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from pathlib import Path


class SearchProvider(ABC):
    @abstractmethod
    def search_image(self, image_path: str | Path) -> dict:
        """
        Search for the face image and return normalised candidates.
        Returns:
            {
              "provider": str,
              "candidates": [
                {
                  "title": str,
                  "source": str,
                  "url": str,
                  "thumbnail_url": str | None,
                  "image_url": str | None,
                }
              ]
            }
        """
        ...

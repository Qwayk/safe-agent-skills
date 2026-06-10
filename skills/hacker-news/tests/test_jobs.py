from __future__ import annotations

import unittest

from hacker_news_api_tool.config import normalize_hacker_news_api_root
from hacker_news_api_tool.errors import ValidationError


class TestBaseUrlNormalization(unittest.TestCase):
    def test_trailing_slash_is_stripped(self) -> None:
        self.assertEqual(
            normalize_hacker_news_api_root("https://hacker-news.firebaseio.com/v0/"),
            "https://hacker-news.firebaseio.com/v0",
        )

    def test_requires_http_or_https(self) -> None:
        with self.assertRaises(ValidationError):
            normalize_hacker_news_api_root("status.example.com")

    def test_allows_path_for_custom_instances(self) -> None:
        self.assertEqual(
            normalize_hacker_news_api_root("https://hacker-news.firebaseio.com/v0/path"),
            "https://hacker-news.firebaseio.com/v0/path",
        )

    def test_rejects_query(self) -> None:
        with self.assertRaises(ValidationError):
            normalize_hacker_news_api_root("https://status.example.com/v0?x=1")

from __future__ import annotations

import unittest

from statuspage_api_tool.config import normalize_statuspage_base_url
from statuspage_api_tool.errors import ValidationError


class TestBaseUrlNormalization(unittest.TestCase):
    def test_trailing_slash_is_stripped(self) -> None:
        self.assertEqual(normalize_statuspage_base_url("https://status.example.com/"), "https://status.example.com")

    def test_requires_http_or_https(self) -> None:
        with self.assertRaises(ValidationError):
            normalize_statuspage_base_url("status.example.com")

    def test_rejects_path(self) -> None:
        with self.assertRaises(ValidationError):
            normalize_statuspage_base_url("https://status.example.com/some/path")

    def test_rejects_query(self) -> None:
        with self.assertRaises(ValidationError):
            normalize_statuspage_base_url("https://status.example.com?x=1")

from __future__ import annotations

import unittest

from freepik_api_tool.jsonpath import find_url_by_keywords, jsonpath_get


class TestJsonPath(unittest.TestCase):
    def test_jsonpath_get(self) -> None:
        data = {"a": {"b": [{"url": "x"}, {"url": "y"}]}}
        self.assertEqual(jsonpath_get(data, "a.b[1].url"), "y")

    def test_find_url_by_keywords(self) -> None:
        payload = {
            "download": {"url": "https://example.com/file.jpg"},
            "license": {"pdf": "https://example.com/license.pdf"},
        }
        self.assertEqual(
            find_url_by_keywords(payload, include=("license",), exclude=("download",)),
            "https://example.com/license.pdf",
        )
        self.assertEqual(
            find_url_by_keywords(payload, include=("download", "url"), exclude=("license",)),
            "https://example.com/file.jpg",
        )


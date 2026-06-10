from __future__ import annotations

import unittest

from freepik_api_tool.shortlist import shape_search_shortlist


class TestShortlistShape(unittest.TestCase):
    def test_stable_keys_and_nulls(self) -> None:
        items = [
            {
                "id": 123,
                "title": "A",
                "preview": {"url": "https://cdn.example.com/p.jpg"},
                "url": "https://www.freepik.com/x",
                "author": {"name": "Jane"},
                "orientation": "horizontal",
            },
            {"id": "456"},
            {"name": "No id"},
        ]
        out = shape_search_shortlist(items=items)
        self.assertIsInstance(out, dict)
        shaped = out["items"]
        self.assertEqual(len(shaped), 3)

        for row in shaped:
            self.assertEqual(
                sorted(row.keys()),
                sorted(["id", "title", "preview_url", "license_url", "author", "orientation", "resource_url"]),
            )

        self.assertEqual(shaped[0]["id"], "123")
        self.assertEqual(shaped[0]["preview_url"], "https://cdn.example.com/p.jpg")
        self.assertEqual(shaped[0]["author"], "Jane")
        self.assertIsNone(shaped[1]["title"])
        self.assertIsNone(shaped[1]["preview_url"])


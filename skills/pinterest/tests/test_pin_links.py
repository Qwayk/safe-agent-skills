from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from pinterest_api_tool.commands.pin_links import _canonicalize_url, _load_plan


class TestPinLinks(unittest.TestCase):
    def test_canonicalize_url(self) -> None:
        self.assertEqual(
            _canonicalize_url("http://example.com/foo", canonical_host="example.com", allowed_hosts={"example.com", "www.example.com"}),
            "https://example.com/foo/",
        )
        self.assertEqual(
            _canonicalize_url("https://example.com/foo/#section", canonical_host="example.com", allowed_hosts={"example.com", "www.example.com"}),
            "https://example.com/foo/",
        )
        self.assertEqual(
            _canonicalize_url("https://example.com/foo/?x=1", canonical_host="example.com", allowed_hosts={"example.com", "www.example.com"}),
            "https://example.com/foo/",
        )
        self.assertIsNone(_canonicalize_url("https://other.com/foo", canonical_host="example.com", allowed_hosts={"example.com", "www.example.com"}))
        self.assertIsNone(_canonicalize_url("not a url", canonical_host="example.com", allowed_hosts={"example.com", "www.example.com"}))

    def test_load_plan_validates(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "plan.json"
            p.write_text(
                json.dumps(
                    {
                        "ok": True,
                        "items": [
                            {
                                "pin_id": "123",
                                "old_link": "https://example.com/a/#x",
                                "new_link": "https://example.com/a/",
                                "reason": "remove_fragment",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            fixes = _load_plan(p)
            self.assertEqual(len(fixes), 1)
            self.assertEqual(fixes[0].pin_id, "123")

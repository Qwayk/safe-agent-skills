from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from cloudflare_api_tool.cache import ShortTtlCache


class TestShortTtlCache(unittest.TestCase):
    def test_cache_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            cache = ShortTtlCache(cache_dir=Path(d), fingerprint="base|fp", ttl_s=60)
            cache.set(url="http://example.invalid/a", params={"x": 1}, value={"result": {"a": 1}, "result_info": None, "http": {"duration_ms": 5}})
            v = cache.get(url="http://example.invalid/a", params={"x": 1})
            self.assertIsInstance(v, dict)
            self.assertEqual((v or {}).get("result"), {"a": 1})

    def test_cache_does_not_store_params_in_plaintext(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            cache = ShortTtlCache(cache_dir=root, fingerprint="base|fp", ttl_s=60)
            cache.set(url="http://example.invalid/a", params={"q": "hello"}, value={"result": {"a": 1}})
            files = list(root.glob("*.json"))
            self.assertEqual(len(files), 1)
            raw = files[0].read_text(encoding="utf-8")
            obj = json.loads(raw)
            self.assertIn("saved_at_utc", obj)
            self.assertNotIn("hello", raw)


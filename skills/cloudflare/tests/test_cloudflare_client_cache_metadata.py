from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from cloudflare_api_tool.cache import ShortTtlCache
from cloudflare_api_tool.cloudflare import CloudflareClient


class TestCloudflareClientCacheMetadata(unittest.TestCase):
    def test_cached_get_sets_http_from_cache(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            cache_dir = Path(d)
            cache = ShortTtlCache(cache_dir=cache_dir, fingerprint="base|fp", ttl_s=60)
            cache.set(
                url="http://example.invalid/client/v4/accounts/a/access/apps",
                params=None,
                value={"result": [{"id": "a1"}], "result_info": None, "http": {"duration_ms": 12}},
            )
            cf = CloudflareClient(
                base_url="http://example.invalid/client/v4",
                token="T",
                connect_timeout_s=30,
                read_timeout_s=30,
                verbose=False,
                progress=False,
                cache=cache,
                user_agent="t/0",
            )
            res = cf.get_json("/accounts/a/access/apps", cacheable=True)
            self.assertEqual(res.result, [{"id": "a1"}])
            self.assertTrue((res.http or {}).get("from_cache"))


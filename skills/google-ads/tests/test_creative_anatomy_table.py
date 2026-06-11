from __future__ import annotations

import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from google_ads_api_tool.cli import main


class _FakeGoogleAdsService:
    def __init__(self, rows: list[object]):
        self._rows = rows

    def search(self, request=None, *, customer_id=None, query=None, **kwargs):  # noqa: ARG002
        _ = (request, customer_id, query, kwargs)
        for r in self._rows:
            yield r


class _FakeSearchGoogleAdsRequest:
    def __init__(self) -> None:
        self.customer_id = ""
        self.query = ""
        self.page_size = 0


class _FakeClient:
    def __init__(self, rows: list[object]):
        self._rows = rows

    def get_type(self, name: str):
        if name == "SearchGoogleAdsRequest":
            return _FakeSearchGoogleAdsRequest()
        raise KeyError(name)

    def get_service(self, name: str):
        if name == "GoogleAdsService":
            return _FakeGoogleAdsService(self._rows)
        raise KeyError(name)


class TestCreativeAnatomyTable(unittest.TestCase):
    def test_creative_anatomy_table_created_and_in_manifest(self) -> None:
        os.environ["GOOGLE_ADS_DEVELOPER_TOKEN"] = "DEV_TOKEN_123"
        os.environ["GOOGLE_ADS_CLIENT_ID"] = "CLIENT_ID_123"
        os.environ["GOOGLE_ADS_CLIENT_SECRET"] = "CLIENT_SECRET_123"
        os.environ["GOOGLE_ADS_REFRESH_TOKEN"] = "REFRESH_TOKEN_123"
        try:
            # Minimal row shape for creative anatomy.
            row = {
                "customer": {"id": "123"},
                "campaign": {"id": "1", "resource_name": "customers/123/campaigns/1"},
                "ad_group": {"id": "2", "resource_name": "customers/123/adGroups/2"},
                "ad_group_ad": {
                    "resource_name": "customers/123/adGroupAds/3",
                    "ad": {
                        "id": "99",
                        "type": "RESPONSIVE_SEARCH_AD",
                        "final_urls": ["https://example.com/"],
                        "responsive_search_ad": {
                            "headlines": [{"text": "Headline 1"}, {"text": "Headline 2"}],
                            "descriptions": [{"text": "Desc 1"}],
                        },
                    },
                },
            }

            with tempfile.TemporaryDirectory() as td:
                out_dir = Path(td) / "pack"
                with patch("google_ads_api_tool.google_ads_client.GoogleAdsClient.load_from_dict") as m:
                    m.return_value = _FakeClient([row])
                    buf = io.StringIO()
                    with redirect_stdout(buf):
                        rc = main(
                            [
                                "--output",
                                "json",
                                "snapshot",
                                "export",
                                "--preset",
                                "analysis_pack_v1",
                                "--customer-id",
                                "123",
                                "--since",
                                "2026-01-01",
                                "--until",
                                "2026-01-31",
                                "--out-dir",
                                str(out_dir),
                                "--apply",
                                "--yes",
                            ]
                        )
                self.assertEqual(rc, 0)
                self.assertTrue((out_dir / "tables" / "creative_anatomy.jsonl").exists())

                lines = (out_dir / "tables" / "creative_anatomy.jsonl").read_text(encoding="utf-8").splitlines()
                self.assertGreaterEqual(len(lines), 1)
                obj = json.loads(lines[0])
                self.assertIn("customer", obj)
                self.assertIsInstance(obj["customer"], dict)
                self.assertEqual(obj["customer"].get("id"), "123")
                self.assertIn("ad_group_ad", obj)
                self.assertIsInstance(obj["ad_group_ad"], dict)
                self.assertEqual(obj["ad_group_ad"].get("resource_name"), "customers/123/adGroupAds/3")
                ad = (obj["ad_group_ad"] or {}).get("ad")
                self.assertIsInstance(ad, dict)
                self.assertEqual(ad.get("id"), "99")
                self.assertIn("source_refs", obj)
                self.assertTrue(obj["source_refs"])

                manifest = json.loads((out_dir / "manifest.json").read_text(encoding="utf-8"))
                names = [t.get("name") for t in (manifest.get("tables") or []) if isinstance(t, dict)]
                self.assertIn("creative_anatomy", names)
        finally:
            for k in [
                "GOOGLE_ADS_DEVELOPER_TOKEN",
                "GOOGLE_ADS_CLIENT_ID",
                "GOOGLE_ADS_CLIENT_SECRET",
                "GOOGLE_ADS_REFRESH_TOKEN",
            ]:
                os.environ.pop(k, None)

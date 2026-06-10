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
    def search(self, request=None, *, customer_id=None, query=None, **kwargs):  # noqa: ARG002
        _ = (request, customer_id, kwargs)
        for i in range(10):
            yield {"row": i, "query": query}


class _FakeSearchGoogleAdsRequest:
    def __init__(self) -> None:
        self.customer_id = ""
        self.query = ""
        self.page_size = 0


class _FakeClient:
    def get_type(self, name: str):
        if name == "SearchGoogleAdsRequest":
            return _FakeSearchGoogleAdsRequest()
        raise KeyError(name)

    def get_service(self, name: str):
        if name == "GoogleAdsService":
            return _FakeGoogleAdsService()
        raise KeyError(name)


class TestSnapshotExportMaxRowsTruncation(unittest.TestCase):
    def test_max_rows_truncates_and_records_warnings(self) -> None:
        os.environ["GOOGLE_ADS_DEVELOPER_TOKEN"] = "DEV_TOKEN_123"
        os.environ["GOOGLE_ADS_CLIENT_ID"] = "CLIENT_ID_123"
        os.environ["GOOGLE_ADS_CLIENT_SECRET"] = "CLIENT_SECRET_123"
        os.environ["GOOGLE_ADS_REFRESH_TOKEN"] = "REFRESH_TOKEN_123"
        try:
            with tempfile.TemporaryDirectory() as td:
                out_dir = Path(td) / "pack"
                with patch("google_ads_api_tool.google_ads_client.GoogleAdsClient.load_from_dict") as m:
                    m.return_value = _FakeClient()
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
                                "--max-rows",
                                "3",
                            ]
                        )
                self.assertEqual(rc, 0)
                payload = json.loads(buf.getvalue())
                self.assertTrue(payload["ok"])
                self.assertTrue(payload["warnings"])
                manifest = json.loads((out_dir / "manifest.json").read_text(encoding="utf-8"))
                groups = manifest.get("groups") or []
                self.assertTrue(any(bool(g.get("truncated")) for g in groups if isinstance(g, dict)))
        finally:
            for k in [
                "GOOGLE_ADS_DEVELOPER_TOKEN",
                "GOOGLE_ADS_CLIENT_ID",
                "GOOGLE_ADS_CLIENT_SECRET",
                "GOOGLE_ADS_REFRESH_TOKEN",
            ]:
                os.environ.pop(k, None)

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


class _CountingGoogleAdsService:
    def __init__(self):
        self.calls = 0

    def search(self, request=None, *, customer_id=None, query=None, **kwargs):  # noqa: ARG002
        _ = (request, customer_id, query, kwargs)
        self.calls += 1
        yield {"ok": True, "call": self.calls}


class _FakeSearchGoogleAdsRequest:
    def __init__(self) -> None:
        self.customer_id = ""
        self.query = ""
        self.page_size = 0


class _FakeClient:
    def __init__(self, svc: _CountingGoogleAdsService):
        self._svc = svc

    def get_type(self, name: str):
        if name == "SearchGoogleAdsRequest":
            return _FakeSearchGoogleAdsRequest()
        raise KeyError(name)

    def get_service(self, name: str):
        if name == "GoogleAdsService":
            return self._svc
        raise KeyError(name)


class TestSnapshotExportIncludeOptional(unittest.TestCase):
    def setUp(self) -> None:
        os.environ["GOOGLE_ADS_DEVELOPER_TOKEN"] = "DEV_TOKEN_123"
        os.environ["GOOGLE_ADS_CLIENT_ID"] = "CLIENT_ID_123"
        os.environ["GOOGLE_ADS_CLIENT_SECRET"] = "CLIENT_SECRET_123"
        os.environ["GOOGLE_ADS_REFRESH_TOKEN"] = "REFRESH_TOKEN_123"

    def tearDown(self) -> None:
        for k in [
            "GOOGLE_ADS_DEVELOPER_TOKEN",
            "GOOGLE_ADS_CLIENT_ID",
            "GOOGLE_ADS_CLIENT_SECRET",
            "GOOGLE_ADS_REFRESH_TOKEN",
        ]:
            os.environ.pop(k, None)

    def test_snapshot_export_skips_optional_groups_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            out_dir = Path(td) / "pack"
            svc = _CountingGoogleAdsService()
            with patch("google_ads_api_tool.google_ads_client.GoogleAdsClient.load_from_dict") as m:
                m.return_value = _FakeClient(svc)
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
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertEqual(svc.calls, 4, "analysis_pack_v1 has 4 required groups")
            self.assertFalse((out_dir / "tables" / "asset_groups.jsonl").exists(), "optional group should be skipped")

    def test_snapshot_export_can_include_optional_groups(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            out_dir = Path(td) / "pack"
            svc = _CountingGoogleAdsService()
            with patch("google_ads_api_tool.google_ads_client.GoogleAdsClient.load_from_dict") as m:
                m.return_value = _FakeClient(svc)
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
                            "--include-optional",
                        ]
                    )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertEqual(svc.calls, 5, "analysis_pack_v1 has 1 optional group (asset_groups)")
            self.assertTrue((out_dir / "tables" / "asset_groups.jsonl").exists(), "optional group should be exported")

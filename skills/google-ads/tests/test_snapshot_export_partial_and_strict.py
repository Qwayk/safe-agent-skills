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
    def __init__(self):
        self._calls = 0

    def search(self, request=None, *, customer_id=None, query=None, **kwargs):  # noqa: ARG002
        _ = (request, customer_id, query, kwargs)
        self._calls += 1
        if "ad_group_ad.ad.type" in query:
            raise RuntimeError("boom")
        yield {"ok": True, "call": self._calls}


class _FakeSearchGoogleAdsRequest:
    def __init__(self) -> None:
        self.customer_id = ""
        self.query = ""
        self.page_size = 0


class _FakeClient:
    def __init__(self):
        self._svc = _FakeGoogleAdsService()

    def get_type(self, name: str):
        if name == "SearchGoogleAdsRequest":
            return _FakeSearchGoogleAdsRequest()
        raise KeyError(name)

    def get_service(self, name: str):
        if name == "GoogleAdsService":
            return self._svc
        raise KeyError(name)


class TestSnapshotExportPartialAndStrict(unittest.TestCase):
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

    def test_partial_success_default(self) -> None:
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
                        ]
                    )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["partial_success"])
            self.assertTrue((out_dir / "manifest.json").exists())
            err_lines = (out_dir / "errors" / "errors.jsonl").read_text(encoding="utf-8").splitlines()
            self.assertGreaterEqual(len(err_lines), 1)

    def test_apply_with_timeout_override_does_not_crash(self) -> None:
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
                            "--timeout-s",
                            "1",
                        ]
                    )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])

    def test_strict_mode_fails_on_required_group_failure(self) -> None:
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
                            "--strict",
                        ]
                    )
            self.assertEqual(rc, 1)
            payload = json.loads(buf.getvalue())
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["error_type"], "StrictModeError")
            self.assertTrue((out_dir / "manifest.json").exists())
            err_lines = (out_dir / "errors" / "errors.jsonl").read_text(encoding="utf-8").splitlines()
            self.assertGreaterEqual(len(err_lines), 1)

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


class _FakeRow:
    def __init__(self, i: int):
        self._pb = {"row": i}


class TestSnapshotExportPackStructure(unittest.TestCase):
    def test_snapshot_export_apply_writes_pack_layout_and_manifest(self) -> None:
        os.environ["GOOGLE_ADS_DEVELOPER_TOKEN"] = "DEV_TOKEN_123"
        os.environ["GOOGLE_ADS_CLIENT_ID"] = "CLIENT_ID_123"
        os.environ["GOOGLE_ADS_CLIENT_SECRET"] = "CLIENT_SECRET_123"
        os.environ["GOOGLE_ADS_REFRESH_TOKEN"] = "REFRESH_TOKEN_123"
        try:
            with tempfile.TemporaryDirectory() as td:
                out_dir = Path(td) / "pack"
                rows = [_FakeRow(1), _FakeRow(2)]
                with patch("google_ads_api_tool.google_ads_client.GoogleAdsClient.load_from_dict") as m:
                    m.return_value = _FakeClient(rows)
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
                self.assertFalse(payload["dry_run"])

                manifest_path = out_dir / "manifest.json"
                self.assertTrue(manifest_path.exists())
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                for k in [
                    "schema_version",
                    "tool",
                    "tool_version",
                    "generated_at_utc",
                    "preset",
                    "customer_id",
                    "since",
                    "until",
                    "segmentation",
                    "join_map",
                    "tables",
                    "groups",
                    "warnings",
                    "errors_path",
                    "queries_path",
                ]:
                    self.assertIn(k, manifest)

                # Stable layout.
                self.assertTrue((out_dir / "tables").is_dir())
                self.assertTrue((out_dir / "queries" / "queries.json").exists())
                self.assertTrue((out_dir / "errors" / "errors.jsonl").exists())

                # Tables exist and are JSONL.
                tables = sorted((out_dir / "tables").glob("*.jsonl"))
                self.assertGreaterEqual(len(tables), 1)
                for t in tables:
                    lines = t.read_text(encoding="utf-8").splitlines()
                    for ln in lines:
                        obj = json.loads(ln)
                        self.assertIsInstance(obj, dict)
        finally:
            for k in [
                "GOOGLE_ADS_DEVELOPER_TOKEN",
                "GOOGLE_ADS_CLIENT_ID",
                "GOOGLE_ADS_CLIENT_SECRET",
                "GOOGLE_ADS_REFRESH_TOKEN",
            ]:
                os.environ.pop(k, None)

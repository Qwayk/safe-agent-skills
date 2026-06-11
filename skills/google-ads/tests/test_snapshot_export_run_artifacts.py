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


class TestSnapshotExportRunArtifacts(unittest.TestCase):
    def test_snapshot_export_apply_finalizes_run_artifacts(self) -> None:
        os.environ["GOOGLE_ADS_DEVELOPER_TOKEN"] = "DEV_TOKEN_123"
        os.environ["GOOGLE_ADS_CLIENT_ID"] = "CLIENT_ID_123"
        os.environ["GOOGLE_ADS_CLIENT_SECRET"] = "CLIENT_SECRET_123"
        os.environ["GOOGLE_ADS_REFRESH_TOKEN"] = "REFRESH_TOKEN_123"
        try:
            with tempfile.TemporaryDirectory() as td:
                env_file = Path(td) / ".state" / "google_ads.env"
                env_file.parent.mkdir(parents=True, exist_ok=True)
                out_dir = Path(td) / "pack"

                rows = [_FakeRow(1)]
                with patch("google_ads_api_tool.google_ads_client.GoogleAdsClient.load_from_dict") as m:
                    m.return_value = _FakeClient(rows)
                    buf = io.StringIO()
                    with redirect_stdout(buf):
                        rc = main(
                            [
                                "--output",
                                "json",
                                "--env-file",
                                str(env_file),
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
                self.assertTrue(payload.get("ok"))

                run_id = str(payload.get("run_id") or "").strip()
                artifacts_dir = str(payload.get("artifacts_dir") or "").strip()
                runs_index = str(payload.get("runs_index") or "").strip()
                self.assertTrue(run_id)
                self.assertTrue(artifacts_dir)
                self.assertTrue(runs_index)

                summary_path = Path(artifacts_dir) / "summary.md"
                self.assertTrue(summary_path.exists())

                index_path = Path(runs_index)
                self.assertTrue(index_path.exists())
                self.assertEqual(
                    index_path.resolve(),
                    (Path(td) / ".state" / "runs" / "index.jsonl").resolve(),
                )
                rows = index_path.read_text(encoding="utf-8").splitlines()
                parsed = [json.loads(ln) for ln in rows if ln.strip()]
                self.assertTrue(any(str(r.get("run_id") or "") == run_id for r in parsed))
        finally:
            for k in [
                "GOOGLE_ADS_DEVELOPER_TOKEN",
                "GOOGLE_ADS_CLIENT_ID",
                "GOOGLE_ADS_CLIENT_SECRET",
                "GOOGLE_ADS_REFRESH_TOKEN",
            ]:
                os.environ.pop(k, None)

    def test_snapshot_export_no_artifacts_skips_run_history_writes(self) -> None:
        os.environ["GOOGLE_ADS_DEVELOPER_TOKEN"] = "DEV_TOKEN_123"
        os.environ["GOOGLE_ADS_CLIENT_ID"] = "CLIENT_ID_123"
        os.environ["GOOGLE_ADS_CLIENT_SECRET"] = "CLIENT_SECRET_123"
        os.environ["GOOGLE_ADS_REFRESH_TOKEN"] = "REFRESH_TOKEN_123"
        try:
            with tempfile.TemporaryDirectory() as td:
                env_file = Path(td) / ".state" / "google_ads.env"
                env_file.parent.mkdir(parents=True, exist_ok=True)
                out_dir = Path(td) / "pack"

                rows = [_FakeRow(1)]
                with patch("google_ads_api_tool.google_ads_client.GoogleAdsClient.load_from_dict") as m:
                    m.return_value = _FakeClient(rows)
                    buf = io.StringIO()
                    with redirect_stdout(buf):
                        rc = main(
                            [
                                "--output",
                                "json",
                                "--env-file",
                                str(env_file),
                                "--no-artifacts",
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
                self.assertTrue(payload.get("ok"))
                self.assertIsNone(payload.get("run_id"))
                self.assertIsNone(payload.get("artifacts_dir"))
                self.assertIsNone(payload.get("runs_index"))
                self.assertFalse((Path(td) / ".state" / "runs").exists())
        finally:
            for k in [
                "GOOGLE_ADS_DEVELOPER_TOKEN",
                "GOOGLE_ADS_CLIENT_ID",
                "GOOGLE_ADS_CLIENT_SECRET",
                "GOOGLE_ADS_REFRESH_TOKEN",
            ]:
                os.environ.pop(k, None)

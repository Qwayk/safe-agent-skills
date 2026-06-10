from __future__ import annotations

import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace

from meta_ads_api_tool.audit_log import AuditLogger
from meta_ads_api_tool.commands.snapshot import cmd_snapshot_export
from meta_ads_api_tool.config import Config
from meta_ads_api_tool.graph import PageResult
from meta_ads_api_tool.output import Output


class _FailSecondChunkGraph:
    def __init__(self) -> None:
        self._calls: dict[str, int] = {}

    def list_edge(self, *, object_id: str, edge: str, params=None, max_pages=None, max_items=None) -> PageResult:  # type: ignore[override]
        self._calls[edge] = self._calls.get(edge, 0) + 1
        # Fail the second chunk for campaigns to simulate permissions/fieldset gaps.
        if edge == "campaigns" and self._calls[edge] == 2:
            raise RuntimeError("boom https://graph.facebook.com/v24.0/act_1/campaigns?access_token=SECRET")
        if edge == "campaigns":
            return PageResult(data=[{"id": "c_1", "name": "Camp"}], paging=None, raw_pages=1)
        if edge == "adsets":
            return PageResult(data=[{"id": "as_1", "campaign_id": "c_1"}], paging=None, raw_pages=1)
        if edge == "ads":
            return PageResult(data=[{"id": "a_1", "campaign_id": "c_1", "adset_id": "as_1"}], paging=None, raw_pages=1)
        if edge == "adcreatives":
            return PageResult(data=[{"id": "cr_1"}], paging=None, raw_pages=1)
        if edge == "insights":
            return PageResult(
                data=[{"ad_id": "a_1", "date_start": "2026-01-01", "date_stop": "2026-01-01"}],
                paging=None,
                raw_pages=1,
            )
        return PageResult(data=[], paging=None, raw_pages=1)


class TestChunkingPartialSuccess(unittest.TestCase):
    def _ctx(self) -> dict:
        cfg = Config(
            base_url="https://graph.facebook.com",
            api_version="v24.0",
            access_token="SECRET",
            ad_account_id="act_1",
            timeout_s=1.0,
            max_retries=0,
        )
        return {
            "cfg": cfg,
            "graph": _FailSecondChunkGraph(),
            "out": Output(mode="json"),
            "audit": AuditLogger(path=None, enabled=False),
            "version": "0.0.0-test",
        }

    def test_default_mode_is_partial_success(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            cwd = os.getcwd()
            os.chdir(d)
            try:
                out_dir = Path(d) / "out"
                args = SimpleNamespace(
                    ad_account_id="act_1",
                    preset="ecom_core",
                    out_dir=str(out_dir),
                    run_id="RUNPARTIAL",
                    strict=False,
                    max_pages=1,
                    max_items=0,
                    limit=10,
                    fields_chunk_size=2,
                    param=[],
                )
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = cmd_snapshot_export(args, self._ctx())
                self.assertEqual(rc, 0)
                payload = json.loads(buf.getvalue())
                self.assertTrue(payload["ok"])
                self.assertTrue(payload["snapshot_export"]["partial_success"])
                self.assertGreater(payload["snapshot_export"]["errors_count"], 0)
            finally:
                os.chdir(cwd)

    def test_strict_mode_fails(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            cwd = os.getcwd()
            os.chdir(d)
            try:
                out_dir = Path(d) / "out"
                args = SimpleNamespace(
                    ad_account_id="act_1",
                    preset="ecom_core",
                    out_dir=str(out_dir),
                    run_id="RUNSTRICT",
                    strict=True,
                    max_pages=1,
                    max_items=0,
                    limit=10,
                    fields_chunk_size=2,
                    param=[],
                )
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = cmd_snapshot_export(args, self._ctx())
                self.assertEqual(rc, 1)
                payload = json.loads(buf.getvalue())
                self.assertFalse(payload["ok"])
            finally:
                os.chdir(cwd)


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


class _LeakAttemptGraph:
    def list_edge(self, *, object_id: str, edge: str, params=None, max_pages=None, max_items=None) -> PageResult:  # type: ignore[override]
        if edge == "campaigns":
            raise RuntimeError("HTTP 400 for GET https://graph.facebook.com/v24.0/act_1/campaigns?access_token=SECRET")
        return PageResult(data=[], paging=None, raw_pages=1)


class TestSecretLeaksSnapshot(unittest.TestCase):
    def test_secret_never_appears_in_stdout_or_files(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            cwd = os.getcwd()
            os.chdir(d)
            try:
                out_dir = Path(d) / "out"
                cfg = Config(
                    base_url="https://graph.facebook.com",
                    api_version="v24.0",
                    access_token="SECRET",
                    ad_account_id="act_1",
                    timeout_s=1.0,
                    max_retries=0,
                )
                ctx = {
                    "cfg": cfg,
                    "graph": _LeakAttemptGraph(),
                    "out": Output(mode="json"),
                    "audit": AuditLogger(path=None, enabled=False),
                    "version": "0.0.0-test",
                }
                args = SimpleNamespace(
                    ad_account_id="act_1",
                    preset="ecom_core",
                    out_dir=str(out_dir),
                    run_id="RUNLEAK",
                    strict=False,
                    max_pages=1,
                    max_items=0,
                    limit=10,
                    fields_chunk_size=2,
                    param=[],
                )
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = cmd_snapshot_export(args, ctx)
                self.assertEqual(rc, 0)
                stdout_txt = buf.getvalue()
                self.assertNotIn("SECRET", stdout_txt)

                payload = json.loads(stdout_txt)
                manifest_path = Path(payload["snapshot_export"]["manifest_path"])
                self.assertTrue(manifest_path.exists())
                manifest_txt = manifest_path.read_text(encoding="utf-8")
                self.assertNotIn("SECRET", manifest_txt)

                pack_dir = Path(payload["snapshot_export"]["out_dir"])
                for p in pack_dir.rglob("*.jsonl"):
                    self.assertNotIn("SECRET", p.read_text(encoding="utf-8"))
            finally:
                os.chdir(cwd)


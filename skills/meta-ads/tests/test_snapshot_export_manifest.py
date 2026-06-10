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
from meta_ads_api_tool.errors import ValidationError
from meta_ads_api_tool.graph import PageResult
from meta_ads_api_tool.output import Output


class _StubGraph:
    def __init__(self) -> None:
        self.calls: list[dict] = []

    def list_edge(self, *, object_id: str, edge: str, params=None, max_pages=None, max_items=None) -> PageResult:  # type: ignore[override]
        self.calls.append({"object_id": object_id, "edge": edge, "params": dict(params or {})})
        if edge == "campaigns":
            return PageResult(data=[{"id": "c_1", "name": "Camp"}], paging=None, raw_pages=1)
        if edge == "adsets":
            return PageResult(
                data=[{"id": "as_1", "campaign_id": "c_1", "name": "AS"}],
                paging=None,
                raw_pages=1,
            )
        if edge == "ads":
            return PageResult(
                data=[{"id": "a_1", "campaign_id": "c_1", "adset_id": "as_1", "creative": {"id": "cr_1"}}],
                paging=None,
                raw_pages=1,
            )
        if edge == "adcreatives":
            return PageResult(
                data=[
                    {
                        "id": "cr_1",
                        "name": "Creative",
                        "image_url": "https://cdn.example.com/asset.jpg",
                    }
                ],
                paging=None,
                raw_pages=1,
            )
        if edge == "insights":
            return PageResult(
                data=[{"ad_id": "a_1", "date_start": "2026-01-01", "date_stop": "2026-01-01", "spend": "1.23"}],
                paging=None,
                raw_pages=1,
            )
        return PageResult(data=[], paging=None, raw_pages=1)


class TestSnapshotExportManifest(unittest.TestCase):
    def test_snapshot_export_writes_manifest_and_tables(self) -> None:
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
                    "graph": _StubGraph(),
                    "out": Output(mode="json"),
                    "audit": AuditLogger(path=None, enabled=False),
                    "version": "0.0.0-test",
                }
                args = SimpleNamespace(
                    ad_account_id="act_1",
                    preset="ecom_core",
                    out_dir=str(out_dir),
                    run_id="RUN1",
                    strict=False,
                    max_pages=1,
                    max_items=0,
                    limit=10,
                    fields_chunk_size=50,
                    param=[],
                )

                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = cmd_snapshot_export(args, ctx)
                self.assertEqual(rc, 0)
                payload = json.loads(buf.getvalue())
                self.assertTrue(payload["ok"])
                se = payload["snapshot_export"]
                self.assertEqual(se["run_id"], "RUN1")

                pack_dir = Path(se["out_dir"])
                manifest_path = Path(se["manifest_path"])
                self.assertTrue(pack_dir.exists())
                self.assertTrue(manifest_path.exists())

                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                self.assertEqual(manifest["schema_version"], "1")
                self.assertIn("join_keys", manifest)
                self.assertIn("tables", manifest)
                self.assertIn("assets", manifest)
                self.assertGreaterEqual(len(manifest["tables"]), 3)

                tables_dir = pack_dir / "tables"
                self.assertTrue((tables_dir / "campaigns.jsonl").exists())
                self.assertTrue((tables_dir / "ad_sets.jsonl").exists())
                self.assertTrue((tables_dir / "ads.jsonl").exists())
                self.assertTrue((tables_dir / "creatives.jsonl").exists())
                self.assertTrue((tables_dir / "creative_anatomy.jsonl").exists())
                self.assertTrue((tables_dir / "asset_urls.jsonl").exists())
                self.assertTrue((tables_dir / "insights.jsonl").exists())
            finally:
                os.chdir(cwd)

    def test_snapshot_export_download_assets_opt_in(self) -> None:
        class _StubHttp:
            def request(self, method: str, url: str, *, headers=None, params=None, retries=0):  # type: ignore[override]
                class _Resp:
                    body = b"img"

                return _Resp()

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
                    "graph": _StubGraph(),
                    "http": _StubHttp(),
                    "out": Output(mode="json"),
                    "audit": AuditLogger(path=None, enabled=False),
                    "version": "0.0.0-test",
                }
                args = SimpleNamespace(
                    ad_account_id="act_1",
                    preset="ecom_core",
                    out_dir=str(out_dir),
                    run_id="RUN2",
                    strict=False,
                    download_assets=True,
                    assets_overwrite="if_missing",
                    max_pages=1,
                    max_items=0,
                    limit=10,
                    fields_chunk_size=50,
                    param=[],
                )

                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = cmd_snapshot_export(args, ctx)
                self.assertEqual(rc, 0)
                payload = json.loads(buf.getvalue())
                self.assertTrue(payload["ok"])
                se = payload["snapshot_export"]
                self.assertTrue(se["assets_enabled"])

                pack_dir = Path(se["out_dir"])
                manifest = json.loads((pack_dir / "manifest.json").read_text(encoding="utf-8"))
                self.assertTrue(manifest["assets"]["enabled"])
                tables_dir = pack_dir / "tables"
                self.assertTrue((tables_dir / "creative_anatomy.jsonl").exists())
                self.assertTrue((tables_dir / "asset_urls.jsonl").exists())
                self.assertTrue((tables_dir / "assets.jsonl").exists())
                assets_rows = (tables_dir / "assets.jsonl").read_text(encoding="utf-8").strip().splitlines()
                self.assertGreaterEqual(len(assets_rows), 1)
            finally:
                os.chdir(cwd)

    def test_snapshot_export_since_until_overrides_params(self) -> None:
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
                graph = _StubGraph()
                ctx = {
                    "cfg": cfg,
                    "graph": graph,
                    "out": Output(mode="json"),
                    "audit": AuditLogger(path=None, enabled=False),
                    "version": "0.0.0-test",
                }
                args = SimpleNamespace(
                    ad_account_id="act_1",
                    preset="ecom_core",
                    out_dir=str(out_dir),
                    run_id="RUN3",
                    strict=False,
                    since="2026-02-01",
                    until="2026-02-07",
                    param=[
                        "date_preset=last_7d",
                        'time_range={"since":"2026-01-01","until":"2026-01-31"}',
                    ],
                    max_pages=1,
                    max_items=0,
                    limit=10,
                    fields_chunk_size=200,
                )

                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = cmd_snapshot_export(args, ctx)
                self.assertEqual(rc, 0)

                insight_calls = [c for c in graph.calls if c["edge"] == "insights"]
                self.assertEqual(len(insight_calls), 1)
                p = insight_calls[0]["params"]
                self.assertEqual(p.get("time_range"), '{"since":"2026-02-01","until":"2026-02-07"}')
                self.assertNotIn("date_preset", p)
            finally:
                os.chdir(cwd)

    def test_snapshot_export_extra_insights_breakdown_table(self) -> None:
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
                graph = _StubGraph()
                ctx = {
                    "cfg": cfg,
                    "graph": graph,
                    "out": Output(mode="json"),
                    "audit": AuditLogger(path=None, enabled=False),
                    "version": "0.0.0-test",
                }
                args = SimpleNamespace(
                    ad_account_id="act_1",
                    preset="ecom_core",
                    out_dir=str(out_dir),
                    run_id="RUN4",
                    strict=False,
                    extra_insights_breakdown_table=["placement:publisher_platform,platform_position"],
                    max_pages=1,
                    max_items=0,
                    limit=10,
                    fields_chunk_size=200,
                    param=[],
                )

                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = cmd_snapshot_export(args, ctx)
                self.assertEqual(rc, 0)
                payload = json.loads(buf.getvalue())
                pack_dir = Path(payload["snapshot_export"]["out_dir"])
                tables_dir = pack_dir / "tables"
                self.assertTrue((tables_dir / "insights_placement.jsonl").exists())

                manifest = json.loads((pack_dir / "manifest.json").read_text(encoding="utf-8"))
                tables = {t["table"] for t in manifest.get("tables") or []}
                self.assertIn("insights_placement", tables)

                insight_calls = [c for c in graph.calls if c["edge"] == "insights"]
                self.assertEqual(len(insight_calls), 2)
                breakdown_call = next((c for c in insight_calls if c["params"].get("breakdowns")), None)
                self.assertIsNotNone(breakdown_call)
                self.assertEqual(
                    breakdown_call["params"].get("breakdowns"),
                    "publisher_platform,platform_position",
                )
            finally:
                os.chdir(cwd)

    def test_snapshot_export_rejects_since_until_with_date_preset(self) -> None:
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
                    "graph": _StubGraph(),
                    "out": Output(mode="json"),
                    "audit": AuditLogger(path=None, enabled=False),
                    "version": "0.0.0-test",
                }
                args = SimpleNamespace(
                    ad_account_id="act_1",
                    preset="ecom_core",
                    out_dir=str(out_dir),
                    run_id="RUN5",
                    strict=False,
                    since="2026-02-01",
                    until="2026-02-07",
                    date_preset="last_7d",
                    max_pages=1,
                    max_items=0,
                    limit=10,
                    fields_chunk_size=200,
                    param=[],
                )
                with self.assertRaises(ValidationError):
                    cmd_snapshot_export(args, ctx)
            finally:
                os.chdir(cwd)

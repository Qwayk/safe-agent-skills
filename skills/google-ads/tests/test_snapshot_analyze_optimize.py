from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from google_ads_api_tool.cli import main


def _write_pack_with_tables(pack_dir: Path, *, tables: dict[str, list[dict]]) -> None:
    pack_dir.mkdir(parents=True, exist_ok=True)
    (pack_dir / "tables").mkdir(parents=True, exist_ok=True)
    (pack_dir / "queries").mkdir(parents=True, exist_ok=True)
    (pack_dir / "errors").mkdir(parents=True, exist_ok=True)
    (pack_dir / "queries" / "queries.json").write_text("{}", encoding="utf-8")
    (pack_dir / "errors" / "errors.jsonl").write_text("", encoding="utf-8")

    manifest_tables = []
    for name, rows in tables.items():
        rel = f"tables/{name}.jsonl"
        (pack_dir / rel).write_text(
            "\n".join(json.dumps(r, ensure_ascii=False, sort_keys=True) for r in rows) + "\n", encoding="utf-8"
        )
        manifest_tables.append(
            {
                "name": name,
                "path": rel,
                "row_count": len(rows),
                "truncated": False,
                "join_keys": ["customer.id"],
                "source_group_id": name,
            }
        )

    manifest = {
        "schema_version": 1,
        "tool": "google-ads-api-tool",
        "tool_version": "0.6.0",
        "generated_at_utc": "2026-03-02T00:00:00Z",
        "preset": "analysis_pack_v2",
        "customer_id": "123",
        "since": "2026-01-01",
        "until": "2026-01-31",
        "segmentation": "base",
        "join_map": {"customer.id": {"description": "x", "fields": ["customer.id"]}},
        "tables": manifest_tables,
        "groups": [{"group_id": "ad_daily_metrics", "required": True, "status": "ok", "error_count": 0, "row_count": 1, "truncated": False}],
        "warnings": [],
        "errors_path": "errors/errors.jsonl",
        "queries_path": "queries/queries.json",
    }
    (pack_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")


class TestSnapshotAnalyzeOptimize(unittest.TestCase):
    def test_snapshot_analyze_optimize_works_with_minimal_tables(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            pack_dir = Path(td) / "pack"
            _write_pack_with_tables(
                pack_dir,
                tables={
                    "ad_daily_metrics": [
                        {
                            "customer": {"id": "123"},
                            "campaign": {"id": "1", "resource_name": "customers/123/campaigns/1"},
                            "ad_group": {"id": "2", "resource_name": "customers/123/adGroups/2"},
                            "ad_group_ad": {"resource_name": "customers/123/adGroupAds/1", "ad": {"id": "99"}},
                            "segments": {"date": "2026-01-10"},
                            "metrics": {
                                "impressions": 100,
                                "clicks": 10,
                                "cost_micros": 5000000,
                                "conversions": 3,
                                "conversions_value": 120.0,
                            },
                        }
                    ]
                },
            )

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--output", "json", "snapshot", "analyze", "optimize", "--pack-dir", str(pack_dir)])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertIn("summary", payload)
            self.assertIn("recommendations", payload)
            self.assertIn("ad_daily_metrics", payload["tables_used"])
            self.assertIn("search_terms_daily", payload["tables_missing"])


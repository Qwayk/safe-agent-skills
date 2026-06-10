from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from google_ads_api_tool.cli import main


def _write_minimal_pack(pack_dir: Path, *, preset: str, since: str, until: str, tables: list[dict], groups: list[dict]) -> None:
    pack_dir.mkdir(parents=True, exist_ok=True)
    (pack_dir / "tables").mkdir(parents=True, exist_ok=True)
    (pack_dir / "queries").mkdir(parents=True, exist_ok=True)
    (pack_dir / "errors").mkdir(parents=True, exist_ok=True)
    (pack_dir / "queries" / "queries.json").write_text("{}", encoding="utf-8")
    (pack_dir / "errors" / "errors.jsonl").write_text("", encoding="utf-8")
    manifest = {
        "schema_version": 1,
        "tool": "google-ads-api-tool",
        "tool_version": "0.1.0",
        "generated_at_utc": "2026-02-05T00:00:00Z",
        "preset": preset,
        "customer_id": "123",
        "since": since,
        "until": until,
        "segmentation": "base",
        "join_map": {"campaign.resource_name": {"description": "x", "fields": ["campaign.resource_name"]}},
        "tables": tables,
        "groups": groups,
        "warnings": [],
        "errors_path": "errors/errors.jsonl",
        "queries_path": "queries/queries.json",
    }
    (pack_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")


class TestSnapshotCompare(unittest.TestCase):
    def test_snapshot_compare_dry_run_and_apply(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            pack_a = td_path / "pack_a"
            pack_b = td_path / "pack_b"
            out_dir = td_path / "cmp_out"

            _write_minimal_pack(
                pack_a,
                preset="analysis_pack_v1",
                since="2026-01-01",
                until="2026-01-31",
                tables=[{"name": "campaigns", "row_count": 1}, {"name": "creative_anatomy", "row_count": 1}],
                groups=[{"group_id": "campaigns", "status": "ok"}],
            )
            _write_minimal_pack(
                pack_b,
                preset="analysis_pack_v1",
                since="2026-02-01",
                until="2026-02-28",
                tables=[{"name": "campaigns", "row_count": 2}],
                groups=[{"group_id": "campaigns", "status": "ok"}],
            )

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "snapshot",
                        "compare",
                        "--pack-a",
                        str(pack_a),
                        "--pack-b",
                        str(pack_b),
                        "--out-dir",
                        str(out_dir),
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])
            self.assertFalse(out_dir.exists())

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "snapshot",
                        "compare",
                        "--pack-a",
                        str(pack_a),
                        "--pack-b",
                        str(pack_b),
                        "--out-dir",
                        str(out_dir),
                        "--apply",
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertFalse(payload["dry_run"])
            self.assertTrue((out_dir / "compare_summary.json").exists())


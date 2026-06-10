from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from google_ads_api_tool.cli import main


class TestSnapshotExportDryRun(unittest.TestCase):
    def test_snapshot_export_dry_run_writes_no_pack_and_makes_no_api_calls(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            out_dir = Path(td) / "pack"
            buf = io.StringIO()
            with patch("google_ads_api_tool.google_ads_client.GoogleAdsClient.load_from_dict") as m:
                m.side_effect = AssertionError("should not build google ads client in dry-run")
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
                        ]
                    )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])
            self.assertFalse(out_dir.exists())


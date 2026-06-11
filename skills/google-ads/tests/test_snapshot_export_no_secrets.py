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


class TestSnapshotExportNoSecrets(unittest.TestCase):
    def test_snapshot_export_redacts_env_secrets_on_client_build_error(self) -> None:
        os.environ["GOOGLE_ADS_DEVELOPER_TOKEN"] = "DEV_TOKEN_SUPER_SECRET"
        os.environ["GOOGLE_ADS_CLIENT_ID"] = "CLIENT_ID_SUPER_SECRET"
        os.environ["GOOGLE_ADS_CLIENT_SECRET"] = "CLIENT_SECRET_SUPER_SECRET"
        os.environ["GOOGLE_ADS_REFRESH_TOKEN"] = "REFRESH_TOKEN_SUPER_SECRET"
        try:
            with tempfile.TemporaryDirectory() as td:
                out_dir = Path(td) / "pack"
                with patch("google_ads_api_tool.google_ads_client.GoogleAdsClient.load_from_dict") as m:
                    m.side_effect = RuntimeError(
                        "boom DEV_TOKEN_SUPER_SECRET CLIENT_SECRET_SUPER_SECRET REFRESH_TOKEN_SUPER_SECRET"
                    )
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
                self.assertEqual(rc, 1)
                payload = json.loads(buf.getvalue())
                s = json.dumps(payload)
                self.assertNotIn("DEV_TOKEN_SUPER_SECRET", s)
                self.assertNotIn("CLIENT_SECRET_SUPER_SECRET", s)
                self.assertNotIn("REFRESH_TOKEN_SUPER_SECRET", s)
                # Still writes an auditable pack with errors.
                self.assertTrue((out_dir / "errors" / "errors.jsonl").exists())
                err = (out_dir / "errors" / "errors.jsonl").read_text(encoding="utf-8")
                self.assertNotIn("DEV_TOKEN_SUPER_SECRET", err)
                self.assertNotIn("CLIENT_SECRET_SUPER_SECRET", err)
                self.assertNotIn("REFRESH_TOKEN_SUPER_SECRET", err)
        finally:
            for k in [
                "GOOGLE_ADS_DEVELOPER_TOKEN",
                "GOOGLE_ADS_CLIENT_ID",
                "GOOGLE_ADS_CLIENT_SECRET",
                "GOOGLE_ADS_REFRESH_TOKEN",
            ]:
                os.environ.pop(k, None)


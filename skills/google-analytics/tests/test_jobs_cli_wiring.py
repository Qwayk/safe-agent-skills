from __future__ import annotations

import csv
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from ga4_api_tool import cli


class TestJobsCliWiring(unittest.TestCase):
    def test_jobs_uses_real_config_env_fingerprint(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            td = Path(d)
            env_path = td / ".env"
            env_path.write_text(
                "\n".join(
                    [
                        "GA4_AUTH_MODE=adc",
                        "GA4_TIMEOUT_S=1",
                        "GA4_ADMIN_BASE_URL=http://example.invalid/admin/",
                        "GA4_DATA_BASE_URL=http://example.invalid/data/",
                        "",
                    ]
                ),
                encoding="utf-8",
            )

            jobs_path = td / "jobs.csv"
            with jobs_path.open("w", encoding="utf-8", newline="") as f:
                w = csv.writer(f)
                w.writerow(["action"])
                w.writerow(["read.ping"])

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = cli.main(
                    [
                        "--env-file",
                        str(env_path),
                        "--no-artifacts",
                        "jobs",
                        "run",
                        "--file",
                        str(jobs_path),
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])
            env_fp = payload.get("plan", {}).get("env_fingerprint")
            self.assertIsInstance(env_fp, str)
            self.assertRegex(env_fp, r"^[0-9a-f]{64}$")


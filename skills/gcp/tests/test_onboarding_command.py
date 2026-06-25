from __future__ import annotations

import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout

from gcp_safe_agent_cli.cli import main


class TestOnboardingCommand(unittest.TestCase):
    def test_onboarding_creates_env_from_example(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = os.path.join(td, ".env")
            example_path = os.path.join(td, ".env.example")
            with open(example_path, "w", encoding="utf-8") as f:
                f.write("GCP_QUOTA_PROJECT=quota-proj\n")
                f.write("GCP_ALLOWED_PROJECTS=proj-a,proj-b\n")
                f.write("GCP_ALLOWED_FOLDERS=folder-a\n")
                f.write("GCP_ALLOWED_ORGANIZATIONS=org-a\n")
                f.write("GCP_ALLOWED_BILLING_ACCOUNTS=BA-1\n")
                f.write("GCP_ALLOWED_REGIONS=us-central1\n")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--output", "json", "--env-file", env_path, "onboarding"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["onboarding"]["env_created"])
            self.assertTrue(os.path.exists(env_path))
            self.assertEqual(payload["onboarding"]["missing"], [])

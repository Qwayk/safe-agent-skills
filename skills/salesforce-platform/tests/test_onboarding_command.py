from __future__ import annotations

import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout

from tests import bootstrap  # noqa: F401

from salesforce_platform_safe_agent_cli.cli import main


class TestOnboardingCommand(unittest.TestCase):
    def test_onboarding_creates_env_from_example(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = os.path.join(td, ".env")
            example_path = os.path.join(td, ".env.example")
            with open(example_path, "w", encoding="utf-8") as f:
                f.write("SALESFORCE_INSTANCE_URL=https://example.my.salesforce.com\n")
                f.write("SALESFORCE_API_VERSION=67.0\n")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--output", "json", "--env-file", env_path, "onboarding"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["onboarding"]["env_created"])
            self.assertTrue(os.path.exists(env_path))
            self.assertEqual(payload["onboarding"]["missing"], [])

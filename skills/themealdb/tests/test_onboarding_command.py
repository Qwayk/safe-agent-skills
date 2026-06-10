from __future__ import annotations

import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout

from qwayk_themealdb_safe_agent_cli.cli import main


class TestOnboardingCommand(unittest.TestCase):
    def test_onboarding_creates_env_from_example(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            env_path = os.path.join(temp_dir, ".env")
            example_path = os.path.join(temp_dir, ".env.example")
            with open(example_path, "w", encoding="utf-8") as file_obj:
                file_obj.write("THEMEALDB_BASE_URL=https://www.themealdb.com/api/json/v1\n")
                file_obj.write("THEMEALDB_API_KEY=1\n")
                file_obj.write("THEMEALDB_TIMEOUT_S=30\n")

            buffer = io.StringIO()
            with redirect_stdout(buffer):
                rc = main(["--output", "json", "--env-file", env_path, "onboarding"])
            self.assertEqual(rc, 0)
            payload = json.loads(buffer.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["onboarding"]["env_created"])
            self.assertTrue(os.path.exists(env_path))
            self.assertEqual(
                payload["onboarding"]["next_command"],
                "qwayk-themealdb-safe-agent-cli --output json auth check",
            )

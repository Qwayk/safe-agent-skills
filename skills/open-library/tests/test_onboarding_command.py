from __future__ import annotations

import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from qwayk_open_library_safe_agent_cli.cli import main


class TestOnboardingCommand(unittest.TestCase):
    def test_onboarding_creates_env_from_example(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = os.path.join(td, ".env")
            example_path = os.path.join(td, ".env.example")
            with open(example_path, "w", encoding="utf-8") as f:
                f.write("OPEN_LIBRARY_BASE_URL=https://openlibrary.org\n")
                f.write("OPEN_LIBRARY_TIMEOUT_S=30\n")
                f.write("OPEN_LIBRARY_USER_AGENT_APP=qwayk-open-library-safe-agent-cli\n")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--output", "json", "--env-file", env_path, "onboarding"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["onboarding"]["env_created"])
            self.assertIn("missing", payload["onboarding"])
            self.assertEqual(payload["onboarding"].get("missing", []), [])
            self.assertTrue(os.path.exists(env_path))

    def test_onboarding_writes_audit_log_when_requested(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = os.path.join(td, ".env")
            log_path = os.path.join(td, "audit.jsonl")
            example_path = os.path.join(td, ".env.example")
            with open(example_path, "w", encoding="utf-8") as f:
                f.write("OPEN_LIBRARY_BASE_URL=https://openlibrary.org\n")
                f.write("OPEN_LIBRARY_TIMEOUT_S=30\n")
                f.write("OPEN_LIBRARY_USER_AGENT_APP=qwayk-open-library-safe-agent-cli\n")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        env_path,
                        "--log-file",
                        log_path,
                        "onboarding",
                    ]
                )
            self.assertEqual(rc, 0)
            rows = Path(log_path).read_text(encoding="utf-8").splitlines()
            self.assertGreaterEqual(len(rows), 2)
            parsed = [json.loads(row) for row in rows]
            self.assertEqual(parsed[0]["event"], "command_start")
            self.assertEqual(parsed[-1]["event"], "command_ok")

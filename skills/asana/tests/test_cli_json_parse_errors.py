from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from asana_safe_agent_cli.cli import main


class TestCliErrors(unittest.TestCase):
    def test_missing_command_is_one_json_error(self) -> None:
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            rc = main([])
        payload = json.loads(stdout.getvalue())
        self.assertEqual(rc, 1)
        self.assertFalse(payload["ok"])

    def test_missing_token_does_not_leak_env_file_content(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env = Path(td) / ".env"
            env.write_text("ASANA_ACCESS_TOKEN=\nPRIVATE_MARKER=do-not-print\n", encoding="utf-8")
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                rc = main(["--env-file", str(env), "api", "get-workspaces"])
        self.assertEqual(rc, 1)
        self.assertNotIn("PRIVATE_MARKER", stdout.getvalue())
        self.assertNotIn("do-not-print", stdout.getvalue())


if __name__ == "__main__":
    unittest.main()

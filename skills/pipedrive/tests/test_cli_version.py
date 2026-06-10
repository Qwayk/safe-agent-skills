from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout

from qwayk_pipedrive_safe_agent_cli import __version__
from qwayk_pipedrive_safe_agent_cli.cli import main


class TestCliVersion(unittest.TestCase):
    def test_version_json_no_env_needed(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = main(["--output", "json", "--version"])
        self.assertEqual(rc, 0)
        payload = json.loads(buf.getvalue())
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["tool"], "qwayk-pipedrive-safe-agent-cli")
        self.assertEqual(payload["version"], __version__)

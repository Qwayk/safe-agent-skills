from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from msads_api_tool.cli import main


class TestAuthCheckRedaction(unittest.TestCase):
    def test_auth_check_never_echoes_developer_token(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = Path(d) / ".env"
            env_path.write_text(
                "\n".join(
                    [
                        "MSADS_ENVIRONMENT=prod",
                        "MSADS_TIMEOUT_S=30",
                        "MSADS_DEVELOPER_TOKEN=super-secret-dev-token",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--output", "json", "--env-file", str(env_path), "auth", "check"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["developer_token_present"])
            self.assertNotIn("super-secret-dev-token", buf.getvalue())


from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from x_api_tool.cli import main


class TestAuthCheckLiveMissingToken(unittest.TestCase):
    def test_live_auth_check_requires_oauth_token(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text("X_API_BASE_URL=https://api.x.com/2\n", encoding="utf-8")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--output", "json", "--env-file", str(env_path), "--live", "auth", "check"])
            self.assertEqual(rc, 1)
            payload = json.loads(buf.getvalue())
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["error_type"], "ValidationError")

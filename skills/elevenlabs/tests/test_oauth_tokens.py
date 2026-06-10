from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from elevenlabs_api_tool.cli import main


class TestAuthOutput(unittest.TestCase):
    def test_auth_check_reports_env_key_presence_without_oauth_fields(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = Path(d) / ".env"
            env_path.write_text(
                "\n".join(
                    [
                        "ELEVENLABS_API_BASE_URL=http://example.invalid",
                        "ELEVENLABS_API_KEY=secret-token",
                        "ELEVENLABS_TIMEOUT_S=30",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--env-file", str(env_path), "--output", "json", "auth", "check"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["env_token_present"])
            self.assertNotIn("oauth_token", payload)

from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from hubspot_safe_agent_cli.cli import main


class TestAuthRedaction(unittest.TestCase):
    def test_auth_check_failure_does_not_leak_token(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env = root / ".env"
            secret = "VERY_SECRET_HUBSPOT_TOKEN"
            env.write_text(
                "\n".join(
                    [
                        "HUBSPOT_API_BASE_URL=http://example.invalid",
                        f"HUBSPOT_ACCESS_TOKEN={secret}",
                        "HUBSPOT_TIMEOUT_S=30",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            with patch("hubspot_safe_agent_cli.commands.auth.HttpClient.request") as mock_request:
                mock_request.side_effect = RuntimeError("401")

                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = main(["--env-file", str(env), "auth", "check"])

            self.assertEqual(rc, 1)
            payload = json.loads(buf.getvalue())
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["error_type"], "ToolError")
            self.assertIn("auth check", payload["error"].lower())
            self.assertNotIn(secret, buf.getvalue())

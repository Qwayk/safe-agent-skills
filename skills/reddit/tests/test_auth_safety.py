from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from qwayk_reddit_safe_agent_cli.cli import main


class TestAuthSafety(unittest.TestCase):
    def test_live_auth_failure_does_not_leak_client_secret(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            env_path = Path(temp_dir) / ".env"
            env_path.write_text(
                "\n".join(
                    [
                        "REDDIT_CLIENT_ID=test-client",
                        "REDDIT_CLIENT_SECRET=super-secret-value",
                        "REDDIT_REDIRECT_URI=http://localhost:8080/callback",
                        "REDDIT_CONTACT_USERNAME=exampleuser",
                        "REDDIT_ACCESS_TOKEN=",
                        "",
                    ]
                ),
                encoding="utf-8",
            )

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--output", "json", "--env-file", str(env_path), "--live", "auth", "check"])

            self.assertEqual(rc, 1)
            payload = json.loads(buf.getvalue())
            text = json.dumps(payload, sort_keys=True)
            self.assertNotIn("super-secret-value", text)
            self.assertNotIn("REDDIT_CLIENT_SECRET", text)

    def test_auth_exchange_code_requires_live_before_network(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            env_path = Path(temp_dir) / ".env"
            env_path.write_text(
                "\n".join(
                    [
                        "REDDIT_CLIENT_ID=test-client",
                        "REDDIT_CLIENT_SECRET=super-secret-value",
                        "REDDIT_REDIRECT_URI=http://localhost:8080/callback",
                        "REDDIT_CONTACT_USERNAME=exampleuser",
                        "",
                    ]
                ),
                encoding="utf-8",
            )

            buf = io.StringIO()
            with patch("qwayk_reddit_safe_agent_cli.commands.auth.requests.post") as mock_post:
                with redirect_stdout(buf):
                    rc = main(["--output", "json", "--env-file", str(env_path), "auth", "exchange-code", "--code", "test-code"])

            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            self.assertIn("--live is required", payload["reasons"][0])
            mock_post.assert_not_called()

    def test_auth_refresh_requires_live_before_network(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            env_path = Path(temp_dir) / ".env"
            env_path.write_text(
                "\n".join(
                    [
                        "REDDIT_CLIENT_ID=test-client",
                        "REDDIT_CLIENT_SECRET=super-secret-value",
                        "REDDIT_REDIRECT_URI=http://localhost:8080/callback",
                        "REDDIT_CONTACT_USERNAME=exampleuser",
                        "",
                    ]
                ),
                encoding="utf-8",
            )

            buf = io.StringIO()
            with patch("qwayk_reddit_safe_agent_cli.commands.auth.requests.post") as mock_post:
                with redirect_stdout(buf):
                    rc = main(["--output", "json", "--env-file", str(env_path), "auth", "refresh"])

            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            self.assertIn("--live is required", payload["reasons"][0])
            mock_post.assert_not_called()

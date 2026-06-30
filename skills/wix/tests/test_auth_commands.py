from __future__ import annotations

import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.cli import main


class TestAuthCommands(unittest.TestCase):
    def test_auth_token_request_stores_token_safely(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = os.path.join(td, ".env")
            state_path = os.path.join(td, ".state", "token.json")
            with open(env_path, "w", encoding="utf-8") as f:
                f.write("WIX_API_BASE_URL=https://www.wixapis.com\n")
                f.write("WIX_APP_ID=my-app\n")
                f.write("WIX_APP_SECRET=my-secret\n")
            with patch(
                "wix_safe_agent_cli.commands.auth.request_access_token",
                return_value={
                    "access_token": "new-access-token",
                    "refresh_token": "new-refresh-token",
                    "token_type": "Bearer",
                    "expires_in": 3600,
                },
            ) as request_mock:
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = main(["--env-file", env_path, "auth", "token", "request", "--code", "auth-code-123"])
            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["stored_to"], state_path)
            self.assertIn("legacy custom-auth", " ".join(payload.get("notes", [])))
            self.assertEqual(payload["oauth_token"]["access_token"], "***REDACTED***")
            self.assertEqual(payload["oauth_token"]["refresh_token"], "***REDACTED***")
            request_mock.assert_called_once()
            call = request_mock.call_args.kwargs
            self.assertEqual(call["code"], "auth-code-123")
            self.assertEqual(call["base_url"], "https://www.wixapis.com")
            token = json.loads(Path(state_path).read_text(encoding="utf-8"))
            self.assertEqual(token["access_token"], "new-access-token")
            self.assertEqual(token["refresh_token"], "new-refresh-token")
            output_text = buf.getvalue()
            self.assertNotIn("new-access-token", output_text)
            self.assertNotIn("new-refresh-token", output_text)

    def test_auth_check_errors_when_auth_inputs_are_missing(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = os.path.join(td, ".env")
            with open(env_path, "w", encoding="utf-8") as f:
                f.write("WIX_API_BASE_URL=https://www.wixapis.com\n")
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--env-file", env_path, "auth", "check"])
            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 1)
            self.assertFalse(payload["ok"])
            self.assertIn("Missing official Wix credentials", payload["error"])

    def test_auth_check_runs_official_token_flow(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = os.path.join(td, ".env")
            with open(env_path, "w", encoding="utf-8") as f:
                f.write("WIX_API_BASE_URL=https://www.wixapis.com\n")
                f.write("WIX_APP_ID=my-app\n")
                f.write("WIX_APP_SECRET=my-secret\n")
                f.write("WIX_INSTANCE_ID=inst-1\n")
            with patch(
                "wix_safe_agent_cli.commands.auth.create_access_token",
                return_value={"access_token": "secret-token", "token_type": "Bearer", "expires_in": 3600},
            ) as create_mock:
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = main(["--env-file", env_path, "auth", "check"])
            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["checked_with"], "app_credentials")
            self.assertIn("token_endpoint", payload)
            self.assertEqual(create_mock.call_count, 1)
            output_text = buf.getvalue()
            self.assertNotIn("secret-token", output_text)

    def test_auth_token_create_stores_token_safely(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = os.path.join(td, ".env")
            state_path = os.path.join(td, ".state", "token.json")
            with open(env_path, "w", encoding="utf-8") as f:
                f.write("WIX_APP_ID=my-app\n")
                f.write("WIX_APP_SECRET=my-secret\n")
                f.write("WIX_INSTANCE_ID=inst-1\n")
            with patch(
                "wix_safe_agent_cli.commands.auth.create_access_token",
                return_value={"access_token": "secret-token", "token_type": "Bearer", "expires_in": 3600},
            ):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = main(["--env-file", env_path, "auth", "token", "create"])
            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(os.path.exists(state_path))
            self.assertIn("oauth_token", payload)
            self.assertEqual(payload["oauth_token"]["access_token"], "***REDACTED***")
            token = json.loads(Path(state_path).read_text(encoding="utf-8"))
            self.assertEqual(token["access_token"], "secret-token")

    def test_auth_token_refresh_stores_token_safely(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = os.path.join(td, ".env")
            state_path = os.path.join(td, ".state", "token.json")
            with open(env_path, "w", encoding="utf-8") as f:
                f.write("WIX_API_BASE_URL=https://www.wixapis.com\n")
                f.write("WIX_APP_ID=my-app\n")
                f.write("WIX_APP_SECRET=my-secret\n")
            Path(state_path).parent.mkdir(parents=True, exist_ok=True)
            Path(state_path).write_text(
                json.dumps({"access_token": "old-access", "refresh_token": "refresh-secret"}),
                encoding="utf-8",
            )
            with patch(
                "wix_safe_agent_cli.commands.auth.refresh_access_token",
                return_value={
                    "access_token": "new-secret-token",
                    "refresh_token": "new-refresh-secret",
                    "token_type": "Bearer",
                    "expires_in": 3600,
                },
            ) as refresh_mock:
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = main(["--env-file", env_path, "auth", "token", "refresh"])
            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["stored_to"], state_path)
            self.assertIn("oauth_token", payload)
            self.assertEqual(payload["oauth_token"]["access_token"], "***REDACTED***")
            self.assertEqual(payload["oauth_token"]["refresh_token"], "***REDACTED***")
            refresh_mock.assert_called_once()
            token = json.loads(Path(state_path).read_text(encoding="utf-8"))
            self.assertEqual(token["access_token"], "new-secret-token")
            self.assertEqual(token["refresh_token"], "new-refresh-secret")
            output_text = buf.getvalue()
            self.assertNotIn("new-secret-token", output_text)
            self.assertNotIn("new-refresh-secret", output_text)

    def test_auth_token_inspect_uses_safe_output(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = os.path.join(td, ".env")
            with open(env_path, "w", encoding="utf-8") as f:
                f.write("WIX_API_BASE_URL=https://www.wixapis.com\n")
                f.write("WIX_APP_ID=my-app\n")
                f.write("WIX_APP_SECRET=my-secret\n")
                f.write("WIX_INSTANCE_ID=inst-1\n")
            with patch(
                "wix_safe_agent_cli.commands.auth.inspect_access_token",
                return_value={
                    "active": True,
                    "subject_type": "app_instance",
                    "subject_id": "inst-1",
                    "access_token": "secret-token",
                    "client_id": "my-app",
                },
            ):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = main([
                        "--env-file",
                        env_path,
                        "auth",
                        "token",
                        "inspect",
                        "--token",
                        "secret-token",
                    ])
            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["source"], "provided")
            self.assertEqual(payload["token_info"]["access_token"], "***REDACTED***")

    def test_parser_recognizes_auth_token_request(self) -> None:
        parser = build_parser()
        parsed = parser.parse_args(["auth", "token", "request", "--code", "auth-code-123"])
        self.assertEqual(parsed.auth_cmd, "token")
        self.assertEqual(parsed.token_cmd, "request")
        self.assertTrue(parsed.write_capable)
        self.assertEqual(parsed.func.__name__, "cmd_auth_token_request")

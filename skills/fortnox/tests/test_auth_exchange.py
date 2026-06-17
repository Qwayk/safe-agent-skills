from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from fortnox_api_tool.cli import main


class _FakeResp:
    def __init__(self, status_code: int, payload: dict[str, object]):
        self.status_code = status_code
        self._payload = payload
        self.text = json.dumps(payload)


class TestAuthExchange(unittest.TestCase):
    def test_auth_login_builds_service_account_url_and_state_file(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = Path(d) / ".env"
            env_path.write_text(
                "\n".join(
                    [
                        "FORTNOX_API_BASE_URL=https://api.fortnox.se/3",
                        "FORTNOX_CLIENT_ID=test-client",
                        "FORTNOX_CLIENT_SECRET=test-secret",
                        "FORTNOX_REDIRECT_URI=https://example.com/callback",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_path),
                        "auth",
                        "login",
                        "--service-account",
                        "--state",
                        "known-state",
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertIn("account_type=service", payload["authorize_url"])
            self.assertEqual(payload["state"], "known-state")
            self.assertTrue(Path(payload["state_file"]).exists())

    def test_auth_exchange_code_writes_token_file(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = Path(d) / ".env"
            env_path.write_text(
                "\n".join(
                    [
                        "FORTNOX_API_BASE_URL=https://api.fortnox.se/3",
                        "FORTNOX_CLIENT_ID=test-client",
                        "FORTNOX_CLIENT_SECRET=test-secret",
                        "FORTNOX_REDIRECT_URI=https://example.com/callback",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            state_dir = Path(d) / ".state"
            state_dir.mkdir(parents=True, exist_ok=True)
            (state_dir / "oauth_state.json").write_text(
                json.dumps({"state": "known-state", "redirect_uri": "https://example.com/callback"}),
                encoding="utf-8",
            )
            buf = io.StringIO()
            with patch(
                "fortnox_api_tool.auth_runtime.requests.post",
                return_value=_FakeResp(
                    200,
                    {
                        "access_token": "A",
                        "refresh_token": "R",
                        "expires_in": 3600,
                        "scope": "companyinformation",
                        "token_type": "bearer",
                    },
                ),
            ):
                with redirect_stdout(buf):
                    rc = main(
                        [
                            "--output",
                            "json",
                            "--env-file",
                            str(env_path),
                            "auth",
                            "exchange-code",
                            "--code",
                            "auth-code",
                            "--state",
                            "known-state",
                        ]
                    )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(Path(payload["stored_to"]).exists())
            self.assertEqual(payload["token"]["access_token"], "***REDACTED***")

    def test_auth_exchange_code_honors_custom_token_file_path(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = Path(d) / ".env"
            env_path.write_text(
                "\n".join(
                    [
                        "FORTNOX_API_BASE_URL=https://api.fortnox.se/3",
                        "FORTNOX_CLIENT_ID=test-client",
                        "FORTNOX_CLIENT_SECRET=test-secret",
                        "FORTNOX_REDIRECT_URI=https://example.com/callback",
                        "FORTNOX_TOKEN_FILE=.tokens/custom-token.json",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            state_dir = Path(d) / ".state"
            state_dir.mkdir(parents=True, exist_ok=True)
            (state_dir / "oauth_state.json").write_text(
                json.dumps({"state": "known-state", "redirect_uri": "https://example.com/callback"}),
                encoding="utf-8",
            )
            buf = io.StringIO()
            with patch(
                "fortnox_api_tool.auth_runtime.requests.post",
                return_value=_FakeResp(
                    200,
                    {
                        "access_token": "A",
                        "refresh_token": "R",
                        "expires_in": 3600,
                        "scope": "companyinformation",
                        "token_type": "bearer",
                    },
                ),
            ):
                with redirect_stdout(buf):
                    rc = main(
                        [
                            "--output",
                            "json",
                            "--env-file",
                            str(env_path),
                            "auth",
                            "exchange-code",
                            "--code",
                            "auth-code",
                            "--state",
                            "known-state",
                        ]
                    )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertEqual(Path(payload["stored_to"]), Path(d) / ".tokens" / "custom-token.json")

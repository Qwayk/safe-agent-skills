from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import headless_authentication
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = (action, payload)


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestHeadlessAuthenticationCommands(unittest.TestCase):
    def _ctx(self, **overrides) -> dict:
        cfg = SimpleNamespace(
            base_url="https://www.wixapis.com",
            timeout_s=30.0,
            access_token="token-abc",
            app_id=None,
            app_secret=None,
            instance_id=None,
            has_official_app_auth=False,
        )
        ctx = {
            "cfg": cfg,
            "env_file": "/tmp/.env",
            "tool": "wix-safe-agent-cli",
            "tool_version": "0.0.0",
            "command_str": "wix-safe-agent-cli headless-authentication",
            "apply": False,
            "yes": False,
            "verbose": False,
            "out": Output(mode="json"),
            "audit": _DummyAudit(),
            "plan_in": None,
            "plan_out": None,
            "receipt_out": None,
            "ack_irreversible": False,
            "enforce_reviewed_plan": True,
        }
        ctx.update(overrides)
        return ctx

    def test_parser_recognizes_headless_authentication_commands(self) -> None:
        parser = build_parser()
        cases = [
            ["headless-authentication", "login-v2", "--login-json", '{"email":"a@example.com","password":"secret"}'],
            ["headless-authentication", "retrieve-tokens", "--token-json", '{"clientId":"client-1","grantType":"anonymous"}'],
            ["headless-authentication", "register-v2", "--register-json", '{"email":"a@example.com","password":"secret"}'],
            ["headless-authentication", "change-password", "--password-json", '{"oldPassword":"old","newPassword":"new"}'],
            ["headless-authentication", "logout", "--params-json", '{"postLogoutRedirectUri":"https://example.com"}'],
            ["headless-authentication", "sign-on", "--sign-on-json", '{"email":"a@example.com"}'],
        ]
        for argv in cases:
            with self.subTest(argv=argv):
                args = parser.parse_args(argv)
                self.assertTrue(callable(args.func))

    @patch("wix_safe_agent_cli.commands.headless_authentication.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.headless_authentication.HttpClient")
    def test_login_v2_uses_official_path_and_redacts_secrets(self, mock_client, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"sessionToken": "session-secret"})

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = headless_authentication.cmd_headless_authentication_login_v2(
                SimpleNamespace(login_json='{"email":"a@example.com","password":"input-secret"}'),
                self._ctx(),
            )

        payload = json.loads(buf.getvalue())
        rendered = json.dumps(payload)
        self.assertEqual(rc, 0)
        self.assertEqual(payload["request"]["method"], "POST")
        self.assertEqual(payload["request"]["path"], "/_api/iam/authentication/v2/login")
        self.assertTrue(payload["redacted"])
        self.assertNotIn("input-secret", rendered)
        self.assertNotIn("session-secret", rendered)
        self.assertEqual(payload["request"]["body"]["password"], "[REDACTED]")
        self.assertEqual(payload["response"]["sessionToken"], "[REDACTED]")

    @patch("wix_safe_agent_cli.commands.headless_authentication.HttpClient")
    def test_retrieve_tokens_uses_oauth_token_path_without_auth_and_redacts_tokens(self, mock_client) -> None:
        mock_client.return_value.request.return_value = _DummyResponse(
            {"access_token": "access-secret", "refresh_token": "refresh-secret", "expires_in": 3600}
        )

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = headless_authentication.cmd_headless_authentication_retrieve_tokens(
                SimpleNamespace(token_json='{"clientId":"client-1","grantType":"refresh_token","refreshToken":"refresh-input"}'),
                self._ctx(),
            )

        payload = json.loads(buf.getvalue())
        rendered = json.dumps(payload)
        self.assertEqual(rc, 0)
        self.assertEqual(payload["auth_mode"], "oauth_client_request")
        self.assertEqual(payload["request"]["path"], "/oauth2/token")
        self.assertNotIn("refresh-input", rendered)
        self.assertNotIn("access-secret", rendered)
        self.assertNotIn("refresh-secret", rendered)
        mock_client.return_value.request.assert_called_once()
        self.assertEqual(mock_client.return_value.request.call_args.kwargs["headers"]["Content-Type"], "application/json")

    @patch("wix_safe_agent_cli.commands.headless_authentication.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.headless_authentication.HttpClient")
    def test_register_v2_is_plan_first_and_redacted(self, mock_client, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = headless_authentication.cmd_headless_authentication_register_v2(
                SimpleNamespace(register_json='{"email":"a@example.com","password":"input-secret"}'),
                self._ctx(),
            )

        payload = json.loads(buf.getvalue())
        rendered = json.dumps(payload)
        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["method"], "headlessAuthentication.registerV2")
        self.assertEqual(payload["plan"]["request"]["path"], "/_api/iam/authentication/v2/register")
        self.assertNotIn("input-secret", rendered)
        mock_client.return_value.request.assert_not_called()

    @patch("wix_safe_agent_cli.commands.headless_authentication.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.headless_authentication.HttpClient")
    def test_change_password_requires_ack_and_matching_plan(self, mock_client, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"ok": True})

        with tempfile.TemporaryDirectory() as tmp:
            plan_path = Path(tmp) / "plan.json"
            plan = {
                "method": "headlessAuthentication.changePassword",
                "baseline": {
                    "env_fingerprint": "https://www.wixapis.com",
                    "selector": {"kind": "headless-authentication", "operation": "change-password"},
                },
                "proposed_changes": [{"operation": "change-member-password"}],
            }
            plan_path.write_text(json.dumps(plan), encoding="utf-8")

            refused_buf = io.StringIO()
            with redirect_stdout(refused_buf):
                refused_rc = headless_authentication.cmd_headless_authentication_change_password(
                    SimpleNamespace(password_json='{"oldPassword":"old-secret","newPassword":"new-secret"}'),
                    self._ctx(apply=True, yes=True, plan_in=str(plan_path), ack_irreversible=False),
                )

            accepted_buf = io.StringIO()
            with redirect_stdout(accepted_buf):
                accepted_rc = headless_authentication.cmd_headless_authentication_change_password(
                    SimpleNamespace(password_json='{"oldPassword":"old-secret","newPassword":"new-secret"}'),
                    self._ctx(apply=True, yes=True, plan_in=str(plan_path), ack_irreversible=True),
                )

        refused = json.loads(refused_buf.getvalue())
        accepted = json.loads(accepted_buf.getvalue())
        rendered = json.dumps(accepted)
        self.assertEqual(refused_rc, 0)
        self.assertTrue(refused["dry_run"])
        self.assertIn("apply also requires --ack-irreversible", refused["plan"]["preconditions"])
        self.assertEqual(accepted_rc, 0)
        self.assertFalse(accepted["dry_run"])
        self.assertEqual(accepted["receipt"]["request"]["path"], "/_api/iam/authentication/v2/change-password")
        self.assertNotIn("old-secret", rendered)
        self.assertNotIn("new-secret", rendered)
        mock_client.return_value.request.assert_called_once()

    @patch("wix_safe_agent_cli.commands.headless_authentication.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.headless_authentication.HttpClient")
    def test_logout_and_sign_on_use_official_paths(self, mock_client, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}

        logout_buf = io.StringIO()
        with redirect_stdout(logout_buf):
            logout_rc = headless_authentication.cmd_headless_authentication_logout(
                SimpleNamespace(params_json='{"postLogoutRedirectUri":"https://example.com"}'),
                self._ctx(),
            )

        sign_on_buf = io.StringIO()
        with redirect_stdout(sign_on_buf):
            sign_on_rc = headless_authentication.cmd_headless_authentication_sign_on(
                SimpleNamespace(sign_on_json='{"email":"a@example.com"}'),
                self._ctx(),
            )

        logout = json.loads(logout_buf.getvalue())
        sign_on = json.loads(sign_on_buf.getvalue())
        self.assertEqual(logout_rc, 0)
        self.assertEqual(sign_on_rc, 0)
        self.assertEqual(logout["plan"]["request"]["method"], "GET")
        self.assertEqual(logout["plan"]["request"]["path"], "/_api/iam/authentication/v1/logout")
        self.assertEqual(sign_on["plan"]["request"]["method"], "POST")
        self.assertEqual(sign_on["plan"]["request"]["path"], "/_api/iam/authentication/v2/sign-on")

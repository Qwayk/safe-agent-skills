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
from wix_safe_agent_cli.commands import headless_verification
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = (action, payload)


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestHeadlessVerificationCommands(unittest.TestCase):
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
            "command_str": "wix-safe-agent-cli headless-verification verify-during-authentication",
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

    def test_parser_exposes_headless_verification_command(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "headless-verification",
                "verify-during-authentication",
                "--code",
                "123456",
                "--state-token",
                "state-1",
            ]
        )

        self.assertIs(args.func, headless_verification.cmd_headless_verification_verify_during_authentication)
        self.assertTrue(args.write_capable)
        self.assertEqual(args.code, "123456")
        self.assertEqual(args.state_token, "state-1")

    @patch("wix_safe_agent_cli.commands.headless_verification.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.headless_verification.HttpClient")
    def test_verify_during_authentication_is_plan_first_and_redacted(self, mock_client, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = headless_verification.cmd_headless_verification_verify_during_authentication(
                SimpleNamespace(code="123456", state_token="state-secret", verification_json=None),
                self._ctx(),
            )
        payload = json.loads(buf.getvalue())
        rendered = json.dumps(payload)

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertTrue(payload["redacted"])
        self.assertEqual(payload["plan"]["method"], "headlessVerification.verifyDuringAuthentication")
        self.assertEqual(payload["plan"]["request"]["method"], "POST")
        self.assertEqual(payload["plan"]["request"]["path"], "/_api/iam/verification/v1/auth/verify")
        self.assertNotIn("123456", rendered)
        self.assertNotIn("state-secret", rendered)
        self.assertEqual(payload["plan"]["request"]["body"]["code"], "[REDACTED]")
        self.assertEqual(payload["plan"]["request"]["body"]["stateToken"], "[REDACTED]")
        self.assertEqual(mock_auth.call_args.kwargs["command_family"], "headless-verification")
        mock_client.return_value.request.assert_not_called()

    @patch("wix_safe_agent_cli.commands.headless_verification.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.headless_verification.HttpClient")
    def test_verify_during_authentication_apply_requires_matching_plan(self, mock_client, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"state": "SUCCESS", "sessionToken": "session-secret"})

        with tempfile.TemporaryDirectory() as tmp:
            plan_path = Path(tmp) / "plan.json"
            plan = {
                "method": "headlessVerification.verifyDuringAuthentication",
                "baseline": {
                    "env_fingerprint": "https://www.wixapis.com",
                    "selector": {"kind": "headless-verification", "operation": "verify-during-authentication"},
                },
                "proposed_changes": [{"operation": "verify-during-authentication"}],
            }
            plan_path.write_text(json.dumps(plan), encoding="utf-8")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = headless_verification.cmd_headless_verification_verify_during_authentication(
                    SimpleNamespace(code=None, state_token=None, verification_json='{"code":"123456","stateToken":"state-secret"}'),
                    self._ctx(apply=True, yes=True, plan_in=str(plan_path)),
                )
        payload = json.loads(buf.getvalue())
        rendered = json.dumps(payload)

        self.assertEqual(rc, 0)
        self.assertFalse(payload["dry_run"])
        self.assertEqual(payload["receipt"]["request"]["path"], "/_api/iam/verification/v1/auth/verify")
        self.assertEqual(payload["receipt"]["response"]["sessionToken"], "[REDACTED]")
        self.assertNotIn("123456", rendered)
        self.assertNotIn("state-secret", rendered)
        self.assertNotIn("session-secret", rendered)
        call = mock_client.return_value.request.call_args
        self.assertEqual(call.kwargs["method"], "POST")
        self.assertEqual(call.kwargs["url"], "https://www.wixapis.com/_api/iam/verification/v1/auth/verify")
        self.assertEqual(call.kwargs["json_body"], {"code": "123456", "stateToken": "state-secret"})

    def test_verify_during_authentication_requires_code_and_state_token(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = headless_verification.cmd_headless_verification_verify_during_authentication(
                SimpleNamespace(code=None, state_token=None, verification_json='{"code":"123456"}'),
                self._ctx(),
            )
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertEqual(payload["error_type"], "ValidationError")
        self.assertIn("stateToken", payload["error"])

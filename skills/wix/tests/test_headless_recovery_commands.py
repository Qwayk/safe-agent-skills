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
from wix_safe_agent_cli.commands import headless_recovery
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = (action, payload)


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestHeadlessRecoveryCommands(unittest.TestCase):
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
            "command_str": "wix-safe-agent-cli headless-recovery send-recovery-email",
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

    def test_parser_exposes_headless_recovery_command(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "headless-recovery",
                "send-recovery-email",
                "--recovery-json",
                '{"email":"a@example.com","redirectUrl":"https://example.com/login"}',
            ]
        )

        self.assertIs(args.func, headless_recovery.cmd_headless_recovery_send_recovery_email)
        self.assertTrue(args.write_capable)

    @patch("wix_safe_agent_cli.commands.headless_recovery.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.headless_recovery.HttpClient")
    def test_send_recovery_email_is_plan_first_and_uses_official_path(self, mock_client, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = headless_recovery.cmd_headless_recovery_send_recovery_email(
                SimpleNamespace(recovery_json='{"email":"a@example.com","redirectUrl":"https://example.com/login"}'),
                self._ctx(),
            )
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["method"], "headlessRecovery.sendRecoveryEmail")
        self.assertEqual(payload["plan"]["request"]["method"], "POST")
        self.assertEqual(payload["plan"]["request"]["path"], "/_api/iam/recovery/v1/send-email")
        self.assertIn("apply also requires --ack-irreversible", payload["plan"]["preconditions"])
        self.assertIn("connected Wix site must be published", payload["plan"]["preconditions"])
        self.assertEqual(mock_auth.call_args.kwargs["command_family"], "headless-recovery")
        mock_client.return_value.request.assert_not_called()

    @patch("wix_safe_agent_cli.commands.headless_recovery.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.headless_recovery.HttpClient")
    def test_send_recovery_email_requires_ack_and_matching_plan(self, mock_client, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"ok": True, "resetToken": "secret-token"})

        with tempfile.TemporaryDirectory() as tmp:
            plan_path = Path(tmp) / "plan.json"
            plan = {
                "method": "headlessRecovery.sendRecoveryEmail",
                "baseline": {
                    "env_fingerprint": "https://www.wixapis.com",
                    "selector": {"kind": "headless-recovery", "operation": "send-recovery-email"},
                },
                "proposed_changes": [{"operation": "send-recovery-email"}],
            }
            plan_path.write_text(json.dumps(plan), encoding="utf-8")

            refused_buf = io.StringIO()
            with redirect_stdout(refused_buf):
                refused_rc = headless_recovery.cmd_headless_recovery_send_recovery_email(
                    SimpleNamespace(recovery_json='{"email":"a@example.com"}'),
                    self._ctx(apply=True, yes=True, plan_in=str(plan_path), ack_irreversible=False),
                )

            accepted_buf = io.StringIO()
            with redirect_stdout(accepted_buf):
                accepted_rc = headless_recovery.cmd_headless_recovery_send_recovery_email(
                    SimpleNamespace(recovery_json='{"email":"a@example.com"}'),
                    self._ctx(apply=True, yes=True, plan_in=str(plan_path), ack_irreversible=True),
                )

        refused = json.loads(refused_buf.getvalue())
        accepted = json.loads(accepted_buf.getvalue())
        rendered = json.dumps(accepted)
        self.assertEqual(refused_rc, 0)
        self.assertTrue(refused["dry_run"])
        self.assertEqual(accepted_rc, 0)
        self.assertFalse(accepted["dry_run"])
        self.assertEqual(accepted["receipt"]["request"]["path"], "/_api/iam/recovery/v1/send-email")
        self.assertNotIn("secret-token", rendered)
        self.assertEqual(accepted["receipt"]["response"]["resetToken"], "[REDACTED]")
        mock_client.return_value.request.assert_called_once()

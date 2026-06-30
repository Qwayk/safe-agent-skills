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
from wix_safe_agent_cli.commands import payment_link_settings
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = (action, payload)


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestPaymentLinkSettingsCommands(unittest.TestCase):
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
            "command_str": "wix-safe-agent-cli payment-link-settings",
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

    def test_parser_recognizes_payment_link_settings_commands(self) -> None:
        parser = build_parser()
        cases = [
            ["payment-link-settings", "get"],
            ["payment-link-settings", "update", "--settings-json", '{"checkoutSettings":{"enabled":true}}'],
        ]
        for argv in cases:
            with self.subTest(argv=argv):
                args = parser.parse_args(argv)
                self.assertTrue(callable(args.func))

    @patch("wix_safe_agent_cli.commands.payment_link_settings.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.payment_link_settings.HttpClient")
    def test_get_uses_official_path(self, mock_client, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"paymentLinksSettings": {"id": "settings"}})

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = payment_link_settings.cmd_payment_link_settings_get(SimpleNamespace(), self._ctx())

        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertEqual(payload["request"]["method"], "GET")
        self.assertEqual(payload["request"]["path"], "/payment-links/v1/payment-links-settings")
        self.assertEqual(mock_auth.call_args.kwargs["command_family"], "payment-link-settings")

    @patch("wix_safe_agent_cli.commands.payment_link_settings.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.payment_link_settings.HttpClient")
    def test_update_emits_reviewed_plan_on_official_path(self, mock_client, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = payment_link_settings.cmd_payment_link_settings_update(
                SimpleNamespace(settings_json='{"checkoutSettings":{"enabled":true}}'),
                self._ctx(),
            )

        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["method"], "paymentLinksSettings.updatePaymentLinksSettings")
        self.assertEqual(payload["plan"]["request"]["method"], "PATCH")
        self.assertEqual(payload["plan"]["request"]["path"], "/payment-links/v1/payment-links-settings")
        self.assertNotIn("apply also requires --ack-irreversible", payload["plan"]["preconditions"])
        mock_client.return_value.request.assert_not_called()

    @patch("wix_safe_agent_cli.commands.payment_link_settings.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.payment_link_settings.HttpClient")
    def test_update_apply_requires_matching_plan_and_calls_provider(self, mock_client, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"paymentLinksSettings": {"id": "settings"}})

        with tempfile.TemporaryDirectory() as tmp:
            plan_path = Path(tmp) / "plan.json"
            plan = {
                "method": "paymentLinksSettings.updatePaymentLinksSettings",
                "baseline": {
                    "env_fingerprint": "https://www.wixapis.com",
                    "selector": {"scope": "site-payment-link-settings"},
                },
                "proposed_changes": [{"operation": "update-payment-link-settings"}],
            }
            plan_path.write_text(json.dumps(plan), encoding="utf-8")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = payment_link_settings.cmd_payment_link_settings_update(
                    SimpleNamespace(settings_json='{"checkoutSettings":{"enabled":true}}'),
                    self._ctx(apply=True, yes=True, plan_in=str(plan_path)),
                )

        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertFalse(payload["dry_run"])
        self.assertEqual(payload["receipt"]["request"]["method"], "PATCH")
        self.assertEqual(payload["receipt"]["request"]["path"], "/payment-links/v1/payment-links-settings")
        mock_client.return_value.request.assert_called_once()

    @patch("wix_safe_agent_cli.commands.payment_link_settings.HttpClient")
    def test_update_rejects_empty_settings_before_request(self, mock_client) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = payment_link_settings.cmd_payment_link_settings_update(
                SimpleNamespace(settings_json="{}"),
                self._ctx(),
            )

        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 1)
        self.assertEqual(payload["error_type"], "ValidationError")
        mock_client.return_value.request.assert_not_called()

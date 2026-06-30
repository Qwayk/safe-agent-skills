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
from wix_safe_agent_cli.commands import portfolio_settings
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = action, payload


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestPortfolioSettingsCommands(unittest.TestCase):
    def _ctx(self, **overrides) -> dict:
        cfg = SimpleNamespace(
            base_url="https://www.wixapis.com",
            timeout_s=30.0,
            app_id=None,
            app_secret=None,
            instance_id=None,
            access_token="token-abc",
            has_official_app_auth=False,
        )
        ctx = {
            "cfg": cfg,
            "env_file": "/tmp/.env",
            "verbose": False,
            "out": Output(mode="json"),
            "audit": _DummyAudit(),
            "tool": "wix-safe-agent-cli",
            "tool_version": "0.0.0",
            "command_str": "wix-safe-agent-cli portfolio-settings",
            "apply": False,
            "yes": False,
            "plan_in": None,
            "plan_out": None,
            "receipt_out": None,
            "ack_irreversible": False,
        }
        ctx.update(overrides)
        return ctx

    @patch("wix_safe_agent_cli.commands.portfolio_settings.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.portfolio_settings.HttpClient")
    def test_get_portfolio_settings_builds_expected_request(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "Bearer token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"portfolioSettings": {"media": {"layout": "GRID"}}})
        args = SimpleNamespace()
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = portfolio_settings.cmd_portfolio_settings_get(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["method"], "portfolio-settings.get")
        self.assertEqual(payload["request"]["method"], "GET")
        self.assertEqual(payload["request"]["path"], "/portfolio/v1/settings")
        mock_auth.assert_called_once()
        self.assertEqual(mock_auth.call_args.kwargs["command_family"], "portfolio-settings")

    @patch("wix_safe_agent_cli.commands.portfolio_settings.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.portfolio_settings.HttpClient")
    def test_update_portfolio_settings_dry_run_emits_reviewed_plan(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "Bearer token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"portfolioSettings": {"displayProjectDate": False, "revision": "7"}})
        args = SimpleNamespace(settings_json='{"portfolioSettings":{"displayProjectDate":true}}')
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = portfolio_settings.cmd_portfolio_settings_update(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        plan = payload["plan"]
        self.assertEqual(plan["method"], "portfolio-settings.update")
        self.assertEqual(plan["request"]["method"], "PATCH")
        self.assertEqual(plan["request"]["path"], "/portfolio/v1/settings")
        self.assertEqual(plan["request"]["body"]["portfolioSettings"]["revision"], "7")
        self.assertEqual(plan["selector"], {"kind": "portfolio-settings", "scope": "site-portfolio-settings"})
        self.assertIn("before_state", plan["baseline"])
        self.assertEqual(mock_client.return_value.request.call_count, 1)

    @patch("wix_safe_agent_cli.commands.portfolio_settings.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.portfolio_settings.HttpClient")
    def test_update_portfolio_settings_apply_uses_plan_and_emits_receipt(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "Bearer token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.side_effect = [
            _DummyResponse({"portfolioSettings": {"displayProjectDate": False, "revision": "7"}}),
            _DummyResponse({"portfolioSettings": {"displayProjectDate": True, "revision": "8"}}),
            _DummyResponse({"portfolioSettings": {"displayProjectDate": True, "revision": "8"}}),
        ]
        plan = {
            "method": "portfolio-settings.update",
            "baseline": {
                "env_fingerprint": "https://www.wixapis.com",
                "selector": {"kind": "portfolio-settings", "scope": "site-portfolio-settings"},
            },
            "proposed_changes": [{"operation": "update-portfolio-settings", "scope": "site-portfolio-settings"}],
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            plan_path = Path(tmpdir) / "plan.json"
            plan_path.write_text(json.dumps(plan), encoding="utf-8")
            args = SimpleNamespace(settings_json='{"portfolioSettings":{"displayProjectDate":true}}')
            ctx = self._ctx(apply=True, yes=True, plan_in=str(plan_path))

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = portfolio_settings.cmd_portfolio_settings_update(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertFalse(payload["dry_run"])
        self.assertEqual(payload["method"], "portfolio-settings.update")
        self.assertEqual(payload["request"]["method"], "PATCH")
        self.assertEqual(payload["receipt"]["verification"]["type"], "read-after-write")
        self.assertTrue(payload["receipt"]["verification"]["ok"])
        self.assertEqual(payload["request"]["body"]["portfolioSettings"]["revision"], "7")
        self.assertEqual(mock_client.return_value.request.call_count, 3)

    @patch("wix_safe_agent_cli.commands.portfolio_settings.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.portfolio_settings.HttpClient")
    def test_update_refuses_mismatched_revision(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "Bearer token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"portfolioSettings": {"displayProjectDate": False, "revision": "7"}})
        args = SimpleNamespace(settings_json='{"portfolioSettings":{"displayProjectDate":true,"revision":"6"}}')
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = portfolio_settings.cmd_portfolio_settings_update(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertIn("revision", payload["reasons"][0])
        self.assertEqual(mock_client.return_value.request.call_count, 1)

    @patch("wix_safe_agent_cli.commands.portfolio_settings.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.portfolio_settings.HttpClient")
    def test_update_rejects_non_object_settings_json(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        args = SimpleNamespace(settings_json='["bad"]')
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = portfolio_settings.cmd_portfolio_settings_update(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error_type"], "ValidationError")
        mock_auth.assert_not_called()
        mock_client.assert_not_called()

    def test_parser_exposes_portfolio_settings_commands(self) -> None:
        parser = build_parser()
        get_args = parser.parse_args(["portfolio-settings", "get"])
        update_args = parser.parse_args(["portfolio-settings", "update", "--settings-json", "{}"])

        self.assertIs(get_args.func, portfolio_settings.cmd_portfolio_settings_get)
        self.assertFalse(get_args.write_capable)
        self.assertIs(update_args.func, portfolio_settings.cmd_portfolio_settings_update)
        self.assertTrue(update_args.write_capable)

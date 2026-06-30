from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.commands import events_settings
from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = action, payload


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestEventsSettingsCommands(unittest.TestCase):
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
            "command_str": "wix-safe-agent-cli events-settings",
            "apply": False,
            "yes": False,
            "plan_in": None,
            "plan_out": None,
            "receipt_out": None,
            "ack_irreversible": False,
        }
        ctx.update(overrides)
        return ctx

    @patch("wix_safe_agent_cli.commands.events_settings.HttpClient")
    def test_get_events_settings_builds_expected_request(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"eventsSettings": {"id": "settings-1"}})
        args = SimpleNamespace()
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = events_settings.cmd_events_settings_get(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["method"], "events-settings.get")
        self.assertEqual(payload["request"]["method"], "GET")
        self.assertEqual(payload["request"]["path"], "/events/v1/settings")

    @patch("wix_safe_agent_cli.commands.events_settings.HttpClient")
    def test_update_events_settings_dry_run_emits_developer_preview_plan(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"eventsSettings": {"id": "settings-1"}})
        args = SimpleNamespace(events_settings_id="settings-1", settings_json='{"eventsSettings":{"delayedPaymentCaptureEnabled":true}}')
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = events_settings.cmd_events_settings_update(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        plan = payload["plan"]
        self.assertEqual(plan["method"], "events-settings.update")
        self.assertEqual(plan["request"]["method"], "PATCH")
        self.assertEqual(plan["request"]["path"], "/events/v1/settings/settings-1")
        self.assertIn("developer-preview", plan["risk_reasons"])

    @patch("wix_safe_agent_cli.commands.events_settings.HttpClient")
    def test_update_refuses_when_current_settings_id_differs(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"eventsSettings": {"id": "settings-2"}})
        args = SimpleNamespace(events_settings_id="settings-1", settings_json='{"eventsSettings":{"delayedPaymentCaptureEnabled":true}}')
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = events_settings.cmd_events_settings_update(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertIn("settings-2", payload["reasons"][0])

    def test_parser_exposes_events_settings_commands(self) -> None:
        parser = build_parser()
        get_args = parser.parse_args(["events-settings", "get"])
        update_args = parser.parse_args(
            ["events-settings", "update", "--events-settings-id", "settings-1", "--settings-json", "{}"]
        )

        self.assertIs(get_args.func, events_settings.cmd_events_settings_get)
        self.assertFalse(get_args.write_capable)
        self.assertIs(update_args.func, events_settings.cmd_events_settings_update)
        self.assertTrue(update_args.write_capable)

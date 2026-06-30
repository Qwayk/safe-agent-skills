from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import multilingual_locale_settings
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def __init__(self) -> None:
        self.writes: list[tuple[str, dict]] = []

    def write(self, action: str, payload: dict) -> None:
        self.writes.append((action, payload))


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestMultilingualLocaleSettingsCommands(unittest.TestCase):
    def _ctx(self, **overrides) -> dict:
        cfg = SimpleNamespace(
            base_url="https://www.wixapis.com",
            timeout_s=30.0,
            access_token="site-token",
            api_key=None,
            account_id=None,
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
            "command_str": "wix-safe-agent-cli multilingual-locale-settings",
            "apply": False,
            "yes": False,
            "verbose": False,
            "out": Output(mode="json"),
            "audit": _DummyAudit(),
            "plan_in": None,
            "plan_out": None,
            "receipt_out": None,
            "ack_irreversible": False,
            "enforce_reviewed_plan": False,
        }
        ctx.update(overrides)
        return ctx

    def test_parser_recognizes_locale_settings_commands(self) -> None:
        parser = build_parser()

        get_args = parser.parse_args(["multilingual-locale-settings", "get"])
        self.assertEqual(get_args.multilingual_locale_settings_cmd, "get")
        self.assertFalse(get_args.write_capable)
        self.assertEqual(get_args.func.__name__, "cmd_multilingual_locale_settings_get")

        update_args = parser.parse_args(
            ["multilingual-locale-settings", "update", "--locale-settings-json", '{"revision":"1"}']
        )
        self.assertEqual(update_args.multilingual_locale_settings_cmd, "update")
        self.assertTrue(update_args.write_capable)

    @patch("wix_safe_agent_cli.commands.multilingual_locale_settings.HttpClient")
    def test_get_uses_official_path_and_app_token(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"localeSettings": {"revision": "1"}})

        args = SimpleNamespace()
        ctx = self._ctx()
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = multilingual_locale_settings.cmd_multilingual_locale_settings_get(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertEqual(payload["method"], "multilingual-locale-settings.get")
        self.assertEqual(payload["request"]["path"], "/locale-settings/v2/settings")
        call = mock_client.return_value.request.call_args
        self.assertEqual(call.kwargs["method"], "GET")
        self.assertEqual(call.kwargs["headers"]["Authorization"], "site-token")
        self.assertNotIn("wix-account-id", call.kwargs["headers"])

    def test_set_mode_enable_dry_run_does_not_require_ack(self) -> None:
        args = SimpleNamespace(enabled="true")
        ctx = self._ctx()
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = multilingual_locale_settings.cmd_multilingual_locale_settings_set_mode(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["request"]["path"], "/locale-settings/v2/settings/mode")
        self.assertEqual(payload["plan"]["request"]["body"], {"multilingualModeEnabled": True})
        self.assertNotIn("apply requires --ack-irreversible", payload["plan"]["preconditions"])

    def test_set_mode_disable_requires_ack_for_apply(self) -> None:
        args = SimpleNamespace(enabled="false")
        ctx = self._ctx(apply=True, yes=True, ack_irreversible=False)
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = multilingual_locale_settings.cmd_multilingual_locale_settings_set_mode(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertIn("apply requires --ack-irreversible", payload["plan"]["preconditions"])
        self.assertIn("translated-content-removal", payload["plan"]["risk_reasons"])

    @patch("wix_safe_agent_cli.commands.multilingual_locale_settings.HttpClient")
    def test_set_mode_disable_apply_with_ack(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse(
            {"localeSettings": {"revision": "2", "multilingualModeEnabled": False}}
        )

        args = SimpleNamespace(enabled="false")
        ctx = self._ctx(apply=True, yes=True, ack_irreversible=True)
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = multilingual_locale_settings.cmd_multilingual_locale_settings_set_mode(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertFalse(payload["dry_run"])
        call = mock_client.return_value.request.call_args
        self.assertEqual(call.kwargs["method"], "POST")
        self.assertTrue(str(call.kwargs["url"]).endswith("/locale-settings/v2/settings/mode"))
        self.assertEqual(call.kwargs["json_body"], {"multilingualModeEnabled": False})

    def test_update_requires_revision(self) -> None:
        args = SimpleNamespace(locale_settings_json='{"autoSwitch":true}')
        ctx = self._ctx()
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = multilingual_locale_settings.cmd_multilingual_locale_settings_update(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertIn("revision", payload["error"])

    def test_update_rejects_mode_change(self) -> None:
        args = SimpleNamespace(locale_settings_json='{"revision":"1","multilingualModeEnabled":true}')
        ctx = self._ctx()
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = multilingual_locale_settings.cmd_multilingual_locale_settings_update(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertIn("set-mode", payload["error"])

    @patch("wix_safe_agent_cli.commands.multilingual_locale_settings.HttpClient")
    def test_update_apply_uses_patch_body(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"localeSettings": {"revision": "2"}})

        args = SimpleNamespace(locale_settings_json='{"revision":"1","autoSwitch":true}')
        ctx = self._ctx(apply=True, yes=True)
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = multilingual_locale_settings.cmd_multilingual_locale_settings_update(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertFalse(payload["dry_run"])
        call = mock_client.return_value.request.call_args
        self.assertEqual(call.kwargs["method"], "PATCH")
        self.assertEqual(call.kwargs["json_body"], {"localeSettings": {"revision": "1", "autoSwitch": True}})


if __name__ == "__main__":
    unittest.main()

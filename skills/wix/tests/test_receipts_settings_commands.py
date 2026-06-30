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
from wix_safe_agent_cli.commands import receipts_settings
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = (action, payload)


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestReceiptsSettingsCommands(unittest.TestCase):
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
            "command_str": "wix-safe-agent-cli receipts-settings",
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

    def test_parser_recognizes_receipts_settings_commands(self) -> None:
        parser = build_parser()
        cases = [
            ["receipts-settings", "get"],
            ["receipts-settings", "update", "--settings-json", '{"revision":"1","numbering":{"prefix":"R-"}}'],
        ]
        for argv in cases:
            with self.subTest(argv=argv):
                args = parser.parse_args(argv)
                self.assertTrue(callable(args.func))

    @patch("wix_safe_agent_cli.commands.receipts_settings.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.receipts_settings.HttpClient")
    def test_get_uses_official_path(self, mock_client, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"receiptsSettings": {"revision": "1"}})

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = receipts_settings.cmd_receipts_settings_get(SimpleNamespace(), self._ctx())

        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertEqual(payload["request"]["method"], "GET")
        self.assertEqual(payload["request"]["path"], "/receipts/v1/receipts-settings")
        self.assertEqual(mock_auth.call_args.kwargs["command_family"], "receipts-settings")

    @patch("wix_safe_agent_cli.commands.receipts_settings.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.receipts_settings.HttpClient")
    def test_update_emits_reviewed_plan_on_official_path(self, mock_client, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = receipts_settings.cmd_receipts_settings_update(
                SimpleNamespace(settings_json='{"revision":"1","numbering":{"prefix":"R-"}}'),
                self._ctx(),
            )

        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["method"], "receiptsSettings.updateReceiptsSettings")
        self.assertEqual(payload["plan"]["request"]["method"], "PATCH")
        self.assertEqual(payload["plan"]["request"]["path"], "/receipts/v1/receipts-settings")
        self.assertEqual(payload["plan"]["selector"], {"scope": "site-receipts-settings", "revision": "1"})
        self.assertIn("requires-current-revision", payload["plan"]["risk_reasons"])
        self.assertNotIn("apply also requires --ack-irreversible", payload["plan"]["preconditions"])
        mock_client.return_value.request.assert_not_called()

    @patch("wix_safe_agent_cli.commands.receipts_settings.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.receipts_settings.HttpClient")
    def test_update_apply_requires_matching_plan_and_calls_provider(self, mock_client, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"receiptsSettings": {"revision": "2"}})

        with tempfile.TemporaryDirectory() as tmp:
            plan_path = Path(tmp) / "plan.json"
            plan = {
                "method": "receiptsSettings.updateReceiptsSettings",
                "baseline": {
                    "env_fingerprint": "https://www.wixapis.com",
                    "selector": {"scope": "site-receipts-settings", "revision": "1"},
                },
                "proposed_changes": [{"operation": "update-receipts-settings"}],
            }
            plan_path.write_text(json.dumps(plan), encoding="utf-8")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = receipts_settings.cmd_receipts_settings_update(
                    SimpleNamespace(settings_json='{"revision":"1","numbering":{"prefix":"R-"}}'),
                    self._ctx(apply=True, yes=True, plan_in=str(plan_path)),
                )

        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertFalse(payload["dry_run"])
        self.assertEqual(payload["receipt"]["request"]["method"], "PATCH")
        self.assertEqual(payload["receipt"]["request"]["path"], "/receipts/v1/receipts-settings")
        mock_client.return_value.request.assert_called_once()

    @patch("wix_safe_agent_cli.commands.receipts_settings.HttpClient")
    def test_update_rejects_missing_revision_before_request(self, mock_client) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = receipts_settings.cmd_receipts_settings_update(
                SimpleNamespace(settings_json='{"numbering":{"prefix":"R-"}}'),
                self._ctx(),
            )

        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 1)
        self.assertEqual(payload["error_type"], "ValidationError")
        mock_client.return_value.request.assert_not_called()

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
from wix_safe_agent_cli.commands import receipt_presets
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = (action, payload)


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestReceiptPresetsCommands(unittest.TestCase):
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
            "command_str": "wix-safe-agent-cli receipt-presets",
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

    def test_parser_recognizes_receipt_presets_commands(self) -> None:
        parser = build_parser()
        cases = [
            ["receipt-presets", "create", "--receipt-preset-json", '{"name":"Default"}'],
            ["receipt-presets", "get", "--receipt-preset-id", "rp-1"],
            ["receipt-presets", "update", "--receipt-preset-json", '{"id":"rp-1","revision":"1","name":"Default"}'],
            ["receipt-presets", "delete", "--receipt-preset-id", "rp-1"],
            ["receipt-presets", "list"],
            ["receipt-presets", "get-default"],
            ["receipt-presets", "set-default", "--receipt-preset-id", "rp-1"],
            ["receipt-presets", "update-extended-fields", "--receipt-preset-id", "rp-1", "--extended-fields-json", '{"extendedFields":{"namespaces":{}}}'],
        ]
        for argv in cases:
            with self.subTest(argv=argv):
                args = parser.parse_args(argv)
                self.assertTrue(callable(args.func))

    @patch("wix_safe_agent_cli.commands.receipt_presets.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.receipt_presets.HttpClient")
    def test_reads_use_official_paths(self, mock_client, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"receiptPresets": []})
        cases = [
            (receipt_presets.cmd_receipt_presets_get, SimpleNamespace(receipt_preset_id="rp-1"), "/receipts/v1/receipt-presets/rp-1"),
            (receipt_presets.cmd_receipt_presets_list, SimpleNamespace(), "/receipts/v1/receipt-presets"),
            (receipt_presets.cmd_receipt_presets_get_default, SimpleNamespace(), "/receipts/v1/receipt-presets/default"),
        ]
        for func, args, path in cases:
            with self.subTest(path=path):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = func(args, self._ctx())
                payload = json.loads(buf.getvalue())
                self.assertEqual(rc, 0)
                self.assertEqual(payload["request"]["method"], "GET")
                self.assertEqual(payload["request"]["path"], path)
        self.assertEqual(mock_auth.call_args.kwargs["command_family"], "receipt-presets")

    @patch("wix_safe_agent_cli.commands.receipt_presets.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.receipt_presets.HttpClient")
    def test_writes_emit_reviewed_plans_on_official_paths(self, mock_client, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        cases = [
            (
                receipt_presets.cmd_receipt_presets_create,
                SimpleNamespace(receipt_preset_json='{"name":"Default"}'),
                "receiptPresets.createReceiptPreset",
                "POST",
                "/receipts/v1/receipt-presets",
                False,
            ),
            (
                receipt_presets.cmd_receipt_presets_update,
                SimpleNamespace(receipt_preset_json='{"id":"rp-1","revision":"1","name":"Default"}'),
                "receiptPresets.updateReceiptPreset",
                "PATCH",
                "/receipts/v1/receipt-presets/rp-1",
                False,
            ),
            (
                receipt_presets.cmd_receipt_presets_delete,
                SimpleNamespace(receipt_preset_id="rp-1"),
                "receiptPresets.deleteReceiptPreset",
                "DELETE",
                "/receipts/v1/receipt-presets/rp-1",
                True,
            ),
            (
                receipt_presets.cmd_receipt_presets_set_default,
                SimpleNamespace(receipt_preset_id="rp-1"),
                "receiptPresets.setDefaultReceiptPreset",
                "POST",
                "/receipts/v1/receipt-presets/default/rp-1",
                False,
            ),
            (
                receipt_presets.cmd_receipt_presets_update_extended_fields,
                SimpleNamespace(receipt_preset_id="rp-1", extended_fields_json='{"extendedFields":{"namespaces":{}}}'),
                "receiptPresets.updateExtendedFields",
                "POST",
                "/receipts/v1/receipt-presets/rp-1/update-extended-fields",
                False,
            ),
        ]
        for func, args, method_name, http_method, path, requires_ack in cases:
            with self.subTest(method_name=method_name):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = func(args, self._ctx())
                payload = json.loads(buf.getvalue())
                self.assertEqual(rc, 0)
                self.assertTrue(payload["dry_run"])
                self.assertEqual(payload["plan"]["method"], method_name)
                self.assertEqual(payload["plan"]["request"]["method"], http_method)
                self.assertEqual(payload["plan"]["request"]["path"], path)
                if requires_ack:
                    self.assertIn("apply also requires --ack-irreversible", payload["plan"]["preconditions"])
                else:
                    self.assertNotIn("apply also requires --ack-irreversible", payload["plan"]["preconditions"])
        mock_client.return_value.request.assert_not_called()

    @patch("wix_safe_agent_cli.commands.receipt_presets.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.receipt_presets.HttpClient")
    def test_apply_requires_matching_plan_and_calls_provider(self, mock_client, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"receiptPreset": {"id": "rp-1"}})
        with tempfile.TemporaryDirectory() as tmp:
            plan_path = Path(tmp) / "plan.json"
            selector = {"receiptPresetId": "rp-1"}
            plan = {
                "method": "receiptPresets.setDefaultReceiptPreset",
                "baseline": {"env_fingerprint": "https://www.wixapis.com", "selector": selector},
                "proposed_changes": [{"operation": "set-default-receipt-preset"}],
            }
            plan_path.write_text(json.dumps(plan), encoding="utf-8")
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = receipt_presets.cmd_receipt_presets_set_default(
                    SimpleNamespace(receipt_preset_id="rp-1"),
                    self._ctx(apply=True, yes=True, plan_in=str(plan_path)),
                )
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertFalse(payload["dry_run"])
        self.assertEqual(payload["receipt"]["request"]["path"], "/receipts/v1/receipt-presets/default/rp-1")
        mock_client.return_value.request.assert_called_once()

    @patch("wix_safe_agent_cli.commands.receipt_presets.HttpClient")
    def test_update_requires_revision_before_request(self, mock_client) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = receipt_presets.cmd_receipt_presets_update(
                SimpleNamespace(receipt_preset_json='{"id":"rp-1","name":"Default"}'),
                self._ctx(),
            )
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 1)
        self.assertEqual(payload["error_type"], "ValidationError")
        mock_client.return_value.request.assert_not_called()

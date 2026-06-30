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
from wix_safe_agent_cli.commands import receipts
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = (action, payload)


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestReceiptsCommands(unittest.TestCase):
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
            "command_str": "wix-safe-agent-cli receipts",
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

    def test_parser_recognizes_receipts_commands(self) -> None:
        parser = build_parser()
        cases = [
            ["receipts", "create", "--receipt-json", '{"transactionId":"txn-1"}'],
            ["receipts", "get", "--receipt-id", "r-1"],
            ["receipts", "query", "--query-json", "{}"],
            ["receipts", "get-latest-number", "--prefix", "INV"],
            ["receipts", "regenerate-document", "--receipt-id", "r-1"],
            ["receipts", "send-email", "--receipt-id", "r-1", "--send-json", "{}"],
            ["receipts", "update-extended-fields", "--receipt-id", "r-1", "--extended-fields-json", '{"extendedFields":{"namespaces":{}}}'],
        ]
        for argv in cases:
            with self.subTest(argv=argv):
                args = parser.parse_args(argv)
                self.assertTrue(callable(args.func))

    @patch("wix_safe_agent_cli.commands.receipts.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.receipts.HttpClient")
    def test_reads_use_official_paths(self, mock_client, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"receipts": []})
        cases = [
            (
                receipts.cmd_receipts_get,
                SimpleNamespace(receipt_id="r-1"),
                "GET",
                "/receipts/v1/receipts/r-1",
                None,
                None,
            ),
            (
                receipts.cmd_receipts_query,
                SimpleNamespace(query_json='{"filter":{"transactionId":"txn-1"}}'),
                "POST",
                "/receipts/v1/receipts/query",
                {"filter": {"transactionId": "txn-1"}},
                None,
            ),
            (
                receipts.cmd_receipts_get_latest_number,
                SimpleNamespace(prefix="INV"),
                "GET",
                "/receipts/v1/receipts/get-latest-number",
                None,
                {"prefix": "INV"},
            ),
        ]
        for func, args, http_method, path, body, params in cases:
            with self.subTest(path=path):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = func(args, self._ctx())
                payload = json.loads(buf.getvalue())
                self.assertEqual(rc, 0)
                self.assertEqual(payload["request"]["method"], http_method)
                self.assertEqual(payload["request"]["path"], path)
                if body is None:
                    self.assertNotIn("body", payload["request"])
                else:
                    self.assertEqual(payload["request"]["body"], body)
                if params is None:
                    self.assertNotIn("params", payload["request"])
                else:
                    self.assertEqual(payload["request"]["params"], params)

        self.assertEqual(mock_auth.call_args.kwargs["command_family"], "receipts")

    @patch("wix_safe_agent_cli.commands.receipts.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.receipts.HttpClient")
    def test_writes_emit_reviewed_plans_on_official_paths(self, mock_client, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        cases = [
            (
                receipts.cmd_receipts_create,
                SimpleNamespace(receipt_json='{"transactionId":"txn-1"}'),
                "receipts.createReceipt",
                "POST",
                "/receipts/v1/receipts",
                True,
            ),
            (
                receipts.cmd_receipts_regenerate_document,
                SimpleNamespace(receipt_id="r-1"),
                "receipts.regenerateReceiptDocument",
                "POST",
                "/receipts/v1/receipts/r-1/regenerate-receipt-document",
                False,
            ),
            (
                receipts.cmd_receipts_send_email,
                SimpleNamespace(receipt_id="r-1", send_json="{}"),
                "receipts.sendReceiptEmail",
                "POST",
                "/receipts/v1/receipts/r-1/send-email",
                True,
            ),
            (
                receipts.cmd_receipts_update_extended_fields,
                SimpleNamespace(receipt_id="r-1", extended_fields_json='{"extendedFields":{"namespaces":{}}}'),
                "receipts.updateExtendedFields",
                "POST",
                "/receipts/v1/receipts/r-1/update-extended-fields",
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

    @patch("wix_safe_agent_cli.commands.receipts.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.receipts.HttpClient")
    def test_apply_requires_matching_plan_and_calls_provider(self, mock_client, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"receipt": {"id": "r-1"}})
        with tempfile.TemporaryDirectory() as tmp:
            plan_path = Path(tmp) / "plan.json"
            selector = {"receiptId": "r-1"}
            plan = {
                "method": "receipts.updateExtendedFields",
                "baseline": {"env_fingerprint": "https://www.wixapis.com", "selector": selector},
                "proposed_changes": [{"operation": "update-receipt-extended-fields"}],
            }
            plan_path.write_text(json.dumps(plan), encoding="utf-8")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = receipts.cmd_receipts_update_extended_fields(
                    SimpleNamespace(receipt_id="r-1", extended_fields_json='{"extendedFields":{"namespaces":{}}}'),
                    self._ctx(apply=True, yes=True, plan_in=str(plan_path)),
                )

        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertFalse(payload["dry_run"])
        self.assertEqual(payload["receipt"]["request"]["method"], "POST")
        self.assertEqual(payload["receipt"]["request"]["path"], "/receipts/v1/receipts/r-1/update-extended-fields")
        mock_client.return_value.request.assert_called_once()

    @patch("wix_safe_agent_cli.commands.receipts.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.receipts.HttpClient")
    def test_send_email_apply_refuses_without_ack_irreversible(self, mock_client, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        with tempfile.TemporaryDirectory() as tmp:
            plan_path = Path(tmp) / "plan.json"
            plan = {
                "method": "receipts.sendReceiptEmail",
                "baseline": {"env_fingerprint": "https://www.wixapis.com", "selector": {"receiptId": "r-1"}},
            }
            plan_path.write_text(json.dumps(plan), encoding="utf-8")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = receipts.cmd_receipts_send_email(
                    SimpleNamespace(receipt_id="r-1", send_json="{}"),
                    self._ctx(apply=True, yes=True, plan_in=str(plan_path), ack_irreversible=False),
                )

        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertIn("apply also requires --ack-irreversible", payload["plan"]["preconditions"])
        mock_client.return_value.request.assert_not_called()

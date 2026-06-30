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
from wix_safe_agent_cli.commands import payment_link_payments
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = (action, payload)


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestPaymentLinkPaymentsCommands(unittest.TestCase):
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
            "command_str": "wix-safe-agent-cli payment-link-payments",
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

    def test_parser_recognizes_payment_link_payments_commands(self) -> None:
        parser = build_parser()
        cases = [
            ["payment-link-payments", "query", "--query-json", "{}"],
            ["payment-link-payments", "search", "--search-json", "{}"],
            ["payment-link-payments", "issue-receipt", "--payment-link-payment-id", "plp-1"],
        ]
        for argv in cases:
            with self.subTest(argv=argv):
                args = parser.parse_args(argv)
                self.assertTrue(callable(args.func))

    @patch("wix_safe_agent_cli.commands.payment_link_payments.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.payment_link_payments.HttpClient")
    def test_reads_use_official_paths(self, mock_client, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"paymentLinkPayments": []})

        cases = [
            (
                payment_link_payments.cmd_payment_link_payments_query,
                SimpleNamespace(query_json='{"filter":{"paymentLinkId":"pl-1"}}'),
                "/payment-links/v1/payment-link-payments/query",
                {"filter": {"paymentLinkId": "pl-1"}},
            ),
            (
                payment_link_payments.cmd_payment_link_payments_search,
                SimpleNamespace(search_json='{"search":{"expression":"buyer@example.com"}}'),
                "/payment-links/v1/payment-link-payments/search",
                {"search": {"expression": "buyer@example.com"}},
            ),
        ]
        for func, args, path, body in cases:
            with self.subTest(path=path):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = func(args, self._ctx())
                payload = json.loads(buf.getvalue())
                self.assertEqual(rc, 0)
                self.assertEqual(payload["request"]["method"], "POST")
                self.assertEqual(payload["request"]["path"], path)
                self.assertEqual(payload["request"]["body"], body)

        self.assertEqual(mock_auth.call_args.kwargs["command_family"], "payment-link-payments")

    @patch("wix_safe_agent_cli.commands.payment_link_payments.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.payment_link_payments.HttpClient")
    def test_issue_receipt_emits_reviewed_plan_on_official_path(self, mock_client, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = payment_link_payments.cmd_payment_link_payments_issue_receipt(
                SimpleNamespace(payment_link_payment_id="plp-1"),
                self._ctx(),
            )

        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["method"], "paymentLinkPayments.issueReceipt")
        self.assertEqual(payload["plan"]["request"]["method"], "POST")
        self.assertEqual(payload["plan"]["request"]["path"], "/payment-links/v1/payment-link-payments/plp-1/issue-receipt")
        self.assertNotIn("body", payload["plan"]["request"])
        self.assertNotIn("apply also requires --ack-irreversible", payload["plan"]["preconditions"])
        mock_client.return_value.request.assert_not_called()

    @patch("wix_safe_agent_cli.commands.payment_link_payments.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.payment_link_payments.HttpClient")
    def test_issue_receipt_apply_requires_matching_plan_and_calls_provider(self, mock_client, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"receipt": {"id": "receipt-1"}})

        with tempfile.TemporaryDirectory() as tmp:
            plan_path = Path(tmp) / "plan.json"
            selector = {"paymentLinkPaymentId": "plp-1"}
            plan = {
                "method": "paymentLinkPayments.issueReceipt",
                "baseline": {"env_fingerprint": "https://www.wixapis.com", "selector": selector},
                "proposed_changes": [{"operation": "issue-payment-link-payment-receipt"}],
            }
            plan_path.write_text(json.dumps(plan), encoding="utf-8")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = payment_link_payments.cmd_payment_link_payments_issue_receipt(
                    SimpleNamespace(payment_link_payment_id="plp-1"),
                    self._ctx(apply=True, yes=True, plan_in=str(plan_path)),
                )

        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertFalse(payload["dry_run"])
        self.assertEqual(payload["receipt"]["request"]["method"], "POST")
        self.assertEqual(payload["receipt"]["request"]["path"], "/payment-links/v1/payment-link-payments/plp-1/issue-receipt")
        self.assertNotIn("body", payload["receipt"]["request"])
        mock_client.return_value.request.assert_called_once()

    @patch("wix_safe_agent_cli.commands.payment_link_payments.HttpClient")
    def test_issue_receipt_requires_payment_id_before_request(self, mock_client) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = payment_link_payments.cmd_payment_link_payments_issue_receipt(
                SimpleNamespace(payment_link_payment_id=""),
                self._ctx(),
            )
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 1)
        self.assertEqual(payload["error_type"], "ValidationError")
        mock_client.return_value.request.assert_not_called()

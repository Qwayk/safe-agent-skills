from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import payments
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


class TestPaymentsParser(unittest.TestCase):
    def test_parser_recognizes_transactions_list_and_is_read_only(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "payments",
                "transactions-list",
                "--from-created",
                "2026-01-01T00:00:00Z",
                "--status",
                "APPROVED",
            ]
        )

        self.assertEqual(args.payments_cmd, "transactions-list")
        self.assertFalse(args.write_capable)
        self.assertIs(args.func, payments.cmd_payments_transactions_list)


class TestPaymentsCommands(unittest.TestCase):
    def _ctx(self, *, verbose: bool = False) -> dict:
        cfg = SimpleNamespace(
            base_url="https://www.wixapis.com",
            timeout_s=30.0,
            app_id=None,
            app_secret=None,
            instance_id=None,
            access_token="token-abc",
            has_official_app_auth=False,
        )
        return {
            "cfg": cfg,
            "env_file": "/tmp/.env",
            "verbose": verbose,
            "out": Output(mode="json"),
            "audit": _DummyAudit(),
        }

    @patch("wix_safe_agent_cli.commands.payments.HttpClient")
    @patch("wix_safe_agent_cli.commands.payments.resolve_auth_mode")
    def test_transactions_list_builds_expected_request(
        self,
        mock_auth: unittest.mock.MagicMock,
        mock_client: unittest.mock.MagicMock,
    ) -> None:
        mock_auth.return_value = {"mode": "access_token", "headers": {"Authorization": "token-abc"}}
        mock_client.return_value.request.return_value = _DummyResponse({"transactions": [{"transactionId": "txn-1"}]})
        args = SimpleNamespace(
            from_created="2026-01-01T00:00:00Z",
            to_created="2026-01-31T23:59:59Z",
            limit=25,
            offset=10,
            order="date:asc",
            status=["APPROVED", "PENDING", "APPROVED"],
            payment_method="CreditCard",
            payment_provider="wixpayments",
            currency="USD",
            from_updated="2026-02-01T00:00:00Z",
            to_updated="2026-02-02T00:00:00Z",
            app_id="app-123",
            include_refunds=True,
            ignore_totals=True,
        )
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = payments.cmd_payments_transactions_list(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["method"], "payments.transactions-list")
        self.assertEqual(payload["request"]["method"], "GET")
        self.assertEqual(payload["request"]["path"], "/payments/v2/transactions")
        self.assertEqual(payload["request"]["params"]["from"], "2026-01-01T00:00:00Z")
        self.assertEqual(payload["request"]["params"]["to"], "2026-01-31T23:59:59Z")
        self.assertEqual(payload["request"]["params"]["limit"], 25)
        self.assertEqual(payload["request"]["params"]["offset"], 10)
        self.assertEqual(payload["request"]["params"]["order"], "date:asc")
        self.assertEqual(payload["request"]["params"]["status"], ["APPROVED", "PENDING"])
        self.assertEqual(payload["request"]["params"]["paymentMethod"], "CreditCard")
        self.assertEqual(payload["request"]["params"]["paymentProvider"], "wixpayments")
        self.assertEqual(payload["request"]["params"]["currency"], "USD")
        self.assertEqual(payload["request"]["params"]["fromUpdated"], "2026-02-01T00:00:00Z")
        self.assertEqual(payload["request"]["params"]["toUpdated"], "2026-02-02T00:00:00Z")
        self.assertEqual(payload["request"]["params"]["appId"], "app-123")
        self.assertTrue(payload["request"]["params"]["includeRefunds"])
        self.assertTrue(payload["request"]["params"]["ignoreTotals"])
        self.assertEqual(payload["response"]["transactions"][0]["transactionId"], "txn-1")

        http_call = mock_client.return_value.request.call_args
        self.assertTrue(str(http_call.kwargs["url"]).endswith("/payments/v2/transactions"))
        self.assertEqual(http_call.kwargs["params"]["limit"], 25)
        self.assertEqual(mock_auth.call_args.kwargs["command_family"], "payments")

    def test_transactions_list_rejects_out_of_range_limit(self) -> None:
        args = SimpleNamespace(
            from_created=None,
            to_created=None,
            limit=1001,
            offset=None,
            order=None,
            status=None,
            payment_method=None,
            payment_provider=None,
            currency=None,
            from_updated=None,
            to_updated=None,
            app_id=None,
            include_refunds=None,
            ignore_totals=None,
        )
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = payments.cmd_payments_transactions_list(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertFalse(payload["ok"])
        self.assertIn("at most 1000", payload["error"])

    def test_transactions_list_rejects_invalid_order(self) -> None:
        args = SimpleNamespace(
            from_created=None,
            to_created=None,
            limit=None,
            offset=None,
            order="created:asc",
            status=None,
            payment_method=None,
            payment_provider=None,
            currency=None,
            from_updated=None,
            to_updated=None,
            app_id=None,
            include_refunds=None,
            ignore_totals=None,
        )
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = payments.cmd_payments_transactions_list(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertFalse(payload["ok"])
        self.assertIn("date:asc or date:desc", payload["error"])

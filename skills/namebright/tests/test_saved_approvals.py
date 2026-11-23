from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch
from urllib.parse import urlsplit

import requests

from namebright_safe_cli.cli import main
from namebright_safe_cli.client import NameBrightClient


class SimulatedNameBright:
    def __init__(self) -> None:
        self.paid_pending = False
        self.order_visible = False
        self.lose_reply = False
        self.move_visible = False
        self.move_sent = False
        self.expiry_changed = False
        self.purchase_status = "AvailableForRenewal"
        self.unit_price: float | None = 17.50
        self.writes: list[tuple[str, str]] = []
        self.reads: list[str] = []

    def request(self, *, method, url, headers, data=None, allow_redirects, **_kwargs):
        assert not allow_redirects
        assert urlsplit(url).hostname == "api.namebright.com"
        path = urlsplit(url).path.lower()
        code = 200
        if path == "/auth/token":
            payload = {"access_token": f"fake-token:{data['client_id']}", "expires_in": 1800}
        elif method == "POST":
            self.writes.append((path, headers["Authorization"]))
            if self.lose_reply:
                raise requests.Timeout()
            if path.endswith("/initiate"):
                self.move_sent = True
                payload = {}
            elif self.paid_pending:
                code = 202
                payload = {"customerOrderNumber": "sample-order", "message": "Paid. Order pending."}
            else:
                code = 201
                payload = {"orderId": 1, "totalPrice": 17.50, "orderItems": []}
        else:
            self.reads.append(path)
            if "/availability/" in path:
                payload = {
                    "domainName": "example.com", "status": self.purchase_status,
                    "unitPrice": self.unit_price, "promotion": {"promotionPrice": 0},
                }
            elif path == "/orders/sample-order":
                if self.order_visible:
                    payload = {"orderId": 1, "totalPrice": 17.50, "orderItems": []}
                else:
                    code = 404
                    payload = {"title": "Order not found"}
            elif path.endswith("/outboundpush/pending"):
                payload = ["example.com"] if self.move_sent and self.move_visible else []
            elif path.endswith("/outboundpush/completed"):
                payload = []
            elif path.endswith("/domains/example.com"):
                expiry = "2028-07-01" if self.expiry_changed and self.writes else "2027-07-01"
                payload = {"domainName": "example.com", "expirationDate": expiry}
            elif path == "/rest/account":
                payload = {"accountBalance": 101}
            else:
                raise AssertionError((method, path))

        response = requests.Response()
        response.url = url
        response.status_code = code
        response._content = json.dumps(payload).encode()
        return response


class SavedApprovalTests(unittest.TestCase):
    renew = ["purchase", "renew", "--domain-name", "example.com", "--years", "1"]

    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.folder = Path(tmp.name)
        self.config = self._settings("original", "one")
        self.plan = self.folder / "plan.json"
        self.receipt = self.folder / "receipt.json"
        self.provider = SimulatedNameBright()

    def _settings(self, filename: str, account: str) -> Path:
        path = self.folder / filename
        path.write_text(f"NAMEBRIGHT_CLIENT_ID={account}\nNAMEBRIGHT_CLIENT_SECRET=fake-test-secret\n")
        return path

    def _cli(self, *args: str, config: Path | None = None) -> tuple[int, dict]:
        out = io.StringIO()
        with patch.object(NameBrightClient, "_throttle"), redirect_stdout(out):
            code = main(
                ["--output", "json", "--env-file", str(config or self.config), "--no-artifacts", *args],
                client_factory=lambda **kwargs: NameBrightClient(transport=self.provider, **kwargs),
            )
        return code, json.loads(out.getvalue())

    def _preview(self, operations: list[str]) -> dict:
        code, result = self._cli("--plan-out", str(self.plan), *operations)
        self.assertEqual(code, 0)
        return result["plan"]

    def _apply(self, *, config: Path | None = None, receipt: Path | None = None) -> tuple[int, dict]:
        return self._cli(
            "--apply", "--yes", "--ack-spend", "--plan-in", str(self.plan),
            "--receipt-out", str(receipt or self.receipt), *self.renew, config=config,
        )

    def test_account_and_input_paths_are_checked_before_write(self) -> None:
        self._preview(self.renew)
        original = self.plan.read_bytes()
        other = self._settings("changed", "two")
        _, changed = self._apply(config=other)
        self.assertTrue(changed["refused"])
        for path in (self.plan, self.config):
            _, result = self._apply(receipt=path)
            self.assertTrue(result["refused"])
        self.assertEqual(self.plan.read_bytes(), original)
        self.assertEqual(self.provider.writes, [])

        self.provider.expiry_changed = True
        _, accepted = self._apply()
        self.assertTrue(accepted["receipt"]["verification"]["ok"])
        self.assertEqual(self.provider.writes, [("/rest/purchase/renew", "Bearer fake-token:one")])

    def test_current_registration_status_and_renewal_prices(self) -> None:
        self.provider.purchase_status = "AvailableForRegistration"
        quoted = self._preview(["purchase", "register", "--domain-name", "example.com", "--years", "1"])
        self.assertEqual(quoted["purchase_quote"]["quoted_total_price"], "17.5")
        self.provider.purchase_status = "AvailableForRenewal"
        self.provider.unit_price = None
        unpriced = self._preview(self.renew)
        self.assertNotIn("purchase_quote", unpriced)
        _, result = self._apply()
        self.assertTrue(result["refused"])
        self.assertIn("checkout", result["reasons"][0])
        self.provider.unit_price = 17.50
        self._preview(self.renew)
        self.provider.unit_price = 18.50
        _, changed = self._apply()
        self.assertTrue(changed["refused"])
        self.assertEqual(self.provider.writes, [])

    def test_paid_pending_saves_order_and_never_sends_again(self) -> None:
        self.provider.paid_pending = True
        self._preview(self.renew)
        code, pending = self._apply()
        self.assertEqual(code, 0)
        self.assertFalse(pending["applied"])
        self.assertEqual(pending["outcome"], "paid_pending")
        self.assertFalse(pending["receipt"]["verification"]["ok"])
        self.assertEqual(json.loads(self.receipt.read_text())["order_number"], "sample-order")
        self.assertIn("/orders/sample-order", self.provider.reads)
        self.assertEqual(self.receipt.stat().st_mode & 0o777, 0o600)

        _, repeated = self._apply(receipt=self.folder / "another.json")
        self.assertTrue(repeated["refused"])
        self.provider.order_visible = True
        code, order = self._cli("orders", "get", "--customer-order-number", "sample-order")
        self.assertEqual(code, 0)
        self.assertEqual(order["response"]["orderId"], 1)
        self.assertEqual(len(self.provider.writes), 1)

    def test_unclear_attempt_saves_receipt_and_blocks_repeat(self) -> None:
        self.provider.lose_reply = True
        self._preview(self.renew)
        code, unclear = self._apply()
        self.assertEqual(code, 1)
        self.assertEqual(unclear["outcome"], "unknown")
        self.assertEqual(json.loads(self.receipt.read_text())["outcome"], "unknown")
        _, repeat = self._apply(receipt=self.folder / "retry.json")
        self.assertTrue(repeat["refused"])
        self.assertEqual(len(self.provider.writes), 1)

    def test_a_read_of_an_empty_move_list_is_not_confirmation(self) -> None:
        action = ["outbound-push", "initiate-path", "--domain", "example.com", "--email-address", "recipient@example.com"]
        apply = [
            "--apply", "--yes", "--plan-in", str(self.plan), "--ack-high-risk", "--ack-ownership",
            "--ack-no-snapshot", "--ack-irreversible", "--ack-external-message",
        ]
        self._preview(action)
        _, unconfirmed = self._cli("--receipt-out", str(self.receipt), *apply, *action)
        self.assertFalse(unconfirmed["receipt"]["verification"]["ok"])
        self.provider.move_visible = True
        self.provider.move_sent = False
        self._preview(action)
        _, pending = self._cli("--receipt-out", str(self.folder / "second-move.json"), *apply, *action)
        self.assertTrue(pending["receipt"]["verification"]["ok"])
        self.assertEqual(pending["receipt"]["verification"]["state"], "pending")

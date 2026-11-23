from __future__ import annotations

import io
import json
import stat
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from typing import Any
from unittest.mock import patch
from urllib.parse import urlsplit

from spaceship_safe_agent_cli.cli import main
from spaceship_safe_agent_cli.http import HttpResponse


class SimulatedSpaceship:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str, str]] = []
        self.price: str | None = "17.50"
        self.price_years = 1
        self.currency = "USD"
        self.lose_reply = False
        self.state_code = 404
        self.return_domain = "example.com"
        self.return_price = "200.00"
        self.safe_pay_status = "pendingSellerConfirm"
        self.safe_pay: dict[str, Any] = {}

    def request(self, method, url, *, headers, params=None, json_body=None):
        parts = urlsplit(url)
        assert parts.hostname == "spaceship.dev"
        path = parts.path
        self.calls.append((method, path, headers["X-API-Key"]))
        status = 200
        response_headers = {}
        body: Any
        if method == "POST":
            if self.lose_reply:
                raise RuntimeError("Simulated timeout")
            if "/safepay-transactions" in path:
                status = 201
                self.safe_pay = {
                    **json_body,
                    "transactionId": "59c792a5-ff2c-4093-be04-e5d6f00e12bd",
                    "status": self.safe_pay_status,
                }
                body = self.safe_pay
            else:
                status, body = 202, {}
                response_headers = {"spaceship-async-operationid": "example-operation-id"}
        elif path.endswith("/pricing"):
            prices = {}
            if self.price is not None:
                prices = {
                    action: [{
                        "period": {"value": self.price_years, "unit": "y"},
                        "priceInDefaultCurrency": {
                            "finalPrice": {"amount": self.price, "currency": self.currency},
                            "regularPrice": {"amount": "20.00", "currency": self.currency},
                        },
                    }]
                    for action in ("register", "renew", "transfer")
                }
            body = {"domain": "example.com", "priceClass": "standard", "prices": prices}
        elif path.endswith("/transfer") or path.endswith("/sellerhub/domains/example.com"):
            status = self.state_code
            body = {"status": "existing"} if status == 200 else {}
        elif "/safepay-transactions/" in path:
            body = {
                **self.safe_pay, "domainName": self.return_domain,
                "basePrice": {"amount": self.return_price, "currency": "USD"},
            }
        elif path.endswith("/domains/example.com"):
            body = {"name": "example.com", "expirationDate": "2027-08-01T00:00:00Z"}
        else:
            raise AssertionError((method, path))
        return HttpResponse(status, response_headers, json.dumps(body).encode(), url, 1, None, False)


class AccountApprovalTests(unittest.TestCase):
    renew = ["domains", "renew", "example.com"]
    renewal = {"years": 1, "currentExpirationDate": "2027-08-01T00:00:00Z"}

    def setUp(self) -> None:
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.root = Path(folder.name)
        self.env = self._settings("first.env", "fake-first")
        self.plan = self.root / "plan.json"
        self.receipt = self.root / "receipt.json"
        self.body = self.root / "body.json"
        self.provider = SimulatedSpaceship()

    def _settings(self, file: str, key: str) -> Path:
        path = self.root / file
        path.write_text(f"SPACESHIP_API_KEY={key}\nSPACESHIP_API_SECRET=test-only-secret\n")
        return path

    def _run(self, *args: str, settings: Path | None = None) -> tuple[int, dict]:
        output = io.StringIO()
        with patch("spaceship_safe_agent_cli.cli.HttpClient", return_value=self.provider), redirect_stdout(output):
            rc = main(["--output", "json", "--no-artifacts", "--env-file", str(settings or self.env), *args])
        return rc, json.loads(output.getvalue())

    def _preview(self, command: list[str], body: dict[str, Any]) -> dict:
        self.body.write_text(json.dumps(body))
        rc, response = self._run("--plan-out", str(self.plan), *command, "--body-file", str(self.body))
        self.assertEqual(rc, 0, response)
        return response

    def _apply(
        self, plan: dict[str, Any], command: list[str], *,
        settings: Path | None = None, receipt: Path | None = None,
    ) -> tuple[int, dict]:
        return self._run(
            "--apply", "--yes", "--plan-in", str(self.plan), "--receipt-out", str(receipt or self.receipt),
            *("--" + name for name in plan["required_acknowledgements"]), *command, "--body-file", str(self.body),
            settings=settings,
        )

    def _writes(self) -> list[tuple[str, str, str]]:
        return [call for call in self.provider.calls if call[0] == "POST"]

    def test_plan_checks_account_and_keeps_input_paths(self) -> None:
        plan = self._preview(self.renew, self.renewal)
        self.assertEqual(stat.S_IMODE(self.plan.stat().st_mode), 0o600)
        self.assertEqual(plan["financial_recheck"]["price_quote"]["price"], {"amount": "17.5", "currency": "USD"})
        other = self._settings("second.env", "fake-second")
        original = self.plan.read_bytes()
        _, wrong = self._apply(plan, self.renew, settings=other)
        self.assertTrue(wrong["refused"])
        for input_file in (self.body, self.env, self.plan):
            _, unsafe = self._apply(plan, self.renew, receipt=input_file)
            self.assertTrue(unsafe["refused"])
        self.assertEqual(self.plan.read_bytes(), original)
        self.assertEqual(self._writes(), [])

    def test_one_attempt_and_the_async_id_survive_a_repeat(self) -> None:
        plan = self._preview(self.renew, self.renewal)
        code, accepted = self._apply(plan, self.renew)
        self.assertEqual(code, 0, accepted)
        self.assertEqual(accepted["verification_status"], "accepted_not_completed")
        self.assertEqual(json.loads(self.receipt.read_text())["transport"]["async_operation_id"], "example-operation-id")
        _, repeated = self._apply(plan, self.renew, receipt=self.root / "second.json")
        self.assertTrue(repeated["refused"])
        self.assertEqual(len(self._writes()), 1)

    def test_lost_reply_has_a_saved_unknown_attempt(self) -> None:
        self.provider.lose_reply = True
        plan = self._preview(self.renew, self.renewal)
        code, uncertain = self._apply(plan, self.renew)
        self.assertEqual(code, 1)
        self.assertEqual(uncertain["status_label"], "unknown")
        self.assertEqual(json.loads(self.receipt.read_text())["verification"]["status"], "unknown")
        _, repeated = self._apply(plan, self.renew, receipt=self.root / "second.json")
        self.assertTrue(repeated["refused"])
        self.assertEqual(len(self._writes()), 1)

    def test_changed_and_missing_prices_refuse_before_writing(self) -> None:
        plan = self._preview(self.renew, self.renewal)
        self.provider.currency = "EUR"
        _, changed = self._apply(plan, self.renew)
        self.assertTrue(changed["refused"])
        self.assertIn("price or currency", changed["reasons"][0])
        self.provider.price_years = 2
        plan = self._preview(self.renew, self.renewal)
        self.assertFalse(plan["apply_ready"])
        _, missing = self._apply(plan, self.renew, receipt=self.root / "unpriced.json")
        self.assertTrue(missing["refused"])
        self.assertEqual(self._writes(), [])

    def test_expected_absence_can_apply_but_a_changed_state_requires_review(self) -> None:
        command = ["domains", "transfer", "request", "example.com"]
        plan = self._preview(command, {"autoRenew": False, "authCode": "test-only-code"})
        self.assertIn("ack-no-snapshot", plan["required_acknowledgements"])
        self.provider.state_code = 200
        _, changed = self._apply(plan, command)
        self.assertTrue(changed["refused"])
        self.assertEqual(self._writes(), [])
        self.provider.state_code = 404
        _, accepted = self._apply(plan, command, receipt=self.root / "transfer.json")
        self.assertEqual(accepted["verification_status"], "accepted_not_completed")
        self.assertEqual(len(self._writes()), 1)

    def test_transfer_can_use_billing_and_price_access_without_transfer_read_access(self) -> None:
        command = ["domains", "transfer", "request", "example.com"]
        self.provider.state_code = 403
        plan = self._preview(command, {"autoRenew": False, "authCode": "test-only-code"})
        self.assertEqual(plan["snapshot"]["preflight"]["payload_redacted"], {"state": "read_not_allowed"})
        self.assertIn("ack-no-snapshot", plan["required_acknowledgements"])
        code, accepted = self._apply(plan, command)
        self.assertEqual(code, 0, accepted)
        self.assertEqual(accepted["verification_status"], "accepted_not_completed")
        self.assertEqual(len(self._writes()), 1)

    def test_safepay_confirms_matched_terms_and_identifies_pending_party(self) -> None:
        command = ["sellerhub", "safepay", "create"]
        body = {
            "domainName": "example.com", "type": "buyNow", "initiatedBy": "buyer",
            "basePrice": {"amount": "200.00", "currency": "USD"},
            "feePercentageShare": {"seller": 50, "buyer": 50},
            "sellerEmail": "seller@example.com", "paymentMethod": "creditCard",
        }
        plan = self._preview(command, body)
        _, pending = self._apply(plan, command)
        self.assertEqual(pending["status_label"], "transaction_created")
        self.assertEqual(pending["verification"]["transaction_status"], "pendingSellerConfirm")
        self.assertEqual(pending["verification_status"], "verified")
        self.assertNotIn("seller@example.com", json.dumps(pending))
        for field, value in (("return_domain", "another.example"), ("return_price", "201.00")):
            with self.subTest(mismatch=field), patch.object(self.provider, field, value):
                plan = self._preview(command, body)
                _, uncertain = self._apply(plan, command, receipt=self.root / f"{field}.json")
                self.assertEqual(uncertain["verification_status"], "unverified")
                self.assertEqual(uncertain["verification"]["reason"], "safepay_terms_mismatch")

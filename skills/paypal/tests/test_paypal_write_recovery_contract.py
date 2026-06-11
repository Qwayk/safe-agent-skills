from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from typing import Any
from unittest.mock import patch

from paypal_safe_agent_cli.cli import main

def _assert_no_recovery_contract(self, contract: dict[str, Any]) -> None:
    self.assertFalse(contract["automatic_rollback"])
    self.assertEqual(contract["snapshots"], [])
    self.assertEqual(contract["backups"], [])
    self.assertIsNone(contract["rollback_plan"])
    self.assertEqual(contract["verification_mode"], "best-effort")


class FakeHttpResponse:
    def __init__(self, status: int, payload: dict[str, Any] | list[Any]) -> None:
        self.status = status
        self._payload = payload
        self.body = json.dumps(payload).encode("utf-8")

    def json(self) -> Any:
        return self._payload

    def text(self) -> str:
        return json.dumps(self._payload)


class FakeHttpClient:
    responses: list[FakeHttpResponse] = []
    requests: list[tuple[str, str]] = []

    def __init__(self, *, timeout_s: float, verbose: bool, user_agent: str) -> None:
        _ = timeout_s, verbose, user_agent

    def request(self, method: str, url: str, **_: Any) -> FakeHttpResponse:
        FakeHttpClient.requests.append((method, url))
        if not FakeHttpClient.responses:
            raise AssertionError(f"Unexpected HTTP request: {method} {url}")
        return FakeHttpClient.responses.pop(0)


class TestPayPalWriteRecoveryContract(unittest.TestCase):
    def test_dry_run_write_plan_has_no_recovery_contract(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env = root / ".env"
            body = root / "body.json"
            env.write_text(
                "\n".join(
                    [
                        "PAYPAL_ENVIRONMENT=sandbox",
                        "PAYPAL_CLIENT_ID=test-client",
                        "PAYPAL_CLIENT_SECRET=test-secret",
                        "PAYPAL_TIMEOUT_S=30",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            body.write_text("{}", encoding="utf-8")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env),
                        "catalog-products",
                        "create",
                        "--body-file",
                        str(body),
                    ]
                )

            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])
            self.assertEqual(payload["method"], "POST")
            self.assertTrue(payload["plan"]["before_state"]["required"])
            self.assertFalse(payload["plan"]["before_state"]["supported"])
            self.assertEqual(payload["plan"]["verification_plan"]["type"], "best_effort_after_apply")
            _assert_no_recovery_contract(self, payload["plan"]["recovery"])

    def test_apply_write_refuses_before_auth_or_http_without_before_state(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env = root / ".env"
            body = root / "body.json"
            env.write_text(
                "\n".join(
                    [
                        "PAYPAL_ENVIRONMENT=sandbox",
                        "PAYPAL_CLIENT_ID=test-client",
                        "PAYPAL_CLIENT_SECRET=test-secret",
                        "PAYPAL_TIMEOUT_S=30",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            body.write_text("{}", encoding="utf-8")

            FakeHttpClient.requests = []
            receipt_out = root / "receipt.json"

            with patch("paypal_safe_agent_cli.commands.paypal.HttpClient", FakeHttpClient), patch(
                "paypal_safe_agent_cli.commands.paypal.resolve_access_token",
            ) as mock_resolve:
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = main(
                        [
                            "--env-file",
                            str(env),
                            "--apply",
                            "--receipt-out",
                            str(receipt_out),
                            "catalog-products",
                            "create",
                            "--body-file",
                            str(body),
                        ]
                    )

            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            self.assertIn("before-state snapshot", " ".join(payload["reasons"]))
            self.assertNotIn("receipt", payload)
            self.assertFalse(receipt_out.exists())
            self.assertFalse(mock_resolve.called)
            self.assertEqual(FakeHttpClient.requests, [])

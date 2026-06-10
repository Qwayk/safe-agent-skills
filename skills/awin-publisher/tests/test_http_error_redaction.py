from __future__ import annotations

import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from typing import Any
from unittest.mock import patch

import requests

from awin_publisher_safe_agent_cli.cli import main


def _error_response(
    method: str,
    url: str,
    params: dict[str, Any],
    body: str,
    *,
    status: int = 401,
    content_type: str = "text/plain",
) -> requests.Response:
    response = requests.Response()
    response.status_code = status
    response._content = body.encode("utf-8")
    response.headers["content-type"] = content_type
    response.url = requests.Request(method=method, url=url, params=params).prepare().url or url
    return response


def _write_env(root: str, *lines: str) -> str:
    env_file = os.path.join(root, ".env")
    with open(env_file, "w", encoding="utf-8") as fh:
        for line in lines:
            fh.write(line.rstrip() + "\n")
    return env_file


class TestHttpErrorRedaction(unittest.TestCase):
    def test_auth_check_http_error_redacts_awin_api_token_in_stdout_stderr_and_audit(self) -> None:
        token = "TOKEN_SECRET_123"
        provider_body = f'{{"error":"bad credentials","echo":"{token}"}}'

        with patch("awin_publisher_safe_agent_cli.http.requests.Session.request") as mocked_request:
            mocked_request.side_effect = (
                lambda method, url, headers=None, params=None, **kwargs: _error_response(
                    method, url, params or {}, provider_body
                )
            )

            with tempfile.TemporaryDirectory() as td:
                env_file = _write_env(td, f"AWIN_API_TOKEN={token}")
                log_path = Path(td) / "audit.jsonl"
                stdout = io.StringIO()
                stderr = io.StringIO()
                with redirect_stdout(stdout), redirect_stderr(stderr):
                    rc = main(
                        [
                            "--output",
                            "json",
                            "--env-file",
                            env_file,
                            "--log-file",
                            str(log_path),
                            "--verbose",
                            "auth",
                            "check",
                        ]
                    )

                out = json.loads(stdout.getvalue())
                combined = stdout.getvalue() + stderr.getvalue() + log_path.read_text(encoding="utf-8")

        self.assertEqual(rc, 1)
        self.assertEqual(out["error_type"], "RuntimeError")
        self.assertIn("HTTP 401", out["error"])
        self.assertIn("response_body=<suppressed", out["error"])
        self.assertNotIn(provider_body, combined)
        self.assertNotIn(token, combined)

    def test_legacy_feed_http_error_redacts_awin_feed_api_key_in_url_and_provider_body(self) -> None:
        feed_key = "FEED_SECRET_456"
        provider_body = f"legacy auth failed for {feed_key}"

        with patch("awin_publisher_safe_agent_cli.http.requests.Session.request") as mocked_request:
            mocked_request.side_effect = (
                lambda method, url, headers=None, params=None, **kwargs: _error_response(
                    method, url, params or {}, provider_body
                )
            )

            with tempfile.TemporaryDirectory() as td:
                env_file = _write_env(td, f"AWIN_FEED_API_KEY={feed_key}")
                log_path = Path(td) / "audit.jsonl"
                stdout = io.StringIO()
                stderr = io.StringIO()
                with redirect_stdout(stdout), redirect_stderr(stderr):
                    rc = main(
                        [
                            "--output",
                            "json",
                            "--env-file",
                            env_file,
                            "--log-file",
                            str(log_path),
                            "--verbose",
                            "feeds",
                            "legacy-list",
                            "--out",
                            str(Path(td) / "legacy.csv"),
                        ]
                    )

                out = json.loads(stdout.getvalue())
                combined = stdout.getvalue() + stderr.getvalue() + log_path.read_text(encoding="utf-8")

        self.assertEqual(rc, 1)
        self.assertEqual(out["error_type"], "RuntimeError")
        self.assertIn("apikey/<redacted>", combined)
        self.assertNotIn(provider_body, combined)
        self.assertNotIn(feed_key, combined)

    def test_proof_of_purchase_http_error_redacts_awin_pop_key_and_does_not_write_receipt(self) -> None:
        pop_key = "POP_SECRET_789"
        provider_body = f'{{"error":"bad key","x-api-key":"{pop_key}"}}'

        with patch("awin_publisher_safe_agent_cli.http.requests.Session.request") as mocked_request:
            mocked_request.side_effect = (
                lambda method, url, headers=None, params=None, json=None, **kwargs: _error_response(
                    method, url, params or {}, provider_body
                )
            )

            with tempfile.TemporaryDirectory() as td:
                env_file = _write_env(td, f"AWIN_PROOF_OF_PURCHASE_API_KEY={pop_key}")
                orders_path = Path(td) / "orders.json"
                orders_path.write_text(
                    json.dumps(
                        {
                            "orders": [
                                {
                                    "orderReference": "ORD-1",
                                    "amount": 123.45,
                                    "currency": "EUR",
                                    "transactionTime": 1762859931,
                                }
                            ]
                        }
                    ),
                    encoding="utf-8",
                )
                plan_path = Path(td) / "plan.json"
                receipt_path = Path(td) / "receipt.json"

                dry_run_stdout = io.StringIO()
                with redirect_stdout(dry_run_stdout):
                    dry_run_rc = main(
                        [
                            "--output",
                            "json",
                            "--env-file",
                            env_file,
                            "--no-artifacts",
                            "--plan-out",
                            str(plan_path),
                            "proof-of-purchase",
                            "orders",
                            "create",
                            "--publisher-id",
                            "777",
                            "--advertiser-id",
                            "55",
                            "--orders-file",
                            str(orders_path),
                        ]
                    )

                self.assertEqual(dry_run_rc, 0)
                self.assertTrue(plan_path.exists())

                log_path = Path(td) / "audit.jsonl"
                stdout = io.StringIO()
                stderr = io.StringIO()
                with redirect_stdout(stdout), redirect_stderr(stderr):
                    rc = main(
                        [
                            "--output",
                            "json",
                            "--env-file",
                            env_file,
                            "--no-artifacts",
                            "--log-file",
                            str(log_path),
                            "--verbose",
                            "--apply",
                            "--yes",
                            "--plan-in",
                            str(plan_path),
                            "--receipt-out",
                            str(receipt_path),
                            "proof-of-purchase",
                            "orders",
                            "create",
                            "--publisher-id",
                            "777",
                            "--advertiser-id",
                            "55",
                            "--orders-file",
                            str(orders_path),
                        ]
                    )

                out = json.loads(stdout.getvalue())
                combined = stdout.getvalue() + stderr.getvalue() + log_path.read_text(encoding="utf-8")
                receipt_exists = receipt_path.exists()

        self.assertEqual(rc, 1)
        self.assertEqual(out["error_type"], "RuntimeError")
        self.assertFalse(receipt_exists)
        self.assertNotIn(provider_body, combined)
        self.assertNotIn(pop_key, combined)

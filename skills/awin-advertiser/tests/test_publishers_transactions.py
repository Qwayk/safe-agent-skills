from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from awin_advertiser_safe_agent_cli.cli import main
from awin_advertiser_safe_agent_cli.http import HttpClient, HttpResponse
from awin_advertiser_safe_agent_cli.commands import offers as offers_cmd
from awin_advertiser_safe_agent_cli.commands import product_feeds as product_feeds_cmd
from awin_advertiser_safe_agent_cli.commands import transactions as transactions_cmd
from awin_advertiser_safe_agent_cli.commands.transactions import _build_list_query
from awin_advertiser_safe_agent_cli.errors import ValidationError


class TestPublishersCommand(unittest.TestCase):
    def test_publishers_list_requires_advertiser_id(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text("AWIN_API_BASE_URL=https://api.awin.com\nAWIN_API_TOKEN=token\n", encoding="utf-8")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--output", "json", "--env-file", str(env_path), "publishers", "list"])
            self.assertEqual(rc, 1)
            payload = json.loads(buf.getvalue())
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["error_type"], "ValidationError")

    @patch.object(HttpClient, "request")
    def test_publishers_list_passes_bearer_access_token(self, request_mock) -> None:
        request_mock.return_value = HttpResponse(
            status=200,
            headers={},
            body=b'{"publishers":[{"id":"p1"},{"id":"p2"}]}',
            url="https://api.awin.com/advertisers/123/publishers",
        )
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text("AWIN_API_BASE_URL=https://api.awin.com\nAWIN_API_TOKEN=token\n", encoding="utf-8")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main([
                    "--output",
                    "json",
                    "--env-file",
                    str(env_path),
                    "publishers",
                    "list",
                    "--advertiser-id",
                    "123",
                ])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertEqual(payload["count"], 2)
            self.assertEqual(payload["endpoint"], "/advertisers/123/publishers")
            request_mock.assert_called_once()
            called_args = request_mock.call_args.args
            called_kwargs = request_mock.call_args.kwargs
            self.assertEqual(called_args[0], "GET")
            self.assertEqual(called_args[1], "https://api.awin.com/advertisers/123/publishers")
            self.assertEqual(called_kwargs["headers"]["Authorization"], "Bearer token")
            self.assertEqual(called_kwargs["params"]["accessToken"], "token")


class TestTransactionsListCommand(unittest.TestCase):
    def test_transactions_list_requires_dates(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text("AWIN_API_BASE_URL=https://api.awin.com\nAWIN_API_TOKEN=token\n", encoding="utf-8")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main([
                    "--output",
                    "json",
                    "--env-file",
                    str(env_path),
                    "transactions",
                    "list",
                    "--advertiser-id",
                    "123",
                ])
            self.assertEqual(rc, 1)
            payload = json.loads(buf.getvalue())
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["error_type"], "ValidationError")

    @patch.object(HttpClient, "request")
    def test_transactions_list_passes_query_filters(self, request_mock) -> None:
        request_mock.return_value = HttpResponse(
            status=200,
            headers={},
            body=b'{"transactions":[{"id":"t1"},{"id":"t2"},{"id":"t3"}]}',
            url="https://api.awin.com/advertisers/123/transactions/",
        )
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text("AWIN_API_BASE_URL=https://api.awin.com\nAWIN_API_TOKEN=token\n", encoding="utf-8")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main([
                    "--output",
                    "json",
                    "--env-file",
                    str(env_path),
                    "transactions",
                    "list",
                    "--advertiser-id",
                    "123",
                    "--start-date",
                    "2026-06-01T00:00:00Z",
                    "--end-date",
                    "2026-06-08T23:59:59Z",
                    "--date-type",
                    "transaction",
                    "--publisher-id",
                    "pub1",
                    "--publisher-id",
                    "pub2",
                    "--status",
                    "approved",
                    "--timezone",
                    "UTC",
                    "--show-basket-products",
                ])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertEqual(payload["count"], 3)
            request_mock.assert_called_once()
            called_args = request_mock.call_args.args
            called_kwargs = request_mock.call_args.kwargs
            self.assertEqual(called_args[0], "GET")
            self.assertEqual(called_args[1], "https://api.awin.com/advertisers/123/transactions/")
            self.assertEqual(called_kwargs["params"]["startDate"], "2026-06-01T00:00:00Z")
            self.assertEqual(called_kwargs["params"]["endDate"], "2026-06-08T23:59:59Z")
            self.assertEqual(called_kwargs["params"]["dateType"], "transaction")
            self.assertEqual(called_kwargs["params"]["publisherId"], "pub1,pub2")
            self.assertEqual(called_kwargs["params"]["status"], "approved")
            self.assertEqual(called_kwargs["params"]["timezone"], "UTC")
            self.assertEqual(called_kwargs["params"]["showBasketProducts"], "true")
            self.assertEqual(called_kwargs["params"]["accessToken"], "token")

    def test_build_list_query_accepts_documented_enums(self) -> None:
        params = _build_list_query(
            SimpleNamespace(
                start_date="2026-06-01T00:00:00Z",
                end_date="2026-06-08T23:59:59Z",
                date_type="validation",
                publisher_id=["pub1", "pub2"],
                status="pending",
                timezone="UTC",
                show_basket_products=True,
            ),
        )
        self.assertEqual(params["dateType"], "validation")
        self.assertEqual(params["status"], "pending")
        self.assertEqual(params["publisherId"], "pub1,pub2")
        self.assertEqual(params["showBasketProducts"], "true")

    def test_build_list_query_rejects_invalid_date_type(self) -> None:
        with self.assertRaises(ValidationError):
            _build_list_query(
                SimpleNamespace(
                    start_date="2026-06-01T00:00:00Z",
                    end_date="2026-06-08T23:59:59Z",
                    date_type="update",
                    publisher_id=None,
                    status=None,
                    timezone=None,
                    show_basket_products=False,
                ),
            )

    def test_build_list_query_rejects_invalid_status(self) -> None:
        with self.assertRaises(ValidationError):
            _build_list_query(
                SimpleNamespace(
                    start_date="2026-06-01T00:00:00Z",
                    end_date="2026-06-08T23:59:59Z",
                    date_type=None,
                    publisher_id=None,
                    status="running",
                    timezone=None,
                    show_basket_products=False,
                ),
            )


class TestTransactionsByIdsCommand(unittest.TestCase):
    def test_transactions_by_ids_requires_ids(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text("AWIN_API_BASE_URL=https://api.awin.com\nAWIN_API_TOKEN=token\n", encoding="utf-8")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main([
                    "--output",
                    "json",
                    "--env-file",
                    str(env_path),
                    "transactions",
                    "by-ids",
                    "--advertiser-id",
                    "123",
                ])
            self.assertEqual(rc, 1)
            payload = json.loads(buf.getvalue())
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["error_type"], "ValidationError")

    @patch.object(HttpClient, "request")
    def test_transactions_by_ids_passes_bearer_query_flags(self, request_mock) -> None:
        request_mock.return_value = HttpResponse(
            status=200,
            headers={},
            body=b'{"transactions":[{"id":"t1"}]}',
            url="https://api.awin.com/advertisers/123/transactions",
        )
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text("AWIN_API_BASE_URL=https://api.awin.com\nAWIN_API_TOKEN=token\n", encoding="utf-8")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main([
                    "--output",
                    "json",
                    "--env-file",
                    str(env_path),
                    "transactions",
                    "by-ids",
                    "--advertiser-id",
                    "123",
                    "--ids",
                    "t1,t2,t3",
                    "--timezone",
                    "UTC",
                    "--show-basket-products",
                ])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertEqual(payload["count"], 1)
            called_kwargs = request_mock.call_args.kwargs
            called_args = request_mock.call_args.args
            self.assertEqual(called_args[0], "GET")
            self.assertEqual(called_args[1], "https://api.awin.com/advertisers/123/transactions")
            self.assertEqual(called_kwargs["params"]["ids"], "t1,t2,t3")
            self.assertEqual(called_kwargs["params"]["timezone"], "UTC")
            self.assertEqual(called_kwargs["params"]["showBasketProducts"], "true")
            self.assertEqual(called_kwargs["headers"]["Authorization"], "Bearer token")
            self.assertEqual(called_kwargs["params"]["accessToken"], "token")


class TestTransactionsBatchValidateCommand(unittest.TestCase):
    def _write_batch_file(self, path: Path, content: object) -> None:
        path.write_text(json.dumps(content, ensure_ascii=False, indent=2), encoding="utf-8")

    def test_batch_validate_requires_batch_file(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text("AWIN_API_BASE_URL=https://api.awin.com\nAWIN_API_TOKEN=token\n", encoding="utf-8")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main([
                    "--output",
                    "json",
                    "--env-file",
                    str(env_path),
                    "transactions",
                    "batch",
                    "validate",
                    "--advertiser-id",
                    "123",
                ])
            self.assertEqual(rc, 1)
            payload = json.loads(buf.getvalue())
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["error_type"], "ValidationError")

    @patch.object(HttpClient, "request")
    def test_batch_validate_dry_run_writes_plan_file(self, request_mock) -> None:
        request_mock.return_value = HttpResponse(
            status=200,
            headers={},
            body=b'{"ok":true}',
            url="https://api.awin.com/advertisers/123/transactions/batch",
        )
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text("AWIN_API_BASE_URL=https://api.awin.com\nAWIN_API_TOKEN=token\n", encoding="utf-8")
            batch_path = Path(td) / "batch.json"
            self._write_batch_file(
                batch_path,
                [
                    {
                        "action": "approve",
                        "transaction": {
                            "transactionId": "tr-1",
                        },
                    }
                ],
            )
            plan_path = Path(td) / "plan.json"

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main([
                    "--output",
                    "json",
                    "--env-file",
                    str(env_path),
                    "transactions",
                    "batch",
                    "validate",
                    "--advertiser-id",
                    "123",
                    "--batch-file",
                    str(batch_path),
                    "--plan-out",
                    str(plan_path),
                ])

            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])
            self.assertEqual(payload["operation"], "transactions batch validate")
            self.assertEqual(payload["action_count"], 1)
            self.assertEqual(payload["plan_out"], str(plan_path))
            request_mock.assert_not_called()
            self.assertTrue(plan_path.exists())

    def test_batch_validate_accepts_order_ref_target(self) -> None:
        transactions_cmd._validate_batch_payload(
            batch_payload=[
                {
                    "action": "approve",
                    "transaction": {
                        "orderRef": "ORDER-123",
                        "transactionDate": "2026-06-01T00:00:00Z",
                        "timezone": "UTC",
                    },
                }
            ],
        )

    def test_batch_validate_rejects_missing_order_ref_pieces(self) -> None:
        with self.assertRaises(ValidationError):
            transactions_cmd._validate_batch_payload(
                batch_payload=[
                    {
                        "action": "approve",
                        "transaction": {
                            "orderRef": "ORDER-123",
                            "transactionDate": "2026-06-01T00:00:00Z",
                        },
                    }
                ],
            )

    def test_batch_validate_rejects_amend_missing_transaction_parts(self) -> None:
        with self.assertRaises(ValidationError):
            transactions_cmd._validate_batch_payload(
                batch_payload=[
                    {
                        "action": "amend",
                        "transaction": {
                            "transactionId": "tr-1",
                            "amendReason": "update",
                            "currency": "USD",
                            "saleAmount": 15.5,
                        },
                    }
                ],
            )

    def test_batch_validate_rejects_amend_tracking_empty_values(self) -> None:
        with self.assertRaises(ValidationError):
            transactions_cmd._validate_batch_payload(
                batch_payload=[
                    {
                        "action": "amendTrackingParameters",
                        "transaction": {
                            "transactionId": "tr-1",
                            "amendReason": "fix-param",
                            "customParameters": {
                                "put": {
                                    "utm_source": "",
                                    "utm_campaign": "spring",
                                },
                            },
                        },
                    }
                ],
            )

    @patch.object(HttpClient, "request")
    def test_batch_validate_apply_uses_bearer_and_access_token_query(self, request_mock) -> None:
        request_mock.return_value = HttpResponse(
            status=200,
            headers={},
            body=b'{"status":"accepted"}',
            url="https://api.awin.com/advertisers/123/transactions/batch",
        )
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text("AWIN_API_BASE_URL=https://api.awin.com\nAWIN_API_TOKEN=token\n", encoding="utf-8")
            batch_path = Path(td) / "batch.json"
            self._write_batch_file(
                batch_path,
                [
                    {
                        "action": "decline",
                        "transaction": {
                            "orderRef": "o-1",
                            "transactionDate": "2026-06-01T00:00:00Z",
                            "timezone": "UTC",
                            "declineReason": "fraud",
                        },
                    }
                ],
            )
            plan_path = Path(td) / "plan.json"

            with redirect_stdout(io.StringIO()):
                main([
                    "--output",
                    "json",
                    "--env-file",
                    str(env_path),
                    "transactions",
                    "batch",
                    "validate",
                    "--advertiser-id",
                    "123",
                    "--batch-file",
                    str(batch_path),
                    "--plan-out",
                    str(plan_path),
                ])

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main([
                    "--output",
                    "json",
                    "--env-file",
                    str(env_path),
                    "transactions",
                    "batch",
                    "validate",
                    "--advertiser-id",
                    "123",
                    "--batch-file",
                    str(batch_path),
                    "--apply",
                    "--yes",
                    "--ack-irreversible",
                    "--plan-in",
                    str(plan_path),
                ])
            self.assertEqual(rc, 0)
            called_args = request_mock.call_args.args
            called_kwargs = request_mock.call_args.kwargs
            self.assertEqual(called_args[0], "POST")
            self.assertEqual(called_args[1], "https://api.awin.com/advertisers/123/transactions/batch")
            self.assertEqual(called_kwargs["headers"]["Authorization"], "Bearer token")
            self.assertNotIn("x-api-key", called_kwargs["headers"])
            self.assertEqual(called_kwargs["params"]["accessToken"], "token")
            self.assertEqual(called_kwargs["json_body"][0]["transaction"]["declineReason"], "fraud")

    @patch.object(HttpClient, "request")
    def test_batch_validate_rejects_plan_mismatch(self, request_mock) -> None:
        request_mock.return_value = HttpResponse(
            status=200,
            headers={},
            body=b'{"status":"accepted"}',
            url="https://api.awin.com/advertisers/123/transactions/batch",
        )
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text("AWIN_API_BASE_URL=https://api.awin.com\nAWIN_API_TOKEN=token\n", encoding="utf-8")
            batch_path = Path(td) / "batch.json"
            self._write_batch_file(
                batch_path,
                [
                    {
                        "action": "approve",
                        "transaction": {
                            "transactionId": "tr-1",
                        },
                    }
                ],
            )
            plan_path = Path(td) / "plan.json"

            with redirect_stdout(io.StringIO()):
                main([
                    "--output",
                    "json",
                    "--env-file",
                    str(env_path),
                    "transactions",
                    "batch",
                    "validate",
                    "--advertiser-id",
                    "123",
                    "--batch-file",
                    str(batch_path),
                    "--plan-out",
                    str(plan_path),
                ])

            self._write_batch_file(
                batch_path,
                [
                    {
                        "action": "approve",
                        "transaction": {
                            "transactionId": "tr-2",
                        },
                    }
                ],
            )

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main([
                    "--output",
                    "json",
                    "--env-file",
                    str(env_path),
                    "transactions",
                    "batch",
                    "validate",
                    "--advertiser-id",
                    "123",
                    "--batch-file",
                    str(batch_path),
                    "--apply",
                    "--yes",
                    "--ack-irreversible",
                    "--plan-in",
                    str(plan_path),
                ])
            self.assertEqual(rc, 1)
            payload = json.loads(buf.getvalue())
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["error_type"], "SafetyError")
            self.assertIn("batch file changed since --plan-in was created", payload["error"])

    @patch.object(HttpClient, "request")
    def test_batch_validate_apply_requires_apply_gates(self, request_mock) -> None:
        request_mock.return_value = HttpResponse(
            status=200,
            headers={},
            body=b'{"status":"accepted"}',
            url="https://api.awin.com/advertisers/123/transactions/batch",
        )
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text("AWIN_API_BASE_URL=https://api.awin.com\nAWIN_API_TOKEN=token\n", encoding="utf-8")
            batch_path = Path(td) / "batch.json"
            self._write_batch_file(
                batch_path,
                [
                    {
                        "action": "approve",
                        "transaction": {
                            "transactionId": "tr-1",
                        },
                    }
                ],
            )

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main([
                    "--output",
                    "json",
                    "--env-file",
                    str(env_path),
                    "transactions",
                    "batch",
                    "validate",
                    "--advertiser-id",
                    "123",
                    "--batch-file",
                    str(batch_path),
                    "--apply",
                ])
            self.assertEqual(rc, 1)
            payload = json.loads(buf.getvalue())
            self.assertEqual(payload["error_type"], "SafetyError")
            self.assertIn("requires --apply with --plan-in", payload["error"])


    @patch.object(HttpClient, "request")
    def test_batch_validate_rejects_invalid_action_payload(self, request_mock) -> None:
        request_mock.return_value = HttpResponse(
            status=200,
            headers={},
            body=b'{"status":"accepted"}',
            url="https://api.awin.com/advertisers/123/transactions/batch",
        )
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text("AWIN_API_BASE_URL=https://api.awin.com\nAWIN_API_TOKEN=token\n", encoding="utf-8")
            batch_path = Path(td) / "batch.json"
            self._write_batch_file(
                batch_path,
                [
                    {
                        "action": "bad",
                        "transaction": {
                            "transactionId": "tr-1",
                        },
                    }
                ],
            )

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main([
                    "--output",
                    "json",
                    "--env-file",
                    str(env_path),
                    "transactions",
                    "batch",
                    "validate",
                    "--advertiser-id",
                    "123",
                    "--batch-file",
                    str(batch_path),
                ])
            self.assertEqual(rc, 1)
            payload = json.loads(buf.getvalue())
            self.assertFalse(payload["ok"])
            self.assertIn("must be one of approve|decline|amend|amendTrackingParameters", payload["error"])

    def test_batch_validate_enforces_max_actions(self) -> None:
        with patch.object(transactions_cmd, "_MAX_BATCH_ACTIONS", 2):
            with self.assertRaises(ValidationError):
                transactions_cmd._validate_batch_payload(
                    batch_payload=[
                        {
                            "action": "approve",
                            "transaction": {"transactionId": "tr-1"},
                        },
                        {
                            "action": "approve",
                            "transaction": {"transactionId": "tr-2"},
                        },
                        {
                            "action": "approve",
                            "transaction": {"transactionId": "tr-3"},
                        },
                    ],
                )


class TestPublishersTransactionsRedaction(unittest.TestCase):
    @patch.object(HttpClient, "request")
    def test_transactions_by_ids_redacts_token_in_errors(self, request_mock) -> None:
        request_mock.side_effect = RuntimeError("failure for token token123")
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text("AWIN_API_BASE_URL=https://api.awin.com\nAWIN_API_TOKEN=token123\n", encoding="utf-8")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main([
                    "--output",
                    "json",
                    "--env-file",
                    str(env_path),
                    "transactions",
                    "by-ids",
                    "--advertiser-id",
                    "123",
                    "--ids",
                    "t1",
                ])
            self.assertEqual(rc, 1)
            payload = json.loads(buf.getvalue())
            self.assertFalse(payload["ok"])
            self.assertIn("***REDACTED***", payload["error"])
            self.assertNotIn("token123", payload["error"])


class TestTransactionsJobsCommand(unittest.TestCase):
    def test_transactions_jobs_list_requires_advertiser_id(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text("AWIN_API_BASE_URL=https://api.awin.com\nAWIN_API_TOKEN=token\n", encoding="utf-8")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--output", "json", "--env-file", str(env_path), "transactions", "jobs", "list"])
            self.assertEqual(rc, 1)
            payload = json.loads(buf.getvalue())
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["error_type"], "ValidationError")

    @patch.object(HttpClient, "request")
    def test_transactions_jobs_list_passes_header_only_auth(self, request_mock) -> None:
        request_mock.return_value = HttpResponse(
            status=200,
            headers={},
            body=b'[{"id":"job-1","status":"done"}]',
            url="https://api.awin.com/advertisers/123/transactions/jobs",
        )
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text("AWIN_API_BASE_URL=https://api.awin.com\nAWIN_API_TOKEN=token\n", encoding="utf-8")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main([
                    "--output",
                    "json",
                    "--env-file",
                    str(env_path),
                    "transactions",
                    "jobs",
                    "list",
                    "--advertiser-id",
                    "123",
                ])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertEqual(payload["count"], 1)
            self.assertEqual(payload["endpoint"], "/advertisers/123/transactions/jobs")
            request_mock.assert_called_once()
            called_args = request_mock.call_args.args
            called_kwargs = request_mock.call_args.kwargs
            self.assertEqual(called_args[0], "GET")
            self.assertEqual(called_args[1], "https://api.awin.com/advertisers/123/transactions/jobs")
            self.assertEqual(called_kwargs["headers"]["Authorization"], "Bearer token")
            self.assertNotIn("accessToken", called_kwargs["params"])
            self.assertNotIn("accessToken", payload.get("query", {}))

    @patch.object(HttpClient, "request")
    def test_transactions_jobs_show_passes_job_output_filter(self, request_mock) -> None:
        request_mock.return_value = HttpResponse(
            status=200,
            headers={},
            body=b'{"jobId":"job-7","status":"done"}',
            url="https://api.awin.com/advertisers/123/transactions/jobs/job-7?output=errors",
        )
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text("AWIN_API_BASE_URL=https://api.awin.com\nAWIN_API_TOKEN=token\n", encoding="utf-8")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main([
                    "--output",
                    "json",
                    "--env-file",
                    str(env_path),
                    "transactions",
                    "jobs",
                    "show",
                    "--advertiser-id",
                    "123",
                    "--job-id",
                    "job-7",
                    "--job-output",
                    "errors",
                ])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertEqual(payload["command"], "transactions jobs show")
            self.assertEqual(payload["job"]["jobId"], "job-7")
            request_mock.assert_called_once()
            called_kwargs = request_mock.call_args.kwargs
            self.assertEqual(called_kwargs["params"]["output"], "errors")
            self.assertFalse(called_kwargs["params"].get("accessToken"))


class TestReportsCommands(unittest.TestCase):
    def test_reports_publisher_requires_dates(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text("AWIN_API_BASE_URL=https://api.awin.com\nAWIN_API_TOKEN=token\n", encoding="utf-8")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main([
                    "--output",
                    "json",
                    "--env-file",
                    str(env_path),
                    "reports",
                    "publisher",
                    "--advertiser-id",
                    "123",
                ])
            self.assertEqual(rc, 1)
            payload = json.loads(buf.getvalue())
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["error_type"], "ValidationError")

    @patch.object(HttpClient, "request")
    def test_reports_publisher_passes_access_token_and_filters(self, request_mock) -> None:
        request_mock.return_value = HttpResponse(
            status=200,
            headers={},
            body=b'{"rows":[{"publisherId":"p1","revenue":10}]}',
            url="https://api.awin.com/advertisers/123/reports/publisher",
        )
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text("AWIN_API_BASE_URL=https://api.awin.com\nAWIN_API_TOKEN=token\n", encoding="utf-8")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main([
                    "--output",
                    "json",
                    "--env-file",
                    str(env_path),
                    "reports",
                    "publisher",
                    "--advertiser-id",
                    "123",
                    "--start-date",
                    "2026-06-01",
                    "--end-date",
                    "2026-06-08T23:59:59Z",
                    "--date-type",
                    "transaction",
                    "--timezone",
                    "UTC",
                ])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertEqual(payload["command"], "reports publisher")
            self.assertEqual(payload["count"], 1)
            request_mock.assert_called_once()
            called_args = request_mock.call_args.args
            called_kwargs = request_mock.call_args.kwargs
            self.assertEqual(called_args[1], "https://api.awin.com/advertisers/123/reports/publisher")
            self.assertEqual(called_kwargs["params"]["startDate"], "2026-06-01")
            self.assertEqual(called_kwargs["params"]["endDate"], "2026-06-08T23:59:59Z")
            self.assertEqual(called_kwargs["params"]["dateType"], "transaction")
            self.assertEqual(called_kwargs["params"]["timezone"], "UTC")
            self.assertEqual(called_kwargs["params"]["accessToken"], "token")

    @patch.object(HttpClient, "request")
    def test_reports_campaign_passes_campaign_filters(self, request_mock) -> None:
        request_mock.return_value = HttpResponse(
            status=200,
            headers={},
            body=b'{"rows":[{"campaign":"spring","revenue":10}]}',
            url="https://api.awin.com/advertisers/123/reports/campaign",
        )
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text("AWIN_API_BASE_URL=https://api.awin.com\nAWIN_API_TOKEN=token\n", encoding="utf-8")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main([
                    "--output",
                    "json",
                    "--env-file",
                    str(env_path),
                    "reports",
                    "campaign",
                    "--advertiser-id",
                    "123",
                    "--start-date",
                    "2026-06-01",
                    "--end-date",
                    "2026-06-08T23:59:59Z",
                    "--campaign",
                    "spr-1",
                    "--publisher-id",
                    "p1",
                    "--publisher-id",
                    "p2",
                    "--include-numbers-without-campaign",
                    "--interval",
                    "month",
                    "--timezone",
                    "UTC",
                ])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertEqual(payload["command"], "reports campaign")
            self.assertEqual(payload["count"], 1)
            called_kwargs = request_mock.call_args.kwargs
            self.assertEqual(called_kwargs["params"]["campaign"], "spr-1")
            self.assertEqual(called_kwargs["params"]["publisherIds"], "p1,p2")
            self.assertEqual(called_kwargs["params"]["includeNumbersWithoutCampaign"], "true")
            self.assertEqual(called_kwargs["params"]["interval"], "month")
            self.assertNotIn("dateType", called_kwargs["params"])

    @patch.object(HttpClient, "request")
    def test_reports_campaign_rejects_date_type_flag(self, request_mock) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text("AWIN_API_BASE_URL=https://api.awin.com\nAWIN_API_TOKEN=token\n", encoding="utf-8")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main([
                    "--output",
                    "json",
                    "--env-file",
                    str(env_path),
                    "reports",
                    "campaign",
                    "--advertiser-id",
                    "123",
                    "--start-date",
                    "2026-06-01",
                    "--end-date",
                    "2026-06-08T23:59:59Z",
                    "--date-type",
                    "transaction",
                ])
            self.assertEqual(rc, 1)
            payload = json.loads(buf.getvalue())
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["error_type"], "ValidationError")
            request_mock.assert_not_called()

    @patch.object(HttpClient, "request")
    def test_reports_campaign_rejects_short_campaign(self, request_mock) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text("AWIN_API_BASE_URL=https://api.awin.com\nAWIN_API_TOKEN=token\n", encoding="utf-8")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main([
                    "--output",
                    "json",
                    "--env-file",
                    str(env_path),
                    "reports",
                    "campaign",
                    "--advertiser-id",
                    "123",
                    "--start-date",
                    "2026-06-01",
                    "--end-date",
                    "2026-06-08T23:59:59Z",
                    "--campaign",
                    "ab",
                ])
            self.assertEqual(rc, 1)
            payload = json.loads(buf.getvalue())
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["error_type"], "ValidationError")
            request_mock.assert_not_called()

    @patch.object(HttpClient, "request")
    def test_reports_campaign_rejects_long_campaign(self, request_mock) -> None:
        long_campaign = "x" * 129
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text("AWIN_API_BASE_URL=https://api.awin.com\nAWIN_API_TOKEN=token\n", encoding="utf-8")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main([
                    "--output",
                    "json",
                    "--env-file",
                    str(env_path),
                    "reports",
                    "campaign",
                    "--advertiser-id",
                    "123",
                    "--start-date",
                    "2026-06-01",
                    "--end-date",
                    "2026-06-08T23:59:59Z",
                    "--campaign",
                    long_campaign,
                ])
            self.assertEqual(rc, 1)
            payload = json.loads(buf.getvalue())
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["error_type"], "ValidationError")
            request_mock.assert_not_called()

    @patch.object(HttpClient, "request")
    def test_reports_campaign_rejects_invalid_interval(self, request_mock) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text("AWIN_API_BASE_URL=https://api.awin.com\nAWIN_API_TOKEN=token\n", encoding="utf-8")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main([
                    "--output",
                    "json",
                    "--env-file",
                    str(env_path),
                    "reports",
                    "campaign",
                    "--advertiser-id",
                    "123",
                    "--start-date",
                    "2026-06-01",
                    "--end-date",
                    "2026-06-08T23:59:59Z",
                    "--campaign",
                    "spr",
                    "--interval",
                    "week",
                ])
            self.assertEqual(rc, 1)
            payload = json.loads(buf.getvalue())
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["error_type"], "ValidationError")
            self.assertIn("invalid choice: 'week'", payload["error"])
            request_mock.assert_not_called()


class TestSharedReadSetupNeeded(unittest.TestCase):
    def test_missing_token_returns_blocked_setup_needed_for_multiple_read_commands(self) -> None:
        commands = [
            ["transactions", "jobs", "list", "--advertiser-id", "123"],
            ["transactions", "jobs", "show", "--advertiser-id", "123", "--job-id", "job-1"],
            ["reports", "publisher", "--advertiser-id", "123", "--start-date", "2026-06-01", "--end-date", "2026-06-08"],
            ["reports", "campaign", "--advertiser-id", "123", "--start-date", "2026-06-01", "--end-date", "2026-06-08"],
        ]
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text("AWIN_API_BASE_URL=https://api.awin.com\n", encoding="utf-8")

            for cmd in commands:
                with self.subTest(cmd=cmd):
                    buf = io.StringIO()
                    with redirect_stdout(buf):
                        rc = main(["--output", "json", "--env-file", str(env_path), *cmd])
                    self.assertEqual(rc, 1)
                    payload = json.loads(buf.getvalue())
                    self.assertFalse(payload["ok"])
                    self.assertTrue(payload["blocked"])
                    self.assertTrue(payload["setup_needed"])
                    self.assertEqual(payload["error_type"], "SetupNeeded")


class TestConversionOrdersCreateCommand(unittest.TestCase):
    def _write_orders_file(self, path: Path, content: object) -> None:
        path.write_text(json.dumps(content, ensure_ascii=False, indent=2), encoding="utf-8")

    def test_conversion_create_requires_orders_file(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text("AWIN_API_BASE_URL=https://api.awin.com\nAWIN_API_TOKEN=token\n", encoding="utf-8")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main([
                    "--output",
                    "json",
                    "--env-file",
                    str(env_path),
                    "conversion",
                    "orders",
                    "create",
                    "--advertiser-id",
                    "123",
                ])
            self.assertEqual(rc, 1)
            payload = json.loads(buf.getvalue())
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["error_type"], "ValidationError")

    @patch.object(HttpClient, "request")
    def test_conversion_create_rejects_webhook_in_orders_file(self, request_mock) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text("AWIN_API_BASE_URL=https://api.awin.com\nAWIN_API_TOKEN=token\n", encoding="utf-8")
            orders_path = Path(td) / "orders.json"
            self._write_orders_file(
                orders_path,
                {
                    "webhook": {"url": "https://bad.example.com/webhook"},
                    "orders": [
                        {
                            "orderReference": "o-1",
                            "amount": 12.34,
                            "channel": "API",
                            "currency": "EUR",
                            "commissionGroups": [{"code": "CG1", "amount": 1.2}],
                            "awc": "A1",
                        }
                    ],
                },
            )

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main([
                    "--output",
                    "json",
                    "--env-file",
                    str(env_path),
                    "conversion",
                    "orders",
                    "create",
                    "--advertiser-id",
                    "123",
                    "--orders-file",
                    str(orders_path),
                ])
            self.assertEqual(rc, 1)
            payload = json.loads(buf.getvalue())
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["error_type"], "ValidationError")
            self.assertIn("top-level webhook object", payload["error"])
            request_mock.assert_not_called()

    @patch.object(HttpClient, "request")
    def test_conversion_create_dry_run_writes_plan_file_and_does_not_call_http(self, request_mock) -> None:
        request_mock.return_value = HttpResponse(
            status=200,
            headers={},
            body=b'{"ok":true}',
            url="https://api.awin.com/s2s/advertiser/123/orders",
        )
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text("AWIN_API_BASE_URL=https://api.awin.com\nAWIN_API_TOKEN=token\n", encoding="utf-8")
            orders_path = Path(td) / "orders.json"
            self._write_orders_file(
                orders_path,
                {
                    "orders": [
                        {
                            "orderReference": "o-1",
                            "amount": 12.34,
                            "channel": "API",
                            "currency": "EUR",
                            "commissionGroups": [{"code": "CG1", "amount": 1.2}],
                            "awc": "A1",
                        }
                    ]
                },
            )
            plan_path = Path(td) / "plan.json"

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main([
                    "--output",
                    "json",
                    "--env-file",
                    str(env_path),
                    "conversion",
                    "orders",
                    "create",
                    "--advertiser-id",
                    "123",
                    "--orders-file",
                    str(orders_path),
                    "--plan-out",
                    str(plan_path),
                ])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])
            self.assertEqual(payload["operation"], "conversion orders create")
            self.assertTrue(plan_path.exists())
            self.assertEqual(payload["plan_out"], str(plan_path))
            request_mock.assert_not_called()

    @patch.object(HttpClient, "request")
    def test_conversion_create_apply_uses_x_api_key_only(self, request_mock) -> None:
        request_mock.return_value = HttpResponse(
            status=201,
            headers={},
            body=b'{"ok":true}',
            url="https://api.awin.com/s2s/advertiser/123/orders",
        )
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text("AWIN_API_BASE_URL=https://api.awin.com\nAWIN_API_TOKEN=token\n", encoding="utf-8")
            orders_path = Path(td) / "orders.json"
            self._write_orders_file(
                orders_path,
                {
                    "orders": [
                        {
                            "orderReference": "o-1",
                            "amount": 12.34,
                            "channel": "API",
                            "currency": "EUR",
                            "commissionGroups": [{"code": "CG1", "amount": 1.2}],
                            "publisherId": "pub-1",
                            "clickTime": "2026-06-01T00:00:00Z",
                        }
                    ]
                },
            )
            plan_path = Path(td) / "plan.json"
            with redirect_stdout(io.StringIO()):
                main([
                    "--output",
                    "json",
                    "--env-file",
                    str(env_path),
                    "conversion",
                    "orders",
                    "create",
                    "--advertiser-id",
                    "123",
                    "--orders-file",
                    str(orders_path),
                    "--plan-out",
                    str(plan_path),
                ])

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main([
                    "--output",
                    "json",
                    "--env-file",
                    str(env_path),
                    "conversion",
                    "orders",
                    "create",
                    "--advertiser-id",
                    "123",
                    "--orders-file",
                    str(orders_path),
                    "--apply",
                    "--yes",
                    "--ack-irreversible",
                    "--plan-in",
                    str(plan_path),
                ])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertFalse(payload["dry_run"])
            called_args = request_mock.call_args.args
            called_kwargs = request_mock.call_args.kwargs
            self.assertEqual(called_args[0], "POST")
            self.assertEqual(called_args[1], "https://api.awin.com/s2s/advertiser/123/orders")
            self.assertEqual(called_kwargs["headers"]["x-api-key"], "token")
            self.assertNotIn("Authorization", called_kwargs["headers"])
            self.assertNotIn("accessToken", called_kwargs["params"])

    @patch.object(HttpClient, "request")
    def test_conversion_create_rejects_invalid_order_missing_required_fields(self, request_mock) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text("AWIN_API_BASE_URL=https://api.awin.com\nAWIN_API_TOKEN=token\n", encoding="utf-8")
            orders_path = Path(td) / "orders.json"
            self._write_orders_file(
                orders_path,
                {
                    "orders": [
                        {
                            "orderReference": "o-1",
                            "amount": 12.34,
                            "currency": "EUR",
                            "commissionGroups": [{"code": "CG1", "amount": 1.2}],
                            "awc": "A1",
                        }
                    ]
                },
            )
            plan_path = Path(td) / "plan.json"
            with redirect_stdout(io.StringIO()):
                main([
                    "--output",
                    "json",
                    "--env-file",
                    str(env_path),
                    "conversion",
                    "orders",
                    "create",
                    "--advertiser-id",
                    "123",
                    "--orders-file",
                    str(orders_path),
                    "--plan-out",
                    str(plan_path),
                ])

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main([
                    "--output",
                    "json",
                    "--env-file",
                    str(env_path),
                    "conversion",
                    "orders",
                    "create",
                    "--advertiser-id",
                    "123",
                    "--orders-file",
                    str(orders_path),
                ])
            self.assertEqual(rc, 1)
            payload = json.loads(buf.getvalue())
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["error_type"], "ValidationError")
            self.assertIn("missing required field", payload["error"])
            request_mock.assert_not_called()

    @patch.object(HttpClient, "request")
    def test_conversion_create_rejects_order_without_identity_pair_or_awc(self, request_mock) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text("AWIN_API_BASE_URL=https://api.awin.com\nAWIN_API_TOKEN=token\n", encoding="utf-8")
            orders_path = Path(td) / "orders.json"
            self._write_orders_file(
                orders_path,
                {
                    "orders": [
                        {
                            "orderReference": "o-1",
                            "amount": 12.34,
                            "channel": "API",
                            "currency": "EUR",
                            "commissionGroups": [{"code": "CG1", "amount": 1.2}],
                        }
                    ]
                },
            )

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main([
                    "--output",
                    "json",
                    "--env-file",
                    str(env_path),
                    "conversion",
                    "orders",
                    "create",
                    "--advertiser-id",
                    "123",
                    "--orders-file",
                    str(orders_path),
                ])
            self.assertEqual(rc, 1)
            payload = json.loads(buf.getvalue())
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["error_type"], "ValidationError")
            self.assertIn("either awc, or both publisherId and clickTime", payload["error"])
            request_mock.assert_not_called()

    @patch.object(HttpClient, "request")
    def test_conversion_create_safety_gates(self, request_mock) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text("AWIN_API_BASE_URL=https://api.awin.com\nAWIN_API_TOKEN=token\n", encoding="utf-8")
            orders_path = Path(td) / "orders.json"
            self._write_orders_file(
                orders_path,
                {
                    "orders": [
                        {
                            "orderReference": "o-1",
                            "amount": 12.34,
                            "channel": "API",
                            "currency": "EUR",
                            "commissionGroups": [{"code": "CG1", "amount": 1.2}],
                            "awc": "A1",
                        }
                    ]
                },
            )
            plan_path = Path(td) / "plan.json"
            with redirect_stdout(io.StringIO()):
                main([
                    "--output",
                    "json",
                    "--env-file",
                    str(env_path),
                    "conversion",
                    "orders",
                    "create",
                    "--advertiser-id",
                    "123",
                    "--orders-file",
                    str(orders_path),
                    "--plan-out",
                    str(plan_path),
                ])

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main([
                    "--output",
                    "json",
                    "--env-file",
                    str(env_path),
                    "conversion",
                    "orders",
                    "create",
                    "--advertiser-id",
                    "123",
                    "--orders-file",
                    str(orders_path),
                    "--apply",
                ])
            self.assertEqual(rc, 1)
            payload = json.loads(buf.getvalue())
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["error_type"], "SafetyError")
            self.assertIn("requires --apply with --plan-in", payload["error"])

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main([
                    "--output",
                    "json",
                    "--env-file",
                    str(env_path),
                    "conversion",
                    "orders",
                    "create",
                    "--advertiser-id",
                    "123",
                    "--orders-file",
                    str(orders_path),
                    "--apply",
                    "--yes",
                    "--plan-in",
                    str(plan_path),
                ])
            self.assertEqual(rc, 1)
            payload = json.loads(buf.getvalue())
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["error_type"], "SafetyError")
            self.assertIn("requires --apply --yes --ack-irreversible", payload["error"])

    @patch.object(HttpClient, "request")
    def test_conversion_create_requires_plan_in_for_apply(self, request_mock) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text("AWIN_API_BASE_URL=https://api.awin.com\nAWIN_API_TOKEN=token\n", encoding="utf-8")
            orders_path = Path(td) / "orders.json"
            self._write_orders_file(
                orders_path,
                {
                    "orders": [
                        {
                            "orderReference": "o-1",
                            "amount": 12.34,
                            "channel": "API",
                            "currency": "EUR",
                            "commissionGroups": [{"code": "CG1", "amount": 1.2}],
                            "awc": "A1",
                        }
                    ]
                },
            )

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main([
                    "--output",
                    "json",
                    "--env-file",
                    str(env_path),
                    "conversion",
                    "orders",
                    "create",
                    "--advertiser-id",
                    "123",
                    "--orders-file",
                    str(orders_path),
                    "--apply",
                    "--yes",
                    "--ack-irreversible",
                ])
            self.assertEqual(rc, 1)
            payload = json.loads(buf.getvalue())
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["error_type"], "SafetyError")
            self.assertIn("requires --apply with --plan-in", payload["error"])
            request_mock.assert_not_called()

    @patch.object(HttpClient, "request")
    def test_conversion_create_requires_matching_plan_webhook(self, request_mock) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text("AWIN_API_BASE_URL=https://api.awin.com\nAWIN_API_TOKEN=token\n", encoding="utf-8")
            orders_path = Path(td) / "orders.json"
            self._write_orders_file(
                orders_path,
                {
                    "orders": [
                        {
                            "orderReference": "o-1",
                            "amount": 12.34,
                            "channel": "API",
                            "currency": "EUR",
                            "commissionGroups": [{"code": "CG1", "amount": 1.2}],
                            "awc": "A1",
                        }
                    ]
                },
            )
            plan_path = Path(td) / "plan.json"

            with redirect_stdout(io.StringIO()):
                main([
                    "--output",
                    "json",
                    "--env-file",
                    str(env_path),
                    "conversion",
                    "orders",
                    "create",
                    "--advertiser-id",
                    "123",
                    "--orders-file",
                    str(orders_path),
                    "--plan-out",
                    str(plan_path),
                ])

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main([
                    "--output",
                    "json",
                    "--env-file",
                    str(env_path),
                    "conversion",
                    "orders",
                    "create",
                    "--advertiser-id",
                    "123",
                    "--orders-file",
                    str(orders_path),
                    "--apply",
                    "--yes",
                    "--ack-irreversible",
                    "--plan-in",
                    str(plan_path),
                    "--webhook-url",
                    "https://new.example.com/webhook",
                ])
            self.assertEqual(rc, 1)
            payload = json.loads(buf.getvalue())
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["error_type"], "SafetyError")
            self.assertIn("does not match --webhook-url", payload["error"])
            request_mock.assert_not_called()

    @patch.object(HttpClient, "request")
    def test_conversion_create_plan_in_drift_check(self, request_mock) -> None:
        request_mock.return_value = HttpResponse(
            status=201,
            headers={},
            body=b'{"ok":true}',
            url="https://api.awin.com/s2s/advertiser/123/orders",
        )
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text("AWIN_API_BASE_URL=https://api.awin.com\nAWIN_API_TOKEN=token\n", encoding="utf-8")
            orders_path = Path(td) / "orders.json"
            self._write_orders_file(
                orders_path,
                {
                    "orders": [
                        {
                            "orderReference": "o-1",
                            "amount": 12.34,
                            "channel": "API",
                            "currency": "EUR",
                            "commissionGroups": [{"code": "CG1", "amount": 1.2}],
                            "awc": "A1",
                        }
                    ]
                },
            )
            plan_path = Path(td) / "plan.json"

            buf = io.StringIO()
            with redirect_stdout(buf):
                main([
                    "--output",
                    "json",
                    "--env-file",
                    str(env_path),
                    "conversion",
                    "orders",
                    "create",
                    "--advertiser-id",
                    "123",
                    "--orders-file",
                    str(orders_path),
                    "--plan-out",
                    str(plan_path),
                ])

            self._write_orders_file(
                orders_path,
                {
                    "orders": [
                        {
                            "orderReference": "o-1",
                            "amount": 13.34,
                            "channel": "API",
                            "currency": "EUR",
                            "commissionGroups": [{"code": "CG1", "amount": 1.2}],
                            "awc": "A1",
                        }
                    ]
                },
            )
            request_mock.reset_mock()

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main([
                    "--output",
                    "json",
                    "--env-file",
                    str(env_path),
                    "conversion",
                    "orders",
                    "create",
                    "--advertiser-id",
                    "123",
                    "--orders-file",
                    str(orders_path),
                    "--apply",
                    "--yes",
                    "--ack-irreversible",
                    "--plan-in",
                    str(plan_path),
                ])
            self.assertEqual(rc, 1)
            payload = json.loads(buf.getvalue())
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["error_type"], "SafetyError")
            self.assertIn("orders file changed since --plan-in was created", payload["error"])
            request_mock.assert_not_called()

    @patch.object(HttpClient, "request")
    def test_conversion_create_applies_and_writes_receipt(self, request_mock) -> None:
        request_mock.return_value = HttpResponse(
            status=201,
            headers={},
            body=b'{"ok":true}',
            url="https://api.awin.com/s2s/advertiser/123/orders",
        )
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text("AWIN_API_BASE_URL=https://api.awin.com\nAWIN_API_TOKEN=token\n", encoding="utf-8")
            orders_path = Path(td) / "orders.json"
            self._write_orders_file(
                orders_path,
                {
                    "orders": [
                        {
                            "orderReference": "o-1",
                            "amount": 12.34,
                            "channel": "API",
                            "currency": "EUR",
                            "commissionGroups": [{"code": "CG1", "amount": 1.2}],
                            "awc": "A1",
                        }
                    ]
                },
            )
            plan_path = Path(td) / "plan.json"
            with redirect_stdout(io.StringIO()):
                main([
                    "--output",
                    "json",
                    "--env-file",
                    str(env_path),
                    "conversion",
                    "orders",
                    "create",
                    "--advertiser-id",
                    "123",
                    "--orders-file",
                    str(orders_path),
                    "--plan-out",
                    str(plan_path),
                ])
            receipt_path = Path(td) / "receipt.json"

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main([
                    "--output",
                    "json",
                    "--env-file",
                    str(env_path),
                    "conversion",
                    "orders",
                    "create",
                    "--advertiser-id",
                    "123",
                    "--orders-file",
                    str(orders_path),
                    "--apply",
                    "--yes",
                    "--ack-irreversible",
                    "--plan-in",
                    str(plan_path),
                    "--receipt-out",
                    str(receipt_path),
                ])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertFalse(payload["dry_run"])
            self.assertTrue(receipt_path.exists())
            self.assertEqual(payload["receipt_out"], str(receipt_path))


class TestOffersCreateCommand(unittest.TestCase):
    def _write_offer_file(self, path: Path, content: object) -> None:
        path.write_text(json.dumps(content, ensure_ascii=False, indent=2), encoding="utf-8")

    @patch.object(HttpClient, "request")
    def test_offers_create_auth_mode_is_bearer_only(self, request_mock) -> None:
        request_mock.return_value = HttpResponse(
            status=201,
            headers={},
            body=b'{"ok":true}',
            url="https://api.awin.com/promotion/advertiser/123",
        )
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text("AWIN_API_BASE_URL=https://api.awin.com\nAWIN_API_TOKEN=token\n", encoding="utf-8")
            offer_path = Path(td) / "offer.json"
            self._write_offer_file(
                offer_path,
                {
                    "title": "Spring Offer",
                    "description": "Long enough description",
                    "terms": "Use this code at checkout",
                    "type": "promotion",
                    "url": "https://example.com/offers/spring",
                    "startDate": "2026-06-01",
                    "endDate": "2026-06-30",
                    "appliesToAllRegions": True,
                    "promotionCategories": ["cat"],
                },
            )
            plan_path = Path(td) / "plan.json"

            with redirect_stdout(io.StringIO()):
                main([
                    "--output",
                    "json",
                    "--env-file",
                    str(env_path),
                    "offers",
                    "create",
                    "--advertiser-id",
                    "123",
                    "--offer-file",
                    str(offer_path),
                    "--plan-out",
                    str(plan_path),
                ])

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main([
                    "--output",
                    "json",
                    "--env-file",
                    str(env_path),
                    "offers",
                    "create",
                    "--advertiser-id",
                    "123",
                    "--offer-file",
                    str(offer_path),
                    "--apply",
                    "--yes",
                    "--ack-irreversible",
                    "--plan-in",
                    str(plan_path),
                ])
            self.assertEqual(rc, 0)
            called_kwargs = request_mock.call_args.kwargs
            self.assertEqual(called_kwargs["headers"].get("Authorization"), "Bearer token")
            self.assertNotIn("accessToken", called_kwargs["params"])

    def test_offers_create_rejects_voucher_without_code(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text("AWIN_API_BASE_URL=https://api.awin.com\nAWIN_API_TOKEN=token\n", encoding="utf-8")
            offer_path = Path(td) / "offer.json"
            self._write_offer_file(
                offer_path,
                {
                    "title": "Voucher Offer",
                    "description": "Desc",
                    "terms": "Terms apply",
                    "type": "voucher",
                    "url": "https://example.com/offers/voucher",
                    "startDate": "2026-06-01",
                    "endDate": "2026-06-30",
                    "appliesToAllRegions": True,
                    "promotionCategories": ["cat"],
                },
            )

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main([
                    "--output",
                    "json",
                    "--env-file",
                    str(env_path),
                    "offers",
                    "create",
                    "--advertiser-id",
                    "123",
                    "--offer-file",
                    str(offer_path),
                ])
            self.assertEqual(rc, 1)
            payload = json.loads(buf.getvalue())
            self.assertEqual(payload["error_type"], "ValidationError")
            self.assertIn("voucherCode", payload["error"])

    def test_offers_create_plan_in_required_for_apply(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text("AWIN_API_BASE_URL=https://api.awin.com\nAWIN_API_TOKEN=token\n", encoding="utf-8")
            offer_path = Path(td) / "offer.json"
            self._write_offer_file(
                offer_path,
                {
                    "title": "Spring Offer",
                    "description": "Long enough description",
                    "terms": "Use this code at checkout",
                    "type": "promotion",
                    "url": "https://example.com/offers/spring",
                    "startDate": "2026-06-01",
                    "endDate": "2026-06-30",
                    "appliesToAllRegions": True,
                    "promotionCategories": ["cat"],
                },
            )

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main([
                    "--output",
                    "json",
                    "--env-file",
                    str(env_path),
                    "offers",
                    "create",
                    "--advertiser-id",
                    "123",
                    "--offer-file",
                    str(offer_path),
                    "--apply",
                    "--yes",
                    "--ack-irreversible",
                ])
            self.assertEqual(rc, 1)
            payload = json.loads(buf.getvalue())
            self.assertEqual(payload["error_type"], "SafetyError")
            self.assertIn("requires --apply with --plan-in", payload["error"])

    def test_offers_create_rejects_plan_drift(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text("AWIN_API_BASE_URL=https://api.awin.com\nAWIN_API_TOKEN=token\n", encoding="utf-8")
            offer_path = Path(td) / "offer.json"
            self._write_offer_file(
                offer_path,
                {
                    "title": "Spring Offer",
                    "description": "Long enough description",
                    "terms": "Use this code at checkout",
                    "type": "promotion",
                    "url": "https://example.com/offers/spring",
                    "startDate": "2026-06-01",
                    "endDate": "2026-06-30",
                    "appliesToAllRegions": True,
                    "promotionCategories": ["cat"],
                },
            )
            plan_path = Path(td) / "plan.json"

            with redirect_stdout(io.StringIO()):
                main([
                    "--output",
                    "json",
                    "--env-file",
                    str(env_path),
                    "offers",
                    "create",
                    "--advertiser-id",
                    "123",
                    "--offer-file",
                    str(offer_path),
                    "--plan-out",
                    str(plan_path),
                ])

            self._write_offer_file(
                offer_path,
                {
                    "title": "Spring Offer updated",
                    "description": "Long enough description",
                    "terms": "Use this code at checkout",
                    "type": "promotion",
                    "url": "https://example.com/offers/spring",
                    "startDate": "2026-06-01",
                    "endDate": "2026-06-30",
                    "appliesToAllRegions": True,
                    "promotionCategories": ["cat"],
                },
            )

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main([
                    "--output",
                    "json",
                    "--env-file",
                    str(env_path),
                    "offers",
                    "create",
                    "--advertiser-id",
                    "123",
                    "--offer-file",
                    str(offer_path),
                    "--apply",
                    "--yes",
                    "--ack-irreversible",
                    "--plan-in",
                    str(plan_path),
                ])
            self.assertEqual(rc, 1)
            payload = json.loads(buf.getvalue())
            self.assertEqual(payload["error_type"], "SafetyError")
            self.assertIn("offer file changed since --plan-in was created", payload["error"])


class TestProductFeedsUploadCommand(unittest.TestCase):
    def _write_feed_file(self, path: Path, lines: list[dict[str, str]]) -> None:
        data = "\n".join(json.dumps(row, ensure_ascii=False) for row in lines)
        path.write_text(data + "\n", encoding="utf-8")

    def test_product_feeds_upload_rejects_missing_required_fields(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text("AWIN_API_BASE_URL=https://api.awin.com\nAWIN_API_TOKEN=token\n", encoding="utf-8")
            feed_path = Path(td) / "feed.jsonl"
            self._write_feed_file(
                feed_path,
                [
                    {
                        "id": "p1",
                        "title": "Product",
                        "description": "desc",
                        "link": "https://x",
                        # image_link missing
                    }
                ],
            )

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main([
                    "--output",
                    "json",
                    "--env-file",
                    str(env_path),
                    "product-feeds",
                    "upload",
                    "--advertiser-id",
                    "123",
                    "--vertical",
                    "retail",
                    "--locale",
                    "en_GB",
                    "--feed-file",
                    str(feed_path),
                ])
            self.assertEqual(rc, 1)
            payload = json.loads(buf.getvalue())
            self.assertEqual(payload["error_type"], "ValidationError")
            self.assertIn("missing required field(s)", payload["error"])

    def test_product_feeds_upload_rejects_invalid_jsonl_line(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text("AWIN_API_BASE_URL=https://api.awin.com\nAWIN_API_TOKEN=token\n", encoding="utf-8")
            feed_path = Path(td) / "feed.jsonl"
            feed_path.write_text(
                '{"id": "p1", "title": "Product", "description": "desc", "link": "https://x", "image_link": "https://x/1"}\n{bad',
                encoding="utf-8",
            )

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main([
                    "--output",
                    "json",
                    "--env-file",
                    str(env_path),
                    "product-feeds",
                    "upload",
                    "--advertiser-id",
                    "123",
                    "--vertical",
                    "retail",
                    "--locale",
                    "en_GB",
                    "--feed-file",
                    str(feed_path),
                ])
            self.assertEqual(rc, 1)
            payload = json.loads(buf.getvalue())
            self.assertEqual(payload["error_type"], "ValidationError")
            self.assertIn("not valid JSONL", payload["error"])

    @patch.object(HttpClient, "request")
    def test_product_feeds_upload_auth_mode_is_bearer_only(self, request_mock) -> None:
        request_mock.return_value = HttpResponse(
            status=200,
            headers={},
            body=b'{"status":"ok"}',
            url="https://api.awin.com/advertisers/123/awinfeeds/retail/en_GB/products",
        )
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text("AWIN_API_BASE_URL=https://api.awin.com\nAWIN_API_TOKEN=token\n", encoding="utf-8")
            feed_path = Path(td) / "feed.jsonl"
            self._write_feed_file(
                feed_path,
                [
                    {
                        "id": "p1",
                        "title": "Product",
                        "description": "desc",
                        "link": "https://x",
                        "image_link": "https://x/1",
                    }
                ],
            )
            plan_path = Path(td) / "plan.json"

            with redirect_stdout(io.StringIO()):
                main([
                    "--output",
                    "json",
                    "--env-file",
                    str(env_path),
                    "product-feeds",
                    "upload",
                    "--advertiser-id",
                    "123",
                    "--vertical",
                    "retail",
                    "--locale",
                    "en_GB",
                    "--feed-file",
                    str(feed_path),
                    "--plan-out",
                    str(plan_path),
                ])

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main([
                    "--output",
                    "json",
                    "--env-file",
                    str(env_path),
                    "product-feeds",
                    "upload",
                    "--advertiser-id",
                    "123",
                    "--vertical",
                    "retail",
                    "--locale",
                    "en_GB",
                    "--feed-file",
                    str(feed_path),
                    "--apply",
                    "--yes",
                    "--ack-irreversible",
                    "--plan-in",
                    str(plan_path),
                ])
            self.assertEqual(rc, 0)
            called_kwargs = request_mock.call_args.kwargs
            called_args = request_mock.call_args.args
            self.assertEqual(called_args[0], "POST")
            self.assertEqual(called_args[1], "https://api.awin.com/advertisers/123/awinfeeds/retail/en_GB/products")
            self.assertEqual(called_kwargs["headers"]["Authorization"], "Bearer token")
            self.assertNotIn("accessToken", called_kwargs["params"])

    @patch.object(HttpClient, "request")
    def test_product_feeds_upload_rejects_validation_errors_on_success_status(self, request_mock) -> None:
        request_mock.return_value = HttpResponse(
            status=200,
            headers={},
            body=b'{"status":"ok","errors":[{"row":1,"error":"bad price"}]}',
            url="https://api.awin.com/advertisers/123/awinfeeds/retail/en_GB/products",
        )
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text("AWIN_API_BASE_URL=https://api.awin.com\nAWIN_API_TOKEN=token\n", encoding="utf-8")
            feed_path = Path(td) / "feed.jsonl"
            self._write_feed_file(
                feed_path,
                [
                    {
                        "id": "p1",
                        "title": "Product",
                        "description": "desc",
                        "link": "https://x",
                        "image_link": "https://x/1",
                    }
                ],
            )
            plan_path = Path(td) / "plan.json"

            with redirect_stdout(io.StringIO()):
                main([
                    "--output",
                    "json",
                    "--env-file",
                    str(env_path),
                    "product-feeds",
                    "upload",
                    "--advertiser-id",
                    "123",
                    "--vertical",
                    "retail",
                    "--locale",
                    "en_GB",
                    "--feed-file",
                    str(feed_path),
                    "--plan-out",
                    str(plan_path),
                ])

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main([
                    "--output",
                    "json",
                    "--env-file",
                    str(env_path),
                    "product-feeds",
                    "upload",
                    "--advertiser-id",
                    "123",
                    "--vertical",
                    "retail",
                    "--locale",
                    "en_GB",
                    "--feed-file",
                    str(feed_path),
                    "--apply",
                    "--yes",
                    "--ack-irreversible",
                    "--plan-in",
                    str(plan_path),
                ])
            self.assertEqual(rc, 1)
            payload = json.loads(buf.getvalue())
            self.assertEqual(payload["error_type"], "ValidationError")
            self.assertIn("validation failed", payload["error"])

    def test_product_feeds_upload_plan_in_required_for_apply(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text("AWIN_API_BASE_URL=https://api.awin.com\nAWIN_API_TOKEN=token\n", encoding="utf-8")
            feed_path = Path(td) / "feed.jsonl"
            self._write_feed_file(
                feed_path,
                [
                    {
                        "id": "p1",
                        "title": "Product",
                        "description": "desc",
                        "link": "https://x",
                        "image_link": "https://x/1",
                    }
                ],
            )

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main([
                    "--output",
                    "json",
                    "--env-file",
                    str(env_path),
                    "product-feeds",
                    "upload",
                    "--advertiser-id",
                    "123",
                    "--vertical",
                    "retail",
                    "--locale",
                    "en_GB",
                    "--feed-file",
                    str(feed_path),
                    "--apply",
                    "--yes",
                    "--ack-irreversible",
                ])
            self.assertEqual(rc, 1)
            payload = json.loads(buf.getvalue())
            self.assertEqual(payload["error_type"], "SafetyError")
            self.assertIn("requires --apply with --plan-in", payload["error"])

    @patch.object(HttpClient, "request")
    def test_product_feeds_upload_rejects_drifted_feed_file(self, request_mock) -> None:
        request_mock.return_value = HttpResponse(
            status=200,
            headers={},
            body=b'{"status":"ok"}',
            url="https://api.awin.com/advertisers/123/awinfeeds/retail/en_GB/products",
        )
        with tempfile.TemporaryDirectory() as td:
            env_path = Path(td) / ".env"
            env_path.write_text("AWIN_API_BASE_URL=https://api.awin.com\nAWIN_API_TOKEN=token\n", encoding="utf-8")
            feed_path = Path(td) / "feed.jsonl"
            self._write_feed_file(
                feed_path,
                [
                    {
                        "id": "p1",
                        "title": "Product",
                        "description": "desc",
                        "link": "https://x",
                        "image_link": "https://x/1",
                    }
                ],
            )
            plan_path = Path(td) / "plan.json"

            with redirect_stdout(io.StringIO()):
                main([
                    "--output",
                    "json",
                    "--env-file",
                    str(env_path),
                    "product-feeds",
                    "upload",
                    "--advertiser-id",
                    "123",
                    "--vertical",
                    "retail",
                    "--locale",
                    "en_GB",
                    "--feed-file",
                    str(feed_path),
                    "--plan-out",
                    str(plan_path),
                ])

            self._write_feed_file(
                feed_path,
                [
                    {
                        "id": "p1",
                        "title": "Product A",
                        "description": "desc",
                        "link": "https://x",
                        "image_link": "https://x/1",
                    },
                    {
                        "id": "p2",
                        "title": "Product B",
                        "description": "desc2",
                        "link": "https://x2",
                        "image_link": "https://x2/1",
                    },
                ],
            )

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main([
                    "--output",
                    "json",
                    "--env-file",
                    str(env_path),
                    "product-feeds",
                    "upload",
                    "--advertiser-id",
                    "123",
                    "--vertical",
                    "retail",
                    "--locale",
                    "en_GB",
                    "--feed-file",
                    str(feed_path),
                    "--apply",
                    "--yes",
                    "--ack-irreversible",
                    "--plan-in",
                    str(plan_path),
                ])
            self.assertEqual(rc, 1)
            payload = json.loads(buf.getvalue())
            self.assertEqual(payload["error_type"], "SafetyError")
            self.assertIn("feed file changed since --plan-in was created", payload["error"])

    def test_product_feeds_upload_enforces_max_rows(self) -> None:
        lines = [
            {
                "id": "p1",
                "title": "Product",
                "description": "desc",
                "link": "https://x",
                "image_link": "https://x/1",
            }
            for _ in range(3)
        ]
        with tempfile.TemporaryDirectory() as td:
            feed_path = Path(td) / "feed.jsonl"
            self._write_feed_file(feed_path, lines)

            with patch.object(product_feeds_cmd, "_MAX_PRODUCTS", 2):
                with self.assertRaises(ValidationError):
                    product_feeds_cmd._load_feed_payload(str(feed_path))

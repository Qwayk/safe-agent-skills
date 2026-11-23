from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from awin_advertiser_safe_agent_cli.cli import main
from awin_advertiser_safe_agent_cli.http import HttpResponse, HttpStatusError


class TestWriteResults(unittest.TestCase):
    def setUp(self) -> None:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.settings = self.root / ".env"
        self.settings.write_text("AWIN_API_TOKEN=fixture-token\nAWIN_ADVERTISER_ID=111\n")
        self.orders = self.root / "orders.json"
        self.orders.write_text(json.dumps([
            {"orderReference": ref, "amount": 10, "currency": "GBP", "channel": "aw", "awc": "fixture-click",
             "commissionGroups": [{"code": "DEFAULT", "amount": 10}]}
            for ref in ("order-1", "order-2")
        ]))
        self.offer = self.root / "offer.json"
        self.offer.write_text(json.dumps({
            "title": "Example offer", "description": "An example", "terms": "Sample terms", "type": "promotion",
            "url": "https://example.com", "startDate": "2026-11-23", "endDate": "2026-11-24",
            "appliesToAllRegions": True, "promotionCategories": [1],
        }))
        self.batch = self.root / "batch.json"
        self.batch.write_text('[{"action":"approve","transaction":{"transactionId":123}}]')
        self.feed = self.root / "feed.jsonl"
        self.feed.write_bytes(
            b'{"id":"1","title":"Example","description":"Sample","link":"https://example.com","image_link":"https://example.com/image"}\r\n'
        )
        self.commands = {
            "orders": ["conversion", "orders", "create", "--orders-file", str(self.orders)],
            "offer": ["offers", "create", "--offer-file", str(self.offer)],
            "batch": ["transactions", "batch", "validate", "--batch-file", str(self.batch)],
            "feed": ["product-feeds", "upload", "--vertical", "retail", "--locale", "en_GB", "--feed-file", str(self.feed)],
        }

    def run_tool(self, name: str, *flags: str) -> tuple[int, dict]:
        with redirect_stdout(out := io.StringIO()):
            rc = main(["--env-file", str(self.settings), *flags, *self.commands[name], "--advertiser-id", "111"])
        return rc, json.loads(out.getvalue())

    def save_plan(self, name: str) -> Path:
        plan = self.root / (name + "-plan.json")
        with patch("awin_advertiser_safe_agent_cli.http.HttpClient.request") as send:
            rc, _ = self.run_tool(name, "--plan-out", str(plan))
            self.assertEqual(rc, 0)
            send.assert_not_called()
        return plan

    def apply_reply(self, name: str, status: int, body: dict) -> tuple[int, dict, object]:
        plan = self.save_plan(name)
        response = HttpResponse(status, {}, json.dumps(body).encode(), "https://api.awin.com")
        with patch("awin_advertiser_safe_agent_cli.http.HttpClient.request", return_value=response) as send:
            rc, result = self.run_tool(name, "--apply", "--yes", "--ack-irreversible", "--plan-in", str(plan))
        send.assert_called_once()
        self.assertEqual(json.loads(Path(result["receipt_out"]).read_text()), result["receipt"])
        return rc, result, send.call_args

    def test_all_write_plans_refuse_a_changed_token(self) -> None:
        for name in self.commands:
            with self.subTest(name=name):
                self.settings.write_text("AWIN_API_TOKEN=fixture-token\n")
                plan = self.save_plan(name)
                self.settings.write_text("AWIN_API_TOKEN=fixture-replacement\n")
                with patch("awin_advertiser_safe_agent_cli.http.HttpClient.request") as send:
                    rc, result = self.run_tool(name, "--apply", "--yes", "--ack-irreversible", "--plan-in", str(plan))
                self.assertNotEqual(rc, 0)
                self.assertEqual(result["error_type"], "SafetyError")
                send.assert_not_called()

    def test_older_plan_has_to_be_recreated(self) -> None:
        plan = self.save_plan("offer")
        data = json.loads(plan.read_text())
        del data["baseline"]["credential_fingerprint"]
        plan.write_text(json.dumps(data))
        with patch("awin_advertiser_safe_agent_cli.http.HttpClient.request") as send:
            rc, result = self.run_tool("offer", "--apply", "--yes", "--ack-irreversible", "--plan-in", str(plan))
        self.assertEqual(rc, 1)
        self.assertEqual(result["error_type"], "SafetyError")
        send.assert_not_called()

    def test_changed_input_cannot_use_the_old_feed_plan(self) -> None:
        plan = self.save_plan("feed")
        self.feed.write_bytes(self.feed.read_bytes().replace(b"Sample", b"Changed"))
        with patch("awin_advertiser_safe_agent_cli.http.HttpClient.request") as send:
            rc, result = self.run_tool("feed", "--apply", "--yes", "--ack-irreversible", "--plan-in", str(plan))
        self.assertEqual(rc, 1)
        self.assertEqual(result["error_type"], "SafetyError")
        send.assert_not_called()

    def test_accepted_orders_are_pending(self) -> None:
        rc, result, _ = self.apply_reply("orders", 202, {"batchId": "batch-1"})
        self.assertEqual(rc, 0)
        self.assertEqual(result["result"]["state"], "pending")
        self.assertEqual(result["result"]["batch_id"], "batch-1")
        self.assertFalse(result["receipt"]["verification"]["ok"])

    def test_partly_failed_orders_are_not_reported_as_complete(self) -> None:
        rc, result, _ = self.apply_reply("orders", 206, {
            "batchId": "batch-1", "successfulOrders": [{"orderReference": "order-1"}],
            "failedOrders": [{"order": {"orderReference": "order-2"}, "errors": [{"message": "invalid amount"}]}],
        })
        self.assertEqual(rc, 1)
        self.assertEqual(result["result"]["state"], "partial")
        self.assertEqual(result["result"]["successful_orders"], 1)
        self.assertEqual(result["result"]["failed_order_references"], ["order-2"])
        self.assertFalse(result["receipt"]["verification"]["ok"])

    def test_batch_receipt_keeps_job_id(self) -> None:
        rc, result, _ = self.apply_reply("batch", 200, {"status": "pending", "jobId": "job-7"})
        self.assertEqual(rc, 0)
        self.assertEqual(result["result"]["job_id"], "job-7")
        self.assertEqual(result["result"]["state"], "pending")
        self.assertFalse(result["receipt"]["verification"]["ok"])

    def test_documented_inner_batch_status(self) -> None:
        for code, state, expected_rc in ((200, "confirmed", 0), (304, "unchanged", 0), (422, "rejected", 1)):
            with self.subTest(code=code):
                rc, result, _ = self.apply_reply("batch", 200, {"statusCodeValue": code, "body": {}})
                self.assertEqual(rc, expected_rc)
                self.assertEqual(result["result"]["awin_status"], code)
                self.assertEqual(result["result"]["state"], state)
                self.assertEqual(result["receipt"]["verification"]["ok"], rc == 0)

    def test_feed_receipt_preserves_version_and_exact_uploaded_bytes(self) -> None:
        rc, result, call = self.apply_reply("feed", 200, {"productsReceived": 1, "version": 18})
        self.assertEqual(rc, 0)
        self.assertEqual(result["result"]["feed_version"], 18)
        self.assertEqual(call.kwargs["headers"]["content-type"], "application/jsonlines")
        self.assertEqual(call.kwargs["data"], self.feed.read_bytes())
        self.assertTrue(result["receipt"]["verification"]["ok"])

    def test_feed_without_a_confirmed_count_and_version_is_unclear(self) -> None:
        for body in ({}, {"productsReceived": 2, "version": 18}):
            with self.subTest(body=body):
                rc, result, _ = self.apply_reply("feed", 200, body)
                self.assertEqual(rc, 1)
                self.assertEqual(result["result"]["state"], "unknown")
                self.assertFalse(result["receipt"]["verification"]["ok"])

    def test_lost_reply_writes_unclear_receipt_without_a_retry(self) -> None:
        plan = self.save_plan("offer")
        with patch("awin_advertiser_safe_agent_cli.http.HttpClient.request", side_effect=RuntimeError("Timed out: fixture-token")) as send:
            rc, result = self.run_tool("offer", "--apply", "--yes", "--ack-irreversible", "--plan-in", str(plan))
        send.assert_called_once()
        self.assertEqual(rc, 1)
        self.assertEqual(result["result"]["state"], "unknown")
        self.assertIsNone(result["receipt"]["changed"])
        self.assertNotIn("fixture-token", Path(result["receipt_out"]).read_text())

    def test_a_reported_http_rejection_writes_a_receipt(self) -> None:
        plan = self.save_plan("offer")
        error = HttpStatusError(400, "Invalid offer")
        with patch("awin_advertiser_safe_agent_cli.http.HttpClient.request", side_effect=error):
            rc, result = self.run_tool("offer", "--apply", "--yes", "--ack-irreversible", "--plan-in", str(plan))
        self.assertEqual(rc, 1)
        self.assertEqual(result["result"]["state"], "rejected")
        self.assertFalse(result["receipt"]["changed"])
        self.assertTrue(Path(result["receipt_out"]).is_file())

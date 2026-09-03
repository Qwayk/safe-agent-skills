from __future__ import annotations

import argparse
import unittest
from pathlib import Path

from elevenlabs_api_tool.commands.operation_runner import configure_operation_parser
from elevenlabs_api_tool.commands.usage import cmd_usage_get
from elevenlabs_api_tool.inventory_generator import build_inventory
from elevenlabs_api_tool.operations import INVENTORY, OPERATIONS, Operation


class TestRuntimeContracts(unittest.TestCase):
    def test_sensitive_get_safety_matches_generated_coverage(self) -> None:
        paths = {
            "/v1/convai/conversations/{conversation_id}/sip-messages",
            "/v1/convai/conversations/messages/text-search",
            "/v1/convai/conversations/messages/smart-search",
            "/v1/convai/phone-numbers/{phone_number_id}/sip-messages",
        }
        coverage = {}
        for line in Path("docs/api_coverage.md").read_text(encoding="utf-8").splitlines():
            if line.startswith("| GET "):
                endpoint, _, _, _, safety, _ = line.strip().strip("|").split("|", 5)
                path = endpoint[4:].strip()
                if path in paths:
                    coverage[path] = tuple(x.strip() for x in safety.split(","))
        for path in paths:
            runtime = next(e for e in INVENTORY if e.path == path and e.method == "GET")
            self.assertEqual(("read", "sensitive_output"), tuple(runtime.safety))
            self.assertEqual(tuple(runtime.safety), coverage[path])

    def test_usage_get_uses_stable_post_analytics_contract(self) -> None:
        calls: list[dict[str, object]] = []

        class Response:
            def json(self):
                return {"data": []}

        class Client:
            def request(self, method, url, **kwargs):
                calls.append({"method": method, "url": url, **kwargs})
                return Response()

        class Out:
            def emit(self, value):
                self.value = value

        class Audit:
            def write(self, *args):
                pass

        class Config:
            token = "token"
            base_url = "https://api.example"

        ctx = {"live": True, "cfg": Config(), "http_client": Client(), "out": Out(), "audit": Audit()}
        args = argparse.Namespace(
            start_unix=1700000000000,
            end_unix=1700086400000,
            include_workspace_metrics=False,
            breakdown_type=None,
            aggregation_interval="day",
            aggregation_bucket_size=None,
            metric=None,
        )
        cmd_usage_get(args, ctx)
        self.assertEqual("POST", calls[0]["method"])
        self.assertEqual("https://api.example/v1/workspace/analytics/query/usage-by-product-over-time", calls[0]["url"])
        self.assertEqual({"start_time": 1700000000000, "end_time": 1700086400000, "interval_seconds": 86400}, calls[0]["json"])

    def test_contract_metadata_is_generated_for_usage_post(self) -> None:
        entry = next(e for e in INVENTORY if e.name == "usage_by_product_over_time")
        self.assertEqual((), entry.required_path_params)
        self.assertEqual((), entry.required_query_params)
        self.assertEqual((), entry.required_headers)
        self.assertTrue(entry.request_body_required)
        self.assertEqual(("application/json",), entry.request_body_content_types)
        self.assertIn("application/json", entry.response_content_types)

    def test_runtime_operation_preserves_request_and_webhook_contract(self) -> None:
        entry = next(e for e in INVENTORY if e.name == "handle_twilio_outbound_call")
        operation = next(o for o in OPERATIONS if o.name == entry.name)
        self.assertEqual(entry.request_body_fields, operation.request_body_fields)
        self.assertEqual(entry.webhook_events, operation.webhook_events)

    def test_wss_and_callback_rows_have_no_cli_or_wss_out_requirement(self) -> None:
        callback_rows = [e for e in INVENTORY if e.method == "CALLBACK"]
        self.assertTrue(callback_rows)
        self.assertTrue(all(e.cli_command is None for e in callback_rows))
        op = Operation("wss", "Test", "", "WEBSOCKET", "wss://example", "wss test", ("write", "binary_output"), "https://example")
        parser = argparse.ArgumentParser()
        configure_operation_parser(parser, op)
        self.assertIsNone(parser.parse_args([]).out)

    def test_generated_inventory_includes_operation_contract_helpers(self) -> None:
        rows = build_inventory()
        row = next(r for r in rows if r["name"] == "usage_by_product_over_time")
        for key in ("required_path_params", "required_query_params", "required_headers", "request_body_required", "request_body_content_types", "response_content_types"):
            self.assertIn(key, row)

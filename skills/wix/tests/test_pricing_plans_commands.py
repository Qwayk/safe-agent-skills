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
from wix_safe_agent_cli.commands import pricing_plans
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = (action, payload)


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestPricingPlansCommands(unittest.TestCase):
    def _ctx(self, **overrides) -> dict:
        cfg = SimpleNamespace(
            base_url="https://www.wixapis.com",
            timeout_s=30.0,
            access_token="site-app-token",
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
            "command_str": "wix-safe-agent-cli pricing-plans",
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

    @staticmethod
    def _current_plan(*, name: str = "Starter") -> dict:
        return {"id": "plan-1", "name": name, "revision": "3"}

    def _write_plan(self, plan: dict) -> str:
        handle = tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json")
        json.dump(plan, handle)
        handle.close()
        return handle.name

    def test_parser_recognizes_pricing_plan_subcommands(self) -> None:
        parser = build_parser()

        get_args = parser.parse_args(["pricing-plans", "get", "--plan-id", "plan-1"])
        self.assertEqual(get_args.pricing_plans_cmd, "get")
        self.assertFalse(get_args.write_capable)

        query_args = parser.parse_args(["pricing-plans", "query"])
        self.assertEqual(query_args.pricing_plans_cmd, "query")
        self.assertFalse(query_args.write_capable)

        search_args = parser.parse_args(["pricing-plans", "search"])
        self.assertEqual(search_args.pricing_plans_cmd, "search")
        self.assertFalse(search_args.write_capable)

        count_args = parser.parse_args(["pricing-plans", "count"])
        self.assertEqual(count_args.pricing_plans_cmd, "count")
        self.assertFalse(count_args.write_capable)

        create_args = parser.parse_args(
            ["pricing-plans", "create", "--pricing-plan-json", '{"name":"Starter"}']
        )
        self.assertEqual(create_args.pricing_plans_cmd, "create")
        self.assertTrue(create_args.write_capable)

        update_args = parser.parse_args(
            ["pricing-plans", "update", "--plan-id", "plan-1", "--pricing-plan-json", '{"name":"Pro"}']
        )
        self.assertEqual(update_args.pricing_plans_cmd, "update")
        self.assertTrue(update_args.write_capable)

        delete_args = parser.parse_args(["pricing-plans", "delete", "--plan-id", "plan-1"])
        self.assertEqual(delete_args.pricing_plans_cmd, "delete")
        self.assertTrue(delete_args.write_capable)

        bulk_update_args = parser.parse_args(
            [
                "pricing-plans",
                "bulk-update",
                "--bulk-update-json",
                '[{"id":"plan-1","revision":"1","pricingVariants":[{"id":"pv-1","name":"Monthly","billingTerms":{"billingCycle":{"period":"MONTH","count":"1"},"startType":"ON_PURCHASE","endType":"UNTIL_CANCELLED"},"pricingStrategies":[{"flatRate":{"amount":"10"}}]}]}]',
            ]
        )
        self.assertEqual(bulk_update_args.pricing_plans_cmd, "bulk-update")
        self.assertTrue(bulk_update_args.write_capable)

    @patch("wix_safe_agent_cli.commands.pricing_plans.HttpClient")
    def test_get_builds_expected_request(self, mock_client) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"plan": {"id": "plan-1"}})
        args = SimpleNamespace(plan_id="plan-1")

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = pricing_plans.cmd_pricing_plans_get(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["request"]["path"], "/pricing-plans/v3/plans/plan-1")

    @patch("wix_safe_agent_cli.commands.pricing_plans.HttpClient")
    def test_query_builds_expected_request(self, mock_client) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"plans": []})
        args = SimpleNamespace(query_json='{"filter":{"archived":{"$eq":false}}}')

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = pricing_plans.cmd_pricing_plans_query(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertEqual(payload["request"]["path"], "/pricing-plans/v3/plans/query")
        self.assertEqual(payload["request"]["body"], {"filter": {"archived": {"$eq": False}}})

    @patch("wix_safe_agent_cli.commands.pricing_plans.HttpClient")
    def test_search_builds_expected_request(self, mock_client) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"plans": []})
        args = SimpleNamespace(search_json='{"search":{"expression":"gold"}}')

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = pricing_plans.cmd_pricing_plans_search(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertEqual(payload["request"]["path"], "/pricing-plans/v3/plans/search")
        self.assertEqual(payload["request"]["body"], {"search": {"expression": "gold"}})

    @patch("wix_safe_agent_cli.commands.pricing_plans.HttpClient")
    def test_count_wraps_filter_json(self, mock_client) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"count": 2})
        args = SimpleNamespace(filter_json='{"archived":{"$eq":false}}')

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = pricing_plans.cmd_pricing_plans_count(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertEqual(payload["request"]["path"], "/pricing-plans/v3/plans/count")
        self.assertEqual(payload["request"]["body"], {"filter": {"archived": {"$eq": False}}})

    def test_create_dry_run_builds_plan(self) -> None:
        args = SimpleNamespace(pricing_plan_json='{"name":"Starter"}')

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = pricing_plans.cmd_pricing_plans_create(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["method"], "pricing-plans.create")
        self.assertFalse(payload["plan"]["state_capture"]["before_state_available"])

    @patch("wix_safe_agent_cli.commands.pricing_plans.HttpClient")
    def test_create_apply_requires_reviewed_plan(self, mock_client) -> None:
        args = SimpleNamespace(pricing_plan_json='{"name":"Starter"}')

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = pricing_plans.cmd_pricing_plans_create(args, self._ctx(apply=True, yes=True))
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertEqual(mock_client.return_value.request.call_count, 0)

    @patch("wix_safe_agent_cli.commands.pricing_plans.HttpClient")
    def test_update_apply_requires_reviewed_plan_before_http(self, mock_client) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"plan": self._current_plan()})
        args = SimpleNamespace(plan_id="plan-1", pricing_plan_json='{"name":"Pro"}')

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = pricing_plans.cmd_pricing_plans_update(args, self._ctx(apply=True, yes=True))
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertEqual(payload["method"], "pricing-plans.update")
        self.assertEqual(mock_client.return_value.request.call_count, 1)

    @patch("wix_safe_agent_cli.commands.pricing_plans.HttpClient")
    def test_update_apply_uses_plan_in_and_verifies(self, mock_client) -> None:
        mock_client.return_value.request.side_effect = [
            _DummyResponse({"plan": self._current_plan(name="Starter")}),
            _DummyResponse({"plan": self._current_plan(name="Starter")}),
            _DummyResponse({"plan": self._current_plan(name="Starter")}),
            _DummyResponse({"plan": {"id": "plan-1", "name": "Pro", "revision": "4"}}),
            _DummyResponse({"plan": {"id": "plan-1", "name": "Pro", "revision": "4"}}),
        ]
        args = SimpleNamespace(plan_id="plan-1", pricing_plan_json='{"name":"Pro"}')

        dry_buf = io.StringIO()
        with redirect_stdout(dry_buf):
            pricing_plans.cmd_pricing_plans_update(args, self._ctx())
        plan_path = self._write_plan(json.loads(dry_buf.getvalue())["plan"])
        try:
            apply_ctx = self._ctx(apply=True, yes=True, plan_in=plan_path)
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = pricing_plans.cmd_pricing_plans_update(args, apply_ctx)
            payload = json.loads(buf.getvalue())

            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["receipt"]["verification"]["after"]["name"], "Pro")
        finally:
            Path(plan_path).unlink()

    @patch("wix_safe_agent_cli.commands.pricing_plans.HttpClient")
    def test_delete_without_ack_stays_dry_run(self, mock_client) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"plan": self._current_plan()})
        args = SimpleNamespace(plan_id="plan-1")

        dry_buf = io.StringIO()
        with redirect_stdout(dry_buf):
            pricing_plans.cmd_pricing_plans_delete(args, self._ctx())
        plan_path = self._write_plan(json.loads(dry_buf.getvalue())["plan"])
        try:
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = pricing_plans.cmd_pricing_plans_delete(
                    args,
                    self._ctx(apply=True, yes=True, plan_in=plan_path, ack_irreversible=False),
                )
            payload = json.loads(buf.getvalue())

            self.assertEqual(rc, 0)
            self.assertTrue(payload["dry_run"])
            self.assertFalse(payload.get("refused", False))
        finally:
            Path(plan_path).unlink()

    @patch("wix_safe_agent_cli.commands.pricing_plans.HttpClient")
    def test_delete_apply_requires_plan_in_before_http(self, mock_client) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"plan": self._current_plan()})
        args = SimpleNamespace(plan_id="plan-1")

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = pricing_plans.cmd_pricing_plans_delete(
                args,
                self._ctx(apply=True, yes=True, ack_irreversible=True),
            )
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertEqual(mock_client.return_value.request.call_count, 1)

    @patch("wix_safe_agent_cli.commands.pricing_plans.HttpClient")
    def test_delete_apply_verifies_404(self, mock_client) -> None:
        mock_client.return_value.request.side_effect = [
            _DummyResponse({"plan": self._current_plan()}),
            _DummyResponse({"plan": self._current_plan()}),
            _DummyResponse({"plan": self._current_plan()}),
            _DummyResponse({}),
            RuntimeError("HTTP 404 for GET https://www.wixapis.com/pricing-plans/v3/plans/plan-1\n{}"),
        ]
        args = SimpleNamespace(plan_id="plan-1")

        dry_buf = io.StringIO()
        with redirect_stdout(dry_buf):
            pricing_plans.cmd_pricing_plans_delete(args, self._ctx())
        plan_path = self._write_plan(json.loads(dry_buf.getvalue())["plan"])
        try:
            apply_ctx = self._ctx(apply=True, yes=True, plan_in=plan_path, ack_irreversible=True)
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = pricing_plans.cmd_pricing_plans_delete(args, apply_ctx)
            payload = json.loads(buf.getvalue())

            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["receipt"]["verification"]["actual_http_status"], 404)
        finally:
            Path(plan_path).unlink()

    def test_bulk_update_dry_run_builds_plan(self) -> None:
        args = SimpleNamespace(
            bulk_update_json='[{"id":"plan-1","revision":"3","pricingVariants":[{"id":"pv-1","name":"Monthly","billingTerms":{"billingCycle":{"period":"MONTH","count":"1"},"startType":"ON_PURCHASE","endType":"UNTIL_CANCELLED"},"pricingStrategies":[{"flatRate":{"amount":"12"}}]}]}]'
        )
        with patch("wix_safe_agent_cli.commands.pricing_plans.HttpClient") as mock_client:
            mock_client.return_value.request.return_value = _DummyResponse({"plan": self._current_plan()})
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = pricing_plans.cmd_pricing_plans_bulk_update(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["method"], "pricing-plans.bulk-update")
        request_body = payload["plan"]["request"]["body"]
        self.assertEqual(request_body["returnEntity"], True)
        self.assertEqual(request_body["plans"][0]["plan"]["id"], "plan-1")

    @patch("wix_safe_agent_cli.commands.pricing_plans.HttpClient")
    def test_bulk_update_apply_requires_reviewed_plan_before_write(self, mock_client) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"plan": self._current_plan()})
        args = SimpleNamespace(
            bulk_update_json='[{"id":"plan-1","revision":"3","pricingVariants":[{"id":"pv-1","name":"Monthly","billingTerms":{"billingCycle":{"period":"MONTH","count":"1"},"startType":"ON_PURCHASE","endType":"UNTIL_CANCELLED"},"pricingStrategies":[{"flatRate":{"amount":"12"}}]}]}]'
        )

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = pricing_plans.cmd_pricing_plans_bulk_update(args, self._ctx(apply=True, yes=True))
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertEqual(payload["method"], "pricing-plans.bulk-update")
        self.assertEqual(mock_client.return_value.request.call_count, 1)

    def test_bulk_update_rejects_duplicate_plan_ids(self) -> None:
        args = SimpleNamespace(
            bulk_update_json='[{"id":"plan-1","revision":"3","pricingVariants":[{"id":"pv-1","name":"Monthly","billingTerms":{"billingCycle":{"period":"MONTH","count":"1"},"startType":"ON_PURCHASE","endType":"UNTIL_CANCELLED"},"pricingStrategies":[{"flatRate":{"amount":"12"}}]}]},{"id":"plan-1","revision":"4","pricingVariants":[{"id":"pv-2","name":"Yearly","billingTerms":{"billingCycle":{"period":"YEAR","count":"1"},"startType":"ON_PURCHASE","endType":"UNTIL_CANCELLED"},"pricingStrategies":[{"flatRate":{"amount":"120"}}]}]}]'
        )
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = pricing_plans.cmd_pricing_plans_bulk_update(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertIn("duplicate plan id", payload["error"])

    def test_bulk_update_rejects_plan_name_changes(self) -> None:
        args = SimpleNamespace(
            bulk_update_json='[{"id":"plan-1","revision":"3","name":"Renamed","pricingVariants":[{"id":"pv-1","name":"Monthly","billingTerms":{"billingCycle":{"period":"MONTH","count":"1"},"startType":"ON_PURCHASE","endType":"UNTIL_CANCELLED"},"pricingStrategies":[{"flatRate":{"amount":"12"}}]}]}]'
        )
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = pricing_plans.cmd_pricing_plans_bulk_update(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertIn("not supported by Bulk Update Plans", payload["error"])

    @patch("wix_safe_agent_cli.commands.pricing_plans.HttpClient")
    def test_bulk_update_apply_verifies_metadata_and_readback(self, mock_client) -> None:
        updated_plan = {
            "id": "plan-1",
            "name": "Starter",
            "revision": "4",
            "pricingVariants": [
                {
                    "id": "pv-1",
                    "name": "Monthly",
                    "billingTerms": {
                        "billingCycle": {"period": "MONTH", "count": "1"},
                        "startType": "ON_PURCHASE",
                        "endType": "UNTIL_CANCELLED",
                    },
                    "pricingStrategies": [{"flatRate": {"amount": "12"}}],
                }
            ],
        }
        mock_client.return_value.request.side_effect = [
            _DummyResponse({"plan": self._current_plan()}),
            _DummyResponse({"plan": self._current_plan()}),
            _DummyResponse({"plan": self._current_plan()}),
            _DummyResponse(
                {
                    "results": [
                        {"itemMetadata": {"id": "plan-1", "originalIndex": 0, "success": True}, "item": updated_plan}
                    ],
                    "bulkActionMetadata": {"totalSuccesses": 1, "totalFailures": 0, "undetailedFailures": 0},
                }
            ),
            _DummyResponse({"plan": updated_plan}),
        ]
        args = SimpleNamespace(
            bulk_update_json='[{"id":"plan-1","revision":"3","pricingVariants":[{"id":"pv-1","name":"Monthly","billingTerms":{"billingCycle":{"period":"MONTH","count":"1"},"startType":"ON_PURCHASE","endType":"UNTIL_CANCELLED"},"pricingStrategies":[{"flatRate":{"amount":"12"}}]}]}]'
        )

        dry_buf = io.StringIO()
        with redirect_stdout(dry_buf):
            pricing_plans.cmd_pricing_plans_bulk_update(args, self._ctx())
        plan_path = self._write_plan(json.loads(dry_buf.getvalue())["plan"])
        try:
            apply_ctx = self._ctx(apply=True, yes=True, plan_in=plan_path)
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = pricing_plans.cmd_pricing_plans_bulk_update(args, apply_ctx)
            payload = json.loads(buf.getvalue())

            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["receipt"]["verification"]["bulkActionMetadata"]["totalFailures"], 0)
            self.assertEqual(payload["receipt"]["verification"]["after"]["plan-1"]["revision"], "4")
        finally:
            Path(plan_path).unlink()

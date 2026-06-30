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
from wix_safe_agent_cli.commands import coupons
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = (action, payload)


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


def _installed_apps_payload(*apps: str) -> dict:
    return {"site": {"installedWixApps": list(apps)}}


class TestCouponsCommands(unittest.TestCase):
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
            "command_str": "wix-safe-agent-cli coupons",
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
    def _current_coupon(*, coupon_id: str = "coupon-1", amount: int = 20) -> dict:
        return {
            "id": coupon_id,
            "specification": {
                "name": "Summer Sale",
                "code": "SAVE20",
                "startTime": "2026-06-24T00:00:00Z",
                "scope": {"namespace": "stores", "group": "all"},
                "percentOffRate": amount,
            },
        }

    def _write_plan(self, plan: dict) -> str:
        handle = tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json")
        json.dump(plan, handle)
        handle.close()
        return handle.name

    def test_parser_recognizes_coupon_subcommands(self) -> None:
        parser = build_parser()

        get_args = parser.parse_args(["coupons", "get", "--coupon-id", "coupon-1"])
        self.assertEqual(get_args.coupons_cmd, "get")
        self.assertFalse(get_args.write_capable)

        query_args = parser.parse_args(["coupons", "query"])
        self.assertEqual(query_args.coupons_cmd, "query")
        self.assertFalse(query_args.write_capable)

        create_args = parser.parse_args(["coupons", "create", "--coupon-json", '{"specification":{"name":"A","code":"B","startTime":"2026-06-24T00:00:00Z","minimumSubtotal":{"amount":"10"},"percentOffRate":10}}'])
        self.assertEqual(create_args.coupons_cmd, "create")
        self.assertTrue(create_args.write_capable)

        update_args = parser.parse_args(["coupons", "update", "--coupon-id", "coupon-1", "--coupon-json", '{"specification":{"percentOffRate":15}}'])
        self.assertEqual(update_args.coupons_cmd, "update")
        self.assertTrue(update_args.write_capable)

        delete_args = parser.parse_args(["coupons", "delete", "--coupon-id", "coupon-1"])
        self.assertEqual(delete_args.coupons_cmd, "delete")
        self.assertTrue(delete_args.write_capable)

        bulk_create_args = parser.parse_args(["coupons", "bulk-create", "--coupons-json", '[{"specification":{"name":"A","code":"A1","startTime":"2026-06-24T00:00:00Z","minimumSubtotal":{"amount":"10"},"percentOffRate":10}}]'])
        self.assertEqual(bulk_create_args.coupons_cmd, "bulk-create")
        self.assertTrue(bulk_create_args.write_capable)

        bulk_delete_args = parser.parse_args(["coupons", "bulk-delete", "--coupon-ids-json", '["coupon-1"]'])
        self.assertEqual(bulk_delete_args.coupons_cmd, "bulk-delete")
        self.assertTrue(bulk_delete_args.write_capable)

    @patch("wix_safe_agent_cli.commands.coupons.HttpClient")
    def test_get_builds_expected_request(self, mock_client) -> None:
        mock_client.return_value.request.side_effect = [
            _DummyResponse(_installed_apps_payload("stores")),
            _DummyResponse({"coupon": self._current_coupon()}),
        ]
        args = SimpleNamespace(coupon_id="coupon-1")

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = coupons.cmd_coupons_get(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["request"]["path"], "/stores/v2/coupons/coupon-1")

    @patch("wix_safe_agent_cli.commands.coupons.HttpClient")
    def test_query_builds_expected_request(self, mock_client) -> None:
        mock_client.return_value.request.side_effect = [
            _DummyResponse(_installed_apps_payload("pricingPlans")),
            _DummyResponse({"coupons": []}),
        ]
        args = SimpleNamespace(query_json='{"paging":{"limit":25}}')

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = coupons.cmd_coupons_query(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertEqual(payload["request"]["path"], "/stores/v2/coupons/query")
        self.assertEqual(payload["request"]["body"], {"paging": {"limit": 25}})

    def test_create_dry_run_builds_plan(self) -> None:
        args = SimpleNamespace(
            coupon_json='{"specification":{"name":"Summer","code":"SAVE20","startTime":"2026-06-24T00:00:00Z","minimumSubtotal":{"amount":"10"},"percentOffRate":20}}'
        )
        with patch("wix_safe_agent_cli.commands.coupons.HttpClient") as mock_client:
            mock_client.return_value.request.return_value = _DummyResponse(_installed_apps_payload("stores"))
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = coupons.cmd_coupons_create(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["method"], "coupons.create")
        self.assertFalse(payload["plan"]["state_capture"]["before_state_available"])

    @patch("wix_safe_agent_cli.commands.coupons.HttpClient")
    def test_create_apply_requires_reviewed_plan_before_write(self, mock_client) -> None:
        mock_client.return_value.request.return_value = _DummyResponse(_installed_apps_payload("stores"))
        args = SimpleNamespace(
            coupon_json='{"specification":{"name":"Summer","code":"SAVE20","startTime":"2026-06-24T00:00:00Z","minimumSubtotal":{"amount":"10"},"percentOffRate":20}}'
        )

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = coupons.cmd_coupons_create(args, self._ctx(apply=True, yes=True))
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertEqual(mock_client.return_value.request.call_count, 1)

    @patch("wix_safe_agent_cli.commands.coupons.HttpClient")
    def test_update_refuses_coupon_type_change(self, mock_client) -> None:
        mock_client.return_value.request.side_effect = [
            _DummyResponse(_installed_apps_payload("stores")),
            _DummyResponse({"coupon": self._current_coupon()}),
        ]
        args = SimpleNamespace(coupon_id="coupon-1", coupon_json='{"specification":{"fixedPriceAmount":{"amount":"5"}}}')

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = coupons.cmd_coupons_update(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertIn("cannot change the coupon type", payload["reasons"][0])

    @patch("wix_safe_agent_cli.commands.coupons.HttpClient")
    def test_update_apply_uses_plan_in_and_verifies(self, mock_client) -> None:
        mock_client.return_value.request.side_effect = [
            _DummyResponse(_installed_apps_payload("stores")),
            _DummyResponse({"coupon": self._current_coupon(amount=20)}),
            _DummyResponse(_installed_apps_payload("stores")),
            _DummyResponse({"coupon": self._current_coupon(amount=20)}),
            _DummyResponse({"coupon": self._current_coupon(amount=20)}),
            _DummyResponse({}),
            _DummyResponse({"coupon": self._current_coupon(amount=25)}),
        ]
        args = SimpleNamespace(coupon_id="coupon-1", coupon_json='{"specification":{"percentOffRate":25}}')

        dry_buf = io.StringIO()
        with redirect_stdout(dry_buf):
            coupons.cmd_coupons_update(args, self._ctx())
        plan_path = self._write_plan(json.loads(dry_buf.getvalue())["plan"])
        try:
            apply_ctx = self._ctx(apply=True, yes=True, plan_in=plan_path)
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = coupons.cmd_coupons_update(args, apply_ctx)
            payload = json.loads(buf.getvalue())

            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["receipt"]["verification"]["after"]["specification"]["percentOffRate"], 25)
        finally:
            Path(plan_path).unlink()

    @patch("wix_safe_agent_cli.commands.coupons.HttpClient")
    def test_delete_without_ack_stays_dry_run(self, mock_client) -> None:
        mock_client.return_value.request.side_effect = [
            _DummyResponse(_installed_apps_payload("stores")),
            _DummyResponse({"coupon": self._current_coupon()}),
            _DummyResponse(_installed_apps_payload("stores")),
            _DummyResponse({"coupon": self._current_coupon()}),
        ]
        args = SimpleNamespace(coupon_id="coupon-1")

        dry_buf = io.StringIO()
        with redirect_stdout(dry_buf):
            coupons.cmd_coupons_delete(args, self._ctx())
        plan_path = self._write_plan(json.loads(dry_buf.getvalue())["plan"])
        try:
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = coupons.cmd_coupons_delete(args, self._ctx(apply=True, yes=True, plan_in=plan_path))
            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(payload["dry_run"])
            self.assertFalse(payload.get("refused", False))
        finally:
            Path(plan_path).unlink()

    @patch("wix_safe_agent_cli.commands.coupons.HttpClient")
    def test_delete_apply_requires_plan_before_write(self, mock_client) -> None:
        mock_client.return_value.request.side_effect = [
            _DummyResponse(_installed_apps_payload("stores")),
            _DummyResponse({"coupon": self._current_coupon()}),
        ]
        args = SimpleNamespace(coupon_id="coupon-1")

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = coupons.cmd_coupons_delete(args, self._ctx(apply=True, yes=True, ack_irreversible=True))
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertEqual(mock_client.return_value.request.call_count, 2)

    @patch("wix_safe_agent_cli.commands.coupons.HttpClient")
    def test_bulk_create_dry_run_builds_plan(self, mock_client) -> None:
        mock_client.return_value.request.return_value = _DummyResponse(_installed_apps_payload("events"))
        args = SimpleNamespace(
            coupons_json='[{"specification":{"name":"Summer","code":"SAVE20","startTime":"2026-06-24T00:00:00Z","minimumSubtotal":{"amount":"10"},"percentOffRate":20}}]'
        )

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = coupons.cmd_coupons_bulk_create(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["method"], "coupons.bulk-create")

    @patch("wix_safe_agent_cli.commands.coupons.HttpClient")
    def test_bulk_create_apply_requires_reviewed_plan_before_write(self, mock_client) -> None:
        mock_client.return_value.request.return_value = _DummyResponse(_installed_apps_payload("events"))
        args = SimpleNamespace(
            coupons_json='[{"specification":{"name":"Summer","code":"SAVE20","startTime":"2026-06-24T00:00:00Z","minimumSubtotal":{"amount":"10"},"percentOffRate":20}}]'
        )

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = coupons.cmd_coupons_bulk_create(args, self._ctx(apply=True, yes=True))
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertEqual(mock_client.return_value.request.call_count, 1)

    @patch("wix_safe_agent_cli.commands.coupons.HttpClient")
    def test_bulk_delete_apply_uses_plan_in_and_verifies(self, mock_client) -> None:
        mock_client.return_value.request.side_effect = [
            _DummyResponse(_installed_apps_payload("stores")),
            _DummyResponse({"coupon": self._current_coupon(coupon_id="coupon-1")}),
            _DummyResponse({"coupon": self._current_coupon(coupon_id="coupon-2")}),
            _DummyResponse(_installed_apps_payload("stores")),
            _DummyResponse({"coupon": self._current_coupon(coupon_id="coupon-1")}),
            _DummyResponse({"coupon": self._current_coupon(coupon_id="coupon-2")}),
            _DummyResponse({"coupon": self._current_coupon(coupon_id="coupon-1")}),
            _DummyResponse({"coupon": self._current_coupon(coupon_id="coupon-2")}),
            _DummyResponse({}),
            RuntimeError("HTTP 404 Not Found"),
            RuntimeError("HTTP 404 Not Found"),
        ]
        args = SimpleNamespace(coupon_ids_json='["coupon-1","coupon-2"]')

        dry_buf = io.StringIO()
        with redirect_stdout(dry_buf):
            coupons.cmd_coupons_bulk_delete(args, self._ctx())
        plan_path = self._write_plan(json.loads(dry_buf.getvalue())["plan"])
        try:
            apply_ctx = self._ctx(apply=True, yes=True, plan_in=plan_path, ack_irreversible=True)
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = coupons.cmd_coupons_bulk_delete(args, apply_ctx)
            payload = json.loads(buf.getvalue())

            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(len(payload["receipt"]["verification"]["checks"]), 2)
        finally:
            Path(plan_path).unlink()

    @patch("wix_safe_agent_cli.commands.coupons.HttpClient")
    def test_installed_app_precheck_refuses_when_missing(self, mock_client) -> None:
        mock_client.return_value.request.return_value = _DummyResponse(_installed_apps_payload("wix_forms"))
        args = SimpleNamespace(coupon_id="coupon-1")

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = coupons.cmd_coupons_get(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertIn("Required installed Wix app missing for coupons", payload["error"])

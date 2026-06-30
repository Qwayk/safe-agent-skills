from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import bookings_services_v2
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


class TestBookingsServicesV2Parser(unittest.TestCase):
    def test_parser_recognizes_services_v2_commands_and_write_flags(self) -> None:
        parser = build_parser()

        read_args = parser.parse_args(["bookings-services-v2", "get", "--service-id", "svc-1"])
        self.assertEqual(read_args.bookings_services_v2_cmd, "get")
        self.assertFalse(read_args.write_capable)
        self.assertIs(read_args.func, bookings_services_v2.cmd_bookings_services_v2_get)

        write_args = parser.parse_args(
            ["bookings-services-v2", "set-service-locations", "--service-id", "svc-1", "--request-json", "{}"]
        )
        self.assertEqual(write_args.bookings_services_v2_cmd, "set-service-locations")
        self.assertTrue(write_args.write_capable)
        self.assertIs(write_args.func, bookings_services_v2.cmd_bookings_services_v2_set_service_locations)

        expected = {
            "get",
            "query",
            "search",
            "count",
            "create",
            "update",
            "delete",
            "bulk-create",
            "bulk-update",
            "bulk-update-by-filter",
            "bulk-delete",
            "bulk-delete-by-filter",
            "query-policies",
            "query-locations",
            "query-categories",
            "set-service-locations",
            "enable-pricing-plans",
            "disable-pricing-plans",
            "set-custom-slug",
            "validate-slug",
            "clone",
            "create-add-on-group",
            "delete-add-on-group",
            "list-add-on-groups-by-service-id",
            "set-add-ons-for-group",
            "update-add-on-group",
        }
        self.assertEqual(set(parser._subparsers._group_actions[0].choices["bookings-services-v2"]._subparsers._group_actions[0].choices), expected)


class TestBookingsServicesV2Commands(unittest.TestCase):
    def _ctx(self, *, plan_in: str | None = None, apply: bool = False, yes: bool = False, ack: bool = False) -> dict:
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
            "verbose": False,
            "out": Output(mode="json"),
            "audit": _DummyAudit(),
            "plan_in": plan_in,
            "plan_out": None,
            "receipt_out": None,
            "apply": apply,
            "yes": yes,
            "ack_irreversible": ack,
            "enforce_reviewed_plan": True,
        }

    @patch("wix_safe_agent_cli.commands.bookings_services_v2.HttpClient")
    @patch("wix_safe_agent_cli.commands.bookings_services_v2.resolve_auth_mode")
    def test_read_methods_use_official_paths(self, mock_auth: unittest.mock.MagicMock, mock_client: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"mode": "access_token", "headers": {"Authorization": "token-abc"}}
        mock_client.return_value.request.return_value = _DummyResponse({"service": {"id": "svc-1"}})

        args = SimpleNamespace(service_id="svc-1")
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = bookings_services_v2.cmd_bookings_services_v2_get(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertEqual(payload["method"], "bookings-services-v2.get")
        self.assertEqual(payload["request"]["path"], "/_api/bookings/v2/services/svc-1")
        self.assertTrue(mock_client.return_value.request.call_args.kwargs["url"].endswith("/_api/bookings/v2/services/svc-1"))

    @patch("wix_safe_agent_cli.commands.bookings_services_v2.HttpClient")
    @patch("wix_safe_agent_cli.commands.bookings_services_v2.resolve_auth_mode")
    def test_query_and_count_normalize_bodies(self, mock_auth: unittest.mock.MagicMock, mock_client: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"mode": "access_token", "headers": {"Authorization": "token-abc"}}
        mock_client.return_value.request.return_value = _DummyResponse({"services": []})

        query_args = SimpleNamespace(query_json='{"filter":{"status":{"$eq":"ACTIVE"}}}')
        query_ctx = self._ctx()
        query_buf = io.StringIO()
        with redirect_stdout(query_buf):
            rc_query = bookings_services_v2.cmd_bookings_services_v2_query(query_args, query_ctx)
        query_payload = json.loads(query_buf.getvalue())

        self.assertEqual(rc_query, 0)
        self.assertEqual(query_payload["request"]["path"], "/_api/bookings/v2/services/query")
        self.assertEqual(query_payload["request"]["body"], {"query": {"filter": {"status": {"$eq": "ACTIVE"}}}})

        count_args = SimpleNamespace(filter_json='{"status":{"$eq":"ACTIVE"}}')
        count_ctx = self._ctx()
        count_buf = io.StringIO()
        with redirect_stdout(count_buf):
            rc_count = bookings_services_v2.cmd_bookings_services_v2_count(count_args, count_ctx)
        count_payload = json.loads(count_buf.getvalue())

        self.assertEqual(rc_count, 0)
        self.assertEqual(count_payload["request"]["path"], "/_api/bookings/v2/services/count")
        self.assertEqual(count_payload["request"]["body"], {"filter": {"status": {"$eq": "ACTIVE"}}})

    def test_create_dry_run_builds_reviewed_plan(self) -> None:
        args = SimpleNamespace(service_json='{"name":"Consultation","type":"APPOINTMENT"}')
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = bookings_services_v2.cmd_bookings_services_v2_create(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["method"], "bookings-services-v2.create")
        self.assertEqual(payload["plan"]["request"]["path"], "/_api/bookings/v2/services")
        self.assertIn("apply requires --plan-in, --apply, and --yes", payload["plan"]["preconditions"])

    def test_delete_and_location_replacement_require_irreversible_ack(self) -> None:
        delete_args = SimpleNamespace(service_id="svc-1")
        delete_ctx = self._ctx()
        delete_buf = io.StringIO()
        with redirect_stdout(delete_buf):
            rc_delete = bookings_services_v2.cmd_bookings_services_v2_delete(delete_args, delete_ctx)
        delete_payload = json.loads(delete_buf.getvalue())

        self.assertEqual(rc_delete, 0)
        self.assertEqual(delete_payload["plan"]["request"]["path"], "/_api/bookings/v2/services/svc-1")
        self.assertIn("apply also requires --ack-irreversible", delete_payload["plan"]["preconditions"])

        location_args = SimpleNamespace(service_id="svc-1", request_json='{"locations":[]}')
        location_ctx = self._ctx()
        location_buf = io.StringIO()
        with redirect_stdout(location_buf):
            rc_location = bookings_services_v2.cmd_bookings_services_v2_set_service_locations(location_args, location_ctx)
        location_payload = json.loads(location_buf.getvalue())

        self.assertEqual(rc_location, 0)
        self.assertEqual(location_payload["plan"]["request"]["path"], "/_api/bookings/v2/services/svc-1/locations")
        self.assertIn("apply also requires --ack-irreversible", location_payload["plan"]["preconditions"])

    def test_update_rejects_body_service_id_mismatch(self) -> None:
        args = SimpleNamespace(service_id="svc-1", service_json='{"id":"svc-2","name":"Wrong"}')
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = bookings_services_v2.cmd_bookings_services_v2_update(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertIn("does not match --service-id", payload["reasons"][0])

    def test_bulk_services_limit_is_enforced(self) -> None:
        args = SimpleNamespace(services_json=json.dumps([{"id": str(i)} for i in range(101)]))
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = bookings_services_v2.cmd_bookings_services_v2_bulk_create(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertFalse(payload["ok"])
        self.assertIn("cannot include more than 100", payload["error"])

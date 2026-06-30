from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import bookings_resources_v2
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


class TestBookingsResourcesV2Parser(unittest.TestCase):
    def test_parser_recognizes_resources_v2_commands_and_write_flags(self) -> None:
        parser = build_parser()

        read_args = parser.parse_args(["bookings-resources-v2", "get", "--resource-id", "res-1"])
        self.assertEqual(read_args.bookings_resources_v2_cmd, "get")
        self.assertFalse(read_args.write_capable)
        self.assertIs(read_args.func, bookings_resources_v2.cmd_bookings_resources_v2_get)

        write_args = parser.parse_args(["bookings-resources-v2", "create", "--resource-json", '{"name":"Room A"}'])
        self.assertEqual(write_args.bookings_resources_v2_cmd, "create")
        self.assertTrue(write_args.write_capable)
        self.assertIs(write_args.func, bookings_resources_v2.cmd_bookings_resources_v2_create)

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
            "bulk-delete",
        }
        self.assertEqual(
            set(parser._subparsers._group_actions[0].choices["bookings-resources-v2"]._subparsers._group_actions[0].choices),
            expected,
        )


class TestBookingsResourcesV2Commands(unittest.TestCase):
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

    @patch("wix_safe_agent_cli.commands.bookings_resources_v2.HttpClient")
    @patch("wix_safe_agent_cli.commands.bookings_resources_v2.resolve_auth_mode")
    def test_read_methods_use_official_paths(self, mock_auth: unittest.mock.MagicMock, mock_client: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"mode": "access_token", "headers": {"Authorization": "token-abc"}}
        mock_client.return_value.request.return_value = _DummyResponse({"resource": {"id": "res-1"}})

        args = SimpleNamespace(resource_id="res-1")
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = bookings_resources_v2.cmd_bookings_resources_v2_get(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertEqual(payload["method"], "bookings-resources-v2.get")
        self.assertEqual(payload["request"]["path"], "/bookings/v2/resources/res-1")
        self.assertTrue(mock_client.return_value.request.call_args.kwargs["url"].endswith("/bookings/v2/resources/res-1"))

    @patch("wix_safe_agent_cli.commands.bookings_resources_v2.HttpClient")
    @patch("wix_safe_agent_cli.commands.bookings_resources_v2.resolve_auth_mode")
    def test_query_search_and_count_normalize_bodies(self, mock_auth: unittest.mock.MagicMock, mock_client: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"mode": "access_token", "headers": {"Authorization": "token-abc"}}
        mock_client.return_value.request.return_value = _DummyResponse({"resources": []})

        query_args = SimpleNamespace(query_json='{"filter":{"typeId":{"$eq":"type-1"}}}')
        query_buf = io.StringIO()
        with redirect_stdout(query_buf):
            rc_query = bookings_resources_v2.cmd_bookings_resources_v2_query(query_args, self._ctx())
        query_payload = json.loads(query_buf.getvalue())

        search_args = SimpleNamespace(search_json='{"filter":{"typeId":{"$eq":"type-1"}}}')
        search_buf = io.StringIO()
        with redirect_stdout(search_buf):
            rc_search = bookings_resources_v2.cmd_bookings_resources_v2_search(search_args, self._ctx())
        search_payload = json.loads(search_buf.getvalue())

        count_args = SimpleNamespace(filter_json='{"typeId":{"$eq":"type-1"}}')
        count_buf = io.StringIO()
        with redirect_stdout(count_buf):
            rc_count = bookings_resources_v2.cmd_bookings_resources_v2_count(count_args, self._ctx())
        count_payload = json.loads(count_buf.getvalue())

        self.assertEqual(rc_query, 0)
        self.assertEqual(query_payload["request"]["path"], "/bookings/v2/resources/query")
        self.assertEqual(query_payload["request"]["body"], {"query": {"filter": {"typeId": {"$eq": "type-1"}}}})
        self.assertEqual(rc_search, 0)
        self.assertEqual(search_payload["request"]["path"], "/bookings/v2/resources/search")
        self.assertEqual(
            search_payload["request"]["body"],
            {"search": {"filter": {"typeId": {"$eq": "type-1"}}}},
        )
        self.assertEqual(rc_count, 0)
        self.assertEqual(count_payload["request"]["path"], "/bookings/v2/resources/count")
        self.assertEqual(count_payload["request"]["body"], {"filter": {"typeId": {"$eq": "type-1"}}})

    def test_create_dry_run_builds_reviewed_plan(self) -> None:
        args = SimpleNamespace(resource_json='{"name":"Room A"}')
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = bookings_resources_v2.cmd_bookings_resources_v2_create(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["method"], "bookings-resources-v2.create")
        self.assertEqual(payload["plan"]["request"]["path"], "/bookings/v2/resources")
        self.assertIn("apply requires --plan-in, --apply, and --yes", payload["plan"]["preconditions"])

    def test_update_requires_revision_and_rejects_body_id_mismatch(self) -> None:
        missing_revision_args = SimpleNamespace(resource_id="res-1", resource_json='{"id":"res-1","name":"Room B"}')
        missing_revision_buf = io.StringIO()
        with redirect_stdout(missing_revision_buf):
            rc_missing_revision = bookings_resources_v2.cmd_bookings_resources_v2_update(missing_revision_args, self._ctx())
        missing_revision_payload = json.loads(missing_revision_buf.getvalue())

        mismatch_args = SimpleNamespace(resource_id="res-1", resource_json='{"id":"res-2","revision":"1","name":"Wrong"}')
        mismatch_buf = io.StringIO()
        with redirect_stdout(mismatch_buf):
            rc_mismatch = bookings_resources_v2.cmd_bookings_resources_v2_update(mismatch_args, self._ctx())
        mismatch_payload = json.loads(mismatch_buf.getvalue())

        self.assertEqual(rc_missing_revision, 1)
        self.assertIn("resource.revision is required", missing_revision_payload["error"])
        self.assertEqual(rc_mismatch, 0)
        self.assertTrue(mismatch_payload["refused"])
        self.assertIn("does not match --resource-id", mismatch_payload["reasons"][0])

    def test_delete_and_bulk_delete_require_irreversible_ack(self) -> None:
        delete_args = SimpleNamespace(resource_id="res-1")
        delete_buf = io.StringIO()
        with redirect_stdout(delete_buf):
            rc_delete = bookings_resources_v2.cmd_bookings_resources_v2_delete(delete_args, self._ctx())
        delete_payload = json.loads(delete_buf.getvalue())

        bulk_args = SimpleNamespace(ids_json='["res-1","res-2"]')
        bulk_buf = io.StringIO()
        with redirect_stdout(bulk_buf):
            rc_bulk = bookings_resources_v2.cmd_bookings_resources_v2_bulk_delete(bulk_args, self._ctx())
        bulk_payload = json.loads(bulk_buf.getvalue())

        self.assertEqual(rc_delete, 0)
        self.assertEqual(delete_payload["plan"]["request"]["path"], "/bookings/v2/resources/res-1")
        self.assertIn("apply also requires --ack-irreversible", delete_payload["plan"]["preconditions"])
        self.assertEqual(rc_bulk, 0)
        self.assertEqual(bulk_payload["plan"]["request"]["path"], "/bookings/v2/bulk/resources/delete")
        self.assertEqual(bulk_payload["plan"]["request"]["body"], {"ids": ["res-1", "res-2"]})
        self.assertIn("apply also requires --ack-irreversible", bulk_payload["plan"]["preconditions"])

    def test_bulk_resources_limit_is_enforced(self) -> None:
        args = SimpleNamespace(resources_json=json.dumps([{"name": str(i)} for i in range(51)]))
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = bookings_resources_v2.cmd_bookings_resources_v2_bulk_create(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertFalse(payload["ok"])
        self.assertIn("cannot include more than 50", payload["error"])

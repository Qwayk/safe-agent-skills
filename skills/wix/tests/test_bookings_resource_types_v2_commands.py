from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import bookings_resource_types_v2
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        pass


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestBookingsResourceTypesV2Parser(unittest.TestCase):
    def test_parser_recognizes_resource_types_v2_commands_and_write_flags(self) -> None:
        parser = build_parser()

        read_args = parser.parse_args(["bookings-resource-types-v2", "get", "--resource-type-id", "rt-1"])
        self.assertEqual(read_args.bookings_resource_types_v2_cmd, "get")
        self.assertFalse(read_args.write_capable)
        self.assertIs(read_args.func, bookings_resource_types_v2.cmd_bookings_resource_types_v2_get)

        write_args = parser.parse_args(["bookings-resource-types-v2", "create", "--resource-type-json", '{"name":"Room"}'])
        self.assertEqual(write_args.bookings_resource_types_v2_cmd, "create")
        self.assertTrue(write_args.write_capable)
        self.assertIs(write_args.func, bookings_resource_types_v2.cmd_bookings_resource_types_v2_create)

        expected = {"get", "query", "count", "create", "update", "delete"}
        self.assertEqual(
            set(parser._subparsers._group_actions[0].choices["bookings-resource-types-v2"]._subparsers._group_actions[0].choices),
            expected,
        )


class TestBookingsResourceTypesV2Commands(unittest.TestCase):
    def _ctx(self) -> dict:
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
            "plan_in": None,
            "plan_out": None,
            "receipt_out": None,
            "apply": False,
            "yes": False,
            "ack_irreversible": False,
            "enforce_reviewed_plan": True,
        }

    @patch("wix_safe_agent_cli.commands.bookings_resource_types_v2.HttpClient")
    @patch("wix_safe_agent_cli.commands.bookings_resource_types_v2.resolve_auth_mode")
    def test_read_methods_use_official_paths(self, mock_auth: unittest.mock.MagicMock, mock_client: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"mode": "access_token", "headers": {"Authorization": "token-abc"}}
        mock_client.return_value.request.return_value = _DummyResponse({"resourceType": {"id": "rt-1"}})

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = bookings_resource_types_v2.cmd_bookings_resource_types_v2_get(SimpleNamespace(resource_type_id="rt-1"), self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertEqual(payload["method"], "bookings-resource-types-v2.get")
        self.assertEqual(payload["request"]["path"], "/bookings/v2/resources/resource-types/rt-1")
        self.assertTrue(mock_client.return_value.request.call_args.kwargs["url"].endswith("/bookings/v2/resources/resource-types/rt-1"))

    @patch("wix_safe_agent_cli.commands.bookings_resource_types_v2.HttpClient")
    @patch("wix_safe_agent_cli.commands.bookings_resource_types_v2.resolve_auth_mode")
    def test_query_and_count_normalize_bodies(self, mock_auth: unittest.mock.MagicMock, mock_client: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"mode": "access_token", "headers": {"Authorization": "token-abc"}}
        mock_client.return_value.request.return_value = _DummyResponse({"resourceTypes": []})

        query_buf = io.StringIO()
        with redirect_stdout(query_buf):
            rc_query = bookings_resource_types_v2.cmd_bookings_resource_types_v2_query(
                SimpleNamespace(query_json='{"filter":{"name":{"$startsWith":"room"}}}'),
                self._ctx(),
            )
        query_payload = json.loads(query_buf.getvalue())

        count_buf = io.StringIO()
        with redirect_stdout(count_buf):
            rc_count = bookings_resource_types_v2.cmd_bookings_resource_types_v2_count(
                SimpleNamespace(filter_json='{"name":{"$startsWith":"room"}}'),
                self._ctx(),
            )
        count_payload = json.loads(count_buf.getvalue())

        self.assertEqual(rc_query, 0)
        self.assertEqual(query_payload["request"]["path"], "/bookings/v2/resources/resource-types/query")
        self.assertEqual(query_payload["request"]["body"], {"query": {"filter": {"name": {"$startsWith": "room"}}}})
        self.assertEqual(rc_count, 0)
        self.assertEqual(count_payload["request"]["path"], "/bookings/v2/resources/resource-types/count")
        self.assertEqual(count_payload["request"]["body"], {"filter": {"name": {"$startsWith": "room"}}})

    def test_create_dry_run_builds_reviewed_plan(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = bookings_resource_types_v2.cmd_bookings_resource_types_v2_create(
                SimpleNamespace(resource_type_json='{"name":"Room"}'),
                self._ctx(),
            )
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["method"], "bookings-resource-types-v2.create")
        self.assertEqual(payload["plan"]["request"]["path"], "/bookings/v2/resources/resource-types")

    def test_update_requires_revision_and_rejects_body_id_mismatch(self) -> None:
        missing_revision_buf = io.StringIO()
        with redirect_stdout(missing_revision_buf):
            rc_missing_revision = bookings_resource_types_v2.cmd_bookings_resource_types_v2_update(
                SimpleNamespace(resource_type_id="rt-1", resource_type_json='{"id":"rt-1","name":"Room"}'),
                self._ctx(),
            )
        missing_revision_payload = json.loads(missing_revision_buf.getvalue())

        mismatch_buf = io.StringIO()
        with redirect_stdout(mismatch_buf):
            rc_mismatch = bookings_resource_types_v2.cmd_bookings_resource_types_v2_update(
                SimpleNamespace(resource_type_id="rt-1", resource_type_json='{"id":"rt-2","revision":"1","name":"Wrong"}'),
                self._ctx(),
            )
        mismatch_payload = json.loads(mismatch_buf.getvalue())

        self.assertEqual(rc_missing_revision, 1)
        self.assertIn("resourceType.revision is required", missing_revision_payload["error"])
        self.assertEqual(rc_mismatch, 0)
        self.assertTrue(mismatch_payload["refused"])
        self.assertIn("does not match --resource-type-id", mismatch_payload["reasons"][0])

    def test_delete_requires_irreversible_ack(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = bookings_resource_types_v2.cmd_bookings_resource_types_v2_delete(SimpleNamespace(resource_type_id="rt-1"), self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertEqual(payload["plan"]["request"]["path"], "/bookings/v2/resources/resource-types/rt-1")
        self.assertIn("apply also requires --ack-irreversible", payload["plan"]["preconditions"])

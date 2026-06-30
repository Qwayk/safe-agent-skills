from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import bookings_policies
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        pass


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestBookingsPoliciesParser(unittest.TestCase):
    def test_parser_recognizes_policy_commands_and_write_flags(self) -> None:
        parser = build_parser()

        read_args = parser.parse_args(["bookings-policies", "get", "--booking-policy-id", "policy-1"])
        self.assertEqual(read_args.bookings_policies_cmd, "get")
        self.assertFalse(read_args.write_capable)
        self.assertIs(read_args.func, bookings_policies.cmd_bookings_policies_get)

        write_args = parser.parse_args(["bookings-policies", "create", "--policy-json", '{"name":"Standard"}'])
        self.assertEqual(write_args.bookings_policies_cmd, "create")
        self.assertTrue(write_args.write_capable)
        self.assertIs(write_args.func, bookings_policies.cmd_bookings_policies_create)

        expected = {"get", "query", "count", "strictest", "create", "update", "delete", "set-default"}
        self.assertEqual(
            set(parser._subparsers._group_actions[0].choices["bookings-policies"]._subparsers._group_actions[0].choices),
            expected,
        )


class TestBookingsPoliciesCommands(unittest.TestCase):
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

    @patch("wix_safe_agent_cli.commands.bookings_policies.HttpClient")
    @patch("wix_safe_agent_cli.commands.bookings_policies.resolve_auth_mode")
    def test_read_methods_use_official_paths(self, mock_auth: unittest.mock.MagicMock, mock_client: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"mode": "access_token", "headers": {"Authorization": "token-abc"}}
        mock_client.return_value.request.return_value = _DummyResponse({"bookingPolicy": {"id": "policy-1"}})

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = bookings_policies.cmd_bookings_policies_get(SimpleNamespace(booking_policy_id="policy-1"), self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertEqual(payload["method"], "bookings-policies.get")
        self.assertEqual(payload["request"]["path"], "/bookings/v1/booking-policies/policy-1")
        self.assertTrue(mock_client.return_value.request.call_args.kwargs["url"].endswith("/bookings/v1/booking-policies/policy-1"))

    @patch("wix_safe_agent_cli.commands.bookings_policies.HttpClient")
    @patch("wix_safe_agent_cli.commands.bookings_policies.resolve_auth_mode")
    def test_query_count_and_strictest_normalize_bodies(self, mock_auth: unittest.mock.MagicMock, mock_client: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"mode": "access_token", "headers": {"Authorization": "token-abc"}}
        mock_client.return_value.request.return_value = _DummyResponse({"bookingPolicies": []})

        query_buf = io.StringIO()
        with redirect_stdout(query_buf):
            rc_query = bookings_policies.cmd_bookings_policies_query(
                SimpleNamespace(query_json='{"filter":{"name":{"$startsWith":"Std"}}}'),
                self._ctx(),
            )
        query_payload = json.loads(query_buf.getvalue())

        count_buf = io.StringIO()
        with redirect_stdout(count_buf):
            rc_count = bookings_policies.cmd_bookings_policies_count(
                SimpleNamespace(filter_json='{"default":{"$eq":false}}'),
                self._ctx(),
            )
        count_payload = json.loads(count_buf.getvalue())

        strictest_buf = io.StringIO()
        with redirect_stdout(strictest_buf):
            rc_strictest = bookings_policies.cmd_bookings_policies_strictest(
                SimpleNamespace(request_json='{"bookingPolicyIds":["policy-1","policy-2"]}'),
                self._ctx(),
            )
        strictest_payload = json.loads(strictest_buf.getvalue())

        self.assertEqual(rc_query, 0)
        self.assertEqual(query_payload["request"]["path"], "/bookings/v1/booking-policies/query")
        self.assertEqual(query_payload["request"]["body"], {"query": {"filter": {"name": {"$startsWith": "Std"}}}})
        self.assertEqual(rc_count, 0)
        self.assertEqual(count_payload["request"]["path"], "/bookings/v1/booking-policies/count")
        self.assertEqual(count_payload["request"]["body"], {"filter": {"default": {"$eq": False}}})
        self.assertEqual(rc_strictest, 0)
        self.assertEqual(strictest_payload["request"]["path"], "/bookings/v1/booking-policies/strictest")
        self.assertEqual(strictest_payload["request"]["body"], {"bookingPolicyIds": ["policy-1", "policy-2"]})

    def test_create_dry_run_builds_reviewed_plan(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = bookings_policies.cmd_bookings_policies_create(
                SimpleNamespace(policy_json='{"name":"Standard"}'),
                self._ctx(),
            )
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["method"], "bookings-policies.create")
        self.assertEqual(payload["plan"]["request"]["path"], "/bookings/v1/booking-policies")
        self.assertEqual(payload["plan"]["request"]["body"], {"bookingPolicy": {"name": "Standard"}})

    def test_update_requires_revision_and_rejects_body_id_mismatch(self) -> None:
        missing_revision_buf = io.StringIO()
        with redirect_stdout(missing_revision_buf):
            rc_missing_revision = bookings_policies.cmd_bookings_policies_update(
                SimpleNamespace(booking_policy_id="policy-1", policy_json='{"id":"policy-1","name":"Standard"}'),
                self._ctx(),
            )
        missing_revision_payload = json.loads(missing_revision_buf.getvalue())

        mismatch_buf = io.StringIO()
        with redirect_stdout(mismatch_buf):
            rc_mismatch = bookings_policies.cmd_bookings_policies_update(
                SimpleNamespace(booking_policy_id="policy-1", policy_json='{"id":"policy-2","revision":"1","name":"Wrong"}'),
                self._ctx(),
            )
        mismatch_payload = json.loads(mismatch_buf.getvalue())

        self.assertEqual(rc_missing_revision, 1)
        self.assertIn("bookingPolicy.revision is required", missing_revision_payload["error"])
        self.assertEqual(rc_mismatch, 0)
        self.assertTrue(mismatch_payload["refused"])
        self.assertIn("does not match --booking-policy-id", mismatch_payload["reasons"][0])

    def test_delete_and_set_default_require_irreversible_ack(self) -> None:
        delete_buf = io.StringIO()
        with redirect_stdout(delete_buf):
            rc_delete = bookings_policies.cmd_bookings_policies_delete(SimpleNamespace(booking_policy_id="policy-1"), self._ctx())
        delete_payload = json.loads(delete_buf.getvalue())

        default_buf = io.StringIO()
        with redirect_stdout(default_buf):
            rc_default = bookings_policies.cmd_bookings_policies_set_default(SimpleNamespace(booking_policy_id="policy-1"), self._ctx())
        default_payload = json.loads(default_buf.getvalue())

        self.assertEqual(rc_delete, 0)
        self.assertEqual(delete_payload["plan"]["request"]["path"], "/bookings/v1/booking-policies/policy-1")
        self.assertIn("apply also requires --ack-irreversible", delete_payload["plan"]["preconditions"])
        self.assertEqual(rc_default, 0)
        self.assertEqual(default_payload["plan"]["request"]["path"], "/bookings/v1/booking-policies/policy-1:setDefault")
        self.assertIn("apply also requires --ack-irreversible", default_payload["plan"]["preconditions"])

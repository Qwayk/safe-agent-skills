from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import bookings_service_options_v1
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        pass


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestBookingsServiceOptionsV1Parser(unittest.TestCase):
    def test_parser_recognizes_service_options_commands_and_write_flags(self) -> None:
        parser = build_parser()

        read_args = parser.parse_args(["bookings-service-options-v1", "get", "--service-options-id", "options-1"])
        self.assertEqual(read_args.bookings_service_options_v1_cmd, "get")
        self.assertFalse(read_args.write_capable)
        self.assertIs(read_args.func, bookings_service_options_v1.cmd_bookings_service_options_v1_get)

        write_args = parser.parse_args(["bookings-service-options-v1", "create", "--options-json", '{"serviceId":"service-1","options":[],"variants":[]}'])
        self.assertEqual(write_args.bookings_service_options_v1_cmd, "create")
        self.assertTrue(write_args.write_capable)
        self.assertIs(write_args.func, bookings_service_options_v1.cmd_bookings_service_options_v1_create)

        expected = {"get", "get-by-service-id", "query", "create", "update", "delete", "clone"}
        self.assertEqual(
            set(parser._subparsers._group_actions[0].choices["bookings-service-options-v1"]._subparsers._group_actions[0].choices),
            expected,
        )


class TestBookingsServiceOptionsV1Commands(unittest.TestCase):
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

    @patch("wix_safe_agent_cli.commands.bookings_service_options_v1.HttpClient")
    @patch("wix_safe_agent_cli.commands.bookings_service_options_v1.resolve_auth_mode")
    def test_get_and_get_by_service_id_use_official_paths(self, mock_auth: unittest.mock.MagicMock, mock_client: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"mode": "access_token", "headers": {"Authorization": "token-abc"}}
        mock_client.return_value.request.return_value = _DummyResponse({"serviceOptionsAndVariants": {"id": "options-1"}})

        get_buf = io.StringIO()
        with redirect_stdout(get_buf):
            rc_get = bookings_service_options_v1.cmd_bookings_service_options_v1_get(SimpleNamespace(service_options_id="options-1"), self._ctx())
        get_payload = json.loads(get_buf.getvalue())

        service_buf = io.StringIO()
        with redirect_stdout(service_buf):
            rc_service = bookings_service_options_v1.cmd_bookings_service_options_v1_get_by_service_id(SimpleNamespace(service_id="service-1"), self._ctx())
        service_payload = json.loads(service_buf.getvalue())

        self.assertEqual(rc_get, 0)
        self.assertEqual(rc_service, 0)
        self.assertEqual(get_payload["request"]["path"], "/bookings/v1/serviceOptionsAndVariants/options-1")
        self.assertEqual(service_payload["request"]["path"], "/bookings/v1/serviceOptionsAndVariants/service_id/service-1")
        self.assertEqual(mock_client.return_value.request.call_args.kwargs["method"], "GET")

    @patch("wix_safe_agent_cli.commands.bookings_service_options_v1.HttpClient")
    @patch("wix_safe_agent_cli.commands.bookings_service_options_v1.resolve_auth_mode")
    def test_query_wraps_filter_json_in_official_query_body(self, mock_auth: unittest.mock.MagicMock, mock_client: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"mode": "access_token", "headers": {"Authorization": "token-abc"}}
        mock_client.return_value.request.return_value = _DummyResponse({"serviceOptionsAndVariants": []})

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = bookings_service_options_v1.cmd_bookings_service_options_v1_query(SimpleNamespace(query_json='{"filter":{"serviceId":{"$eq":"service-1"}}}'), self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertEqual(payload["request"]["path"], "/bookings/v1/serviceOptionsAndVariants/query")
        self.assertEqual(payload["request"]["body"], {"query": {"filter": {"serviceId": {"$eq": "service-1"}}}})
        self.assertEqual(mock_client.return_value.request.call_args.kwargs["method"], "POST")

    def test_create_and_clone_build_reviewed_plans(self) -> None:
        create_buf = io.StringIO()
        with redirect_stdout(create_buf):
            rc_create = bookings_service_options_v1.cmd_bookings_service_options_v1_create(
                SimpleNamespace(options_json='{"serviceId":"service-1","options":[],"variants":[]}'),
                self._ctx(),
            )
        create_payload = json.loads(create_buf.getvalue())

        clone_buf = io.StringIO()
        with redirect_stdout(clone_buf):
            rc_clone = bookings_service_options_v1.cmd_bookings_service_options_v1_clone(
                SimpleNamespace(clone_from_id="options-1", request_json='{"serviceId":"service-2"}'),
                self._ctx(),
            )
        clone_payload = json.loads(clone_buf.getvalue())

        self.assertEqual(rc_create, 0)
        self.assertTrue(create_payload["dry_run"])
        self.assertEqual(create_payload["plan"]["request"]["path"], "/bookings/v1/serviceOptionsAndVariants")
        self.assertEqual(rc_clone, 0)
        self.assertEqual(clone_payload["plan"]["request"]["path"], "/bookings/v1/serviceOptionsAndVariants/options-1/clone")
        self.assertNotIn("apply also requires --ack-irreversible", clone_payload["plan"]["preconditions"])

    def test_update_requires_revision_and_matching_id(self) -> None:
        missing_revision = io.StringIO()
        with redirect_stdout(missing_revision):
            rc_missing = bookings_service_options_v1.cmd_bookings_service_options_v1_update(
                SimpleNamespace(service_options_id="options-1", options_json='{"id":"options-1","serviceId":"service-1"}'),
                self._ctx(),
            )
        missing_payload = json.loads(missing_revision.getvalue())

        mismatched_id = io.StringIO()
        with redirect_stdout(mismatched_id):
            rc_mismatch = bookings_service_options_v1.cmd_bookings_service_options_v1_update(
                SimpleNamespace(service_options_id="options-1", options_json='{"id":"options-2","revision":"1"}'),
                self._ctx(),
            )
        mismatch_payload = json.loads(mismatched_id.getvalue())

        self.assertEqual(rc_missing, 1)
        self.assertIn("revision is required", missing_payload["error"])
        self.assertEqual(rc_mismatch, 0)
        self.assertTrue(mismatch_payload["refused"])
        self.assertIn("does not match --service-options-id", mismatch_payload["reasons"][0])

    def test_delete_builds_irreversible_reviewed_plan(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = bookings_service_options_v1.cmd_bookings_service_options_v1_delete(
                SimpleNamespace(service_options_id="options-1"),
                self._ctx(),
            )
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["request"]["method"], "DELETE")
        self.assertEqual(payload["plan"]["request"]["path"], "/bookings/v1/serviceOptionsAndVariants/options-1")
        self.assertIn("apply also requires --ack-irreversible", payload["plan"]["preconditions"])


if __name__ == "__main__":
    unittest.main()

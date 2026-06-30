from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import bookings_staff_members
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        pass


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestBookingsStaffMembersParser(unittest.TestCase):
    def test_parser_recognizes_staff_members_commands_and_write_flags(self) -> None:
        parser = build_parser()

        read_args = parser.parse_args(["bookings-staff-members", "get", "--staff-member-id", "staff-1"])
        self.assertEqual(read_args.bookings_staff_members_cmd, "get")
        self.assertFalse(read_args.write_capable)
        self.assertIs(read_args.func, bookings_staff_members.cmd_bookings_staff_members_get)

        write_args = parser.parse_args(["bookings-staff-members", "create", "--staff-member-json", '{"name":"Ada"}'])
        self.assertEqual(write_args.bookings_staff_members_cmd, "create")
        self.assertTrue(write_args.write_capable)
        self.assertIs(write_args.func, bookings_staff_members.cmd_bookings_staff_members_create)

        expected = {
            "get",
            "query",
            "search",
            "count",
            "get-deleted",
            "list-deleted",
            "create",
            "update",
            "delete",
            "assign-working-hours-schedule",
            "bulk-update-tags",
            "bulk-update-tags-by-filter",
            "connect-to-user",
            "disconnect-from-user",
            "remove-from-trash",
        }
        self.assertEqual(
            set(parser._subparsers._group_actions[0].choices["bookings-staff-members"]._subparsers._group_actions[0].choices),
            expected,
        )


class TestBookingsStaffMembersCommands(unittest.TestCase):
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

    @patch("wix_safe_agent_cli.commands.bookings_staff_members.HttpClient")
    @patch("wix_safe_agent_cli.commands.bookings_staff_members.resolve_auth_mode")
    def test_read_methods_use_official_paths_and_params(self, mock_auth: unittest.mock.MagicMock, mock_client: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"mode": "access_token", "headers": {"Authorization": "token-abc"}}
        mock_client.return_value.request.return_value = _DummyResponse({"staffMember": {"id": "staff-1"}})

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = bookings_staff_members.cmd_bookings_staff_members_get(
                SimpleNamespace(staff_member_id="staff-1", field=["RESOURCE_DETAILS"]),
                self._ctx(),
            )
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertEqual(payload["method"], "bookings-staff-members.get")
        self.assertEqual(payload["request"]["path"], "/bookings/v1/staff-members/staff-1")
        self.assertEqual(payload["request"]["params"], {"fields": "RESOURCE_DETAILS"})
        self.assertTrue(mock_client.return_value.request.call_args.kwargs["url"].endswith("/bookings/v1/staff-members/staff-1"))
        self.assertEqual(mock_client.return_value.request.call_args.kwargs["params"], {"fields": "RESOURCE_DETAILS"})

    @patch("wix_safe_agent_cli.commands.bookings_staff_members.HttpClient")
    @patch("wix_safe_agent_cli.commands.bookings_staff_members.resolve_auth_mode")
    def test_query_search_count_and_trash_reads_use_official_paths(self, mock_auth: unittest.mock.MagicMock, mock_client: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"mode": "access_token", "headers": {"Authorization": "token-abc"}}
        mock_client.return_value.request.return_value = _DummyResponse({"staffMembers": []})

        query_buf = io.StringIO()
        with redirect_stdout(query_buf):
            rc_query = bookings_staff_members.cmd_bookings_staff_members_query(
                SimpleNamespace(query_json='{"filter":{"name":{"$startsWith":"A"}}}'),
                self._ctx(),
            )
        query_payload = json.loads(query_buf.getvalue())

        search_buf = io.StringIO()
        with redirect_stdout(search_buf):
            rc_search = bookings_staff_members.cmd_bookings_staff_members_search(
                SimpleNamespace(search_json='{"search":{"fields":["name"],"expression":"Ada"}}'),
                self._ctx(),
            )
        search_payload = json.loads(search_buf.getvalue())

        count_buf = io.StringIO()
        with redirect_stdout(count_buf):
            rc_count = bookings_staff_members.cmd_bookings_staff_members_count(
                SimpleNamespace(filter_json='{"name":{"$startsWith":"A"}}'),
                self._ctx(),
            )
        count_payload = json.loads(count_buf.getvalue())

        list_deleted_buf = io.StringIO()
        with redirect_stdout(list_deleted_buf):
            rc_list_deleted = bookings_staff_members.cmd_bookings_staff_members_list_deleted(
                SimpleNamespace(field=["RESOURCE_DETAILS"], limit=50, cursor="cursor-1"),
                self._ctx(),
            )
        list_deleted_payload = json.loads(list_deleted_buf.getvalue())

        self.assertEqual(rc_query, 0)
        self.assertEqual(query_payload["request"]["path"], "/bookings/v1/staff-members/query")
        self.assertEqual(query_payload["request"]["body"], {"query": {"filter": {"name": {"$startsWith": "A"}}}})
        self.assertEqual(rc_search, 0)
        self.assertEqual(search_payload["request"]["path"], "/bookings/v1/staff-members/search")
        self.assertEqual(rc_count, 0)
        self.assertEqual(count_payload["request"]["path"], "/bookings/v1/staff-members/count")
        self.assertEqual(count_payload["request"]["body"], {"filter": {"name": {"$startsWith": "A"}}})
        self.assertEqual(rc_list_deleted, 0)
        self.assertEqual(list_deleted_payload["request"]["path"], "/bookings/v2/staff-members/trash-bin")
        self.assertEqual(
            list_deleted_payload["request"]["params"],
            {"fields": "RESOURCE_DETAILS", "paging.limit": 50, "paging.cursor": "cursor-1"},
        )

    def test_create_dry_run_builds_reviewed_plan(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = bookings_staff_members.cmd_bookings_staff_members_create(
                SimpleNamespace(staff_member_json='{"name":"Ada"}'),
                self._ctx(),
            )
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["method"], "bookings-staff-members.create")
        self.assertEqual(payload["plan"]["request"]["path"], "/bookings/v1/staff-members")

    def test_update_requires_revision_and_rejects_body_id_mismatch(self) -> None:
        missing_revision_buf = io.StringIO()
        with redirect_stdout(missing_revision_buf):
            rc_missing_revision = bookings_staff_members.cmd_bookings_staff_members_update(
                SimpleNamespace(staff_member_id="staff-1", staff_member_json='{"id":"staff-1","name":"Ada"}'),
                self._ctx(),
            )
        missing_revision_payload = json.loads(missing_revision_buf.getvalue())

        mismatch_buf = io.StringIO()
        with redirect_stdout(mismatch_buf):
            rc_mismatch = bookings_staff_members.cmd_bookings_staff_members_update(
                SimpleNamespace(staff_member_id="staff-1", staff_member_json='{"id":"staff-2","revision":"1","name":"Wrong"}'),
                self._ctx(),
            )
        mismatch_payload = json.loads(mismatch_buf.getvalue())

        self.assertEqual(rc_missing_revision, 1)
        self.assertIn("staffMember.revision is required", missing_revision_payload["error"])
        self.assertEqual(rc_mismatch, 0)
        self.assertTrue(mismatch_payload["refused"])
        self.assertIn("does not match --staff-member-id", mismatch_payload["reasons"][0])

    def test_destructive_methods_require_irreversible_ack(self) -> None:
        delete_buf = io.StringIO()
        with redirect_stdout(delete_buf):
            rc_delete = bookings_staff_members.cmd_bookings_staff_members_delete(SimpleNamespace(staff_member_id="staff-1"), self._ctx())
        delete_payload = json.loads(delete_buf.getvalue())

        remove_buf = io.StringIO()
        with redirect_stdout(remove_buf):
            rc_remove = bookings_staff_members.cmd_bookings_staff_members_remove_from_trash(
                SimpleNamespace(staff_member_id="staff-1"),
                self._ctx(),
            )
        remove_payload = json.loads(remove_buf.getvalue())

        self.assertEqual(rc_delete, 0)
        self.assertEqual(delete_payload["plan"]["request"]["path"], "/bookings/v1/staff-members/staff-1")
        self.assertIn("apply also requires --ack-irreversible", delete_payload["plan"]["preconditions"])
        self.assertEqual(rc_remove, 0)
        self.assertEqual(remove_payload["plan"]["request"]["path"], "/bookings/v2/staff-members/trash-bin/staff-1")
        self.assertIn("apply also requires --ack-irreversible", remove_payload["plan"]["preconditions"])

    def test_schedule_connect_disconnect_and_bulk_paths(self) -> None:
        schedule_buf = io.StringIO()
        with redirect_stdout(schedule_buf):
            rc_schedule = bookings_staff_members.cmd_bookings_staff_members_assign_working_hours_schedule(
                SimpleNamespace(staff_member_id="staff-1", schedule_id="schedule-1", field=["RESOURCE_DETAILS"]),
                self._ctx(),
            )
        schedule_payload = json.loads(schedule_buf.getvalue())

        bulk_buf = io.StringIO()
        with redirect_stdout(bulk_buf):
            rc_bulk = bookings_staff_members.cmd_bookings_staff_members_bulk_update_tags(
                SimpleNamespace(tags_json='{"ids":["staff-1"],"assignTags":{"tags":{"tagIds":["tag-1"]}}}'),
                self._ctx(),
            )
        bulk_payload = json.loads(bulk_buf.getvalue())

        filter_buf = io.StringIO()
        with redirect_stdout(filter_buf):
            rc_filter = bookings_staff_members.cmd_bookings_staff_members_bulk_update_tags_by_filter(
                SimpleNamespace(tags_filter_json='{"filter":{"description":{"$startsWith":"Experienced"}},"assignTags":{"tags":{"tagIds":["tag-1"]}}}'),
                self._ctx(),
            )
        filter_payload = json.loads(filter_buf.getvalue())

        connect_buf = io.StringIO()
        with redirect_stdout(connect_buf):
            rc_connect = bookings_staff_members.cmd_bookings_staff_members_connect_to_user(
                SimpleNamespace(staff_member_id="staff-1", connect_json=None),
                self._ctx(),
            )
        connect_payload = json.loads(connect_buf.getvalue())

        disconnect_buf = io.StringIO()
        with redirect_stdout(disconnect_buf):
            rc_disconnect = bookings_staff_members.cmd_bookings_staff_members_disconnect_from_user(
                SimpleNamespace(staff_member_id="staff-1", disconnect_json=None),
                self._ctx(),
            )
        disconnect_payload = json.loads(disconnect_buf.getvalue())

        self.assertEqual(rc_schedule, 0)
        self.assertEqual(schedule_payload["plan"]["request"]["path"], "/bookings/v1/staff-members/staff-1/assign-working-hours-schedule")
        self.assertEqual(schedule_payload["plan"]["request"]["body"], {"scheduleId": "schedule-1", "fields": ["RESOURCE_DETAILS"]})
        self.assertEqual(rc_bulk, 0)
        self.assertEqual(bulk_payload["plan"]["request"]["path"], "/bookings/v1/bulk/staff-members/update-tags")
        self.assertEqual(rc_filter, 0)
        self.assertEqual(filter_payload["plan"]["request"]["path"], "/bookings/v1/bulk/staff-members/update-tags-by-filter")
        self.assertEqual(rc_connect, 0)
        self.assertEqual(connect_payload["plan"]["request"]["path"], "/bookings/v1/staff-members/staff-1/connect-staff-member-to-user")
        self.assertEqual(connect_payload["plan"]["request"]["body"], {"staffMemberId": "staff-1"})
        self.assertEqual(rc_disconnect, 0)
        self.assertEqual(disconnect_payload["plan"]["request"]["path"], "/bookings/v1/staff-members/staff-1/disconnect-staff-member-from-user")
        self.assertEqual(disconnect_payload["plan"]["request"]["body"], {"staffMemberId": "staff-1"})

    def test_bulk_update_tags_refuses_more_than_100_ids(self) -> None:
        body = {"ids": [f"staff-{idx}" for idx in range(101)]}
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = bookings_staff_members.cmd_bookings_staff_members_bulk_update_tags(
                SimpleNamespace(tags_json=json.dumps(body)),
                self._ctx(),
            )
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertIn("more than 100", payload["error"])

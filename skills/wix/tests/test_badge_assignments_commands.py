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
from wix_safe_agent_cli.commands import badge_assignments
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = (action, payload)


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestBadgeAssignmentsCommands(unittest.TestCase):
    def _ctx(self, **overrides) -> dict:
        cfg = SimpleNamespace(
            base_url="https://www.wixapis.com",
            timeout_s=30.0,
            app_id=None,
            app_secret=None,
            instance_id=None,
            access_token="token-abc",
            has_official_app_auth=False,
        )
        ctx = {
            "cfg": cfg,
            "env_file": "/tmp/.env",
            "verbose": False,
            "out": Output(mode="json"),
            "audit": _DummyAudit(),
            "tool": "wix-safe-agent-cli",
            "tool_version": "0.0.0",
            "command_str": "wix-safe-agent-cli badge-assignments",
            "apply": False,
            "yes": False,
            "plan_in": None,
            "plan_out": None,
            "receipt_out": None,
            "ack_irreversible": False,
            "enforce_reviewed_plan": True,
        }
        ctx.update(overrides)
        return ctx

    @patch("wix_safe_agent_cli.commands.badge_assignments.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.badge_assignments.HttpClient")
    def test_query_uses_official_path(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"badgeAssignments": []})

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = badge_assignments.cmd_badge_assignments_query(
                SimpleNamespace(query_json='{"query":{"filter":{"memberId":{"$eq":"member-1"}}}}'),
                self._ctx(),
            )
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertEqual(payload["request"]["method"], "POST")
        self.assertEqual(payload["request"]["path"], "/badges/v4/assignments/query")
        self.assertEqual(payload["request"]["body"], {"query": {"filter": {"memberId": {"$eq": "member-1"}}}})
        self.assertEqual(mock_auth.call_args.kwargs["command_family"], "badge-assignments")

    @patch("wix_safe_agent_cli.commands.badge_assignments.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.badge_assignments.HttpClient")
    def test_write_commands_are_plan_first(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}

        cases = [
            (
                badge_assignments.cmd_badge_assignments_create,
                SimpleNamespace(assignment_json='{"badgeAssignment":{"badgeId":"badge-1","memberId":"member-1"}}'),
                "POST",
                "/badges/v4/assignments",
                {"kind": "badge-assignments", "operation": "create"},
            ),
            (
                badge_assignments.cmd_badge_assignments_bulk_create,
                SimpleNamespace(assignments_json='{"badgeAssignments":[{"badgeId":"badge-1","memberId":"member-1"}]}'),
                "POST",
                "/badges/v4/bulk/assignments/create",
                {"kind": "badge-assignments", "operation": "bulk-create"},
            ),
            (
                badge_assignments.cmd_badge_assignments_bulk_update_tags,
                SimpleNamespace(tags_json='{"ids":["assign-1"],"assignTags":["vip"]}'),
                "POST",
                "/badges/v4/bulk/assignments/bulk-update-tags",
                {"kind": "badge-assignments", "operation": "bulk-update-tags"},
            ),
        ]
        for func, args, method, path, selector in cases:
            with self.subTest(path=path):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = func(args, self._ctx())
                payload = json.loads(buf.getvalue())
                self.assertEqual(rc, 0)
                self.assertTrue(payload["dry_run"])
                self.assertEqual(payload["plan"]["request"]["method"], method)
                self.assertEqual(payload["plan"]["request"]["path"], path)
                self.assertEqual(payload["plan"]["selector"], selector)

        mock_client.return_value.request.assert_not_called()

    @patch("wix_safe_agent_cli.commands.badge_assignments.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.badge_assignments.HttpClient")
    def test_destructive_and_broad_plans_require_ack(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}

        cases = [
            (
                badge_assignments.cmd_badge_assignments_delete,
                SimpleNamespace(assignment_id="assign-1"),
                "DELETE",
                "/badges/v4/assignments/assign-1",
                {"kind": "badge-assignments", "assignment_id": "assign-1", "operation": "delete"},
            ),
            (
                badge_assignments.cmd_badge_assignments_bulk_delete,
                SimpleNamespace(delete_json='{"ids":["assign-1"]}'),
                "POST",
                "/badges/v4/bulk/assignments/delete",
                {"kind": "badge-assignments", "operation": "bulk-delete"},
            ),
            (
                badge_assignments.cmd_badge_assignments_bulk_update_tags_by_filter,
                SimpleNamespace(filter_json='{"filter":{},"assignTags":["vip"]}'),
                "POST",
                "/badges/v4/bulk/assignments/update-tags-by-filter",
                {"kind": "badge-assignments", "operation": "bulk-update-tags-by-filter"},
            ),
        ]
        for func, args, method, path, selector in cases:
            with self.subTest(path=path):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = func(args, self._ctx())
                payload = json.loads(buf.getvalue())
                self.assertEqual(rc, 0)
                self.assertTrue(payload["dry_run"])
                self.assertEqual(payload["plan"]["request"]["method"], method)
                self.assertEqual(payload["plan"]["request"]["path"], path)
                self.assertEqual(payload["plan"]["selector"], selector)
                self.assertIn("apply also requires --ack-irreversible", payload["plan"]["preconditions"])

        mock_client.return_value.request.assert_not_called()

    @patch("wix_safe_agent_cli.commands.badge_assignments.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.badge_assignments.HttpClient")
    def test_reviewed_plan_apply_sends_request_and_emits_receipt(
        self,
        mock_client: unittest.mock.MagicMock,
        mock_auth: unittest.mock.MagicMock,
    ) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"badgeAssignment": {"id": "assign-1"}})

        with tempfile.TemporaryDirectory() as tmp:
            plan_path = str(Path(tmp) / "plan.json")
            args = SimpleNamespace(assignment_json='{"badgeAssignment":{"badgeId":"badge-1","memberId":"member-1"}}')
            dry_buf = io.StringIO()
            with redirect_stdout(dry_buf):
                dry_rc = badge_assignments.cmd_badge_assignments_create(args, self._ctx(plan_out=plan_path))
            self.assertEqual(dry_rc, 0)
            self.assertTrue(Path(plan_path).exists())
            mock_client.return_value.request.assert_not_called()

            apply_buf = io.StringIO()
            with redirect_stdout(apply_buf):
                apply_rc = badge_assignments.cmd_badge_assignments_create(args, self._ctx(apply=True, yes=True, plan_in=plan_path))
            payload = json.loads(apply_buf.getvalue())

        self.assertEqual(apply_rc, 0)
        self.assertFalse(payload["dry_run"])
        self.assertEqual(payload["receipt"]["request"]["path"], "/badges/v4/assignments")
        self.assertEqual(payload["receipt"]["response"], {"badgeAssignment": {"id": "assign-1"}})
        call = mock_client.return_value.request.call_args.kwargs
        self.assertEqual(call["method"], "POST")
        self.assertTrue(str(call["url"]).endswith("/badges/v4/assignments"))

    def test_parser_exposes_badge_assignments_commands_and_write_flags(self) -> None:
        parser = build_parser()
        cases = [
            (["badge-assignments", "query"], badge_assignments.cmd_badge_assignments_query, False),
            (
                ["badge-assignments", "create", "--assignment-json", "{}"],
                badge_assignments.cmd_badge_assignments_create,
                True,
            ),
            (
                ["badge-assignments", "delete", "--assignment-id", "assign-1"],
                badge_assignments.cmd_badge_assignments_delete,
                True,
            ),
            (
                ["badge-assignments", "bulk-create", "--assignments-json", "{}"],
                badge_assignments.cmd_badge_assignments_bulk_create,
                True,
            ),
            (
                ["badge-assignments", "bulk-delete", "--delete-json", "{}"],
                badge_assignments.cmd_badge_assignments_bulk_delete,
                True,
            ),
            (
                ["badge-assignments", "bulk-update-tags", "--tags-json", "{}"],
                badge_assignments.cmd_badge_assignments_bulk_update_tags,
                True,
            ),
            (
                ["badge-assignments", "bulk-update-tags-by-filter", "--filter-json", "{}"],
                badge_assignments.cmd_badge_assignments_bulk_update_tags_by_filter,
                True,
            ),
        ]
        for argv, func, write_capable in cases:
            with self.subTest(argv=argv):
                args = parser.parse_args(argv)
                self.assertIs(args.func, func)
                self.assertEqual(args.write_capable, write_capable)

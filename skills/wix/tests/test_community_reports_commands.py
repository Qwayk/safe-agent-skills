from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import community_reports
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = action, payload


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestCommunityReportsCommands(unittest.TestCase):
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
            "tool": "wix-safe-agent-cli",
            "tool_version": "0.0.0",
            "command_str": "wix-safe-agent-cli community-reports",
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

    def test_parser_exposes_community_reports_commands(self) -> None:
        parser = build_parser()
        cases = [
            (["community-reports", "get", "--report-id", "report-1"], "get", False),
            (["community-reports", "query"], "query", False),
            (["community-reports", "count-by-reason-types"], "count-by-reason-types", False),
            (["community-reports", "create", "--report-json", '{"report":{"reason":"SPAM"}}'], "create", True),
            (
                ["community-reports", "update", "--report-id", "report-1", "--report-json", '{"report":{"revision":"1"}}'],
                "update",
                True,
            ),
            (
                [
                    "community-reports",
                    "upsert",
                    "--entity-name",
                    "comment",
                    "--entity-id",
                    "comment-1",
                    "--report-json",
                    '{"report":{"reason":"SPAM"}}',
                ],
                "upsert",
                True,
            ),
            (["community-reports", "delete", "--report-id", "report-1"], "delete", True),
            (
                ["community-reports", "bulk-delete-by-filter", "--filter-json", '{"filter":{"entityName":"comment"}}'],
                "bulk-delete-by-filter",
                True,
            ),
        ]
        for argv, command, write_capable in cases:
            with self.subTest(command=command):
                args = parser.parse_args(argv)
                self.assertEqual(args.community_reports_cmd, command)
                self.assertEqual(args.write_capable, write_capable)

    @patch("wix_safe_agent_cli.commands.community_groups.HttpClient")
    def test_read_commands_use_official_paths_and_bodies(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"reports": []})
        cases = [
            (
                community_reports.cmd_community_reports_get,
                SimpleNamespace(report_id="report-1"),
                "GET",
                "/reports/v2/reports/report-1",
                None,
            ),
            (
                community_reports.cmd_community_reports_query,
                SimpleNamespace(query_json='{"filter":{"entityName":"comment"}}'),
                "POST",
                "/reports/v2/reports/query",
                {"query": {"filter": {"entityName": "comment"}}},
            ),
            (
                community_reports.cmd_community_reports_count_by_reason_types,
                SimpleNamespace(request_json='{"entityName":"comment","entityId":"comment-1"}'),
                "POST",
                "/reports/v2/reports/reason-types/count",
                {"entityName": "comment", "entityId": "comment-1"},
            ),
        ]
        for func, args, method, path, body in cases:
            with self.subTest(path=path):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = func(args, self._ctx())
                payload = json.loads(buf.getvalue())
                self.assertEqual(rc, 0)
                self.assertEqual(payload["request"]["method"], method)
                self.assertEqual(payload["request"]["path"], path)
                if body is not None:
                    self.assertEqual(payload["request"]["body"], body)

    @patch("wix_safe_agent_cli.commands.community_groups.HttpClient")
    def test_write_commands_are_plan_first_with_official_paths(self, mock_client: unittest.mock.MagicMock) -> None:
        cases = [
            (
                community_reports.cmd_community_reports_create,
                SimpleNamespace(report_json='{"report":{"reason":"SPAM"}}'),
                "POST",
                "/reports/v2/reports",
                False,
            ),
            (
                community_reports.cmd_community_reports_update,
                SimpleNamespace(report_id="report-1", report_json='{"report":{"revision":"1","reason":"ABUSE"}}'),
                "PATCH",
                "/reports/v2/reports/report-1",
                False,
            ),
            (
                community_reports.cmd_community_reports_upsert,
                SimpleNamespace(entity_name="comment", entity_id="comment-1", report_json='{"report":{"reason":"SPAM"}}'),
                "POST",
                "/reports/v2/reports/upsert/entity-name/comment/entity-id/comment-1",
                False,
            ),
            (
                community_reports.cmd_community_reports_delete,
                SimpleNamespace(report_id="report-1"),
                "DELETE",
                "/reports/v2/reports/report-1",
                True,
            ),
            (
                community_reports.cmd_community_reports_bulk_delete_by_filter,
                SimpleNamespace(filter_json='{"filter":{"entityName":"comment"}}'),
                "POST",
                "/reports/v2/reports/bulk/delete-by-filter",
                True,
            ),
        ]
        for func, args, method, path, requires_ack in cases:
            with self.subTest(path=path):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = func(args, self._ctx())
                payload = json.loads(buf.getvalue())
                self.assertEqual(rc, 0)
                self.assertTrue(payload["dry_run"])
                self.assertEqual(payload["plan"]["request"]["method"], method)
                self.assertEqual(payload["plan"]["request"]["path"], path)
                self.assertEqual("apply also requires --ack-irreversible" in payload["plan"]["preconditions"], requires_ack)
        self.assertFalse(mock_client.return_value.request.called)

    @patch("wix_safe_agent_cli.commands.community_groups.HttpClient")
    def test_rejects_empty_write_body(self, mock_client: unittest.mock.MagicMock) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = community_reports.cmd_community_reports_create(SimpleNamespace(report_json="{}"), self._ctx())
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 1)
        self.assertEqual(payload["error_type"], "ValidationError")
        self.assertFalse(mock_client.return_value.request.called)

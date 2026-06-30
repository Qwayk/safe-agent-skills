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
from wix_safe_agent_cli.commands import member_reports
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = (action, payload)


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestMemberReportsCommands(unittest.TestCase):
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
            "command_str": "wix-safe-agent-cli member-reports",
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

    @patch("wix_safe_agent_cli.commands.member_reports.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.member_reports.HttpClient")
    def test_query_uses_official_path(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"memberReports": []})

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = member_reports.cmd_member_reports_query(
                SimpleNamespace(query_json='{"query":{"filter":{"reportedMemberId":{"$eq":"member-1"}}}}'),
                self._ctx(),
            )
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertEqual(payload["request"]["method"], "POST")
        self.assertEqual(payload["request"]["path"], "/members/v1/member-reports/query")
        self.assertEqual(payload["request"]["body"], {"query": {"filter": {"reportedMemberId": {"$eq": "member-1"}}}})
        self.assertEqual(mock_auth.call_args.kwargs["command_family"], "member-reports")

    @patch("wix_safe_agent_cli.commands.member_reports.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.member_reports.HttpClient")
    def test_report_is_plan_first(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = member_reports.cmd_member_reports_report(
                SimpleNamespace(report_json='{"memberReport":{"reportedMemberId":"member-1","reason":"SPAM"}}'),
                self._ctx(),
            )
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["request"]["method"], "POST")
        self.assertEqual(payload["plan"]["request"]["path"], "/members/v1/member-reports")
        self.assertEqual(payload["plan"]["selector"], {"kind": "member-reports", "operation": "report"})
        mock_client.return_value.request.assert_not_called()

    @patch("wix_safe_agent_cli.commands.member_reports.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.member_reports.HttpClient")
    def test_delete_plan_requires_irreversible_ack(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = member_reports.cmd_member_reports_delete(SimpleNamespace(member_id="member-1"), self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["request"]["method"], "DELETE")
        self.assertEqual(payload["plan"]["request"]["path"], "/members/v1/member-reports/members/member-1")
        self.assertEqual(payload["plan"]["selector"], {"kind": "member-reports", "member_id": "member-1", "operation": "delete"})
        self.assertIn("apply also requires --ack-irreversible", payload["plan"]["preconditions"])
        mock_client.return_value.request.assert_not_called()

    @patch("wix_safe_agent_cli.commands.member_reports.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.member_reports.HttpClient")
    def test_reviewed_plan_apply_sends_request_and_emits_receipt(
        self,
        mock_client: unittest.mock.MagicMock,
        mock_auth: unittest.mock.MagicMock,
    ) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"memberReport": {"id": "report-1"}})

        with tempfile.TemporaryDirectory() as tmp:
            plan_path = str(Path(tmp) / "plan.json")
            args = SimpleNamespace(report_json='{"memberReport":{"reportedMemberId":"member-1","reason":"SPAM"}}')
            dry_buf = io.StringIO()
            with redirect_stdout(dry_buf):
                dry_rc = member_reports.cmd_member_reports_report(args, self._ctx(plan_out=plan_path))
            self.assertEqual(dry_rc, 0)
            self.assertTrue(Path(plan_path).exists())
            mock_client.return_value.request.assert_not_called()

            apply_buf = io.StringIO()
            with redirect_stdout(apply_buf):
                apply_rc = member_reports.cmd_member_reports_report(args, self._ctx(apply=True, yes=True, plan_in=plan_path))
            payload = json.loads(apply_buf.getvalue())

        self.assertEqual(apply_rc, 0)
        self.assertFalse(payload["dry_run"])
        self.assertEqual(payload["receipt"]["request"]["path"], "/members/v1/member-reports")
        self.assertEqual(payload["receipt"]["response"], {"memberReport": {"id": "report-1"}})
        call = mock_client.return_value.request.call_args.kwargs
        self.assertEqual(call["method"], "POST")
        self.assertTrue(str(call["url"]).endswith("/members/v1/member-reports"))

    def test_parser_exposes_member_reports_commands_and_write_flags(self) -> None:
        parser = build_parser()
        cases = [
            (["member-reports", "query"], member_reports.cmd_member_reports_query, False),
            (["member-reports", "report", "--report-json", "{}"], member_reports.cmd_member_reports_report, True),
            (["member-reports", "delete", "--member-id", "member-1"], member_reports.cmd_member_reports_delete, True),
        ]
        for argv, func, write_capable in cases:
            with self.subTest(argv=argv):
                args = parser.parse_args(argv)
                self.assertIs(args.func, func)
                self.assertEqual(args.write_capable, write_capable)

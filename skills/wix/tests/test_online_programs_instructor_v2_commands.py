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
from wix_safe_agent_cli.commands import online_programs_instructor_v2
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = action, payload


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestOnlineProgramsInstructorV2Commands(unittest.TestCase):
    def _ctx(self, **overrides) -> dict:
        cfg = SimpleNamespace(
            base_url="https://www.wixapis.com",
            timeout_s=30.0,
            access_token="site-token",
            api_key=None,
            account_id=None,
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
            "command_str": "wix-safe-agent-cli online-programs-instructor-v2",
            "apply": False,
            "yes": False,
            "verbose": False,
            "out": Output(mode="json"),
            "audit": _DummyAudit(),
            "plan_in": None,
            "plan_out": None,
            "receipt_out": None,
            "ack_irreversible": False,
            "enforce_reviewed_plan": False,
        }
        ctx.update(overrides)
        return ctx

    def test_parser_recognizes_instructor_commands(self) -> None:
        parser = build_parser()
        instructor = '{"name":"Teacher"}'
        update_instructor = '{"id":"instructor-1","name":"Teacher"}'
        assignment = '{"programId":"program-1","assignInstructorIds":["instructor-1"]}'
        cases = [
            (["online-programs-instructor-v2", "create", "--instructor-json", instructor], "create", True),
            (["online-programs-instructor-v2", "update", "--instructor-json", update_instructor], "update", True),
            (["online-programs-instructor-v2", "query"], "query", False),
            (["online-programs-instructor-v2", "assign", "--instructor-id", "instructor-1", "--program-id", "program-1"], "assign", True),
            (["online-programs-instructor-v2", "change-program-instructors", "--assignment-json", assignment], "change-program-instructors", True),
            (["online-programs-instructor-v2", "invite", "--email", "teacher@example.com"], "invite", True),
            (["online-programs-instructor-v2", "list"], "list", False),
            (["online-programs-instructor-v2", "unassign", "--instructor-id", "instructor-1", "--program-id", "program-1"], "unassign", True),
        ]
        for argv, command, write_capable in cases:
            parsed = parser.parse_args(argv)
            self.assertEqual(parsed.online_programs_instructor_v2_cmd, command)
            self.assertEqual(parsed.write_capable, write_capable)

    def test_create_dry_run_wraps_instructor_and_action_id(self) -> None:
        args = SimpleNamespace(instructor_json='{"name":"Teacher"}', action_id="action-1")
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = online_programs_instructor_v2.cmd_online_programs_instructor_v2_create(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["request"]["path"], "/_api/instructors-service/v2/instructors")
        self.assertEqual(payload["plan"]["request"]["body"]["instructor"]["name"], "Teacher")
        self.assertEqual(payload["plan"]["request"]["body"]["actionId"], "action-1")

    @patch("wix_safe_agent_cli.commands.online_programs_programs.HttpClient")
    def test_query_uses_official_path(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"instructors": []})
        args = SimpleNamespace(query_json='{"filter":{"programIds":{"$hasSome":["program-1"]}}}')
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = online_programs_instructor_v2.cmd_online_programs_instructor_v2_query(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertEqual(payload["request"]["path"], "/_api/instructors-service/v2/instructors/query")
        call = mock_client.return_value.request.call_args
        self.assertEqual(call.kwargs["method"], "POST")
        self.assertTrue(str(call.kwargs["url"]).endswith("/_api/instructors-service/v2/instructors/query"))

    def test_update_requires_instructor_id(self) -> None:
        args = SimpleNamespace(instructor_json='{"name":"Teacher"}', action_id=None)
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = online_programs_instructor_v2.cmd_online_programs_instructor_v2_update(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertIn("instructor.id", payload["error"])

    def test_change_program_instructors_validates_max_10(self) -> None:
        body = {"programId": "program-1", "assignInstructorIds": [f"instructor-{i}" for i in range(11)]}
        args = SimpleNamespace(assignment_json=json.dumps(body), action_id=None)
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = online_programs_instructor_v2.cmd_online_programs_instructor_v2_change_program_instructors(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertIn("at most 10", payload["error"])

    def test_invite_requires_irreversible_ack_for_apply(self) -> None:
        args = SimpleNamespace(email="teacher@example.com")
        ctx = self._ctx(apply=True, yes=True, plan_in="/tmp/plan.json")
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = online_programs_instructor_v2.cmd_online_programs_instructor_v2_invite(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertIn("apply also requires --ack-irreversible", payload["plan"]["preconditions"])

    @patch("wix_safe_agent_cli.commands.online_programs_programs.HttpClient")
    def test_assign_apply_with_plan_uses_official_path(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({})
        plan = {
            "method": "online-programs-instructor-v2.assign",
            "baseline": {"env_fingerprint": "https://www.wixapis.com", "selector": {"instructorId": "instructor-1", "programId": "program-1"}},
            "proposed_changes": [{"operation": "assign"}],
        }
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as handle:
            json.dump(plan, handle)
            plan_path = handle.name
        try:
            ctx = self._ctx(apply=True, yes=True, plan_in=plan_path)
            args = SimpleNamespace(instructor_id="instructor-1", program_id="program-1", action_id=None)
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = online_programs_instructor_v2.cmd_online_programs_instructor_v2_assign(args, ctx)
            payload = json.loads(buf.getvalue())
        finally:
            Path(plan_path).unlink()

        self.assertEqual(rc, 0)
        self.assertFalse(payload["dry_run"])
        call = mock_client.return_value.request.call_args
        self.assertEqual(call.kwargs["method"], "POST")
        self.assertTrue(str(call.kwargs["url"]).endswith("/_api/instructors-service/v2/instructors/instructor-1/assign"))
        self.assertEqual(call.kwargs["json_body"], {"programId": "program-1"})


if __name__ == "__main__":
    unittest.main()

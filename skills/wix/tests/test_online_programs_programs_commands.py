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
from wix_safe_agent_cli.commands import online_programs_programs
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


class TestOnlineProgramsProgramsCommands(unittest.TestCase):
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
            "command_str": "wix-safe-agent-cli online-programs-programs",
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

    def test_parser_recognizes_program_commands(self) -> None:
        parser = build_parser()
        program = '{"description":{"title":"Course"}}'
        update_program = '{"id":"program-1","revision":"3","description":{"title":"Course"}}'
        programs = '[{"program":{"id":"program-1","revision":"3"}}]'
        cases = [
            (["online-programs-programs", "create", "--program-json", program], "create", True),
            (["online-programs-programs", "get", "--program-id", "program-1"], "get", False),
            (["online-programs-programs", "update", "--program-json", update_program], "update", True),
            (["online-programs-programs", "delete", "--program-id", "program-1"], "delete", True),
            (["online-programs-programs", "query"], "query", False),
            (["online-programs-programs", "search"], "search", False),
            (["online-programs-programs", "count"], "count", False),
            (["online-programs-programs", "bulk-update", "--programs-json", programs], "bulk-update", True),
            (["online-programs-programs", "archive", "--program-id", "program-1"], "archive", True),
            (["online-programs-programs", "duplicate", "--program-id", "program-1"], "duplicate", True),
            (["online-programs-programs", "end", "--program-id", "program-1"], "end", True),
            (["online-programs-programs", "list-samples"], "list-samples", False),
            (["online-programs-programs", "publish", "--program-id", "program-1"], "publish", True),
        ]
        for argv, command, write_capable in cases:
            parsed = parser.parse_args(argv)
            self.assertEqual(parsed.online_programs_programs_cmd, command)
            self.assertEqual(parsed.write_capable, write_capable)

    @patch("wix_safe_agent_cli.commands.online_programs_programs.HttpClient")
    def test_get_uses_official_path(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"program": {"id": "program-1"}})
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = online_programs_programs.cmd_online_programs_programs_get(SimpleNamespace(program_id="program-1"), self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertEqual(payload["request"], {"method": "GET", "path": "/online-programs/v3/programs/program-1"})
        call = mock_client.return_value.request.call_args
        self.assertEqual(call.kwargs["method"], "GET")
        self.assertTrue(str(call.kwargs["url"]).endswith("/online-programs/v3/programs/program-1"))
        self.assertEqual(call.kwargs["headers"]["Authorization"], "site-token")

    def test_create_dry_run_builds_plan(self) -> None:
        args = SimpleNamespace(program_json='{"description":{"title":"Course"}}')
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = online_programs_programs.cmd_online_programs_programs_create(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["request"]["method"], "POST")
        self.assertEqual(payload["plan"]["request"]["path"], "/online-programs/v3/programs")
        self.assertEqual(payload["plan"]["request"]["body"]["program"]["description"]["title"], "Course")

    def test_update_requires_program_id_and_revision(self) -> None:
        args = SimpleNamespace(program_json='{"id":"program-1","description":{"title":"Course"}}')
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = online_programs_programs.cmd_online_programs_programs_update(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertIn("program.revision", payload["error"])

    def test_delete_requires_irreversible_ack_for_apply(self) -> None:
        args = SimpleNamespace(program_id="program-1")
        ctx = self._ctx(apply=True, yes=True, plan_in="/tmp/plan.json")
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = online_programs_programs.cmd_online_programs_programs_delete(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertIn("apply also requires --ack-irreversible", payload["plan"]["preconditions"])

    def test_bulk_update_validates_max_100(self) -> None:
        programs = [{"program": {"id": f"program-{i}", "revision": "1"}} for i in range(101)]
        args = SimpleNamespace(programs_json=json.dumps(programs), return_entity=None)
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = online_programs_programs.cmd_online_programs_programs_bulk_update(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertIn("100", payload["error"])

    @patch("wix_safe_agent_cli.commands.online_programs_programs.HttpClient")
    def test_publish_apply_with_plan_uses_official_path(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"program": {"id": "program-1", "revision": "4"}})
        plan = {
            "method": "online-programs-programs.publish",
            "baseline": {"env_fingerprint": "https://www.wixapis.com", "selector": {"programId": "program-1"}},
            "proposed_changes": [{"operation": "publish"}],
        }
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as handle:
            json.dump(plan, handle)
            plan_path = handle.name
        try:
            ctx = self._ctx(apply=True, yes=True, plan_in=plan_path)
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = online_programs_programs.cmd_online_programs_programs_publish(SimpleNamespace(program_id="program-1"), ctx)
            payload = json.loads(buf.getvalue())
        finally:
            Path(plan_path).unlink()

        self.assertEqual(rc, 0)
        self.assertFalse(payload["dry_run"])
        call = mock_client.return_value.request.call_args
        self.assertEqual(call.kwargs["method"], "POST")
        self.assertTrue(str(call.kwargs["url"]).endswith("/online-programs/v3/programs/program-1/publish"))


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import crm_tasks
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = action, payload


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestCrmTasksCommands(unittest.TestCase):
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
            "command_str": "wix-safe-agent-cli crm-tasks",
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

    def test_parser_exposes_crm_tasks_commands(self) -> None:
        parser = build_parser()
        cases = [
            (["crm-tasks", "create", "--task-json", '{"task":{"title":"Call"}}'], "create", True),
            (["crm-tasks", "get", "--task-id", "task-1"], "get", False),
            (["crm-tasks", "update", "--task-json", '{"task":{"id":"task-1","revision":"1","title":"Call"}}'], "update", True),
            (["crm-tasks", "delete", "--task-id", "task-1"], "delete", True),
            (["crm-tasks", "query"], "query", False),
            (["crm-tasks", "count", "--filter-json", '{"status":{"$eq":"OPEN"}}'], "count", False),
            (["crm-tasks", "move-after", "--task-id", "task-1", "--move-json", '{"beforeTaskId":"task-0"}'], "move-after", True),
        ]
        for argv, command, write_capable in cases:
            with self.subTest(command=command):
                args = parser.parse_args(argv)
                self.assertEqual(args.crm_tasks_cmd, command)
                self.assertEqual(args.write_capable, write_capable)

    @patch("wix_safe_agent_cli.commands.community_groups.HttpClient")
    def test_reads_use_official_paths(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"ok": True})

        cases = [
            (
                crm_tasks.cmd_crm_tasks_get,
                SimpleNamespace(task_id="task-1"),
                "GET",
                "/crm/tasks/v2/tasks/task-1",
                None,
            ),
            (
                crm_tasks.cmd_crm_tasks_query,
                SimpleNamespace(query_json=None),
                "POST",
                "/crm/tasks/v2/tasks/query",
                {"query": {"sort": [{"fieldName": "createdDate", "order": "DESC"}]}},
            ),
            (
                crm_tasks.cmd_crm_tasks_count,
                SimpleNamespace(filter_json='{"status":{"$eq":"OPEN"}}'),
                "POST",
                "/crm/tasks/v2/tasks/count",
                {"filter": {"status": {"$eq": "OPEN"}}},
            ),
        ]

        for func, args, http_method, path, body in cases:
            with self.subTest(path=path):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = func(args, self._ctx())
                payload = json.loads(buf.getvalue())
                self.assertEqual(rc, 0)
                self.assertEqual(payload["request"]["method"], http_method)
                self.assertEqual(payload["request"]["path"], path)
                if body is not None:
                    self.assertEqual(payload["request"]["body"], body)

    @patch("wix_safe_agent_cli.commands.community_groups.HttpClient")
    def test_plan_first_writes_use_official_paths(self, mock_client: unittest.mock.MagicMock) -> None:
        cases = [
            (
                crm_tasks.cmd_crm_tasks_create,
                SimpleNamespace(task_json='{"task":{"title":"Call"}}'),
                "POST",
                "/crm/tasks/v2/tasks",
                False,
            ),
            (
                crm_tasks.cmd_crm_tasks_update,
                SimpleNamespace(task_json='{"task":{"id":"task-1","revision":"1","title":"Call"}}'),
                "PATCH",
                "/crm/tasks/v2/tasks/task-1",
                False,
            ),
            (
                crm_tasks.cmd_crm_tasks_delete,
                SimpleNamespace(task_id="task-1"),
                "DELETE",
                "/crm/tasks/v2/tasks/task-1",
                True,
            ),
            (
                crm_tasks.cmd_crm_tasks_move_after,
                SimpleNamespace(task_id="task-1", move_json='{"beforeTaskId":"task-0"}'),
                "POST",
                "/crm/tasks/v2/tasks/task-1/move-after",
                False,
            ),
        ]

        for func, args, http_method, path, needs_ack in cases:
            with self.subTest(path=path):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = func(args, self._ctx())
                payload = json.loads(buf.getvalue())
                self.assertEqual(rc, 0)
                self.assertTrue(payload["dry_run"])
                self.assertEqual(payload["plan"]["request"]["method"], http_method)
                self.assertEqual(payload["plan"]["request"]["path"], path)
                if needs_ack:
                    self.assertIn("apply also requires --ack-irreversible", payload["plan"]["preconditions"])
                else:
                    self.assertNotIn("apply also requires --ack-irreversible", payload["plan"]["preconditions"])
                self.assertFalse(mock_client.return_value.request.called)

    @patch("wix_safe_agent_cli.commands.community_groups.HttpClient")
    def test_validates_required_fields(self, mock_client: unittest.mock.MagicMock) -> None:
        cases = [
            (crm_tasks.cmd_crm_tasks_create, SimpleNamespace(task_json='{"title":"Call"}'), "task"),
            (crm_tasks.cmd_crm_tasks_update, SimpleNamespace(task_json='{"task":{"revision":"1"}}'), "task.id"),
            (crm_tasks.cmd_crm_tasks_update, SimpleNamespace(task_json='{"task":{"id":"task-1"}}'), "task.revision"),
            (crm_tasks.cmd_crm_tasks_get, SimpleNamespace(task_id=""), "--task-id"),
            (crm_tasks.cmd_crm_tasks_delete, SimpleNamespace(task_id=None), "--task-id"),
            (crm_tasks.cmd_crm_tasks_move_after, SimpleNamespace(task_id="", move_json=None), "--task-id"),
        ]
        for func, args, expected_error in cases:
            with self.subTest(expected_error=expected_error):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = func(args, self._ctx())
                payload = json.loads(buf.getvalue())
                self.assertEqual(rc, 1)
                self.assertEqual(payload["error_type"], "ValidationError")
                self.assertIn(expected_error, payload["error"])
                self.assertFalse(mock_client.return_value.request.called)

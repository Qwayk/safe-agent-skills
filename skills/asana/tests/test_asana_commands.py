from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from asana_safe_agent_cli.commands.asana import cmd_api, cmd_auth_check
from asana_safe_agent_cli.errors import SafetyError, ValidationError

from .helpers import FakeClient, args, context, response


class TestAsanaCommands(unittest.TestCase):
    def test_read_uses_official_host_and_fixed_path(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            client = FakeClient([response(200, {"data": [{"gid": "w1", "name": "Work"}]})])
            ctx, out, _ = context(td, client)
            rc = cmd_api(args(operation="get-workspaces"), ctx)
        self.assertEqual(rc, 0)
        self.assertEqual(client.calls[0]["url"], "https://app.asana.com/api/1.0/workspaces")
        self.assertEqual(out.last["result"]["data"][0]["gid"], "w1")
        self.assertNotIn("test-token-not-printed", json.dumps(out.last))

    def test_offset_pagination_is_bounded_and_aggregated(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            client = FakeClient(
                [
                    response(200, {"data": [{"gid": "1"}], "next_page": {"offset": "next"}}),
                    response(200, {"data": [{"gid": "2"}], "next_page": None}),
                ]
            )
            ctx, out, _ = context(td, client)
            cmd_api(
                args(
                    operation="get-tasks-for-project",
                    param=["project_gid=p1"],
                    paginate=True,
                    max_pages=5,
                ),
                ctx,
            )
        self.assertEqual(out.last["pages_fetched"], 2)
        self.assertEqual([item["gid"] for item in out.last["result"]["data"]], ["1", "2"])
        self.assertEqual(client.calls[1]["params"]["offset"], "next")

    def test_auth_check_returns_bounded_identity(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            client = FakeClient(
                [response(200, {"data": {"gid": "u1", "name": "User", "resource_type": "user", "email": "private@example.com"}})]
            )
            ctx, out, _ = context(td, client)
            rc = cmd_auth_check(SimpleNamespace(), ctx)
        self.assertEqual(rc, 0)
        self.assertEqual(out.last["identity"], {"gid": "u1", "name": "User", "resource_type": "user"})
        self.assertNotIn("email", out.last["identity"])

    def test_stronger_delete_requires_risk_acknowledgement(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            plan_ctx, plan_out, _ = context(td, FakeClient([response(200, {"data": {"gid": "1"}})]))
            cmd_api(args(operation="delete-task", param=["task_gid=1"]), plan_ctx)
            plan_path = Path(plan_out.last["plan_out"])
            plan = json.loads(plan_path.read_text(encoding="utf-8"))
            with self.assertRaises(SafetyError):
                cmd_api(
                    args(
                        operation="delete-task",
                        apply=True,
                        plan_in=str(plan_path),
                        approve=plan["plan_id"],
                    ),
                    context(td, FakeClient([]))[0],
                )

    def test_attachment_command_requires_form_data_or_file(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(ValidationError):
                cmd_api(
                    args(operation="create-attachment-for-object"),
                    context(td, FakeClient([]))[0],
                )

    def test_json_write_requires_data_envelope_and_documented_top_level_fields(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            ctx = context(td, FakeClient([]))[0]
            with self.assertRaises(ValidationError):
                cmd_api(args(operation="create-task", data_json='{"name":"wrong envelope"}'), ctx)
            with self.assertRaises(ValidationError):
                cmd_api(
                    args(
                        operation="create-task",
                        data_json='{"data":{"name":"ok"},"undocumented":true}',
                    ),
                    ctx,
                )

    def test_attachment_refuses_app_components_field_and_unknown_file_field(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            upload = Path(td) / "brief.txt"
            upload.write_text("safe fixture", encoding="utf-8")
            ctx = context(td, FakeClient([]))[0]
            with self.assertRaises(ValidationError):
                cmd_api(
                    args(
                        operation="create-attachment-for-object",
                        data_json='{"parent":"1","connect_to_app":true}',
                    ),
                    ctx,
                )
            with self.assertRaises(ValidationError):
                cmd_api(
                    args(
                        operation="create-attachment-for-object",
                        data_json='{"parent":"1"}',
                        file=[f"payload={upload}"],
                    ),
                    ctx,
                )

    def test_provider_failure_writes_failed_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            plan_ctx, plan_out, _ = context(td, FakeClient([]))
            cmd_api(
                args(operation="create-task", data_json='{"data":{"name":"new"}}'),
                plan_ctx,
            )
            plan_path = Path(plan_out.last["plan_out"])
            plan = json.loads(plan_path.read_text(encoding="utf-8"))
            apply_ctx, apply_out, _ = context(td, FakeClient([response(403, {"errors": [{"message": "no"}]})]))
            rc = cmd_api(
                args(
                    operation="create-task",
                    apply=True,
                    plan_in=str(plan_path),
                    approve=plan["plan_id"],
                    acknowledge_no_snapshot=True,
                ),
                apply_ctx,
            )
            receipt = json.loads(Path(apply_out.last["receipt_out"]).read_text(encoding="utf-8"))
        self.assertEqual(rc, 1)
        self.assertFalse(receipt["verification"]["verified"])
        self.assertEqual(receipt["provider_status"], 403)

    def test_async_job_wait_reports_terminal_state(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            plan_ctx, plan_out, _ = context(td, FakeClient([]))
            cmd_api(
                args(operation="duplicate-project", param=["project_gid=p1"]),
                plan_ctx,
            )
            plan_path = Path(plan_out.last["plan_out"])
            plan = json.loads(plan_path.read_text(encoding="utf-8"))
            client = FakeClient(
                [
                    response(201, {"data": {"gid": "j1", "resource_type": "job"}}),
                    response(200, {"data": {"gid": "j1", "resource_type": "job", "status": "in_progress"}}),
                    response(200, {"data": {"gid": "j1", "resource_type": "job", "status": "succeeded"}}),
                ]
            )
            apply_ctx, apply_out, _ = context(td, client)
            rc = cmd_api(
                args(
                    operation="duplicate-project",
                    apply=True,
                    plan_in=str(plan_path),
                    approve=plan["plan_id"],
                    acknowledge_no_snapshot=True,
                    acknowledge_risk=True,
                    wait=True,
                ),
                apply_ctx,
            )
        self.assertEqual(rc, 0)
        self.assertEqual(apply_out.last["state"], "succeeded")
        self.assertEqual([call["method"] for call in client.calls], ["POST", "GET", "GET"])
        self.assertEqual(client.calls[0]["retries"], 0)
        self.assertEqual(client.calls[1]["retries"], 2)


if __name__ == "__main__":
    unittest.main()

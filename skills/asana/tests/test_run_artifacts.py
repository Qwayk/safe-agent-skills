from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from asana_safe_agent_cli.commands.asana import _canonical_hash, _plan_fingerprint, cmd_api
from asana_safe_agent_cli.errors import SafetyError

from .helpers import FakeClient, args, context, response


class TestWritePlansAndReceipts(unittest.TestCase):
    def _plan(self, td: str, **overrides: object) -> tuple[Path, dict[str, object]]:
        plan_ctx, plan_out, _ = context(td, FakeClient([]))
        values: dict[str, object] = {
            "operation": "create-task",
            "data_json": '{"data":{"name":"new","followers":["u1","u2"]}}',
        }
        values.update(overrides)
        cmd_api(args(**values), plan_ctx)
        plan_path = Path(plan_out.last["plan_out"])
        return plan_path, json.loads(plan_path.read_text(encoding="utf-8"))

    @staticmethod
    def _rewrite_with_public_plan_id(plan_path: Path, plan: dict[str, object]) -> str:
        plan["plan_id"] = _canonical_hash(_plan_fingerprint(plan))[:20]
        plan_path.write_text(json.dumps(plan), encoding="utf-8")
        return str(plan["plan_id"])

    def test_update_uses_saved_plan_snapshot_approval_and_readback(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            planning_client = FakeClient([response(200, {"data": {"gid": "1", "name": "old"}})])
            plan_ctx, plan_out, _ = context(td, planning_client)
            rc = cmd_api(
                args(
                    operation="update-task",
                    param=["task_gid=1"],
                    data_json='{"data":{"name":"new"}}',
                ),
                plan_ctx,
            )
            plan_path = Path(plan_out.last["plan_out"])
            plan = json.loads(plan_path.read_text(encoding="utf-8"))
            apply_client = FakeClient(
                [
                    response(200, {"data": {"gid": "1", "name": "old"}}),
                    response(200, {"data": {"gid": "1", "name": "new"}}),
                    response(200, {"data": {"gid": "1", "name": "new"}}),
                ]
            )
            apply_ctx, apply_out, _ = context(td, apply_client)
            apply_rc = cmd_api(
                args(
                    operation="update-task",
                    apply=True,
                    plan_in=str(plan_path),
                    approve=plan["plan_id"],
                ),
                apply_ctx,
            )
            receipt_path = Path(apply_out.last["receipt_out"])
            receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        self.assertEqual(rc, 0)
        self.assertEqual(apply_rc, 0)
        self.assertTrue(receipt["verification"]["verified"])
        self.assertEqual([call["method"] for call in apply_client.calls], ["GET", "PUT", "GET"])

    def test_no_snapshot_apply_requires_explicit_acknowledgement(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            plan_ctx, plan_out, _ = context(td, FakeClient([]))
            cmd_api(
                args(operation="create-task", data_json='{"data":{"name":"new"}}'),
                plan_ctx,
            )
            plan_path = Path(plan_out.last["plan_out"])
            plan = json.loads(plan_path.read_text(encoding="utf-8"))
            with self.assertRaises(SafetyError):
                cmd_api(
                    args(
                        operation="create-task",
                        apply=True,
                        plan_in=str(plan_path),
                        approve=plan["plan_id"],
                    ),
                    context(td, FakeClient([]))[0],
                )

    def test_snapshot_drift_refuses_apply(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            plan_ctx, plan_out, _ = context(
                td, FakeClient([response(200, {"data": {"gid": "1", "name": "old"}})])
            )
            cmd_api(
                args(
                    operation="update-task",
                    param=["task_gid=1"],
                    data_json='{"data":{"name":"new"}}',
                ),
                plan_ctx,
            )
            plan_path = Path(plan_out.last["plan_out"])
            plan = json.loads(plan_path.read_text(encoding="utf-8"))
            drift_client = FakeClient([response(200, {"data": {"gid": "1", "name": "changed"}})])
            with self.assertRaises(SafetyError):
                cmd_api(
                    args(
                        operation="update-task",
                        apply=True,
                        plan_in=str(plan_path),
                        approve=plan["plan_id"],
                    ),
                    context(td, drift_client)[0],
                )

    def test_tampered_plan_is_refused_before_provider_call(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            plan_ctx, plan_out, _ = context(td, FakeClient([]))
            cmd_api(
                args(operation="create-task", data_json='{"data":{"name":"new"}}'),
                plan_ctx,
            )
            plan_path = Path(plan_out.last["plan_out"])
            plan = json.loads(plan_path.read_text(encoding="utf-8"))
            approved_id = plan["plan_id"]
            plan["request_body"]["data"]["name"] = "tampered"
            plan_path.write_text(json.dumps(plan), encoding="utf-8")
            client = FakeClient([])
            with self.assertRaises(SafetyError):
                cmd_api(
                    args(
                        operation="create-task",
                        apply=True,
                        plan_in=str(plan_path),
                        approve=approved_id,
                        acknowledge_no_snapshot=True,
                    ),
                    context(td, client)[0],
                )
            self.assertEqual(client.calls, [])

    def test_recomputed_plan_id_cannot_redirect_create_task_to_batch(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            plan_path, plan = self._plan(td)
            target = plan["target"]
            assert isinstance(target, dict)
            target["path"] = "/batch"
            plan["risk_class"] = "write"
            plan["risk_reasons"] = []
            approved_id = self._rewrite_with_public_plan_id(plan_path, plan)
            client = FakeClient([response(200, {"data": {}})])
            with self.assertRaises(SafetyError):
                cmd_api(
                    args(
                        operation="create-task",
                        apply=True,
                        plan_in=str(plan_path),
                        approve=approved_id,
                        acknowledge_no_snapshot=True,
                        acknowledge_risk=True,
                    ),
                    context(td, client)[0],
                )
            self.assertEqual(client.calls, [])

    def test_recomputed_plan_id_cannot_redirect_to_scim(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            plan_path, plan = self._plan(td)
            target = plan["target"]
            assert isinstance(target, dict)
            target["path"] = "/scim/Users"
            approved_id = self._rewrite_with_public_plan_id(plan_path, plan)
            client = FakeClient([response(200, {"data": {}})])
            with self.assertRaises(SafetyError):
                cmd_api(
                    args(
                        operation="create-task",
                        apply=True,
                        plan_in=str(plan_path),
                        approve=approved_id,
                        acknowledge_no_snapshot=True,
                        acknowledge_risk=True,
                    ),
                    context(td, client)[0],
                )
            self.assertEqual(client.calls, [])

    def test_authenticated_plan_binds_all_provider_and_safety_fields(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            upload = Path(td) / "changed.txt"
            upload.write_text("changed file", encoding="utf-8")
            upload_metadata = {
                "field": "file",
                "path": str(upload),
                "name": upload.name,
                "size": upload.stat().st_size,
                "sha256": hashlib.sha256(upload.read_bytes()).hexdigest(),
            }

            def change_target(plan: dict[str, object], key: str, value: object) -> None:
                target = plan["target"]
                assert isinstance(target, dict)
                target[key] = value

            mutations = {
                "method": lambda plan: plan.__setitem__("method", "DELETE"),
                "operation": lambda plan: plan.__setitem__("operation_id", "deleteTask"),
                "command": lambda plan: plan.__setitem__("command", "delete-task"),
                "query": lambda plan: change_target(plan, "query", {"opt_pretty": "true"}),
                "body": lambda plan: plan.__setitem__(
                    "request_body", {"data": {"name": "changed"}}
                ),
                "file metadata": lambda plan: plan.__setitem__("files", [upload_metadata]),
                "risk": lambda plan: (
                    plan.__setitem__("risk_class", "write"),
                    plan.__setitem__("risk_reasons", []),
                ),
                "snapshot": lambda plan: plan.__setitem__(
                    "snapshot",
                    {
                        "available": True,
                        "operation_id": "getTask",
                        "captured_at_utc": "2026-07-27T00:00:00Z",
                        "sha256": "0" * 64,
                        "data": {"data": {"gid": "1"}},
                    },
                ),
                "verification": lambda plan: plan.__setitem__(
                    "verification_operation_id", "getTask"
                ),
            }
            for name, mutate in mutations.items():
                with self.subTest(field=name):
                    case_dir = Path(td) / name.replace(" ", "-")
                    case_dir.mkdir()
                    plan_path, plan = self._plan(str(case_dir))
                    mutate(plan)
                    approved_id = self._rewrite_with_public_plan_id(plan_path, plan)
                    client = FakeClient([response(200, {"data": {}})] * 4)
                    with self.assertRaises(SafetyError):
                        cmd_api(
                            args(
                                operation="create-task",
                                apply=True,
                                plan_in=str(plan_path),
                                approve=approved_id,
                                acknowledge_no_snapshot=True,
                                acknowledge_risk=True,
                            ),
                            context(str(case_dir), client)[0],
                        )
                    self.assertEqual(client.calls, [])

    def test_missing_or_changed_local_signing_state_refuses_before_http(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            for name in ("missing integrity", "changed integrity", "missing key", "changed key"):
                with self.subTest(case=name):
                    case_dir = Path(td) / name.replace(" ", "-")
                    case_dir.mkdir()
                    plan_path, plan = self._plan(str(case_dir))
                    self.assertIn("integrity", plan)
                    key_path = case_dir / ".state" / "plan-signing.key"
                    self.assertTrue(key_path.is_file())
                    if name == "missing integrity":
                        plan.pop("integrity")
                        plan_path.write_text(json.dumps(plan), encoding="utf-8")
                    elif name == "changed integrity":
                        integrity = plan["integrity"]
                        assert isinstance(integrity, dict)
                        integrity["signature"] = "0" * 64
                        plan_path.write_text(json.dumps(plan), encoding="utf-8")
                    elif name == "missing key":
                        key_path.unlink()
                    else:
                        key_path.write_bytes(b"x" * 32)
                    client = FakeClient([response(200, {"data": {}})])
                    with self.assertRaises(SafetyError):
                        cmd_api(
                            args(
                                operation="create-task",
                                apply=True,
                                plan_in=str(plan_path),
                                approve=str(plan["plan_id"]),
                                acknowledge_no_snapshot=True,
                                acknowledge_risk=True,
                            ),
                            context(str(case_dir), client)[0],
                        )
                    self.assertEqual(client.calls, [])

    def test_upload_file_hash_drift_is_refused_before_http(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            upload = Path(td) / "brief.txt"
            upload.write_text("planned content", encoding="utf-8")
            plan_ctx, plan_out, _ = context(td, FakeClient([]))
            cmd_api(
                args(
                    operation="create-attachment-for-object",
                    data_json='{"parent":"1"}',
                    file=[f"file={upload}"],
                ),
                plan_ctx,
            )
            plan_path = Path(plan_out.last["plan_out"])
            plan = json.loads(plan_path.read_text(encoding="utf-8"))
            upload.write_text("changed content", encoding="utf-8")
            client = FakeClient([response(200, {"data": {"gid": "a1"}})])
            with self.assertRaises(SafetyError):
                cmd_api(
                    args(
                        operation="create-attachment-for-object",
                        apply=True,
                        plan_in=str(plan_path),
                        approve=plan["plan_id"],
                        acknowledge_no_snapshot=True,
                        acknowledge_risk=True,
                    ),
                    context(td, client)[0],
                )
            self.assertEqual(client.calls, [])

    def test_request_content_can_elevate_an_ordinary_write_to_stronger_approval(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            plan_ctx, plan_out, _ = context(td, FakeClient([]))
            cmd_api(
                args(
                    operation="create-task",
                    data_json='{"data":{"name":"new","followers":["u1","u2"]}}',
                ),
                plan_ctx,
            )
            plan = json.loads(Path(plan_out.last["plan_out"]).read_text(encoding="utf-8"))
        self.assertEqual(plan["risk_class"], "write_stronger_approval")
        self.assertIn("bulk or fan-out request data", plan["risk_reasons"])
        self.assertIn(
            "visible collaboration, notification, or approval effect",
            plan["risk_reasons"],
        )


if __name__ == "__main__":
    unittest.main()

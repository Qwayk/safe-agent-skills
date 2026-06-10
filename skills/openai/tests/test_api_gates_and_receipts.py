from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from typing import Any
from types import SimpleNamespace
from unittest.mock import patch

from openai_api_tool.api_dispatch import load_operations_from_pinned_snapshot, operations_by_command
from openai_api_tool.audit_log import AuditLogger
from openai_api_tool.commands.api import (
    STREAM_MAX_BYTES,
    STREAM_STOP_TOKEN,
    _classify_operation,
    cmd_api_call,
)
from openai_api_tool.commands.demo import cmd_demo_write
from openai_api_tool.http import HttpResponse
from openai_api_tool.output import Output


class TestApiCommands(unittest.TestCase):
    def _ctx(self, artifacts_dir: Path | None = None, **overrides: Any) -> dict[str, Any]:
        base = {
            "cfg": SimpleNamespace(
                base_url="https://example.invalid",
                api_key="sk-test",
                organization_id=None,
                project_id=None,
                timeout_s=30,
            ),
            "tool": "openai-api-tool",
            "tool_version": "0.1.0",
            "command_str": "openai-api-tool api",
            "project_cfg": None,
            "project_dir": Path("."),
            "env_file": ".env",
            "timeout_s": 30,
            "live": False,
            "verbose": False,
            "apply": False,
            "yes": False,
            "plan_out": None,
            "plan_in": None,
            "receipt_out": None,
            "ack_irreversible": False,
            "ack_spend_money": False,
            "out": Output(mode="json"),
            "audit": AuditLogger(path=None, enabled=False),
            "artifacts_dir": artifacts_dir,
        }
        base.update(overrides)
        return base

    def _args(
        self,
        op: str,
        body_json: str | None = None,
        path_items: list[str] | None = None,
        query_items: list[str] | None = None,
        file_items: list[str] | None = None,
    ) -> SimpleNamespace:
        return SimpleNamespace(
            op=op,
            path_json=None,
            query_json=None,
            body_json=body_json,
            path=path_items,
            query=query_items,
            file=file_items,
        )

    def _assert_no_recovery_contract(self, contract: Any) -> None:
        self.assertIsInstance(contract, dict)
        self.assertFalse(contract.get("automatic_rollback"))
        self.assertEqual(contract.get("backups"), [])
        self.assertEqual(contract.get("snapshots"), [])
        self.assertIsNone(contract.get("rollback_plan"))
        self.assertIn("restore_note", contract)

    def _assert_blocked_before_state(self, plan: dict[str, Any]) -> None:
        before_state = plan.get("before_state")
        self.assertIsInstance(before_state, dict)
        self.assertTrue(before_state.get("required"))
        self.assertFalse(before_state.get("supported"))
        self.assertEqual(before_state.get("status"), "no_snapshot_available")
        self.assertIsNone(before_state.get("saved_path"))
        self.assertIsNone(before_state.get("provider_backup_id"))
        verification_plan = plan.get("verification_plan")
        self.assertIsInstance(verification_plan, dict)
        self.assertEqual(verification_plan.get("type"), "best_effort_after_apply")

    def test_plan_includes_gates(self) -> None:
        args = self._args("ListContainers")
        ctx = self._ctx(apply=False)
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cmd_api_call(args, ctx)
        self.assertEqual(rc, 0)
        payload = json.loads(buf.getvalue())
        plan = payload["plan"]
        classification = plan["classification"]
        self.assertIsInstance(classification["gates"], dict)
        self.assertEqual(classification["gates"]["apply"], classification["is_write"])
        self.assertFalse(payload["dry_run"] is False)

    def test_apply_requires_live(self) -> None:
        args = self._args("CreateContainer", body_json='{"name": "demo"}')
        ctx = self._ctx(apply=True, live=False, yes=True, ack_spend_money=False)
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cmd_api_call(args, ctx)
        self.assertEqual(rc, 0)
        payload = json.loads(buf.getvalue())
        self.assertTrue(payload.get("refused"))
        self.assertTrue(any("--live" in reason for reason in payload.get("reasons", [])))

    def test_get_apply_requires_live(self) -> None:
        args = self._args("ListContainers")
        ctx = self._ctx(apply=True, live=False, yes=True)
        buf = io.StringIO()
        with patch("openai_api_tool.commands.api.HttpClient.request") as mock_request:
            mock_request.side_effect = AssertionError("HttpClient.request should not run when live is false")
            with redirect_stdout(buf):
                rc = cmd_api_call(args, ctx)
        self.assertEqual(rc, 0)
        payload = json.loads(buf.getvalue())
        self.assertTrue(payload.get("refused"))
        self.assertTrue(any("--live" in reason for reason in payload.get("reasons", [])))
        mock_request.assert_not_called()

    def test_get_live_without_apply_executes(self) -> None:
        args = self._args("ListContainers")
        ctx = self._ctx(apply=False, live=True)
        buf = io.StringIO()
        response = HttpResponse(
            status=200,
            headers={"content-type": "application/json"},
            body=b"{\"ok\": true}",
            url="https://example.invalid/containers",
        )
        with patch("openai_api_tool.commands.api.HttpClient.request", return_value=response) as mock_request:
            with redirect_stdout(buf):
                rc = cmd_api_call(args, ctx)
        self.assertEqual(rc, 0)
        payload = json.loads(buf.getvalue())
        self.assertFalse(payload.get("dry_run"))
        mock_request.assert_called_once()

    def test_beta_header_is_sent_for_ops_with_beta(self) -> None:
        args = self._args("ListThreadsMethod")
        ctx = self._ctx(apply=False, live=True)
        buf = io.StringIO()
        response = HttpResponse(
            status=200,
            headers={"content-type": "application/json"},
            body=b"{\"ok\": true}",
            url="https://example.invalid/chatkit/threads",
        )
        with patch("openai_api_tool.commands.api.HttpClient.request", return_value=response) as mock_request:
            with redirect_stdout(buf):
                rc = cmd_api_call(args, ctx)

        self.assertEqual(rc, 0)
        payload = json.loads(buf.getvalue())
        self.assertFalse(payload.get("dry_run"))
        self.assertEqual(mock_request.call_count, 1)
        headers = mock_request.call_args[1]["headers"]
        self.assertEqual(headers.get("OpenAI-Beta"), "chatkit_beta=v1")

    def test_spend_money_apply_requires_plan_in_and_ack(self) -> None:
        args = self._args("Compactconversation", body_json='{"input": "test"}')
        with tempfile.TemporaryDirectory() as tmpd:
            plan_path = Path(tmpd) / "plan.json"
            receipt_path = Path(tmpd) / "receipt.json"

            ctx_plan = self._ctx(apply=False, plan_out=str(plan_path))
            buf_plan = io.StringIO()
            with redirect_stdout(buf_plan):
                rc_plan = cmd_api_call(args, ctx_plan)
            self.assertEqual(rc_plan, 0)
            payload_plan = json.loads(buf_plan.getvalue())
            self.assertIn("plan", payload_plan)
            self.assertIn("recovery", payload_plan["plan"])
            self._assert_no_recovery_contract(payload_plan["plan"]["recovery"])
            self._assert_blocked_before_state(payload_plan["plan"])
            self.assertTrue(plan_path.exists())

            ctx_bad = self._ctx(
                apply=True,
                live=True,
                yes=True,
                ack_spend_money=False,
                plan_in=None,
                receipt_out=str(receipt_path),
            )
            buf_bad = io.StringIO()
            with redirect_stdout(buf_bad):
                rc_bad = cmd_api_call(args, ctx_bad)
            self.assertEqual(rc_bad, 0)
            payload_bad = json.loads(buf_bad.getvalue())
            self.assertTrue(payload_bad.get("refused"))
            self.assertTrue(any("--plan-in" in reason for reason in payload_bad.get("reasons", [])))

            ctx_apply = self._ctx(
                apply=True,
                live=True,
                yes=True,
                ack_spend_money=True,
                plan_in=str(plan_path),
                receipt_out=str(receipt_path),
            )
            buf_apply = io.StringIO()
            with patch("openai_api_tool.commands.api.HttpClient.request") as mock_request:
                mock_request.side_effect = AssertionError("HttpClient.request should not run without before-state")
                with redirect_stdout(buf_apply):
                    rc_apply = cmd_api_call(args, ctx_apply)
            self.assertEqual(rc_apply, 0)
            payload_apply = json.loads(buf_apply.getvalue())
            self.assertFalse(payload_apply.get("dry_run"))
            self.assertTrue(payload_apply.get("refused"))
            self.assertIn("before-state", " ".join(payload_apply.get("reasons", [])))
            self.assertIn("plan", payload_apply)
            self._assert_blocked_before_state(payload_apply["plan"])
            self.assertFalse(receipt_path.exists())
            mock_request.assert_not_called()

    def test_delete_refuses_before_provider_write(self) -> None:
        args = self._args("DeleteContainer", path_items=["container_id=example"])
        with tempfile.TemporaryDirectory() as tmpd:
            plan_path = Path(tmpd) / "plan.json"
            receipt_path = Path(tmpd) / "receipt.json"

            ctx_plan = self._ctx(plan_out=str(plan_path))
            buf_plan = io.StringIO()
            with redirect_stdout(buf_plan):
                rc_plan = cmd_api_call(args, ctx_plan)
            self.assertEqual(rc_plan, 0)
            plan_obj = json.loads(plan_path.read_text(encoding="utf-8"))
            self._assert_blocked_before_state(plan_obj)

            ctx_apply = self._ctx(
                artifacts_dir=Path(tmpd),
                live=True,
                apply=True,
                plan_in=str(plan_path),
                yes=True,
                ack_irreversible=True,
                receipt_out=str(receipt_path),
            )
            buf_apply = io.StringIO()
            with patch("openai_api_tool.commands.api.HttpClient.request") as mock_request:
                mock_request.side_effect = AssertionError("HttpClient.request should not run without before-state")
                with redirect_stdout(buf_apply):
                    rc_apply = cmd_api_call(args, ctx_apply)
            self.assertEqual(rc_apply, 0)
            payload = json.loads(buf_apply.getvalue())
            self.assertTrue(payload.get("refused"))
            self.assertFalse(receipt_path.exists())
            mock_request.assert_not_called()

    def test_create_moderation_enforces_spend_money_flags(self) -> None:
        args = self._args("createModeration", body_json='{"input": "test"}')
        with tempfile.TemporaryDirectory() as tmpd:
            plan_path = Path(tmpd) / "plan.json"
            receipt_path = Path(tmpd) / "receipt.json"

            ctx_plan = self._ctx(apply=False, plan_out=str(plan_path))
            buf_plan = io.StringIO()
            with redirect_stdout(buf_plan):
                rc_plan = cmd_api_call(args, ctx_plan)
            self.assertEqual(rc_plan, 0)
            payload_plan = json.loads(buf_plan.getvalue())
            classification = payload_plan["plan"]["classification"]
            gates = classification["gates"]
            self.assertTrue(classification["spend_money"])
            self.assertTrue(gates["plan_in"])
            self.assertTrue(gates["yes"])
            self.assertTrue(gates["ack_spend_money"])
            self.assertIn("recovery", payload_plan["plan"])
            self._assert_no_recovery_contract(payload_plan["plan"]["recovery"])
            self._assert_blocked_before_state(payload_plan["plan"])

            ctx_ack = self._ctx(
                apply=True,
                live=True,
                yes=True,
                ack_spend_money=False,
                plan_in=str(plan_path),
                receipt_out=str(receipt_path),
            )
            buf_ack = io.StringIO()
            with patch("openai_api_tool.commands.api.HttpClient.request") as mock_request:
                mock_request.side_effect = AssertionError("HttpClient.request should not run when gates fail")
                with redirect_stdout(buf_ack):
                    rc_ack = cmd_api_call(args, ctx_ack)
            self.assertEqual(rc_ack, 0)
            payload_ack = json.loads(buf_ack.getvalue())
            self.assertTrue(payload_ack.get("refused"))
            self.assertTrue(any("--ack-spend-money" in reason for reason in payload_ack.get("reasons", [])))
            mock_request.assert_not_called()

            ctx_yes = self._ctx(
                apply=True,
                live=True,
                yes=False,
                ack_spend_money=True,
                plan_in=str(plan_path),
                receipt_out=str(receipt_path),
            )
            buf_yes = io.StringIO()
            with patch("openai_api_tool.commands.api.HttpClient.request") as mock_request_yes:
                mock_request_yes.side_effect = AssertionError("HttpClient.request should not run when --yes missing")
                with redirect_stdout(buf_yes):
                    rc_yes = cmd_api_call(args, ctx_yes)
            self.assertEqual(rc_yes, 0)
            payload_yes = json.loads(buf_yes.getvalue())
            self.assertTrue(payload_yes.get("refused"))
            self.assertTrue(any("--yes" in reason for reason in payload_yes.get("reasons", [])))
            mock_request_yes.assert_not_called()

            ctx_plan_missing = self._ctx(
                apply=True,
                live=True,
                yes=True,
                ack_spend_money=True,
                receipt_out=str(receipt_path),
            )
            buf_plan_missing = io.StringIO()
            with patch("openai_api_tool.commands.api.HttpClient.request") as mock_request_plan:
                mock_request_plan.side_effect = AssertionError("HttpClient.request should not run when plan-in missing")
                with redirect_stdout(buf_plan_missing):
                    rc_plan_missing = cmd_api_call(args, ctx_plan_missing)
            self.assertEqual(rc_plan_missing, 0)
            payload_plan_missing = json.loads(buf_plan_missing.getvalue())
            self.assertTrue(payload_plan_missing.get("refused"))
            self.assertTrue(any("--plan-in" in reason for reason in payload_plan_missing.get("reasons", [])))

    def test_live_refuses_with_missing_required_inputs(self) -> None:
        args = self._args("CreateContainer")
        with tempfile.TemporaryDirectory() as tmpd:
            ctx = self._ctx(
                artifacts_dir=Path(tmpd),
                live=True,
                apply=True,
                yes=True,
            )
            buf = io.StringIO()
            with patch("openai_api_tool.commands.api.HttpClient.request") as mock_request:
                mock_request.side_effect = AssertionError("HttpClient.request should not run when missing inputs")
                with redirect_stdout(buf):
                    rc = cmd_api_call(args, ctx)
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload.get("refused"))
            self.assertTrue(any("missing required inputs" in reason for reason in payload.get("reasons", [])))
            mock_request.assert_not_called()

    def test_demo_write_includes_no_recovery_contract(self) -> None:
        with tempfile.TemporaryDirectory() as tmpd:
            args = SimpleNamespace(selector="demo-resource")
            plan_path = Path(tmpd) / "plan.json"
            receipt_path = Path(tmpd) / "receipt.json"

            ctx_plan = self._ctx(plan_out=str(plan_path), command_str="openai-api-tool demo write --selector demo-resource")
            buf_plan = io.StringIO()
            with redirect_stdout(buf_plan):
                rc_plan = cmd_demo_write(args, ctx_plan)
            self.assertEqual(rc_plan, 0)
            payload_plan = json.loads(buf_plan.getvalue())
            self.assertIn("plan", payload_plan)
            self.assertIn("recovery", payload_plan["plan"])
            self.assertNotIn("rollback", payload_plan["plan"])
            self._assert_no_recovery_contract(payload_plan["plan"]["recovery"])
            self._assert_blocked_before_state(payload_plan["plan"])

            saved_plan = json.loads(plan_path.read_text(encoding="utf-8"))
            self.assertIn("recovery", saved_plan)
            self._assert_no_recovery_contract(saved_plan["recovery"])
            self._assert_blocked_before_state(saved_plan)

            ctx_apply = self._ctx(
                apply=True,
                plan_in=str(plan_path),
                receipt_out=str(receipt_path),
                command_str="openai-api-tool --apply --plan-in plan.json demo write --selector demo-resource",
            )
            buf_apply = io.StringIO()
            with redirect_stdout(buf_apply):
                rc_apply = cmd_demo_write(args, ctx_apply)
            self.assertEqual(rc_apply, 0)
            payload_apply = json.loads(buf_apply.getvalue())
            self.assertFalse(payload_apply["dry_run"])
            self.assertTrue(payload_apply["refused"])
            self._assert_blocked_before_state(payload_apply["plan"])
            self.assertFalse(receipt_path.exists())

    def test_streaming_write_refuses_before_stream_setup(self) -> None:
        args = self._args("createChatCompletion", body_json='{"input": "hi"}', query_items=["stream=true"])
        with tempfile.TemporaryDirectory() as tmpd:
            plan_path = Path(tmpd) / "plan.json"
            ctx_plan = self._ctx(
                artifacts_dir=Path(tmpd),
                plan_out=str(plan_path),
            )
            buf_plan = io.StringIO()
            with redirect_stdout(buf_plan):
                rc_plan = cmd_api_call(args, ctx_plan)
            self.assertEqual(rc_plan, 0)

            buf_apply = io.StringIO()
            with patch("openai_api_tool.commands.api.HttpClient.request") as mock_request:
                mock_request.side_effect = AssertionError("HttpClient.request should not run without before-state")
                ctx_apply = self._ctx(
                    artifacts_dir=Path(tmpd),
                    live=True,
                    apply=True,
                    plan_in=str(plan_path),
                    yes=True,
                    ack_spend_money=True,
                )
                with redirect_stdout(buf_apply):
                    rc_apply = cmd_api_call(args, ctx_apply)
            self.assertEqual(rc_apply, 0)
            payload_apply = json.loads(buf_apply.getvalue())
            self.assertTrue(payload_apply.get("refused"))
            mock_request.assert_not_called()

    def test_binary_responses_saved_to_artifact(self) -> None:
        args = self._args("RetrieveVideoContent", path_items=["video_id=example"])
        with tempfile.TemporaryDirectory() as tmpd:
            art_dir = Path(tmpd)
            ctx = self._ctx(artifacts_dir=art_dir, live=True, apply=False)
            binary_resp = HttpResponse(
                status=200,
                headers={"content-type": "application/octet-stream"},
                body=b"\x00\x01\x02",
                url="https://example.invalid/videos/example/content",
            )
            buf = io.StringIO()
            with patch("openai_api_tool.commands.api.HttpClient.request", return_value=binary_resp):
                with redirect_stdout(buf):
                    rc = cmd_api_call(args, ctx)
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            artifact = payload["receipt"]["response"]["body"]["artifact"]
            artifact_path = Path(artifact["path"])
            self.assertTrue(artifact_path.exists())
            self.assertEqual(artifact["byte_count"], 3)
            self.assertFalse(payload["receipt"]["response"]["body"]["streamed"])

    def test_json_response_preview_redacts_secrets(self) -> None:
        args = self._args("ListContainers")
        with tempfile.TemporaryDirectory() as tmpd:
            ctx = self._ctx(artifacts_dir=Path(tmpd), live=True, apply=False)
            response = HttpResponse(
                status=200,
                headers={"content-type": "application/json"},
                body=b'{"api_key": "sk-secret", "nested": {"token": "abc"}}',
                url="https://example.invalid/containers",
            )
            buf = io.StringIO()
            with patch("openai_api_tool.commands.api.HttpClient.request", return_value=response):
                with redirect_stdout(buf):
                    rc = cmd_api_call(args, ctx)
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            preview = payload["receipt"]["response"]["body"]["preview"]
            self.assertNotIn("sk-secret", preview)
            self.assertNotIn("abc", preview)

    def test_plan_and_receipt_redact_secrets_but_plan_in_still_matches(self) -> None:
        args = self._args("Compactconversation", body_json='{"secret": "sk-secret", "max_tokens": 5}')
        with tempfile.TemporaryDirectory() as tmpd:
            plan_path = Path(tmpd) / "plan.json"
            receipt_path = Path(tmpd) / "receipt.json"

            ctx_plan = self._ctx(plan_out=str(plan_path))
            buf_plan = io.StringIO()
            with redirect_stdout(buf_plan):
                rc_plan = cmd_api_call(args, ctx_plan)
            self.assertEqual(rc_plan, 0)
            plan_obj = json.loads(plan_path.read_text(encoding="utf-8"))
            body = plan_obj["inputs"]["body"]
            self.assertEqual(body["secret"], "<redacted>")
            self.assertEqual(body["max_tokens"], 5)

            ctx_apply = self._ctx(
                artifacts_dir=Path(tmpd),
                live=True,
                apply=True,
                yes=True,
                ack_spend_money=True,
                plan_in=str(plan_path),
                receipt_out=str(receipt_path),
            )
            buf_apply = io.StringIO()
            with patch("openai_api_tool.commands.api.HttpClient.request") as mock_request:
                mock_request.side_effect = AssertionError("HttpClient.request should not run without before-state")
                with redirect_stdout(buf_apply):
                    rc_apply = cmd_api_call(args, ctx_apply)
            self.assertEqual(rc_apply, 0)

            payload_apply = json.loads(buf_apply.getvalue())
            payload_body = payload_apply["plan"]["inputs"]["body"]
            self.assertEqual(payload_body["secret"], "<redacted>")
            self.assertEqual(payload_body["max_tokens"], 5)
            self.assertTrue(payload_apply.get("refused"))
            self.assertFalse(receipt_path.exists())
            mock_request.assert_not_called()

    def test_major_operations_plan_and_refuse_apply_without_before_state(self) -> None:
        ops = operations_by_command(load_operations_from_pinned_snapshot())
        required_ops = [
            "createResponse",
            "CreateChatSessionMethod",
            "createEmbedding",
            "createImage",
            "createSpeech",
            "createFile",
            "createFineTuningJob",
            "createBatch",
            "createVectorStore",
            "createAssistant",
            "create-realtime-client-secret",
            "admin-api-keys-create",
        ]
        for op_cmd in required_ops:
            with self.subTest(operation=op_cmd):
                op_spec = ops[op_cmd]
                path_items = [f"{name}=sample-{name}" for name in op_spec.required_path_params]
                body_json = '{"input": "value"}' if op_spec.required_request_body else '{"meta": "value"}'
                with tempfile.TemporaryDirectory() as tmpd:
                    plan_path = Path(tmpd) / f"{op_cmd}-plan.json"
                    ctx_plan = self._ctx(artifacts_dir=Path(tmpd), plan_out=str(plan_path))
                    args_plan = self._args(op_cmd, body_json=body_json, path_items=path_items)
                    buf_plan = io.StringIO()
                    with redirect_stdout(buf_plan):
                        rc_plan = cmd_api_call(args_plan, ctx_plan)
                    self.assertEqual(rc_plan, 0)
                    plan_obj = json.loads(plan_path.read_text(encoding="utf-8"))
                    op_data = plan_obj["operation"]
                    self.assertEqual(op_data["method"], op_spec.method)
                    self.assertEqual(op_data["path_template"], op_spec.path)
                    self.assertFalse(plan_obj["requirements"]["missing_required"])
                    self._assert_blocked_before_state(plan_obj)

                    classification = _classify_operation(op_spec)
                    plan_url = op_data["url"]
                    with patch("openai_api_tool.commands.api.HttpClient.request") as mock_request:
                        mock_request.side_effect = AssertionError("HttpClient.request should not run without before-state")
                        ctx_apply = self._ctx(
                            artifacts_dir=Path(tmpd),
                            live=True,
                            apply=True,
                            plan_in=str(plan_path),
                            yes=True,
                            ack_spend_money=bool(classification["gates"]["ack_spend_money"]),
                            ack_irreversible=bool(classification["gates"]["ack_irreversible"]),
                        )
                        buf_apply = io.StringIO()
                        with redirect_stdout(buf_apply):
                            rc_apply = cmd_api_call(args_plan, ctx_apply)
                    self.assertEqual(rc_apply, 0)
                    payload_apply = json.loads(buf_apply.getvalue())
                    self.assertTrue(payload_apply.get("refused"))
                    self.assertEqual(payload_apply["plan"]["operation"]["url"], plan_url)
                    mock_request.assert_not_called()

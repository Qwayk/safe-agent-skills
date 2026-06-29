from __future__ import annotations

import io
import json
import tempfile
from copy import deepcopy
from contextlib import redirect_stdout
from unittest import mock
from pathlib import Path
from typing import Any

import unittest

from zapier_safe_agent_cli.cli import _build_plan, main
from zapier_safe_agent_cli.config import load_config
from zapier_safe_agent_cli.operations import load_operations


class TestOperationSafety(unittest.TestCase):
    def _base_env(self, td: str) -> Path:
        env = Path(td) / ".env"
        env.write_text(
            "\n".join(
                [
                    "ZAPIER_BASE_URL=https://api.zapier.com",
                    "ZAPIER_AI_ACTIONS_BASE_URL=https://actions.zapier.com",
                    "ZAPIER_TRIGGER_INBOX_BASE_URL=https://api.zapier.com",
                    "ZAPIER_ACCESS_TOKEN=unit-test-token-SECRET",
                    "ZAPIER_TIMEOUT_S=30",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        return env

    def _write_env_with_token(self, path: Path, token: str) -> None:
        path.write_text(
            "\n".join(
                [
                    "ZAPIER_BASE_URL=https://api.zapier.com",
                    "ZAPIER_AI_ACTIONS_BASE_URL=https://actions.zapier.com",
                    "ZAPIER_TRIGGER_INBOX_BASE_URL=https://api.zapier.com",
                    f"ZAPIER_ACCESS_TOKEN={token}",
                    "ZAPIER_TIMEOUT_S=30",
                ]
            )
            + "\n",
            encoding="utf-8",
        )

    def test_write_command_defaults_to_plan(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env = self._base_env(td)
            plan_out = Path(td) / "plan.json"
            cmd = [
                "--env-file",
                str(env),
                "--output",
                "json",
                "--plan-out",
                str(plan_out),
                "ai-actions",
                "ai-actions-create-ai-action",
                "--body-json",
                '{"name":"test"}',
            ]
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(cmd)
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])
            self.assertTrue(payload["status"] == "planned")
            self.assertTrue(plan_out.exists())
            self.assertNotIn("unit-test-token-SECRET", buf.getvalue())

    def test_high_risk_apply_requires_plan_in(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env = self._base_env(td)
            cmd = [
                "--env-file",
                str(env),
                "--output",
                "json",
                "--apply",
                "ai-actions",
                "ai-actions-create-ai-action",
                "--body-json",
                '{"name":"test"}',
            ]
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(cmd)
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["refused"])
            self.assertIn("High-risk operations require --plan-in", " ".join(payload.get("reasons", [])))

    def test_plan_in_and_refused_without_ack(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env = self._base_env(td)
            cfg = load_config(str(env))
            op = next(op for op in load_operations() if op.group == "ai-actions" and op.command == "ai-actions-create-ai-action")
            plan = _build_plan(
                cfg=cfg,
                command="qwayk-zapier-safe-agent-cli ai-actions ai-actions-create-ai-action --body-json <redacted-body-json>",
                op=op,
                path_params={},
                query={},
                body={"name": "test"},
                risk="high",
            )
            plan_path = Path(td) / "plan.json"
            plan_path.write_text(json.dumps(plan), encoding="utf-8")

            cmd = [
                "--env-file",
                str(env),
                "--output",
                "json",
                "--apply",
                "--plan-in",
                str(plan_path),
                "ai-actions",
                "ai-actions-create-ai-action",
                "--body-json",
                '{"name":"test"}',
            ]
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(cmd)
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["refused"])
            self.assertIn("ack", " ".join(payload.get("reasons", [])))

    def test_required_query_flags_use_cli_spelling(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env = self._base_env(td)
            plan_out = Path(td) / "plan.json"
            cmd = [
                "--env-file",
                str(env),
                "--output",
                "json",
                "--plan-out",
                str(plan_out),
                "partner",
                "create-zap-guess",
                "--client-id",
                "client_123",
                "--body-json",
                '{"description":"Send a reviewed test notification"}',
            ]
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(cmd)
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])
            self.assertEqual(payload["plan"]["query"]["client_id"], "client_123")

    def test_plan_in_mismatch_refuses_before_request(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env = self._base_env(td)
            cfg = load_config(str(env))
            op = next(op for op in load_operations() if op.group == "ai-actions" and op.command == "ai-actions-create-ai-action")
            body = {"name": "reviewed"}
            plan = _build_plan(
                cfg=cfg,
                command="qwayk-zapier-safe-agent-cli ai-actions ai-actions-create-ai-action --body-json <redacted-body-json>",
                op=op,
                path_params={},
                query={},
                body=body,
                risk="high",
            )
            plan["body_sha256"] = "mismatch"

            plan_path = Path(td) / "plan.json"
            plan_path.write_text(json.dumps(plan), encoding="utf-8")

            with mock.patch("zapier_safe_agent_cli.cli.HttpClient.request") as req:
                cmd = [
                    "--env-file",
                    str(env),
                    "--output",
                    "json",
                    "--apply",
                    "--plan-in",
                    str(plan_path),
                    "--yes",
                    "ai-actions",
                    "ai-actions-create-ai-action",
                    "--body-json",
                    '{"name":"attack"}',
                ]
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = main(cmd)

            self.assertEqual(rc, 0)
            req.assert_not_called()
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["refused"])
            self.assertIn("Reviewed plan does not match this command", " ".join(payload.get("reasons", [])))

    def test_plan_in_path_param_mismatch_refuses_before_request(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env = self._base_env(td)
            cfg = load_config(str(env))
            op = next(op for op in load_operations() if op.group == "ai-actions" and op.command == "ai-actions-delete-ai-action")
            plan = _build_plan(
                cfg=cfg,
                command="qwayk-zapier-safe-agent-cli ai-actions ai-actions-delete-ai-action --ai-action-id id-match-000",
                op=op,
                path_params={"ai_action_id": "id-match-000"},
                query={},
                body=None,
                risk="high",
            )

            plan_path = Path(td) / "plan.json"
            plan_path.write_text(json.dumps(plan), encoding="utf-8")

            with mock.patch("zapier_safe_agent_cli.cli.HttpClient.request") as req:
                cmd = [
                    "--env-file",
                    str(env),
                    "--output",
                    "json",
                    "--apply",
                    "--plan-in",
                    str(plan_path),
                    "--yes",
                    "ai-actions",
                    "ai-actions-delete-ai-action",
                    "--ai-action-id",
                    "id-mismatch-999",
                ]
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = main(cmd)

            self.assertEqual(rc, 0)
            req.assert_not_called()
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["refused"])
            self.assertIn("path_params", " ".join(payload.get("reasons", [])))

    def test_plan_in_reviewed_fields_all_refuse_before_request(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env = self._base_env(td)
            cfg = load_config(str(env))
            op = next(op for op in load_operations() if op.group == "partner" and op.command == "create-zap-guess")
            body = {"description": "Send a reviewed test notification"}
            plan = _build_plan(
                cfg=cfg,
                command="qwayk-zapier-safe-agent-cli partner create-zap-guess --client-id client_123 --body-json <redacted-body-json>",
                op=op,
                path_params={},
                query={"client_id": "client_123"},
                body=body,
                risk="high",
            )
            cases = {
                "operation_id": lambda p: p.update({"operation_id": "wrong-operation-id"}),
                "operation": lambda p: p.update({"operation": "wrong-command"}),
                "method": lambda p: p.update({"method": "GET"}),
                "path": lambda p: p.update({"path": "/v2/wrong"}),
                "base_url": lambda p: p.update({"base_url": "https://example.invalid"}),
                "query": lambda p: p.update({"query": {"client_id": "client_999"}}),
                "body_present": lambda p: p.update({"body_present": False}),
                "body_sha256": lambda p: p.update({"body_sha256": "wrong-hash"}),
                "risk_level": lambda p: p.update({"risk_level": "medium"}),
                "env_fingerprint": lambda p: p.update({"env_fingerprint": "wrong-fingerprint"}),
            }

            for field, mutate in cases.items():
                with self.subTest(field=field):
                    bad_plan = deepcopy(plan)
                    mutate(bad_plan)
                    plan_path = Path(td) / f"plan_{field}.json"
                    plan_path.write_text(json.dumps(bad_plan), encoding="utf-8")

                    with mock.patch("zapier_safe_agent_cli.cli.HttpClient.request") as req:
                        buf = io.StringIO()
                        with redirect_stdout(buf):
                            rc = main(
                                [
                                    "--env-file",
                                    str(env),
                                    "--output",
                                    "json",
                                    "--apply",
                                    "--plan-in",
                                    str(plan_path),
                                    "--yes",
                                    "partner",
                                    "create-zap-guess",
                                    "--client-id",
                                    "client_123",
                                    "--body-json",
                                    json.dumps(body),
                                ]
                            )

                    self.assertEqual(rc, 0)
                    req.assert_not_called()
                    payload = json.loads(buf.getvalue())
                    self.assertTrue(payload["refused"])
                    self.assertIn(field, " ".join(payload.get("reasons", [])))

    def test_plan_in_same_auth_type_token_drift_refuses_before_request(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_a = Path(td) / ".env.a"
            env_b = Path(td) / ".env.b"
            self._write_env_with_token(env_a, "first-token-SECRET")
            self._write_env_with_token(env_b, "second-token-SECRET")

            cfg = load_config(str(env_a))
            op = next(op for op in load_operations() if op.group == "ai-actions" and op.command == "ai-actions-create-ai-action")
            body = {"name": "reviewed"}
            plan = _build_plan(
                cfg=cfg,
                command="qwayk-zapier-safe-agent-cli ai-actions ai-actions-create-ai-action --body-json <redacted-body-json>",
                op=op,
                path_params={},
                query={},
                body=body,
                risk="high",
            )
            self.assertNotIn("first-token-SECRET", json.dumps(plan))

            plan_path = Path(td) / "plan.json"
            plan_path.write_text(json.dumps(plan), encoding="utf-8")

            with mock.patch("zapier_safe_agent_cli.cli.HttpClient.request") as req:
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = main(
                        [
                            "--env-file",
                            str(env_b),
                            "--output",
                            "json",
                            "--apply",
                            "--plan-in",
                            str(plan_path),
                            "--yes",
                            "ai-actions",
                            "ai-actions-create-ai-action",
                            "--body-json",
                            json.dumps(body),
                        ]
                    )

            self.assertEqual(rc, 0)
            req.assert_not_called()
            payload_text = buf.getvalue()
            payload = json.loads(payload_text)
            self.assertTrue(payload["refused"])
            self.assertIn("env_fingerprint", " ".join(payload.get("reasons", [])))
            self.assertNotIn("first-token-SECRET", payload_text)
            self.assertNotIn("second-token-SECRET", payload_text)

    def test_example_plan_and_receipt_parse(self) -> None:
        root = Path(__file__).resolve().parents[1]
        operations = json.loads((root / "src/zapier_safe_agent_cli/operations_data.json").read_text(encoding="utf-8"))
        post_zaps = next(op for op in operations if op["group"] == "partner" and op["command"] == "post-zaps")
        for name in ["docs/examples/plan.example.json", "docs/examples/receipt.example.json"]:
            payload: dict[str, Any] = json.loads((root / name).read_text(encoding="utf-8"))
            self.assertIn("tool", payload)
            self.assertIn("version", payload)
            self.assertEqual(payload["tool"], "qwayk-zapier-safe-agent-cli")
            self.assertEqual(payload["operation"], post_zaps["command"])
            self.assertEqual(payload["operation_id"], post_zaps["operation_id"])
            self.assertEqual(payload["path"], post_zaps["path"])

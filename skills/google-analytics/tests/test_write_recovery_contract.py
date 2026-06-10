from __future__ import annotations

import csv
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from ga4_api_tool.cli import build_parser
from ga4_api_tool.commands.demo import cmd_demo_write
from ga4_api_tool.commands.jobs import cmd_jobs_run
from ga4_api_tool.config import load_config
from ga4_api_tool.errors import SafetyError
from ga4_api_tool.output import Output


class _FakeApiResponse:
    def __init__(self, *, status: int, url: str, json_data: Any | None = None, text: str | None = None) -> None:
        self.status = status
        self.url = url
        self.json = json_data
        self.text = text


class _FakeApiClient:
    def __init__(self, responses: list[_FakeApiResponse]) -> None:
        self.responses = list(responses)
        self.requests: list[dict[str, Any]] = []

    def request(self, **kwargs: Any) -> _FakeApiResponse:  # type: ignore[no-untyped-def]
        self.requests.append(kwargs)
        if not self.responses:
            raise AssertionError("Unexpected API request; no fake response")
        return self.responses.pop(0)


class _DummyAudit:
    def write(self, event: str, payload: dict[str, Any]) -> None:  # type: ignore[no-untyped-def]
        _ = event, payload


class TestWriteRecoveryContract(unittest.TestCase):
    def _assert_no_recovery_contract(self, contract: dict[str, Any]) -> None:
        self.assertIsInstance(contract, dict)
        self.assertFalse(contract.get("automatic_rollback"))
        self.assertEqual(contract.get("backups"), [])
        self.assertEqual(contract.get("snapshots"), [])
        self.assertIsNone(contract.get("rollback_plan"))
        self.assertIn("No automatic rollback", str(contract.get("restore_note", "")))

    def _capture_payload(self, func, args, ctx: dict[str, Any]) -> tuple[int, dict[str, Any]]:
        buf = io.StringIO()
        ctx.setdefault("audit", _DummyAudit())
        with redirect_stdout(buf):
            rc = func(args, ctx)
        payload = json.loads(buf.getvalue())
        self.assertIsInstance(payload, dict)
        return rc, payload

    def _jobs_ctx(self, **overrides: Any) -> dict[str, Any]:
        ctx: dict[str, Any] = {
            "cfg": SimpleNamespace(base_url="http://example.invalid"),
            "tool": "ga4-api-tool",
            "tool_version": "0.0.0",
            "command_str": "ga4-api-tool jobs run",
            "apply": False,
            "yes": False,
            "out": Output(mode="json"),
        }
        ctx.update(overrides)
        return ctx

    def _demo_ctx(self, **overrides: Any) -> dict[str, Any]:
        ctx: dict[str, Any] = {
            "cfg": SimpleNamespace(admin_base_url="http://example.invalid"),
            "tool": "ga4-api-tool",
            "tool_version": "0.0.0",
            "command_str": "ga4-api-tool demo write --selector demo-resource",
            "apply": False,
            "yes": False,
            "plan_in": None,
            "plan_out": None,
            "receipt_out": None,
            "out": Output(mode="json"),
        }
        ctx.update(overrides)
        return ctx

    def test_discovery_write_plan_includes_no_recovery_contract(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text("GA4_API_BASE_URL=http://example.invalid\nGA4_TIMEOUT_S=30\n", encoding="utf-8")
            cfg = load_config(str(env_path))

            parser = build_parser()
            args = parser.parse_args(
                [
                    "--env-file",
                    str(env_path),
                    "data",
                    "v1beta",
                    "properties",
                    "audience-exports",
                    "create",
                    "--parent",
                    "properties/123",
                ]
            )
            rc, payload = self._capture_payload(
                args.func,
                args,
                {
                    "cfg": cfg,
                    "tool": "ga4-api-tool",
                    "tool_version": "0.0.0",
                    "command_str": "ga4-api-tool ...",
                    "timeout_s": 30.0,
                    "verbose": False,
                    "apply": False,
                    "plan_in": None,
                    "plan_out": None,
                    "receipt_out": None,
                    "ack_irreversible": False,
                    "out": Output(mode="json"),
                },
            )
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])
            plan = payload["plan"]
            self.assertIn("recovery", plan)
            self.assertTrue(plan["before_state"]["required"])
            self.assertFalse(plan["before_state"]["supported"])
            self.assertEqual(plan["verification_plan"]["type"], "best_effort_after_apply")
            self._assert_no_recovery_contract(plan["recovery"])

    def test_discovery_write_apply_refuses_before_api_request_without_before_state(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text("GA4_API_BASE_URL=http://example.invalid\nGA4_TIMEOUT_S=30\n", encoding="utf-8")
            cfg = load_config(str(env_path))

            parser = build_parser()
            fake_client = _FakeApiClient(
                [
                    _FakeApiResponse(
                        status=201,
                        url="https://analyticsdata.googleapis.com/v1beta/properties/123/audienceExports",
                        json_data={"status": "created"},
                    )
                ]
            )

            args = parser.parse_args(
                [
                    "--env-file",
                    str(env_path),
                    "--apply",
                    "data",
                    "v1beta",
                    "properties",
                    "audience-exports",
                    "create",
                    "--parent",
                    "properties/123",
                ]
            )
            ctx = {
                "cfg": cfg,
                "tool": "ga4-api-tool",
                "tool_version": "0.0.0",
                "command_str": "ga4-api-tool ...",
                "timeout_s": 30.0,
                "verbose": False,
                "apply": True,
                "plan_in": None,
                "plan_out": None,
                "receipt_out": None,
                "ack_irreversible": False,
                "api_client": fake_client,
                "out": Output(mode="json"),
                "audit": _DummyAudit(),
            }
            with self.assertRaises(SafetyError) as cm:
                args.func(args, ctx)
            self.assertIn("before-state snapshot", str(cm.exception))
            self.assertEqual(fake_client.requests, [])

    def test_jobs_write_plan_includes_no_recovery_contract(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "jobs.csv"
            with path.open("w", encoding="utf-8", newline="") as f:
                w = csv.writer(f)
                w.writerow(["action"])
                w.writerow(["write.ping"])

            args = SimpleNamespace(file=str(path), limit=None)
            rc, payload = self._capture_payload(cmd_jobs_run, args, self._jobs_ctx(apply=False))
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])
            plan = payload["plan"]
            self.assertIn("recovery", plan)
            self.assertTrue(plan["before_state"]["required"])
            self.assertFalse(plan["before_state"]["supported"])
            self.assertEqual(plan["verification_plan"]["type"], "best_effort_after_apply")
            self._assert_no_recovery_contract(plan["recovery"])

    def test_jobs_write_apply_refuses_without_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            job_path = Path(d) / "jobs.csv"
            with job_path.open("w", encoding="utf-8", newline="") as f:
                w = csv.writer(f)
                w.writerow(["action"])
                w.writerow(["write.ping"])

            plan_path = Path(d) / "plan.json"
            receipt_path = Path(d) / "receipt.json"

            args_plan = SimpleNamespace(file=str(job_path), limit=None)
            rc_plan, _payload_plan = self._capture_payload(
                cmd_jobs_run,
                args_plan,
                self._jobs_ctx(apply=False, plan_out=str(plan_path)),
            )
            self.assertEqual(rc_plan, 0)
            self.assertTrue(plan_path.exists())

            args_apply = SimpleNamespace(file=str(job_path), limit=None)
            rc2, payload2 = self._capture_payload(
                cmd_jobs_run,
                args_apply,
                self._jobs_ctx(
                    apply=True,
                    yes=True,
                    plan_in=str(plan_path),
                    receipt_out=str(receipt_path),
                ),
            )
            self.assertEqual(rc2, 0)
            self.assertTrue(payload2["ok"])
            self.assertTrue(payload2["refused"])
            self.assertFalse(payload2["dry_run"])
            self.assertIn("stub write actions", payload2["reasons"][0])
            self.assertNotIn("receipt", payload2)
            self.assertFalse(receipt_path.exists())

    def test_demo_write_plan_includes_no_recovery_contract(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            plan_path = Path(d) / "plan.json"
            args = SimpleNamespace(selector="demo-resource")
            rc, payload = self._capture_payload(
                cmd_demo_write,
                args,
                self._demo_ctx(
                    apply=False,
                    plan_out=str(plan_path),
                    command_str="ga4-api-tool demo write --selector demo-resource",
                ),
            )
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])
            plan = payload["plan"]
            self.assertIn("recovery", plan)
            self.assertTrue(plan["before_state"]["required"])
            self.assertFalse(plan["before_state"]["supported"])
            self.assertEqual(plan["verification_plan"]["type"], "best_effort_after_apply")
            self._assert_no_recovery_contract(plan["recovery"])

    def test_demo_write_apply_refuses_without_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            plan_path = Path(d) / "plan.json"
            receipt_path = Path(d) / "receipt.json"

            args_plan = SimpleNamespace(selector="demo-resource")
            rc_plan, _payload_plan = self._capture_payload(
                cmd_demo_write,
                args_plan,
                self._demo_ctx(
                    apply=False,
                    plan_out=str(plan_path),
                    command_str="ga4-api-tool demo write --selector demo-resource",
                ),
            )
            self.assertEqual(rc_plan, 0)
            self.assertTrue(plan_path.exists())

            args_apply = SimpleNamespace(selector="demo-resource")
            rc2, payload2 = self._capture_payload(
                cmd_demo_write,
                args_apply,
                self._demo_ctx(
                    apply=True,
                    yes=True,
                    plan_in=str(plan_path),
                    receipt_out=str(receipt_path),
                    command_str="ga4-api-tool --apply --yes demo write --selector demo-resource",
                ),
            )
            self.assertEqual(rc2, 0)
            self.assertTrue(payload2["ok"])
            self.assertTrue(payload2["refused"])
            self.assertFalse(payload2["dry_run"])
            self.assertIn("stub", payload2["reasons"][0])
            self.assertNotIn("receipt", payload2)
            self.assertFalse(receipt_path.exists())

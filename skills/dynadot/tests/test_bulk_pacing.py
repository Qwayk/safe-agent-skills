from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace

from dynadot_api_tool.commands.domains import cmd_domains_push, cmd_push_requests_accept
from dynadot_api_tool.dynadot_api import DynadotApiResult
from dynadot_api_tool.output import Output


class _Audit:
    def write(self, event: str, payload: object) -> None:  # noqa: ARG002
        return


class _StubApi:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict]] = []

    def call(self, *, command: str, params: dict | None = None) -> DynadotApiResult:  # type: ignore[override]
        p = dict(params or {})
        self.calls.append((command, p))
        if command == "push":
            return DynadotApiResult(command=command, response={"ResponseCode": "0", "Status": "success"})
        if command == "set_domain_push_request":
            return DynadotApiResult(command=command, response={"ResponseCode": "0", "Status": "success"})
        if command == "get_domain_push_request":
            return DynadotApiResult(command=command, response={"ResponseCode": "0", "Status": "success", "pushDomainName": "[]"})
        raise AssertionError(f"Unexpected command: {command}")


class TestBulkPacing(unittest.TestCase):
    def _ctx(self, **overrides) -> dict:
        ctx = {
            "cfg": SimpleNamespace(base_url="http://example.invalid", api_key=None),
            "tool": "dynadot-api-tool",
            "tool_version": "0.0.0",
            "command_str": "dynadot-api-tool",
            "apply": False,
            "yes": False,
            "plan_in": None,
            "plan_out": None,
            "receipt_out": None,
            "timeout_s": 30.0,
            "verbose": False,
            "out": Output(mode="json"),
            "audit": _Audit(),
            "artifacts_dir": None,
            "api": None,
        }
        ctx.update(overrides)
        return ctx

    def test_domains_push_dry_run_includes_preview(self) -> None:
        args = SimpleNamespace(
            to_username="receiver",
            domain=["a.com", "b.com"],
            domains_file=None,
            no_unlock=False,
            sleep_between_batches_s=0.0,
            max_batches=2,
        )
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cmd_domains_push(args, self._ctx(apply=False, yes=False))
        self.assertEqual(rc, 0)
        payload = json.loads(buf.getvalue())
        self.assertIn("preview", payload)
        self.assertEqual(payload["preview"]["max_batches"], 2)
        self.assertEqual(payload["plan"]["baseline"]["max_batches"], "2")

    def test_domains_push_apply_refuses_before_provider_calls(self) -> None:
        api = _StubApi()
        domains = [f"d{i}.com" for i in range(1, 52)]
        args = SimpleNamespace(
            to_username="receiver",
            domain=domains,
            domains_file=None,
            no_unlock=False,
            sleep_between_batches_s=0.0,
            max_batches=1,
        )
        baseline = {
            "to_username": "receiver",
            "unlock_domain_for_push": "1",
            "domains_semicolon": ";".join([d.lower() for d in domains]),
            "sleep_between_batches_s": "0.0",
            "max_batches": "1",
            "resume_receipt_sha256": "",
        }
        with tempfile.TemporaryDirectory() as td:
            plan_path = f"{td}/plan.json"
            with open(plan_path, "w", encoding="utf-8") as fp:
                fp.write(json.dumps({"env_fingerprint": "http://example.invalid", "baseline": baseline}))
            ctx = self._ctx(apply=True, yes=True, plan_in=plan_path, api=api, command_str="dynadot-api-tool --apply --yes domains push")
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = cmd_domains_push(args, ctx)
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["refused"])
            self.assertEqual(payload["before_state"]["status"], "no_snapshot_available")
            self.assertEqual(api.calls, [])

    def test_push_requests_accept_apply_refuses_before_provider_calls(self) -> None:
        api = _StubApi()
        domains = [f"d{i}.com" for i in range(1, 52)]
        args = SimpleNamespace(
            domain=domains,
            domains_file=None,
            sleep_between_batches_s=0.0,
            max_batches=1,
        )
        baseline = {
            "action": "accept",
            "domains_comma": ",".join([d.lower() for d in domains]),
            "sleep_between_batches_s": "0.0",
            "max_batches": "1",
            "resume_receipt_sha256": "",
        }
        with tempfile.TemporaryDirectory() as td:
            plan_path = f"{td}/plan.json"
            with open(plan_path, "w", encoding="utf-8") as fp:
                fp.write(json.dumps({"env_fingerprint": "http://example.invalid", "baseline": baseline}))
            ctx = self._ctx(apply=True, yes=True, plan_in=plan_path, api=api, command_str="dynadot-api-tool --apply --yes domains push-requests accept")
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = cmd_push_requests_accept(args, ctx)
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["refused"])
            self.assertEqual(payload["before_state"]["status"], "no_snapshot_available")
            self.assertEqual(api.calls, [])

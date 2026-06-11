from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from typing import Any

from dynadot_api_tool.commands.transfers import cmd_transfers_auth_code, cmd_transfers_list, cmd_transfers_status
from dynadot_api_tool.dynadot_api import DynadotApiResult
from dynadot_api_tool.output import Output


class _Audit:
    def write(self, event: str, payload: object) -> None:  # noqa: ARG002
        return


class _StubApi:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, Any]]] = []

    def call(self, *, command: str, params: dict[str, Any] | None = None) -> DynadotApiResult:  # type: ignore[override]
        p = dict(params or {})
        self.calls.append((command, p))
        if command == "transfer_domain_list":
            return DynadotApiResult(command=command, response={"ResponseCode": "0", "Status": "success", "TransferOutDomainList": []})
        if command == "get_transfer_status":
            return DynadotApiResult(command=command, response={"ResponseCode": "0", "Status": "success", "TransferList": []})
        if command == "get_transfer_auth_code":
            return DynadotApiResult(command=command, response={"ResponseCode": "0", "Status": "success", "AuthCode": "EXAMPLE"})
        raise AssertionError(f"Unexpected command: {command}")


class TestReadCommandsBatch2Transfers(unittest.TestCase):
    def _ctx(self, *, api: object) -> dict[str, Any]:
        return {
            "cfg": SimpleNamespace(base_url="http://example.invalid", api_key="TESTKEY"),
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
            "api": api,
        }

    def test_transfers_list_calls_api(self) -> None:
        api = _StubApi()
        args = SimpleNamespace(out=None)
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cmd_transfers_list(args, self._ctx(api=api))
        self.assertEqual(rc, 0)
        payload = json.loads(buf.getvalue())
        self.assertTrue(payload["ok"])
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["command"], "transfer_domain_list")
        self.assertEqual(api.calls, [("transfer_domain_list", {})])
        self.assertNotIn("TESTKEY", buf.getvalue())

    def test_transfers_status_param_mapping(self) -> None:
        api = _StubApi()
        args = SimpleNamespace(domain="Example.com", transfer_type="out", out=None)
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cmd_transfers_status(args, self._ctx(api=api))
        self.assertEqual(rc, 0)
        payload = json.loads(buf.getvalue())
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["command"], "get_transfer_status")
        self.assertEqual(payload["domain"], "example.com")
        self.assertEqual(payload["transfer_type"], "away")
        self.assertEqual(api.calls, [("get_transfer_status", {"domain": "example.com", "transfer_type": "away"})])
        self.assertNotIn("TESTKEY", buf.getvalue())

    def test_transfers_auth_code_param_mapping(self) -> None:
        api = _StubApi()
        args = SimpleNamespace(domain="example.com", out=None)
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cmd_transfers_auth_code(args, self._ctx(api=api))
        self.assertEqual(rc, 0)
        payload = json.loads(buf.getvalue())
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["command"], "get_transfer_auth_code")
        self.assertEqual(payload["domain"], "example.com")
        self.assertNotIn("new_code", payload)
        self.assertNotIn("unlock_domain_for_transfer", payload)
        self.assertEqual(
            api.calls,
            [
                (
                    "get_transfer_auth_code",
                    {"domain": "example.com"},
                )
            ],
        )
        self.assertNotIn("TESTKEY", buf.getvalue())

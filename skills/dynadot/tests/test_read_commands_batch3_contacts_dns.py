from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from typing import Any

from dynadot_api_tool.commands.contacts import cmd_contacts_get, cmd_contacts_list
from dynadot_api_tool.commands.dns import cmd_dns_get
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
        if command == "contact_list":
            return DynadotApiResult(command=command, response={"ResponseCode": "0", "Status": "success", "ContactList": []})
        if command == "get_contact":
            return DynadotApiResult(
                command=command,
                response={
                    "ResponseCode": "0",
                    "Status": "success",
                    "ContactInfo": {"ContactId": str(p.get("contact_id") or ""), "FirstName": "Example"},
                },
            )
        if command == "get_dns":
            return DynadotApiResult(command=command, response={"ResponseCode": "0", "Status": "success", "Domain": p.get("domain")})
        raise AssertionError(f"Unexpected command: {command}")


class TestReadCommandsBatch3ContactsDns(unittest.TestCase):
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

    def test_contacts_list_calls_api_and_has_no_key_leakage(self) -> None:
        api = _StubApi()
        args = SimpleNamespace(out=None)
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cmd_contacts_list(args, self._ctx(api=api))
        self.assertEqual(rc, 0)
        payload = json.loads(buf.getvalue())
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["command"], "contact_list")
        self.assertIsInstance(payload["dynadot"]["raw"], dict)
        self.assertEqual(api.calls, [("contact_list", {})])
        self.assertNotIn("TESTKEY", buf.getvalue())

    def test_contacts_get_maps_contact_id(self) -> None:
        api = _StubApi()
        args = SimpleNamespace(contact_id="123", out=None)
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cmd_contacts_get(args, self._ctx(api=api))
        self.assertEqual(rc, 0)
        payload = json.loads(buf.getvalue())
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["command"], "get_contact")
        self.assertEqual(payload["contact_id"], "123")
        self.assertEqual(api.calls, [("get_contact", {"contact_id": "123"})])
        self.assertNotIn("TESTKEY", buf.getvalue())

    def test_dns_get_maps_domain_and_lowercases(self) -> None:
        api = _StubApi()
        args = SimpleNamespace(domain="ExAmple.COM.", out=None)
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cmd_dns_get(args, self._ctx(api=api))
        self.assertEqual(rc, 0)
        payload = json.loads(buf.getvalue())
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["command"], "get_dns")
        self.assertEqual(payload["domain"], "example.com")
        self.assertEqual(api.calls, [("get_dns", {"domain": "example.com"})])
        self.assertNotIn("TESTKEY", buf.getvalue())


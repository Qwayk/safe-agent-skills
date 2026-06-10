from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from typing import Any

from dynadot_api_tool.commands.orders import cmd_orders_list, cmd_orders_status
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
        if command == "order_list":
            return DynadotApiResult(command=command, response={"ResponseCode": "0", "Status": "success", "OrderList": []})
        if command == "get_order_status":
            return DynadotApiResult(command=command, response={"ResponseCode": "0", "Status": "success", "OrderStatus": "Completed"})
        raise AssertionError(f"Unexpected command: {command}")


class TestReadCommandsBatch2Orders(unittest.TestCase):
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

    def test_orders_list_param_mapping(self) -> None:
        api = _StubApi()
        args = SimpleNamespace(
            search_by="date_range",
            start_date="2024/01/01",
            end_date="2024/01/31",
            payment_method="account_balance,credit_card",
            out=None,
        )
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cmd_orders_list(args, self._ctx(api=api))
        self.assertEqual(rc, 0)
        payload = json.loads(buf.getvalue())
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["command"], "order_list")
        self.assertEqual(payload["search_by"], "date_range")
        self.assertEqual(payload["start_date"], "2024/01/01")
        self.assertEqual(payload["end_date"], "2024/01/31")
        self.assertEqual(payload["payment_method"], "account_balance,credit_card")
        self.assertEqual(
            api.calls,
            [
                (
                    "order_list",
                    {
                        "search_by": "date_range",
                        "start_date": "2024/01/01",
                        "end_date": "2024/01/31",
                        "payment_method": "account_balance,credit_card",
                    },
                )
            ],
        )
        self.assertNotIn("TESTKEY", buf.getvalue())

    def test_orders_status_param_mapping(self) -> None:
        api = _StubApi()
        args = SimpleNamespace(order_id="123456", out=None)
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cmd_orders_status(args, self._ctx(api=api))
        self.assertEqual(rc, 0)
        payload = json.loads(buf.getvalue())
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["command"], "get_order_status")
        self.assertEqual(payload["order_id"], "123456")
        self.assertEqual(api.calls, [("get_order_status", {"order_id": "123456"})])
        self.assertNotIn("TESTKEY", buf.getvalue())

from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from typing import Any

from dynadot_api_tool.commands.account import cmd_account_balance, cmd_account_coupons, cmd_account_info
from dynadot_api_tool.commands.domains import cmd_domains_search
from dynadot_api_tool.commands.pricing import cmd_pricing_tld_price
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
        if command == "account_info":
            return DynadotApiResult(command=command, response={"ResponseCode": "0", "Status": "success", "UserName": "example_user"})
        if command == "get_account_balance":
            return DynadotApiResult(command=command, response={"ResponseCode": "0", "Status": "success", "Currency": "USD", "Balance": "123.45"})
        if command == "list_coupons":
            return DynadotApiResult(command=command, response={"ResponseCode": "0", "Status": "success", "CouponList": []})
        if command == "tld_price":
            return DynadotApiResult(command=command, response={"ResponseCode": "0", "Status": "success", "TldPriceList": []})
        if command == "search":
            return DynadotApiResult(command=command, response={"ResponseCode": "0", "Status": "success", "SearchResult": []})
        raise AssertionError(f"Unexpected command: {command}")


class TestReadCommandsBatch1(unittest.TestCase):
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

    def test_account_info_output_shape_and_no_key_leakage(self) -> None:
        api = _StubApi()
        args = SimpleNamespace(out=None)
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cmd_account_info(args, self._ctx(api=api))
        self.assertEqual(rc, 0)
        payload = json.loads(buf.getvalue())
        self.assertTrue(payload["ok"])
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["command"], "account_info")
        self.assertEqual(payload["dynadot"]["command"], "account_info")
        self.assertEqual(payload["dynadot"]["response_code"], "0")
        self.assertNotIn("TESTKEY", buf.getvalue())

    def test_account_balance_calls_api_and_emits_dynadot_block(self) -> None:
        api = _StubApi()
        args = SimpleNamespace(out=None)
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cmd_account_balance(args, self._ctx(api=api))
        self.assertEqual(rc, 0)
        payload = json.loads(buf.getvalue())
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["command"], "get_account_balance")
        self.assertEqual(api.calls, [("get_account_balance", {})])

    def test_account_coupons_maps_coupon_type(self) -> None:
        api = _StubApi()
        args = SimpleNamespace(coupon_type="registration", out=None)
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cmd_account_coupons(args, self._ctx(api=api))
        self.assertEqual(rc, 0)
        payload = json.loads(buf.getvalue())
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["command"], "list_coupons")
        self.assertEqual(payload["coupon_type"], "registration")
        self.assertEqual(api.calls, [("list_coupons", {"coupon_type": "registration"})])

    def test_pricing_tld_price_param_mapping(self) -> None:
        api = _StubApi()
        args = SimpleNamespace(currency="USD", page=2, page_size=50, out=None)
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cmd_pricing_tld_price(args, self._ctx(api=api))
        self.assertEqual(rc, 0)
        payload = json.loads(buf.getvalue())
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["command"], "tld_price")
        self.assertEqual(api.calls, [("tld_price", {"page_index": 2, "count_per_page": 50, "currency": "usd"})])

    def test_domains_search_param_mapping(self) -> None:
        api = _StubApi()
        args = SimpleNamespace(domain=["A.com", "b.com"], show_price=True, currency="EUR", out=None)
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cmd_domains_search(args, self._ctx(api=api))
        self.assertEqual(rc, 0)
        payload = json.loads(buf.getvalue())
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["command"], "search")
        self.assertTrue(payload["show_price"])
        self.assertEqual(payload["currency"], "EUR")
        self.assertEqual(
            api.calls,
            [("search", {"domain0": "a.com", "domain1": "b.com", "show_price": "1", "currency": "eur"})],
        )

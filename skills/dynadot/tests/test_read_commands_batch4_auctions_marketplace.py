from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from typing import Any

from dynadot_api_tool.commands.auctions import (
    cmd_auctions_bids,
    cmd_auctions_closed,
    cmd_auctions_details,
    cmd_auctions_open,
)
from dynadot_api_tool.commands.backorder_auctions import (
    cmd_backorder_auctions_closed,
    cmd_backorder_auctions_details,
)
from dynadot_api_tool.commands.marketplace import cmd_marketplace_listings_get, cmd_marketplace_listings_list
from dynadot_api_tool.dynadot_api import DynadotApiResult
from dynadot_api_tool.errors import ValidationError
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
        return DynadotApiResult(command=command, response={"ResponseCode": "0", "Status": "success", "Echo": {"command": command, "params": p}})


class TestReadCommandsBatch4AuctionsMarketplace(unittest.TestCase):
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

    def _assert_common_json_shape(self, payload: dict[str, Any]) -> None:
        self.assertTrue(payload["ok"])
        self.assertTrue(payload["dry_run"])
        self.assertIsInstance(payload["command"], str)
        self.assertIsInstance(payload["dynadot"]["raw"], dict)

    def test_marketplace_listings_list_maps_params(self) -> None:
        api = _StubApi()
        args = SimpleNamespace(
            page=2,
            page_size=50,
            currency="usd",
            exclude_pending_sale=True,
            show_other_registrar=True,
            out=None,
        )
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cmd_marketplace_listings_list(args, self._ctx(api=api))
        self.assertEqual(rc, 0)
        payload = json.loads(buf.getvalue())
        self._assert_common_json_shape(payload)
        self.assertEqual(payload["command"], "get_listings")
        self.assertEqual(payload["currency"], "USD")
        self.assertTrue(payload["exclude_pending_sale"])
        self.assertTrue(payload["show_other_registrar"])
        self.assertEqual(
            api.calls,
            [
                (
                    "get_listings",
                    {
                        "page_index": 2,
                        "count_per_page": 50,
                        "currency": "usd",
                        "exclude_pending_sale": "yes",
                        "show_other_registrar": "yes",
                    },
                )
            ],
        )
        self.assertNotIn("TESTKEY", buf.getvalue())

    def test_marketplace_listings_get_normalizes_domain_and_currency(self) -> None:
        api = _StubApi()
        args = SimpleNamespace(domain="ExAmple.COM.", currency="eUr", out=None)
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cmd_marketplace_listings_get(args, self._ctx(api=api))
        self.assertEqual(rc, 0)
        payload = json.loads(buf.getvalue())
        self._assert_common_json_shape(payload)
        self.assertEqual(payload["command"], "get_listing_item")
        self.assertEqual(payload["domain"], "example.com")
        self.assertEqual(payload["currency"], "EUR")
        self.assertEqual(api.calls, [("get_listing_item", {"domain": "example.com", "currency": "eur"})])
        self.assertNotIn("TESTKEY", buf.getvalue())

    def test_auctions_open_maps_types_and_currency(self) -> None:
        api = _StubApi()
        args = SimpleNamespace(page=2, page_size=50, type=["expired", "user"], currency="cny", out=None)
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cmd_auctions_open(args, self._ctx(api=api))
        self.assertEqual(rc, 0)
        payload = json.loads(buf.getvalue())
        self._assert_common_json_shape(payload)
        self.assertEqual(payload["command"], "get_open_auctions")
        self.assertEqual(payload["types"], ["expired", "user"])
        self.assertEqual(payload["currency"], "CNY")
        self.assertEqual(
            api.calls,
            [
                (
                    "get_open_auctions",
                    {"page_index": 2, "count_per_page": 50, "type": "expired,user", "currency": "cny"},
                )
            ],
        )
        self.assertNotIn("TESTKEY", buf.getvalue())

    def test_auctions_open_rejects_page_size_over_50(self) -> None:
        api = _StubApi()
        args = SimpleNamespace(page=1, page_size=51, type=None, currency=None, out=None)
        buf = io.StringIO()
        with redirect_stdout(buf), self.assertRaisesRegex(ValidationError, r"--page-size must be <= 50"):
            cmd_auctions_open(args, self._ctx(api=api))

    def test_auctions_closed_maps_dates_and_currency(self) -> None:
        api = _StubApi()
        args = SimpleNamespace(
            start_date="2026-1-1",
            end_date="2026-01-31",
            currency="Usd",
            out=None,
        )
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cmd_auctions_closed(args, self._ctx(api=api))
        self.assertEqual(rc, 0)
        payload = json.loads(buf.getvalue())
        self._assert_common_json_shape(payload)
        self.assertEqual(payload["command"], "get_closed_auctions")
        self.assertEqual(payload["start_date"], "2026-01-01")
        self.assertEqual(payload["end_date"], "2026-01-31")
        self.assertEqual(payload["currency"], "USD")
        self.assertEqual(
            api.calls,
            [
                (
                    "get_closed_auctions",
                    {
                        "startDate": "2026-01-01",
                        "endDate": "2026-01-31",
                        "currency": "usd",
                    },
                )
            ],
        )
        self.assertNotIn("TESTKEY", buf.getvalue())

    def test_auctions_details_maps_domains_and_currency(self) -> None:
        api = _StubApi()
        args = SimpleNamespace(domain=["ExAmple.COM.", "other.com, Third.COM."], currency="USD", out=None)
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cmd_auctions_details(args, self._ctx(api=api))
        self.assertEqual(rc, 0)
        payload = json.loads(buf.getvalue())
        self._assert_common_json_shape(payload)
        self.assertEqual(payload["command"], "get_auction_details")
        self.assertEqual(payload["domains"], ["example.com", "other.com", "third.com"])
        self.assertEqual(payload["currency"], "USD")
        self.assertEqual(api.calls, [("get_auction_details", {"domain": "example.com,other.com,third.com", "currency": "usd"})])
        self.assertNotIn("TESTKEY", buf.getvalue())

    def test_auctions_bids_maps_pagination(self) -> None:
        api = _StubApi()
        args = SimpleNamespace(page=3, page_size=25, currency="eur", out=None)
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cmd_auctions_bids(args, self._ctx(api=api))
        self.assertEqual(rc, 0)
        payload = json.loads(buf.getvalue())
        self._assert_common_json_shape(payload)
        self.assertEqual(payload["command"], "get_auction_bids")
        self.assertEqual(payload["page"], 3)
        self.assertEqual(payload["page_size"], 25)
        self.assertEqual(payload["currency"], "EUR")
        self.assertEqual(api.calls, [("get_auction_bids", {"page_index": 3, "count_per_page": 25, "currency": "eur"})])
        self.assertNotIn("TESTKEY", buf.getvalue())

    def test_backorder_auctions_closed_maps_dates(self) -> None:
        api = _StubApi()
        args = SimpleNamespace(start_date="2026-1-1", end_date="2026-01-31", currency="CNY", out=None)
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cmd_backorder_auctions_closed(args, self._ctx(api=api))
        self.assertEqual(rc, 0)
        payload = json.loads(buf.getvalue())
        self._assert_common_json_shape(payload)
        self.assertEqual(payload["command"], "get_closed_backorder_auctions")
        self.assertEqual(payload["start_date"], "2026-01-01")
        self.assertEqual(payload["end_date"], "2026-01-31")
        self.assertEqual(payload["currency"], "CNY")
        self.assertEqual(api.calls, [("get_closed_backorder_auctions", {"startDate": "2026-01-01", "endDate": "2026-01-31", "currency": "cny"})])
        self.assertNotIn("TESTKEY", buf.getvalue())

    def test_backorder_auctions_details_maps_domain_and_currency(self) -> None:
        api = _StubApi()
        args = SimpleNamespace(domain="ExAmple.COM.", currency="eur", out=None)
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cmd_backorder_auctions_details(args, self._ctx(api=api))
        self.assertEqual(rc, 0)
        payload = json.loads(buf.getvalue())
        self._assert_common_json_shape(payload)
        self.assertEqual(payload["command"], "get_backorder_auction_details")
        self.assertEqual(payload["domain"], "example.com")
        self.assertEqual(payload["currency"], "EUR")
        self.assertEqual(api.calls, [("get_backorder_auction_details", {"domain": "example.com", "currency": "eur"})])
        self.assertNotIn("TESTKEY", buf.getvalue())

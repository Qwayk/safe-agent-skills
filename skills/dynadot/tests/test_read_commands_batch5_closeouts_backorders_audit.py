from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from typing import Any

from dynadot_api_tool.commands.backorders import cmd_backorders_requests_list
from dynadot_api_tool.commands.closeouts import cmd_closeouts_list
from dynadot_api_tool.commands.cn_audit import cmd_cn_audit_status
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
        return DynadotApiResult(
            command=command,
            response={
                "ResponseCode": "0",
                "Status": "success",
                "Echo": {"command": command, "params": p},
            },
        )


class TestReadCommandsBatch5CloseoutsBackordersAudit(unittest.TestCase):
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

    def test_closeouts_list_maps_pagination_domain_and_currency(self) -> None:
        api = _StubApi()
        args = SimpleNamespace(page=2, page_size=100, currency="eur", domain="ExAmple.COM.", out=None)
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cmd_closeouts_list(args, self._ctx(api=api))
        self.assertEqual(rc, 0)
        payload = json.loads(buf.getvalue())
        self._assert_common_json_shape(payload)
        self.assertEqual(payload["command"], "get_expired_closeout_domains")
        self.assertEqual(payload["page"], 2)
        self.assertEqual(payload["page_size"], 100)
        self.assertEqual(payload["currency"], "EUR")
        self.assertEqual(payload["domain"], "example.com")
        self.assertEqual(
            api.calls,
            [
                (
                    "get_expired_closeout_domains",
                    {"page_index": 2, "count_per_page": 100, "currency": "eur", "domain": "example.com"},
                )
            ],
        )
        self.assertNotIn("TESTKEY", buf.getvalue())

    def test_closeouts_list_rejects_bad_page_and_page_size(self) -> None:
        api = _StubApi()
        bad_page = SimpleNamespace(page=0, page_size=None, currency=None, domain=None, out=None)
        with self.assertRaisesRegex(ValidationError, r"--page must be >= 1"):
            cmd_closeouts_list(bad_page, self._ctx(api=api))

        bad_page_size = SimpleNamespace(page=1, page_size=0, currency=None, domain=None, out=None)
        with self.assertRaisesRegex(ValidationError, r"--page-size must be >= 1"):
            cmd_closeouts_list(bad_page_size, self._ctx(api=api))

    def test_backorders_requests_list_maps_dates(self) -> None:
        api = _StubApi()
        args = SimpleNamespace(start_date="2026-1-1", end_date="2026-01-31", out=None)
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cmd_backorders_requests_list(args, self._ctx(api=api))
        self.assertEqual(rc, 0)
        payload = json.loads(buf.getvalue())
        self._assert_common_json_shape(payload)
        self.assertEqual(payload["command"], "backorder_request_list")
        self.assertEqual(payload["start_date"], "2026-01-01")
        self.assertEqual(payload["end_date"], "2026-01-31")
        self.assertEqual(api.calls, [("backorder_request_list", {"startDate": "2026-01-01", "endDate": "2026-01-31"})])
        self.assertNotIn("TESTKEY", buf.getvalue())

    def test_backorders_requests_list_rejects_bad_date_format(self) -> None:
        api = _StubApi()
        args = SimpleNamespace(start_date="2026/01/01", end_date="2026-01-31", out=None)
        with self.assertRaisesRegex(ValidationError, r"--start-date must be in YYYY-M-D or YYYY-MM-DD"):
            cmd_backorders_requests_list(args, self._ctx(api=api))

    def test_cn_audit_status_maps_contact_id_and_gtld(self) -> None:
        api = _StubApi()
        args = SimpleNamespace(contact_id="testcontactid", gtld=True, out=None)
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cmd_cn_audit_status(args, self._ctx(api=api))
        self.assertEqual(rc, 0)
        payload = json.loads(buf.getvalue())
        self._assert_common_json_shape(payload)
        self.assertEqual(payload["command"], "get_cn_audit_status")
        self.assertEqual(payload["contact_id"], "testcontactid")
        self.assertTrue(payload["gtld"])
        self.assertEqual(api.calls, [("get_cn_audit_status", {"contact_id": "testcontactid", "gtld": 1})])
        self.assertNotIn("TESTKEY", buf.getvalue())

    def test_cn_audit_status_rejects_missing_contact_id(self) -> None:
        api = _StubApi()
        args = SimpleNamespace(contact_id=" ", gtld=False, out=None)
        with self.assertRaisesRegex(ValidationError, r"Missing --contact-id"):
            cmd_cn_audit_status(args, self._ctx(api=api))


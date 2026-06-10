from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace

from dynadot_api_tool.commands.domains import (
    cmd_domains_folders_list,
    cmd_domains_info,
    cmd_domains_list,
    cmd_domains_status,
)
from dynadot_api_tool.dynadot_api import DynadotApiResult
from dynadot_api_tool.output import Output


class _Audit:
    def write(self, event: str, payload: object) -> None:  # noqa: ARG002
        return


class _StubApi:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict | None]] = []

    def call(self, *, command: str, params: dict | None = None) -> DynadotApiResult:  # type: ignore[override]
        self.calls.append((command, dict(params or {})))
        cmd = str(command)
        p = dict(params or {})
        if cmd == "list_domain":
            page_index = int(p.get("page_index") or 1)
            if page_index == 1:
                rows = [{"Name": "a.com"}, {"Name": "b.com"}]
            elif page_index == 2:
                rows = [{"Name": "c.com"}]
            else:
                rows = []
            return DynadotApiResult(command=cmd, response={"ResponseCode": "0", "Status": "success", "MainDomains": rows})
        if cmd == "domain_info":
            domain = str(p.get("domain") or "")
            status = "active" if domain != "bad.com" else "moved"
            return DynadotApiResult(command=cmd, response={"ResponseCode": "0", "Status": "success", "DomainInfo": {"Name": domain, "Status": status}})
        if cmd == "folder_list":
            return DynadotApiResult(
                command=cmd,
                response={"ResponseCode": "0", "Status": "success", "FolderList": [{"FolderId": "1", "FolderName": "Test"}]},
            )
        raise AssertionError(f"Unexpected command: {cmd}")


class TestInventoryExports(unittest.TestCase):
    def _ctx(self, *, api: object) -> dict:
        return {
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
            "api": api,
        }

    def test_domains_list_all_paginates_until_empty(self) -> None:
        api = _StubApi()
        args = SimpleNamespace(page=1, page_size=None, all=True, max_pages=10, sleep_s=0.0, out=None)
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cmd_domains_list(args, self._ctx(api=api))
        self.assertEqual(rc, 0)
        payload = json.loads(buf.getvalue())
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["count"], 3)
        self.assertEqual(payload["stopped_reason"], "empty_page")
        self.assertGreaterEqual(payload["attempted_pages"], 3)

    def test_domains_list_out_writes_export(self) -> None:
        api = _StubApi()
        with tempfile.TemporaryDirectory() as td:
            out_path = f"{td}/domains.json"
            args = SimpleNamespace(page=1, page_size=None, all=False, max_pages=50, sleep_s=0.0, out=out_path)
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = cmd_domains_list(args, self._ctx(api=api))
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertEqual(payload["out_path"], out_path)
            with open(out_path, "r", encoding="utf-8") as f:
                export = json.loads(f.read())
            self.assertEqual(export["command"], "list_domain")
            self.assertEqual(export["count"], 2)

    def test_domains_info_reads_domains_file(self) -> None:
        api = _StubApi()
        with tempfile.TemporaryDirectory() as td:
            f = f"{td}/domains.txt"
            with open(f, "w", encoding="utf-8") as fp:
                fp.write("a.com\nB.com\n")
            args = SimpleNamespace(domain=None, domains_file=f, sleep_s=0.0, max_domains=None, out=None)
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = cmd_domains_info(args, self._ctx(api=api))
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["count"], 2)

    def test_domains_status_derives_status(self) -> None:
        api = _StubApi()
        args = SimpleNamespace(domain=["a.com", "bad.com"], domains_file=None, sleep_s=0.0, max_domains=None, out=None)
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cmd_domains_status(args, self._ctx(api=api))
        self.assertEqual(rc, 0)
        payload = json.loads(buf.getvalue())
        self.assertTrue(payload["ok"])
        statuses = {r["domain"]: r["status"] for r in payload["results"]}
        self.assertEqual(statuses["a.com"], "active")
        self.assertEqual(statuses["bad.com"], "moved")

    def test_domains_folders_list(self) -> None:
        api = _StubApi()
        args = SimpleNamespace(out=None)
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cmd_domains_folders_list(args, self._ctx(api=api))
        self.assertEqual(rc, 0)
        payload = json.loads(buf.getvalue())
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["count"], 1)

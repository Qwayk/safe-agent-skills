from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from pinterest_api_tool.commands.boards import (
    cmd_board_sections_create,
    cmd_board_sections_delete,
    cmd_board_sections_ensure,
    cmd_board_sections_update,
    cmd_boards_create,
    cmd_boards_delete,
)
from pinterest_api_tool.config import Config
from pinterest_api_tool.http import HttpResponse
from pinterest_api_tool.output import Output


class _FakeHttp:
    def __init__(
        self,
        *,
        base_url: str,
        omit_section_id_on_create: bool = False,
        remove_section_on_patch: bool = False,
    ):
        self.base_url = base_url.rstrip("/")
        self.calls: list[dict[str, Any]] = []
        self.boards: list[dict[str, Any]] = []
        self.sections_by_board: dict[str, list[dict[str, Any]]] = {}
        self._next_board_id = 1000
        self._next_section_id = 2000
        self._omit_section_id_on_create = omit_section_id_on_create
        self._remove_section_on_patch = remove_section_on_patch

    def _path(self, url: str) -> str:
        if not url.startswith(self.base_url):
            raise RuntimeError(f"Unexpected URL: {url}")
        return url[len(self.base_url) :]

    def _resp(self, *, status: int, url: str, payload: Any | None = None) -> HttpResponse:
        body = b""
        if payload is not None:
            body = json.dumps(payload).encode("utf-8")
        return HttpResponse(status=status, headers={}, body=body, url=url)

    def request(self, method: str, url: str, **kwargs):  # noqa: ANN001
        allowed = tuple(kwargs.get("allowed_statuses") or ())
        json_body = kwargs.get("json_body")
        path = self._path(url)
        self.calls.append({"method": method, "url": url, "path": path, "json_body": json_body, "allowed": allowed})

        def fail(status: int, payload: Any) -> HttpResponse:
            if status >= 400 and status not in allowed:
                raise RuntimeError(f"HTTP {status} for {method} {url}")
            return self._resp(status=status, url=url, payload=payload)

        if method == "GET" and path == "/boards":
            return self._resp(status=200, url=url, payload={"items": list(self.boards), "bookmark": None})

        if method == "POST" and path == "/boards":
            self._next_board_id += 1
            bid = str(self._next_board_id)
            b = {
                "id": bid,
                "name": str(json_body.get("name") or ""),
                "description": json_body.get("description"),
                "privacy": json_body.get("privacy") or "PUBLIC",
            }
            self.boards.append(b)
            return self._resp(status=201, url=url, payload=b)

        if path.startswith("/boards/") and "/sections" not in path:
            bid = path.split("/", 2)[2]
            board = next((b for b in self.boards if str(b.get("id")) == bid), None)
            if method == "GET":
                if board is None:
                    return fail(404, {"message": "not found"})
                return self._resp(status=200, url=url, payload=board)
            if method == "DELETE":
                if board is None:
                    return fail(404, {"message": "not found"})
                self.boards = [b for b in self.boards if str(b.get("id")) != bid]
                return self._resp(status=204, url=url, payload={})

        if path.startswith("/boards/") and path.endswith("/sections") and method == "GET":
            bid = path.split("/")[2]
            sections = self.sections_by_board.get(bid, [])
            return self._resp(status=200, url=url, payload={"items": list(sections), "bookmark": None})

        if path.startswith("/boards/") and path.endswith("/sections") and method == "POST":
            bid = path.split("/")[2]
            self._next_section_id += 1
            sid = str(self._next_section_id)
            sec: dict[str, Any] = {"id": sid, "name": str(json_body.get("name") or "")}
            self.sections_by_board.setdefault(bid, []).append(sec)
            if self._omit_section_id_on_create:
                return self._resp(status=201, url=url, payload={"name": sec["name"]})
            return self._resp(status=201, url=url, payload=sec)

        if "/sections/" in path and method == "PATCH":
            parts = path.split("/")
            bid = parts[2]
            sid = parts[4]
            sections = self.sections_by_board.get(bid, [])
            if not any(str(s.get("id")) == sid for s in sections):
                return fail(404, {"message": "not found"})
            if self._remove_section_on_patch:
                self.sections_by_board[bid] = [s for s in sections if str(s.get("id")) != sid]
                return self._resp(status=200, url=url, payload={"id": sid})
            for s in sections:
                if str(s.get("id")) == sid:
                    s["name"] = str(json_body.get("name") or "")
                    break
            return self._resp(status=200, url=url, payload={"id": sid, "name": str(json_body.get("name") or "")})

        if "/sections/" in path and method == "DELETE":
            parts = path.split("/")
            bid = parts[2]
            sid = parts[4]
            sections = self.sections_by_board.get(bid, [])
            if not any(str(s.get("id")) == sid for s in sections):
                return fail(404, {"message": "not found"})
            self.sections_by_board[bid] = [s for s in sections if str(s.get("id")) != sid]
            return self._resp(status=204, url=url, payload={})

        raise RuntimeError(f"Unhandled request: {method} {path}")


class _Audit:
    def write(self, event: str, payload):  # noqa: ANN001
        _ = event, payload


class TestBoardsWriteCommands(unittest.TestCase):
    def _ctx(self, tool_dir: Path, http: _FakeHttp, *, apply: bool, yes: bool, ack_irreversible: bool = False) -> dict[str, Any]:
        return {
            "cfg": Config(
                base_url=http.base_url,
                access_token=None,
                app_id=None,
                app_secret=None,
                refresh_token=None,
                timeout_s=30,
            ),
            "http": http,
            "env_file": str(tool_dir / ".env"),
            "out": Output(mode="json"),
            "audit": _Audit(),
            "apply": apply,
            "yes": yes,
            "ack_irreversible": ack_irreversible,
            "ack_spend": False,
            "ack_volume": False,
        }

    def test_boards_create_dry_run_emits_plan_and_no_network(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            tool_dir = Path(d)
            (tool_dir / ".env").write_text("PINTEREST_API_BASE_URL=https://api.pinterest.com/v5\n", encoding="utf-8")
            (tool_dir / ".state").mkdir()
            (tool_dir / ".state" / "token.json").write_text(json.dumps({"access_token": "X"}), encoding="utf-8")

            http = _FakeHttp(base_url="https://api.pinterest.com/v5")
            ctx = self._ctx(tool_dir, http, apply=False, yes=False)
            args = SimpleNamespace(
                name="My Board",
                description=None,
                privacy=None,
                is_ads_only=False,
                ad_account_id=None,
                scan_limit=5000,
                allow_mismatch=False,
            )

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = cmd_boards_create(args, ctx)
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertEqual(payload["ok"], True)
            self.assertEqual(payload["dry_run"], True)
            self.assertEqual(payload["action"], "boards.create")
            self.assertEqual(http.calls, [])

    def test_boards_create_apply_requires_no_snapshot_ack_before_duplicate_scan_or_write(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            tool_dir = Path(d)
            (tool_dir / ".env").write_text("PINTEREST_API_BASE_URL=https://api.pinterest.com/v5\n", encoding="utf-8")
            (tool_dir / ".state").mkdir()
            (tool_dir / ".state" / "token.json").write_text(json.dumps({"access_token": "X"}), encoding="utf-8")

            http = _FakeHttp(base_url="https://api.pinterest.com/v5")
            http.boards = [{"id": "1", "name": "My Board"}]
            ctx = self._ctx(tool_dir, http, apply=True, yes=True)
            args = SimpleNamespace(
                name="My Board",
                description=None,
                privacy=None,
                is_ads_only=False,
                ad_account_id=None,
                scan_limit=5000,
                allow_mismatch=False,
            )

            with self.assertRaisesRegex(RuntimeError, "--ack-no-snapshot"):
                cmd_boards_create(args, ctx)
            self.assertEqual(http.calls, [])

    def test_boards_delete_apply_requires_no_snapshot_ack_before_delete(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            tool_dir = Path(d)
            (tool_dir / ".env").write_text("PINTEREST_API_BASE_URL=https://api.pinterest.com/v5\n", encoding="utf-8")
            (tool_dir / ".state").mkdir()
            (tool_dir / ".state" / "token.json").write_text(json.dumps({"access_token": "X"}), encoding="utf-8")

            http = _FakeHttp(base_url="https://api.pinterest.com/v5")
            http.boards = [{"id": "10", "name": "Delete Me"}]
            ctx = self._ctx(tool_dir, http, apply=True, yes=True, ack_irreversible=True)
            args = SimpleNamespace(id="10", ad_account_id=None)

            with self.assertRaisesRegex(RuntimeError, "--ack-no-snapshot"):
                cmd_boards_delete(args, ctx)
            self.assertEqual(http.calls, [])

    def test_board_sections_ensure_apply_requires_no_snapshot_ack_before_noop_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            tool_dir = Path(d)
            (tool_dir / ".env").write_text("PINTEREST_API_BASE_URL=https://api.pinterest.com/v5\n", encoding="utf-8")
            (tool_dir / ".state").mkdir()
            (tool_dir / ".state" / "token.json").write_text(json.dumps({"access_token": "X"}), encoding="utf-8")

            http = _FakeHttp(base_url="https://api.pinterest.com/v5")
            http.sections_by_board = {"55": [{"id": "s1", "name": "My Section"}]}
            ctx = self._ctx(tool_dir, http, apply=True, yes=True)
            args = SimpleNamespace(board_id="55", name="My Section", ad_account_id=None, scan_limit=5000)

            with self.assertRaisesRegex(RuntimeError, "--ack-no-snapshot"):
                cmd_board_sections_ensure(args, ctx)
            self.assertFalse(any(c["method"] in {"POST", "PATCH", "DELETE"} for c in http.calls))

    def test_board_sections_create_apply_raises_when_create_response_missing_id(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            tool_dir = Path(d)
            (tool_dir / ".env").write_text("PINTEREST_API_BASE_URL=https://api.pinterest.com/v5\n", encoding="utf-8")
            (tool_dir / ".state").mkdir()
            (tool_dir / ".state" / "token.json").write_text(json.dumps({"access_token": "X"}), encoding="utf-8")

            http = _FakeHttp(base_url="https://api.pinterest.com/v5", omit_section_id_on_create=True)
            ctx = self._ctx(tool_dir, http, apply=True, yes=True)
            ctx["ack_no_snapshot"] = True
            args = SimpleNamespace(board_id="55", name="My Section", ad_account_id=None, scan_limit=5000, allow_mismatch=False)

            with self.assertRaisesRegex(RuntimeError, "missing id"):
                cmd_board_sections_create(args, ctx)
            self.assertTrue(any(c["method"] == "POST" and c["path"] == "/boards/55/sections" for c in http.calls))

    def test_board_sections_ensure_apply_raises_when_create_response_missing_id(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            tool_dir = Path(d)
            (tool_dir / ".env").write_text("PINTEREST_API_BASE_URL=https://api.pinterest.com/v5\n", encoding="utf-8")
            (tool_dir / ".state").mkdir()
            (tool_dir / ".state" / "token.json").write_text(json.dumps({"access_token": "X"}), encoding="utf-8")

            http = _FakeHttp(base_url="https://api.pinterest.com/v5", omit_section_id_on_create=True)
            ctx = self._ctx(tool_dir, http, apply=True, yes=True)
            ctx["ack_no_snapshot"] = True
            args = SimpleNamespace(board_id="55", name="My Section", ad_account_id=None, scan_limit=5000)

            with self.assertRaisesRegex(RuntimeError, "missing id"):
                cmd_board_sections_ensure(args, ctx)
            self.assertTrue(any(c["method"] == "POST" and c["path"] == "/boards/55/sections" for c in http.calls))

    def test_board_sections_update_apply_fails_when_section_missing_after_update(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            tool_dir = Path(d)
            (tool_dir / ".env").write_text("PINTEREST_API_BASE_URL=https://api.pinterest.com/v5\n", encoding="utf-8")
            (tool_dir / ".state").mkdir()
            (tool_dir / ".state" / "token.json").write_text(json.dumps({"access_token": "X"}), encoding="utf-8")

            http = _FakeHttp(base_url="https://api.pinterest.com/v5", remove_section_on_patch=True)
            http.sections_by_board = {"55": [{"id": "s1", "name": "Old"}]}
            ctx = self._ctx(tool_dir, http, apply=True, yes=True)
            ctx["ack_no_snapshot"] = True
            args = SimpleNamespace(board_id="55", section_id="s1", name="New", ad_account_id=None)

            with self.assertRaisesRegex(RuntimeError, "Verification failed"):
                cmd_board_sections_update(args, ctx)
            self.assertTrue(any(c["method"] == "PATCH" and c["path"] == "/boards/55/sections/s1" for c in http.calls))

    def test_board_sections_delete_apply_requires_no_snapshot_ack_before_delete(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            tool_dir = Path(d)
            (tool_dir / ".env").write_text("PINTEREST_API_BASE_URL=https://api.pinterest.com/v5\n", encoding="utf-8")
            (tool_dir / ".state").mkdir()
            (tool_dir / ".state" / "token.json").write_text(json.dumps({"access_token": "X"}), encoding="utf-8")

            http = _FakeHttp(base_url="https://api.pinterest.com/v5")
            http.sections_by_board = {"55": [{"id": "s1", "name": "Keep"}]}
            ctx = self._ctx(tool_dir, http, apply=True, yes=True, ack_irreversible=True)
            args = SimpleNamespace(board_id="55", section_id="missing", ad_account_id=None)

            with self.assertRaisesRegex(RuntimeError, "--ack-no-snapshot"):
                cmd_board_sections_delete(args, ctx)
            self.assertEqual(http.calls, [])

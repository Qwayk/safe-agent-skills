from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from pinterest_api_tool.commands.pins import (
    cmd_pins_create,
    cmd_pins_delete,
    cmd_pins_ensure,
    cmd_pins_save,
    cmd_pins_update,
)
from pinterest_api_tool.config import Config
from pinterest_api_tool.http import HttpResponse
from pinterest_api_tool.output import Output


class _FakeHttp:
    def __init__(
        self,
        *,
        base_url: str,
        ignore_patch_keys: set[str] | None = None,
        created_pin_get_link_none: bool = False,
    ):
        self.base_url = base_url.rstrip("/")
        self.calls: list[dict[str, Any]] = []
        self.pins: list[dict[str, Any]] = []
        self._next_pin_id = 3000
        self._ignore_patch_keys = set(ignore_patch_keys or set())
        self._created_pin_ids: set[str] = set()
        self._created_pin_get_link_none = created_pin_get_link_none

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

        if method == "GET" and path.startswith("/boards/") and path.endswith("/pins") and "/sections/" not in path:
            board_id = path.split("/", 3)[2]
            items = [p for p in self.pins if str(p.get("board_id") or "") == board_id]
            return self._resp(status=200, url=url, payload={"items": items, "bookmark": None})

        if method == "GET" and path.startswith("/boards/") and "/sections/" in path and path.endswith("/pins"):
            parts = path.split("/")
            board_id = parts[2]
            section_id = parts[4]
            items = [
                p
                for p in self.pins
                if str(p.get("board_id") or "") == board_id and str(p.get("board_section_id") or "") == section_id
            ]
            return self._resp(status=200, url=url, payload={"items": items, "bookmark": None})

        if method == "POST" and path == "/pins":
            self._next_pin_id += 1
            pid = str(self._next_pin_id)
            pin = {
                "id": pid,
                "board_id": str((json_body or {}).get("board_id") or ""),
                "board_section_id": (json_body or {}).get("board_section_id"),
                "title": (json_body or {}).get("title"),
                "description": (json_body or {}).get("description"),
                "link": (json_body or {}).get("link"),
                "alt_text": (json_body or {}).get("alt_text"),
                "media_source": (json_body or {}).get("media_source"),
            }
            self.pins.append(pin)
            self._created_pin_ids.add(pid)
            return self._resp(status=201, url=url, payload=pin)

        if method == "GET" and path.startswith("/pins/"):
            pid = path.split("/", 2)[2]
            pin = next((p for p in self.pins if str(p.get("id") or "") == pid), None)
            if pin is None:
                return fail(404, {"message": "not found"})
            if self._created_pin_get_link_none and pid in self._created_pin_ids:
                altered = dict(pin)
                altered["link"] = None
                return self._resp(status=200, url=url, payload=altered)
            return self._resp(status=200, url=url, payload=pin)

        if method == "PATCH" and path.startswith("/pins/"):
            pid = path.split("/", 2)[2]
            pin = next((p for p in self.pins if str(p.get("id") or "") == pid), None)
            if pin is None:
                return fail(404, {"message": "not found"})
            for k, v in (json_body or {}).items():
                if k in self._ignore_patch_keys:
                    continue
                pin[k] = v
            return self._resp(status=200, url=url, payload=pin)

        if method == "DELETE" and path.startswith("/pins/") and "/save" not in path:
            pid = path.split("/", 2)[2]
            pin = next((p for p in self.pins if str(p.get("id") or "") == pid), None)
            if pin is None:
                return fail(404, {"message": "not found"})
            self.pins = [p for p in self.pins if str(p.get("id") or "") != pid]
            return self._resp(status=204, url=url, payload={})

        if method == "POST" and path.startswith("/pins/") and path.endswith("/save"):
            source_id = path.split("/", 3)[2]
            source = next((p for p in self.pins if str(p.get("id") or "") == source_id), None)
            if source is None:
                return fail(404, {"message": "not found"})

            self._next_pin_id += 1
            pid = str(self._next_pin_id)
            saved = {
                "id": pid,
                "parent_pin_id": source_id,
                "board_id": str((json_body or {}).get("board_id") or ""),
                "board_section_id": (json_body or {}).get("board_section_id"),
                "link": source.get("link"),
                "title": source.get("title"),
                "description": source.get("description"),
                "alt_text": source.get("alt_text"),
            }
            self.pins.append(saved)
            return self._resp(status=201, url=url, payload=saved)

        raise RuntimeError(f"Unhandled request: {method} {path}")


class _Audit:
    def write(self, event: str, payload):  # noqa: ANN001
        _ = event, payload


class TestPinsWriteCommands(unittest.TestCase):
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

    def test_pins_create_dry_run_emits_plan(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            tool_dir = Path(d)
            (tool_dir / ".env").write_text("PINTEREST_API_BASE_URL=https://api.pinterest.com/v5\n", encoding="utf-8")
            (tool_dir / ".state").mkdir()
            (tool_dir / ".state" / "token.json").write_text(json.dumps({"access_token": "X"}), encoding="utf-8")

            http = _FakeHttp(base_url="https://api.pinterest.com/v5")
            ctx = self._ctx(tool_dir, http, apply=False, yes=False)
            args = SimpleNamespace(
                board_id="b1",
                board_section_id=None,
                ad_account_id=None,
                scan_limit=5000,
                allow_mismatch=False,
                title="T",
                description=None,
                link="https://example.com/post",
                alt_text=None,
                media_source_type="image_url",
                media_url="https://example.com/image.jpg",
                media_id=None,
                media_content_type=None,
                media_data=None,
                media_cover_image_url=None,
            )

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = cmd_pins_create(args, ctx)
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertEqual(payload["ok"], True)
            self.assertEqual(payload["dry_run"], True)
            self.assertEqual(payload["action"], "pins.create")
            self.assertEqual(http.calls, [])

    def test_pins_create_apply_requires_no_snapshot_ack_before_scan_or_write(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            tool_dir = Path(d)
            (tool_dir / ".env").write_text("PINTEREST_API_BASE_URL=https://api.pinterest.com/v5\n", encoding="utf-8")
            (tool_dir / ".state").mkdir()
            (tool_dir / ".state" / "token.json").write_text(json.dumps({"access_token": "X"}), encoding="utf-8")

            http = _FakeHttp(base_url="https://api.pinterest.com/v5")
            http.pins = [{"id": "p1", "board_id": "b1", "board_section_id": None, "link": "https://example.com/post/"}]
            ctx = self._ctx(tool_dir, http, apply=True, yes=True)
            args = SimpleNamespace(
                board_id="b1",
                board_section_id=None,
                ad_account_id=None,
                scan_limit=5000,
                allow_mismatch=False,
                title=None,
                description=None,
                link="http://example.com/post",
                alt_text=None,
                media_source_type="image_url",
                media_url="https://example.com/image.jpg",
                media_id=None,
                media_content_type=None,
                media_data=None,
                media_cover_image_url=None,
            )

            with self.assertRaisesRegex(RuntimeError, "--ack-no-snapshot"):
                cmd_pins_create(args, ctx)
            self.assertEqual(http.calls, [])

    def test_pins_ensure_apply_requires_no_snapshot_ack_before_noop_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            tool_dir = Path(d)
            (tool_dir / ".env").write_text("PINTEREST_API_BASE_URL=https://api.pinterest.com/v5\n", encoding="utf-8")
            (tool_dir / ".state").mkdir()
            (tool_dir / ".state" / "token.json").write_text(json.dumps({"access_token": "X"}), encoding="utf-8")

            http = _FakeHttp(base_url="https://api.pinterest.com/v5")
            http.pins = [{"id": "p1", "board_id": "b1", "board_section_id": None, "link": "https://example.com/post/"}]
            ctx = self._ctx(tool_dir, http, apply=True, yes=True)
            args = SimpleNamespace(
                board_id="b1",
                board_section_id=None,
                link="https://example.com/post",
                ad_account_id=None,
                scan_limit=5000,
                allow_mismatch=False,
                title=None,
                description=None,
                alt_text=None,
                media_source_type="image_url",
                media_url="https://example.com/image.jpg",
                media_id=None,
                media_content_type=None,
                media_data=None,
                media_cover_image_url=None,
            )

            with self.assertRaisesRegex(RuntimeError, "--ack-no-snapshot"):
                cmd_pins_ensure(args, ctx)
            self.assertFalse(any(c["method"] == "POST" and c["path"] == "/pins" for c in http.calls))

    def test_pins_ensure_create_verification_mismatch_requires_allow_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            tool_dir = Path(d)
            (tool_dir / ".env").write_text("PINTEREST_API_BASE_URL=https://api.pinterest.com/v5\n", encoding="utf-8")
            (tool_dir / ".state").mkdir()
            (tool_dir / ".state" / "token.json").write_text(json.dumps({"access_token": "X"}), encoding="utf-8")

            http = _FakeHttp(base_url="https://api.pinterest.com/v5", created_pin_get_link_none=True)
            ctx = self._ctx(tool_dir, http, apply=True, yes=True)
            ctx["ack_no_snapshot"] = True
            args = SimpleNamespace(
                board_id="b1",
                board_section_id=None,
                link="https://example.com/post",
                ad_account_id=None,
                scan_limit=5000,
                allow_mismatch=False,
                title=None,
                description=None,
                alt_text=None,
                media_source_type="image_url",
                media_url="https://example.com/image.jpg",
                media_id=None,
                media_content_type=None,
                media_data=None,
                media_cover_image_url=None,
            )

            with self.assertRaisesRegex(RuntimeError, "Verification failed"):
                cmd_pins_ensure(args, ctx)
            self.assertTrue(any(c["method"] == "POST" and c["path"] == "/pins" for c in http.calls))

    def test_pins_ensure_create_verification_mismatch_allow_mismatch_bypasses(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            tool_dir = Path(d)
            (tool_dir / ".env").write_text("PINTEREST_API_BASE_URL=https://api.pinterest.com/v5\n", encoding="utf-8")
            (tool_dir / ".state").mkdir()
            (tool_dir / ".state" / "token.json").write_text(json.dumps({"access_token": "X"}), encoding="utf-8")

            http = _FakeHttp(base_url="https://api.pinterest.com/v5", created_pin_get_link_none=True)
            ctx = self._ctx(tool_dir, http, apply=True, yes=True)
            ctx["ack_no_snapshot"] = True
            args = SimpleNamespace(
                board_id="b1",
                board_section_id=None,
                link="https://example.com/post",
                ad_account_id=None,
                scan_limit=5000,
                allow_mismatch=True,
                title=None,
                description=None,
                alt_text=None,
                media_source_type="image_url",
                media_url="https://example.com/image.jpg",
                media_id=None,
                media_content_type=None,
                media_data=None,
                media_cover_image_url=None,
            )

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = cmd_pins_ensure(args, ctx)
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["changed"])
            self.assertTrue(payload["no_snapshot_approval"]["acknowledged"])

    def test_pins_update_requires_at_least_one_field(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            tool_dir = Path(d)
            (tool_dir / ".env").write_text("PINTEREST_API_BASE_URL=https://api.pinterest.com/v5\n", encoding="utf-8")
            (tool_dir / ".state").mkdir()
            (tool_dir / ".state" / "token.json").write_text(json.dumps({"access_token": "X"}), encoding="utf-8")

            http = _FakeHttp(base_url="https://api.pinterest.com/v5")
            ctx = self._ctx(tool_dir, http, apply=True, yes=True)
            args = SimpleNamespace(
                id="p1",
                title=None,
                description=None,
                link=None,
                alt_text=None,
                board_id=None,
                board_section_id=None,
                ad_account_id=None,
                allow_mismatch=False,
            )
            with self.assertRaises(RuntimeError) as cm:
                cmd_pins_update(args, ctx)
            self.assertIn("At least one of", str(cm.exception))

    def test_pins_update_verification_mismatch_refuses_without_allow_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            tool_dir = Path(d)
            (tool_dir / ".env").write_text("PINTEREST_API_BASE_URL=https://api.pinterest.com/v5\n", encoding="utf-8")
            (tool_dir / ".state").mkdir()
            (tool_dir / ".state" / "token.json").write_text(json.dumps({"access_token": "X"}), encoding="utf-8")

            http = _FakeHttp(base_url="https://api.pinterest.com/v5", ignore_patch_keys={"title"})
            http.pins = [{"id": "p1", "board_id": "b1", "board_section_id": None, "title": "Old"}]
            ctx = self._ctx(tool_dir, http, apply=True, yes=True)
            ctx["ack_no_snapshot"] = True
            args = SimpleNamespace(
                id="p1",
                title="New",
                description=None,
                link=None,
                alt_text=None,
                board_id=None,
                board_section_id=None,
                ad_account_id=None,
                allow_mismatch=False,
            )

            with self.assertRaisesRegex(RuntimeError, "Verification failed"):
                cmd_pins_update(args, ctx)
            self.assertTrue(any(c["method"] == "PATCH" and c["path"] == "/pins/p1" for c in http.calls))

    def test_pins_delete_requires_ack_irreversible(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            tool_dir = Path(d)
            (tool_dir / ".env").write_text("PINTEREST_API_BASE_URL=https://api.pinterest.com/v5\n", encoding="utf-8")
            (tool_dir / ".state").mkdir()
            (tool_dir / ".state" / "token.json").write_text(json.dumps({"access_token": "X"}), encoding="utf-8")

            http = _FakeHttp(base_url="https://api.pinterest.com/v5")
            ctx = self._ctx(tool_dir, http, apply=True, yes=True, ack_irreversible=False)
            args = SimpleNamespace(id="p1", ad_account_id=None)

            with self.assertRaises(RuntimeError) as cm:
                cmd_pins_delete(args, ctx)
            self.assertIn("--ack-irreversible", str(cm.exception))
            self.assertEqual(http.calls, [])

    def test_pins_delete_apply_requires_no_snapshot_ack_before_delete(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            tool_dir = Path(d)
            (tool_dir / ".env").write_text("PINTEREST_API_BASE_URL=https://api.pinterest.com/v5\n", encoding="utf-8")
            (tool_dir / ".state").mkdir()
            (tool_dir / ".state" / "token.json").write_text(json.dumps({"access_token": "X"}), encoding="utf-8")

            http = _FakeHttp(base_url="https://api.pinterest.com/v5")
            ctx = self._ctx(tool_dir, http, apply=True, yes=True, ack_irreversible=True)
            args = SimpleNamespace(id="missing", ad_account_id=None)

            with self.assertRaisesRegex(RuntimeError, "--ack-no-snapshot"):
                cmd_pins_delete(args, ctx)
            self.assertEqual(http.calls, [])

    def test_pins_save_apply_requires_no_snapshot_ack_before_saved_check_or_write(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            tool_dir = Path(d)
            (tool_dir / ".env").write_text("PINTEREST_API_BASE_URL=https://api.pinterest.com/v5\n", encoding="utf-8")
            (tool_dir / ".state").mkdir()
            (tool_dir / ".state" / "token.json").write_text(json.dumps({"access_token": "X"}), encoding="utf-8")

            http = _FakeHttp(base_url="https://api.pinterest.com/v5")
            http.pins = [
                {"id": "src1", "board_id": "src_board", "board_section_id": None, "link": "https://example.com/post/"},
                {"id": "d1", "board_id": "b1", "board_section_id": None, "parent_pin_id": "src1", "link": "https://example.com/post/"},
            ]
            ctx = self._ctx(tool_dir, http, apply=True, yes=True)
            args = SimpleNamespace(
                id="src1",
                board_id="b1",
                board_section_id=None,
                ad_account_id=None,
                scan_limit=5000,
                allow_mismatch=False,
            )

            with self.assertRaisesRegex(RuntimeError, "--ack-no-snapshot"):
                cmd_pins_save(args, ctx)
            self.assertEqual(http.calls, [])

    def test_pins_save_apply_requires_no_snapshot_ack_before_save_write(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            tool_dir = Path(d)
            (tool_dir / ".env").write_text("PINTEREST_API_BASE_URL=https://api.pinterest.com/v5\n", encoding="utf-8")
            (tool_dir / ".state").mkdir()
            (tool_dir / ".state" / "token.json").write_text(json.dumps({"access_token": "X"}), encoding="utf-8")

            http = _FakeHttp(base_url="https://api.pinterest.com/v5")
            http.pins = [{"id": "src1", "board_id": "src_board", "board_section_id": None, "link": "https://example.com/post/"}]
            ctx = self._ctx(tool_dir, http, apply=True, yes=True)
            args = SimpleNamespace(
                id="src1",
                board_id="b1",
                board_section_id=None,
                ad_account_id=None,
                scan_limit=5000,
                allow_mismatch=False,
            )

            with self.assertRaisesRegex(RuntimeError, "--ack-no-snapshot"):
                cmd_pins_save(args, ctx)
            self.assertEqual(http.calls, [])

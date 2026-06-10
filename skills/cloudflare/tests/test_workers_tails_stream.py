from __future__ import annotations

import io
import json
import sys
import tempfile
import types
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from typing import Any
from unittest.mock import patch

from cloudflare_api_tool.cli import main


class _DummyResponse:
    def __init__(self, *, status: int, url: str, obj: Any | None, body: bytes | None = None):
        self.status_code = int(status)
        self.url = str(url)
        self.headers: dict[str, str] = {}
        if body is not None:
            self.content = body
        else:
            self.content = (json.dumps(obj, ensure_ascii=False) if obj is not None else "").encode("utf-8")

    @property
    def text(self) -> str:
        return self.content.decode("utf-8", errors="replace")


def _write_env(root: Path, *, token: str = "T") -> Path:
    p = root / ".env"
    p.write_text(
        "\n".join(
            [
                "CLOUDFLARE_API_BASE_URL=http://example.invalid/client/v4",
                f"CLOUDFLARE_API_TOKEN={token}",
                "CLOUDFLARE_TIMEOUT_S=30",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return p


def _ok(obj: Any) -> dict[str, Any]:
    return {"success": True, "errors": [], "messages": [], "result": obj}


class _FakeWebSocket:
    def __init__(self, messages: list[str]):
        self._messages = list(messages)

    async def __aenter__(self):  # noqa: ANN201
        return self

    async def __aexit__(self, exc_type, exc, tb):  # noqa: ANN001, ANN201
        return False

    async def recv(self) -> str:
        if not self._messages:
            raise RuntimeError("ConnectionClosed")
        return self._messages.pop(0)


class TestWorkersTailsStream(unittest.TestCase):
    def test_stream_success_writes_file_and_deletes_tail_without_leaking(self) -> None:
        calls: list[dict[str, Any]] = []

        def fake_request(_session, method, url, **kwargs):  # noqa: ANN001
            calls.append({"method": method, "url": str(url), "json": kwargs.get("json")})
            if method == "POST" and str(url).endswith("/accounts/acc1/workers/scripts/s1/tails"):
                return _DummyResponse(
                    status=200,
                    url=url,
                    obj=_ok({"id": "t1", "url": "ws://127.0.0.1:9999/tail?token=SECRET123", "expires_at": "2026-01-01T00:00:00Z"}),
                )
            if method == "DELETE" and str(url).endswith("/accounts/acc1/workers/scripts/s1/tails/t1"):
                return _DummyResponse(status=200, url=url, obj=_ok({}))
            raise AssertionError(f"unexpected call: {method} {url}")

        fake_ws = _FakeWebSocket(["hello", "world"])
        fake_websockets = types.SimpleNamespace(connect=lambda _url, **_kw: fake_ws)

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            env_path = _write_env(Path(d))
            project_dir = Path(d) / "proj"
            out_rel = "tail.log"
            out_abs = project_dir / out_rel

            old = sys.modules.get("websockets")
            sys.modules["websockets"] = fake_websockets  # type: ignore[assignment]
            try:
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = main(
                        [
                            "--env-file",
                            str(env_path),
                            "--project-dir",
                            str(project_dir),
                            "--apply",
                            "--yes",
                            "workers",
                            "tails",
                            "stream",
                            "--account-id",
                            "acc1",
                            "--script-name",
                            "s1",
                            "--duration-s",
                            "1",
                            "--out",
                            out_rel,
                        ]
                    )
            finally:
                if old is None:
                    sys.modules.pop("websockets", None)
                else:
                    sys.modules["websockets"] = old

            self.assertEqual(rc, 0)
            stdout = buf.getvalue()
            payload = json.loads(stdout)
            self.assertTrue(payload["ok"])
            self.assertFalse(payload["dry_run"])

            self.assertNotIn("SECRET123", stdout)
            self.assertNotIn("hello", stdout)
            self.assertNotIn("world", stdout)

            self.assertTrue(out_abs.exists())
            self.assertEqual(out_abs.read_text("utf-8"), "hello\nworld\n")
            self.assertIn("sha256", payload["receipt"]["output_file"])
            self.assertEqual([c["method"] for c in calls], ["POST", "DELETE"])

    def test_stream_failure_redacts_and_still_attempts_cleanup(self) -> None:
        calls: list[dict[str, Any]] = []

        def fake_request(_session, method, url, **kwargs):  # noqa: ANN001
            calls.append({"method": method, "url": str(url), "json": kwargs.get("json")})
            if method == "POST" and str(url).endswith("/accounts/acc1/workers/scripts/s1/tails"):
                return _DummyResponse(
                    status=200,
                    url=url,
                    obj=_ok({"id": "t1", "url": "ws://127.0.0.1:9999/tail?token=SECRET123", "expires_at": "2026-01-01T00:00:00Z"}),
                )
            if method == "DELETE" and str(url).endswith("/accounts/acc1/workers/scripts/s1/tails/t1"):
                return _DummyResponse(status=200, url=url, obj=_ok({}))
            raise AssertionError(f"unexpected call: {method} {url}")

        def connect_raises(url, **_kw):  # noqa: ANN001
            raise RuntimeError(f"connect failed: {url}")

        fake_websockets = types.SimpleNamespace(connect=connect_raises)

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            env_path = _write_env(Path(d))
            project_dir = Path(d) / "proj"

            old = sys.modules.get("websockets")
            sys.modules["websockets"] = fake_websockets  # type: ignore[assignment]
            try:
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = main(
                        [
                            "--env-file",
                            str(env_path),
                            "--project-dir",
                            str(project_dir),
                            "--apply",
                            "--yes",
                            "workers",
                            "tails",
                            "stream",
                            "--account-id",
                            "acc1",
                            "--script-name",
                            "s1",
                            "--duration-s",
                            "1",
                            "--out",
                            "tail.log",
                            "--overwrite",
                        ]
                    )
            finally:
                if old is None:
                    sys.modules.pop("websockets", None)
                else:
                    sys.modules["websockets"] = old

            self.assertEqual(rc, 1)
            stdout = buf.getvalue()
            payload = json.loads(stdout)
            self.assertFalse(payload["ok"])
            self.assertIn("RuntimeError", str(payload.get("error") or ""))
            self.assertNotIn("SECRET123", stdout)
            # Cleanup should still be attempted after tail creation.
            self.assertEqual([c["method"] for c in calls], ["POST", "DELETE"])

    def test_stream_start_tail_missing_id_surfaces_original_error(self) -> None:
        calls: list[dict[str, Any]] = []

        def fake_request(_session, method, url, **kwargs):  # noqa: ANN001
            calls.append({"method": method, "url": str(url), "json": kwargs.get("json")})
            if method == "POST" and str(url).endswith("/accounts/acc1/workers/scripts/s1/tails"):
                return _DummyResponse(
                    status=200,
                    url=url,
                    obj=_ok({"url": "ws://127.0.0.1:9999/tail?token=SECRET123", "expires_at": "2026-01-01T00:00:00Z"}),
                )
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            env_path = _write_env(Path(d))
            project_dir = Path(d) / "proj"

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--project-dir",
                        str(project_dir),
                        "--apply",
                        "--yes",
                        "workers",
                        "tails",
                        "stream",
                        "--account-id",
                        "acc1",
                        "--script-name",
                        "s1",
                        "--duration-s",
                        "1",
                        "--out",
                        "tail.log",
                        "--overwrite",
                    ]
                )

            self.assertEqual(rc, 1)
            stdout = buf.getvalue()
            payload = json.loads(stdout)
            self.assertFalse(payload["ok"])
            self.assertIn("Start tail: missing tail id", payload.get("error", ""))
            self.assertNotIn("Tail cleanup was not attempted", stdout)
            self.assertNotIn("SECRET123", stdout)
            self.assertEqual([c["method"] for c in calls], ["POST"])

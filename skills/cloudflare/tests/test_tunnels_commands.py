from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from typing import Any
from unittest.mock import patch

from cloudflare_api_tool.cli import main


class _DummyResponse:
    def __init__(self, *, status: int, url: str, obj: Any, headers: dict[str, str] | None = None):
        self.status_code = int(status)
        self.url = str(url)
        self.headers = dict(headers or {})
        self.content = json.dumps(obj, ensure_ascii=False).encode("utf-8")


def _write_env(root: Path) -> Path:
    p = root / ".env"
    p.write_text(
        "\n".join(
            [
                "CLOUDFLARE_API_BASE_URL=http://example.invalid/client/v4",
                "CLOUDFLARE_API_TOKEN=T",
                "CLOUDFLARE_TIMEOUT_S=30",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return p


def _ok(obj: Any) -> dict[str, Any]:
    return {"success": True, "errors": [], "messages": [], "result": obj}


class TestTunnelsCommands(unittest.TestCase):
    def test_tunnels_list_path(self) -> None:
        calls: list[str] = []

        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
            calls.append(str(url))
            if method == "GET" and str(url).endswith("/accounts/acc1/cfd_tunnel"):
                return _DummyResponse(status=200, url=url, obj=_ok([{"id": "t1", "name": "x"}]))
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            env_path = _write_env(Path(d))
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--env-file", str(env_path), "tunnels", "list", "--account-id", "acc1"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["command"], "tunnels.list")
            self.assertTrue(calls)

    def test_tunnels_config_get_path(self) -> None:
        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
            if method == "GET" and str(url).endswith("/accounts/acc1/cfd_tunnel/t1/configurations"):
                return _DummyResponse(status=200, url=url, obj=_ok({"ingress": []}))
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            env_path = _write_env(Path(d))
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--env-file", str(env_path), "tunnels", "config", "get", "--account-id", "acc1", "--tunnel-id", "t1"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["command"], "tunnels.config.get")


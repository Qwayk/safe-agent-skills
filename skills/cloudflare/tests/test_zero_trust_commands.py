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


class TestZeroTrustCommands(unittest.TestCase):
    def test_access_apps_list_passes_filters(self) -> None:
        calls: list[dict[str, Any]] = []

        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
            calls.append({"method": method, "url": str(url), "params": kwargs.get("params")})
            if method == "GET" and str(url).endswith("/accounts/acc1/access/apps"):
                return _DummyResponse(status=200, url=url, obj=_ok([{"id": "a1"}]))
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            env_path = _write_env(Path(d))
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "zero-trust",
                        "access",
                        "apps",
                        "list",
                        "--account-id",
                        "acc1",
                        "--search",
                        "hello",
                        "--exact",
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertEqual(calls[0]["params"]["search"], "hello")
            self.assertEqual(calls[0]["params"]["exact"], True)

    def test_gateway_rules_get_path(self) -> None:
        calls: list[str] = []

        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
            calls.append(str(url))
            if method == "GET" and str(url).endswith("/accounts/acc1/gateway/rules/r1"):
                return _DummyResponse(status=200, url=url, obj=_ok({"id": "r1"}))
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            env_path = _write_env(Path(d))
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--env-file", str(env_path), "zero-trust", "gateway", "rules", "get", "--account-id", "acc1", "--rule-id", "r1"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(calls)

    def test_access_apps_resolve_ambiguous_is_error(self) -> None:
        seen_params: dict[str, Any] = {}

        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
            if method == "GET" and str(url).endswith("/accounts/acc1/access/apps"):
                params = kwargs.get("params") or {}
                if isinstance(params, dict):
                    seen_params.update(params)
                return _DummyResponse(status=200, url=url, obj=_ok([{"id": "a1", "name": "x"}, {"id": "a2", "name": "x"}]))
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            env_path = _write_env(Path(d))
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--env-file", str(env_path), "zero-trust", "access", "apps", "resolve", "--account-id", "acc1", "--name", "x", "--exact"])
            self.assertEqual(rc, 1)
            payload = json.loads(buf.getvalue())
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["error_type"], "Ambiguous")
            self.assertEqual(seen_params.get("name"), "x")
            self.assertEqual(seen_params.get("exact"), True)

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


class TestTimeoutProfiles(unittest.TestCase):
    def test_zero_trust_auto_slow_profile_sets_read_timeout_floor(self) -> None:
        seen_timeout = None

        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
            nonlocal seen_timeout
            seen_timeout = kwargs.get("timeout")
            if method == "GET" and str(url).endswith("/accounts/acc1/access/apps"):
                return _DummyResponse(status=200, url=url, obj=_ok([]))
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            env_path = _write_env(Path(d))
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--env-file", str(env_path), "zero-trust", "access", "apps", "list", "--account-id", "acc1"])
            self.assertEqual(rc, 0)
            self.assertEqual(seen_timeout, (30.0, 240.0))

    def test_zero_trust_timeout_profile_default_does_not_force_slow(self) -> None:
        seen_timeout = None

        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
            nonlocal seen_timeout
            seen_timeout = kwargs.get("timeout")
            if method == "GET" and str(url).endswith("/accounts/acc1/access/apps"):
                return _DummyResponse(status=200, url=url, obj=_ok([]))
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            env_path = _write_env(Path(d))
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--timeout-profile",
                        "default",
                        "zero-trust",
                        "access",
                        "apps",
                        "list",
                        "--account-id",
                        "acc1",
                    ]
                )
            self.assertEqual(rc, 0)
            self.assertEqual(seen_timeout, (30.0, 30.0))

    def test_timeout_s_overrides_connect_and_read(self) -> None:
        seen_timeout = None

        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
            nonlocal seen_timeout
            seen_timeout = kwargs.get("timeout")
            if method == "GET" and str(url).endswith("/user/tokens/verify"):
                return _DummyResponse(status=200, url=url, obj=_ok({"status": "active"}))
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            env_path = _write_env(Path(d))
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--env-file", str(env_path), "--timeout-s", "5", "auth", "check"])
            self.assertEqual(rc, 0)
            self.assertEqual(seen_timeout, (5.0, 5.0))


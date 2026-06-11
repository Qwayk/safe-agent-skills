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


class TestAuthDoctorCommand(unittest.TestCase):
    def test_auth_doctor_calls_expected_endpoints(self) -> None:
        called: list[str] = []

        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
            called.append(str(url))
            if method == "GET" and str(url).endswith("/user/tokens/verify"):
                return _DummyResponse(status=200, url=url, obj=_ok({"status": "active"}))
            if method == "GET" and str(url).endswith("/accounts?page=1&per_page=1"):
                return _DummyResponse(status=200, url=url, obj=_ok([{"id": "acc1"}]))
            if method == "GET" and str(url).endswith("/accounts/acc1/workers/scripts"):
                return _DummyResponse(status=200, url=url, obj=_ok([]))
            if method == "GET" and str(url).endswith("/accounts/acc1/cfd_tunnel"):
                return _DummyResponse(status=200, url=url, obj=_ok([]))
            if method == "GET" and str(url).endswith("/accounts/acc1/access/apps"):
                return _DummyResponse(status=200, url=url, obj=_ok([]))
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            env_path = _write_env(Path(d))
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--env-file", str(env_path), "--parallel", "4", "auth", "doctor", "--account-id", "acc1"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["command"], "auth.doctor")
            names = {r["name"] for r in payload["results"]}
            self.assertIn("token_verify", names)
            self.assertIn("accounts_list", names)
            self.assertIn("zero_trust_access_apps_list", names)
            self.assertTrue(called)

    def test_auth_explain_returns_known_permissions_for_speed_trend(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = _write_env(Path(d))
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--env-file", str(env_path), "auth", "explain", "--for", "observability", "speed", "page", "trend"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["known"])
            self.assertIn("Zone Settings Read", payload["required_permissions"])

    def test_auth_explain_handles_unknown_target(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = _write_env(Path(d))
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--env-file", str(env_path), "auth", "explain", "--for", "something", "totally", "custom"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertFalse(payload["known"])

    def test_auth_zone_create_check_reports_allowed_on_validation_error(self) -> None:
        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
            if method == "POST" and str(url).endswith("/zones"):
                return _DummyResponse(
                    status=400,
                    url=url,
                    obj={"success": False, "errors": [{"code": 1004, "message": "name is required"}], "messages": [], "result": None},
                )
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            env_path = _write_env(Path(d))
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--env-file", str(env_path), "auth", "zone-create-check", "--account-id", "acc1"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["command"], "auth.zone_create_check")
            self.assertEqual(payload["result"], "allowed")
            self.assertTrue(payload["permission_ok"])

    def test_auth_zone_create_check_reports_forbidden_on_permission_error(self) -> None:
        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
            if method == "POST" and str(url).endswith("/zones"):
                return _DummyResponse(
                    status=403,
                    url=url,
                    obj={"success": False, "errors": [{"code": 10000, "message": "permission denied"}], "messages": [], "result": None},
                )
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            env_path = _write_env(Path(d))
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--env-file", str(env_path), "auth", "zone-create-check", "--account-id", "acc1"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["result"], "forbidden")
            self.assertFalse(payload["permission_ok"])

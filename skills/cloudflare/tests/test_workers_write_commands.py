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
    def __init__(self, *, status: int, url: str, obj: Any | None, headers: dict[str, str] | None = None, body: bytes | None = None):
        self.status_code = int(status)
        self.url = str(url)
        self.headers = dict(headers or {})
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


class TestWorkersWriteCommands(unittest.TestCase):
    def test_routes_ensure_dry_run_does_not_write(self) -> None:
        calls: list[dict[str, Any]] = []

        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
            calls.append({"method": method, "url": str(url), "json": kwargs.get("json")})
            if method == "GET" and str(url).endswith("/zones/z1/workers/routes"):
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
                        "workers",
                        "routes",
                        "ensure",
                        "--zone-id",
                        "z1",
                        "--pattern",
                        "example.com/*",
                        "--script-name",
                        "s1",
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])
            self.assertEqual(calls[0]["method"], "GET")
            self.assertEqual(len([c for c in calls if c["method"] in {"POST", "PUT", "DELETE"}]), 0)

    def test_routes_ensure_apply_creates_and_verifies(self) -> None:
        calls: list[dict[str, Any]] = []
        routes_after = [{"id": "r1", "pattern": "example.com/*", "script": "s1"}]

        def fake_request(_session, method, url, **kwargs):  # noqa: ANN001
            calls.append({"method": method, "url": str(url), "json": kwargs.get("json")})
            if method == "GET" and str(url).endswith("/zones/z1/workers/routes"):
                # First GET -> empty, second GET -> includes route
                if len([c for c in calls if c["method"] == "GET"]) == 1:
                    return _DummyResponse(status=200, url=url, obj=_ok([]))
                return _DummyResponse(status=200, url=url, obj=_ok(routes_after))
            if method == "POST" and str(url).endswith("/zones/z1/workers/routes"):
                self.assertEqual(kwargs.get("json"), {"pattern": "example.com/*", "script": "s1"})
                return _DummyResponse(status=200, url=url, obj=_ok({"id": "r1", "pattern": "example.com/*", "script": "s1"}))
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            env_path = _write_env(Path(d))
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--yes",
                        "workers",
                        "routes",
                        "ensure",
                        "--zone-id",
                        "z1",
                        "--pattern",
                        "example.com/*",
                        "--script-name",
                        "s1",
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            self.assertEqual(calls, [])

    def test_routes_ensure_absent_requires_yes_when_deleting(self) -> None:
        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
            if method == "GET" and str(url).endswith("/zones/z1/workers/routes"):
                return _DummyResponse(status=200, url=url, obj=_ok([{"id": "r1", "pattern": "example.com/*", "script": "s1"}]))
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            env_path = _write_env(Path(d))
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "workers",
                        "routes",
                        "ensure-absent",
                        "--zone-id",
                        "z1",
                        "--pattern",
                        "example.com/*",
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])

    def test_subdomain_ensure_absent_delete_handles_204(self) -> None:
        calls: list[dict[str, Any]] = []

        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
            calls.append({"method": method, "url": str(url)})
            if method == "GET" and str(url).endswith("/accounts/acc1/workers/subdomain"):
                # Before delete: subdomain exists. After delete: null.
                if len([c for c in calls if c["method"] == "GET"]) == 1:
                    return _DummyResponse(status=200, url=url, obj=_ok({"subdomain": "sd"}))
                return _DummyResponse(status=200, url=url, obj=_ok({"subdomain": ""}))
            if method == "DELETE" and str(url).endswith("/accounts/acc1/workers/subdomain"):
                return _DummyResponse(status=204, url=url, obj=None, body=b"")
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            env_path = _write_env(Path(d))
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--yes",
                        "workers",
                        "subdomain",
                        "ensure-absent",
                        "--account-id",
                        "acc1",
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            self.assertEqual(calls, [])

    def test_domains_attach_apply_puts_and_verifies(self) -> None:
        calls: list[dict[str, Any]] = []
        domain_after = {"id": "d1", "hostname": "api.example.com", "zone_id": "z1", "service": "svc1"}

        def fake_request(_session, method, url, **kwargs):  # noqa: ANN001
            calls.append({"method": method, "url": str(url), "json": kwargs.get("json")})
            if method == "GET" and str(url).endswith("/accounts/acc1/workers/domains"):
                if len([c for c in calls if c["method"] == "GET"]) == 1:
                    return _DummyResponse(status=200, url=url, obj=_ok([]))
                return _DummyResponse(status=200, url=url, obj=_ok([domain_after]))
            if method == "PUT" and str(url).endswith("/accounts/acc1/workers/domains"):
                self.assertEqual(
                    kwargs.get("json"),
                    {"zone_id": "z1", "hostname": "api.example.com", "service": "svc1"},
                )
                return _DummyResponse(status=200, url=url, obj=_ok(domain_after))
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            env_path = _write_env(Path(d))
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--yes",
                        "workers",
                        "domains",
                        "attach",
                        "--account-id",
                        "acc1",
                        "--zone-id",
                        "z1",
                        "--hostname",
                        "api.example.com",
                        "--service",
                        "svc1",
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])

    def test_workers_observability_enable_dry_run_only_gets(self) -> None:
        calls: list[dict[str, Any]] = []

        def fake_request(_session, method, url, **kwargs):  # noqa: ANN001
            calls.append({"method": method, "url": str(url), "json": kwargs.get("json")})
            if method == "GET" and str(url).endswith("/accounts/acc1/workers/scripts/s1/script-settings"):
                return _DummyResponse(
                    status=200,
                    url=url,
                    obj=_ok({"observability": {"enabled": False, "head_sampling_rate": 0.2, "logs": {"enabled": True, "invocation_logs": True}}}),
                )
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            env_path = _write_env(Path(d))
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "workers",
                        "observability",
                        "enable",
                        "--account-id",
                        "acc1",
                        "--script-name",
                        "s1",
                        "--head-sampling-rate",
                        "0.5",
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])
            self.assertEqual([c["method"] for c in calls], ["GET"])

    def test_workers_observability_enable_apply_patches_and_verifies(self) -> None:
        calls: list[dict[str, Any]] = []
        before = {"observability": {"enabled": False, "head_sampling_rate": 0.2, "logs": {"enabled": True, "invocation_logs": True}}}
        after = {"observability": {"enabled": True, "head_sampling_rate": 0.5, "logs": {"enabled": True, "invocation_logs": True}}}

        def fake_request(_session, method, url, **kwargs):  # noqa: ANN001
            calls.append({"method": method, "url": str(url), "json": kwargs.get("json")})
            if method == "GET" and str(url).endswith("/accounts/acc1/workers/scripts/s1/script-settings"):
                if len([c for c in calls if c["method"] == "GET"]) == 1:
                    return _DummyResponse(status=200, url=url, obj=_ok(before))
                return _DummyResponse(status=200, url=url, obj=_ok(after))
            if method == "PATCH" and str(url).endswith("/accounts/acc1/workers/scripts/s1/script-settings"):
                self.assertEqual(
                    kwargs.get("json"),
                    {"observability": {"enabled": True, "head_sampling_rate": 0.5, "logs": {"enabled": True, "invocation_logs": True}}},
                )
                return _DummyResponse(status=200, url=url, obj=_ok(after))
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            env_path = _write_env(Path(d))
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--yes",
                        "workers",
                        "observability",
                        "enable",
                        "--account-id",
                        "acc1",
                        "--script-name",
                        "s1",
                        "--head-sampling-rate",
                        "0.5",
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            self.assertEqual(calls, [])

    def test_workers_observability_disable_apply_patches_and_verifies(self) -> None:
        calls: list[dict[str, Any]] = []
        before = {"observability": {"enabled": True, "head_sampling_rate": 0.4, "logs": {"enabled": True, "invocation_logs": True}}}
        after = {"observability": {"enabled": False, "head_sampling_rate": 0.4, "logs": {"enabled": True, "invocation_logs": True}}}

        def fake_request(_session, method, url, **kwargs):  # noqa: ANN001
            calls.append({"method": method, "url": str(url), "json": kwargs.get("json")})
            if method == "GET" and str(url).endswith("/accounts/acc1/workers/scripts/s1/script-settings"):
                if len([c for c in calls if c["method"] == "GET"]) == 1:
                    return _DummyResponse(status=200, url=url, obj=_ok(before))
                return _DummyResponse(status=200, url=url, obj=_ok(after))
            if method == "PATCH" and str(url).endswith("/accounts/acc1/workers/scripts/s1/script-settings"):
                self.assertEqual(
                    kwargs.get("json"),
                    {"observability": {"enabled": False, "head_sampling_rate": 0.4, "logs": {"enabled": True, "invocation_logs": True}}},
                )
                return _DummyResponse(status=200, url=url, obj=_ok(after))
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            env_path = _write_env(Path(d))
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--yes",
                        "workers",
                        "observability",
                        "disable",
                        "--account-id",
                        "acc1",
                        "--script-name",
                        "s1",
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            self.assertEqual(calls, [])

    def test_workers_observability_sampling_rate_validation(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = _write_env(Path(d))
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "workers",
                        "observability",
                        "enable",
                        "--account-id",
                        "acc1",
                        "--script-name",
                        "s1",
                        "--head-sampling-rate",
                        "1.5",
                    ]
                )
            self.assertEqual(rc, 1)
            payload = json.loads(buf.getvalue())
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["error_type"], "ValidationError")

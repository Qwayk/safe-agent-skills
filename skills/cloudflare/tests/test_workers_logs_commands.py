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


def _write_env(root: Path, *, token: str) -> Path:
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


class TestWorkersLogsCommands(unittest.TestCase):
    def test_auto_discovery_prefers_requestId_over_metadata_requestId(self) -> None:
        bodies: list[dict[str, Any]] = []

        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
            if url.endswith("/accounts/a1/workers/observability/telemetry/keys"):
                return _DummyResponse(
                    status=200,
                    url=url,
                    obj={
                        "success": True,
                        "errors": [],
                        "messages": [],
                        "result": [
                            {"key": "$metadata.requestId"},
                            {"key": "requestId"},
                            {"key": "script_name"},
                        ],
                    },
                )
            if url.endswith("/accounts/a1/workers/observability/telemetry/query"):
                bodies.append(kwargs.get("json") or {})
                return _DummyResponse(
                    status=200,
                    url=url,
                    obj={"success": True, "errors": [], "messages": [], "result": {"statistics": {"rows_read": 0}}},
                )
            raise AssertionError(f"Unexpected request: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root, token="T")
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--project-dir",
                        str(root),
                        "--apply",
                        "workers",
                        "logs",
                        "search",
                        "--account-id",
                        "a1",
                        "--error-id",
                        "E1",
                        "--out",
                        "out.json",
                    ]
                )
            self.assertEqual(rc, 0)
            self.assertEqual(len(bodies), 1)
            params = (bodies[0].get("parameters") or {})
            filters = params.get("filters") or []
            self.assertTrue(filters)
            self.assertEqual(filters[0].get("key"), "requestId")

    def test_dry_run_search_does_not_call_api(self) -> None:
        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
            raise AssertionError(f"Should not call API in dry-run: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root, token="T")
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--project-dir",
                        str(root),
                        "workers",
                        "logs",
                        "search",
                        "--account-id",
                        "a1",
                        "--error-id",
                        "E1",
                        "--out",
                        "out.json",
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])
            self.assertEqual(payload["command"], "workers.logs.search")

    def test_dry_run_keys_does_not_call_api(self) -> None:
        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
            raise AssertionError(f"Should not call API in dry-run: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root, token="T")
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--project-dir",
                        str(root),
                        "workers",
                        "logs",
                        "keys",
                        "--account-id",
                        "a1",
                        "--out",
                        "keys.json",
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])
            self.assertEqual(payload["command"], "workers.logs.keys")

    def test_apply_keys_writes_file_and_never_prints_body(self) -> None:
        sentinel = "pii@example.com"
        calls: list[dict[str, Any]] = []

        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
            calls.append({"method": method, "url": url, "json": kwargs.get("json")})
            if url.endswith("/accounts/a1/workers/observability/telemetry/keys"):
                return _DummyResponse(
                    status=200,
                    url=url,
                    obj={"success": True, "errors": [], "messages": [], "result": [{"key": "x-request-id"}, {"key": f"field_{sentinel}"}]},
                )
            raise AssertionError(f"Unexpected request: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root, token="T")
            out_file = root / "keys.json"
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--project-dir",
                        str(root),
                        "--apply",
                        "workers",
                        "logs",
                        "keys",
                        "--account-id",
                        "a1",
                        "--out",
                        str(out_file.name),
                    ]
                )
            self.assertEqual(rc, 0)
            stdout = buf.getvalue()
            self.assertNotIn(sentinel, stdout)
            payload = json.loads(stdout)
            self.assertTrue(payload["ok"])
            self.assertFalse(payload["dry_run"])
            self.assertEqual(payload["command"], "workers.logs.keys")
            self.assertTrue(out_file.exists())
            self.assertIn(sentinel, out_file.read_text(encoding="utf-8"))
            urls = [c["url"] for c in calls]
            self.assertTrue(any(u.endswith("/accounts/a1/workers/observability/telemetry/keys") for u in urls))

    def test_dry_run_values_does_not_call_api(self) -> None:
        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
            raise AssertionError(f"Should not call API in dry-run: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root, token="T")
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--project-dir",
                        str(root),
                        "workers",
                        "logs",
                        "values",
                        "--account-id",
                        "a1",
                        "--key",
                        "x-request-id",
                        "--type",
                        "string",
                        "--needle",
                        "E1",
                        "--out",
                        "values.json",
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])
            self.assertEqual(payload["command"], "workers.logs.values")

    def test_apply_values_writes_file_and_never_prints_body(self) -> None:
        sentinel = "pii@example.com"
        calls: list[dict[str, Any]] = []

        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
            calls.append({"method": method, "url": url, "json": kwargs.get("json")})
            if url.endswith("/accounts/a1/workers/observability/telemetry/values"):
                return _DummyResponse(status=200, url=url, obj={"success": True, "errors": [], "messages": [], "result": [f"user={sentinel}"]})
            raise AssertionError(f"Unexpected request: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root, token="T")
            out_file = root / "values.json"
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--project-dir",
                        str(root),
                        "--apply",
                        "workers",
                        "logs",
                        "values",
                        "--account-id",
                        "a1",
                        "--key",
                        "x-request-id",
                        "--type",
                        "string",
                        "--needle",
                        "E1",
                        "--out",
                        str(out_file.name),
                    ]
                )
            self.assertEqual(rc, 0)
            stdout = buf.getvalue()
            self.assertNotIn(sentinel, stdout)
            payload = json.loads(stdout)
            self.assertTrue(payload["ok"])
            self.assertFalse(payload["dry_run"])
            self.assertEqual(payload["command"], "workers.logs.values")
            self.assertTrue(out_file.exists())
            self.assertIn(sentinel, out_file.read_text(encoding="utf-8"))
            urls = [c["url"] for c in calls]
            self.assertTrue(any(u.endswith("/accounts/a1/workers/observability/telemetry/values") for u in urls))

    def test_apply_search_writes_file_and_never_prints_body(self) -> None:
        sentinel = "pii@example.com"
        calls: list[dict[str, Any]] = []

        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
            calls.append({"method": method, "url": url, "json": kwargs.get("json")})
            if url.endswith("/accounts/a1/workers/observability/telemetry/keys"):
                return _DummyResponse(
                    status=200,
                    url=url,
                    obj={
                        "success": True,
                        "errors": [],
                        "messages": [],
                        "result": [{"key": "x-request-id"}, {"key": "script_name"}],
                    },
                )
            if url.endswith("/accounts/a1/workers/observability/telemetry/query"):
                return _DummyResponse(
                    status=200,
                    url=url,
                    obj={
                        "success": True,
                        "errors": [],
                        "messages": [],
                        "result": {
                            "events": {"data": [{"message": f"user={sentinel}"}]},
                            "statistics": {"rows_read": 1},
                        },
                    },
                )
            raise AssertionError(f"Unexpected request: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root, token="T")
            out_file = root / "stored_logs.json"
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--project-dir",
                        str(root),
                        "--apply",
                        "workers",
                        "logs",
                        "search",
                        "--account-id",
                        "a1",
                        "--error-id",
                        "E1",
                        "--script-name",
                        "my-worker",
                        "--out",
                        str(out_file.name),
                    ]
                )
            self.assertEqual(rc, 0)
            stdout = buf.getvalue()
            self.assertNotIn(sentinel, stdout)
            payload = json.loads(stdout)
            self.assertTrue(payload["ok"])
            self.assertFalse(payload["dry_run"])
            self.assertEqual(payload["command"], "workers.logs.search")
            self.assertTrue(out_file.exists())
            self.assertIn(sentinel, out_file.read_text(encoding="utf-8"))
            receipt = payload["receipt"]
            self.assertIn("output_file", receipt)
            self.assertIsNotNone(receipt["output_file"].get("sha256"))
            self.assertIsNotNone(receipt["output_file"].get("size_bytes"))
            # Ensure both keys discovery and query were invoked.
            urls = [c["url"] for c in calls]
            self.assertTrue(any(u.endswith("/accounts/a1/workers/observability/telemetry/keys") for u in urls))
            self.assertTrue(any(u.endswith("/accounts/a1/workers/observability/telemetry/query") for u in urls))

    def test_auto_discovery_refusal_when_no_request_id_key(self) -> None:
        calls: list[dict[str, Any]] = []

        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
            calls.append({"method": method, "url": url})
            if url.endswith("/accounts/a1/workers/observability/telemetry/keys"):
                return _DummyResponse(
                    status=200,
                    url=url,
                    obj={"success": True, "errors": [], "messages": [], "result": [{"key": "something_else"}]},
                )
            if url.endswith("/accounts/a1/workers/observability/telemetry/query"):
                raise AssertionError("Should require explicit no-snapshot approval before calling telemetry/query")
            raise AssertionError(f"Unexpected request: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root, token="T")
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--project-dir",
                        str(root),
                        "--apply",
                        "workers",
                        "logs",
                        "search",
                        "--account-id",
                        "a1",
                        "--error-id",
                        "E1",
                        "--out",
                        "out.json",
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            urls = [c["url"] for c in calls]
            self.assertTrue(any(u.endswith("/accounts/a1/workers/observability/telemetry/keys") for u in urls))

    def test_override_request_id_key_skips_keys_call(self) -> None:
        bodies: list[dict[str, Any]] = []

        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
            if url.endswith("/accounts/a1/workers/observability/telemetry/keys"):
                raise AssertionError("Should not call telemetry/keys when --request-id-key is provided")
            if url.endswith("/accounts/a1/workers/observability/telemetry/query"):
                body = kwargs.get("json") or {}
                bodies.append(body)
                return _DummyResponse(status=200, url=url, obj={"success": True, "errors": [], "messages": [], "result": {"statistics": {"rows_read": 0}}})
            raise AssertionError(f"Unexpected request: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root, token="T")
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--project-dir",
                        str(root),
                        "--apply",
                        "workers",
                        "logs",
                        "search",
                        "--account-id",
                        "a1",
                        "--error-id",
                        "E1",
                        "--request-id-key",
                        "my.request.id",
                        "--out",
                        "out.json",
                    ]
                )
            self.assertEqual(rc, 0)
            self.assertEqual(len(bodies), 1)
            body = bodies[0]
            self.assertEqual(body.get("queryId"), "temporary")
            params = body.get("parameters") or {}
            filters = params.get("filters") or []
            self.assertTrue(filters)
            self.assertEqual(filters[0].get("key"), "my.request.id")

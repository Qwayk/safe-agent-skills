from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from typing import Any
from unittest.mock import patch

import requests

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


class TestCoreCommands(unittest.TestCase):
    def test_auth_check_calls_verify_endpoint(self) -> None:
        calls: list[dict[str, Any]] = []

        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
            calls.append({"method": method, "url": url, "params": kwargs.get("params")})
            return _DummyResponse(
                status=200,
                url=url,
                obj={"success": True, "errors": [], "messages": [], "result": {"status": "active"}},
            )

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            env_path = _write_env(Path(d), token="T")
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--env-file", str(env_path), "auth", "check"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertEqual(calls[0]["method"], "GET")
            self.assertTrue(str(calls[0]["url"]).endswith("/user/tokens/verify"))

    def test_auth_probe_calls_common_read_endpoints(self) -> None:
        calls: list[dict[str, Any]] = []

        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
            calls.append({"method": method, "url": url, "params": kwargs.get("params")})
            if url.endswith("/user/tokens/verify"):
                return _DummyResponse(
                    status=200,
                    url=url,
                    obj={"success": True, "errors": [], "messages": [], "result": {"id": "t1", "status": "active"}},
                )
            if url.endswith("/accounts"):
                return _DummyResponse(
                    status=200,
                    url=url,
                    obj={"success": True, "errors": [], "messages": [], "result": [{"id": "a1"}], "result_info": {}},
                )
            if url.endswith("/accounts/a1/workers/scripts"):
                return _DummyResponse(
                    status=200,
                    url=url,
                    obj={"success": True, "errors": [], "messages": [], "result": [{"id": "s1"}], "result_info": {}},
                )
            if url.endswith("/accounts/a1/storage/kv/namespaces"):
                return _DummyResponse(
                    status=200,
                    url=url,
                    obj={"success": True, "errors": [], "messages": [], "result": [{"id": "n1"}], "result_info": {}},
                )
            if url.endswith("/accounts/a1/d1/database"):
                return _DummyResponse(
                    status=200,
                    url=url,
                    obj={"success": True, "errors": [], "messages": [], "result": [{"uuid": "d1"}], "result_info": {}},
                )
            if url.endswith("/zones"):
                return _DummyResponse(
                    status=200,
                    url=url,
                    obj={"success": True, "errors": [], "messages": [], "result": [{"id": "z1"}], "result_info": {}},
                )
            return _DummyResponse(status=404, url=url, obj={"success": False, "errors": [{"message": "nope"}], "result": None})

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            env_path = _write_env(Path(d), token="T")
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--env-file", str(env_path), "--output", "json", "auth", "probe", "--account-id", "a1"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            checks = payload["checks"]
            self.assertTrue(checks["token_verify"]["ok"])
            self.assertTrue(checks["accounts_list"]["ok"])
            self.assertTrue(checks["workers_scripts_list"]["ok"])
            self.assertTrue(checks["workers_kv_namespaces_list"]["ok"])
            self.assertTrue(checks["d1_databases_list"]["ok"])
            self.assertTrue(checks["zones_list"]["ok"])
            urls = [c["url"] for c in calls]
            self.assertIn("http://example.invalid/client/v4/user/tokens/verify", urls)
            self.assertIn("http://example.invalid/client/v4/accounts", urls)
            self.assertIn("http://example.invalid/client/v4/accounts/a1/workers/scripts", urls)
            self.assertIn("http://example.invalid/client/v4/accounts/a1/storage/kv/namespaces", urls)
            self.assertIn("http://example.invalid/client/v4/accounts/a1/d1/database", urls)
            self.assertIn("http://example.invalid/client/v4/zones", urls)

    def test_accounts_list_passes_pagination(self) -> None:
        calls: list[dict[str, Any]] = []

        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
            calls.append({"method": method, "url": url, "params": kwargs.get("params")})
            return _DummyResponse(
                status=200,
                url=url,
                obj={"success": True, "errors": [], "messages": [], "result": [{"id": "a1"}], "result_info": {}},
            )

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            env_path = _write_env(Path(d), token="T")
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--env-file", str(env_path), "accounts", "list", "--page", "2", "--per-page", "10"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertEqual(calls[0]["url"], "http://example.invalid/client/v4/accounts")
            self.assertEqual(calls[0]["params"]["page"], 2)
            self.assertEqual(calls[0]["params"]["per_page"], 10)

    def test_zones_resolve_uses_match_all(self) -> None:
        calls: list[dict[str, Any]] = []

        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
            calls.append({"method": method, "url": url, "params": kwargs.get("params")})
            return _DummyResponse(
                status=200,
                url=url,
                obj={"success": True, "errors": [], "messages": [], "result": [{"id": "z1", "name": "example.com"}]},
            )

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            env_path = _write_env(Path(d), token="T")
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--env-file", str(env_path), "zones", "resolve", "--name", "example.com"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertEqual(calls[0]["url"], "http://example.invalid/client/v4/zones")
            self.assertEqual(calls[0]["params"]["name"], "example.com")
            self.assertEqual(calls[0]["params"]["match"], "all")
            self.assertEqual(calls[0]["params"]["per_page"], 50)

    def test_parse_error_is_json(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = main(["--output", "json", "accounts", "set-default"])
        self.assertEqual(rc, 1)
        payload = json.loads(buf.getvalue())
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error_type"], "ValidationError")

    def test_auth_errors_do_not_leak_token_value(self) -> None:
        secret = "SUPER_SECRET_TOKEN"

        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
            raise requests.RequestException(f"boom {secret}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            env_path = _write_env(Path(d), token=secret)
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--env-file", str(env_path), "auth", "check"])
            self.assertEqual(rc, 1)
            text = buf.getvalue()
            self.assertNotIn(secret, text)
            self.assertIn("<REDACTED>", text)

    def test_runs_list_only_returns_cloudflare_rows(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = _write_env(root, token="T")
            runs_root = root / ".state" / "runs"
            runs_root.mkdir(parents=True, exist_ok=True)
            (runs_root / "index.jsonl").write_text(
                "\n".join(
                    [
                        json.dumps({"run_id": "cf1", "tool": "cloudflare-api-tool"}),
                        json.dumps({"run_id": "dy1", "tool": "dynadot-api-tool"}),
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--env-file", str(env_path), "runs", "list", "--limit", "10"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["count"], 1)
            self.assertEqual(payload["runs"][0]["run_id"], "cf1")

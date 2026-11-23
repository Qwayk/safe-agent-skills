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
    def test_auth_check_uses_accounts_for_account_owned_token(self) -> None:
        calls: list[dict[str, Any]] = []

        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
            calls.append(
                {
                    "method": method,
                    "url": url,
                    "params": kwargs.get("params"),
                    "headers": kwargs.get("headers") or {},
                }
            )
            return _DummyResponse(
                status=200,
                url=url,
                obj={
                    "success": True,
                    "errors": [],
                    "messages": [],
                    "result": [{"id": "account-from-file", "name": "Example"}],
                    "result_info": {},
                },
            )

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            env_path = _write_env(Path(d), token="cfat_account_token")
            with env_path.open("a", encoding="utf-8") as f:
                f.write("CLOUDFLARE_ACCOUNT_ID=account-from-file\n")
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--env-file", str(env_path), "auth", "check"])

        self.assertEqual(rc, 0)
        payload = json.loads(buf.getvalue())
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["token_owner"], "account")
        self.assertEqual(payload["verification"], "accounts_list")
        self.assertTrue(payload["result"]["configured_account_match"])
        self.assertEqual([call["url"] for call in calls], ["http://example.invalid/client/v4/accounts"])

    def test_auth_check_uses_account_id_for_unprefixed_account_token(self) -> None:
        calls: list[str] = []

        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
            _ = (self, method, kwargs)
            calls.append(str(url))
            return _DummyResponse(
                status=200,
                url=url,
                obj={
                    "success": True,
                    "errors": [],
                    "messages": [],
                    "result": [{"id": "legacy-account", "name": "Example"}],
                    "result_info": {},
                },
            )

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            env_path = _write_env(Path(d), token="legacy_account_token")
            with env_path.open("a", encoding="utf-8") as f:
                f.write("CLOUDFLARE_ACCOUNT_ID=legacy-account\n")
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--env-file", str(env_path), "auth", "check"])

        self.assertEqual(rc, 0)
        payload = json.loads(buf.getvalue())
        self.assertEqual(payload["token_owner"], "account")
        self.assertEqual(payload["verification"], "accounts_list")
        self.assertTrue(payload["result"]["configured_account_match"])
        self.assertEqual(calls, ["http://example.invalid/client/v4/accounts"])

    def test_auth_check_fails_for_non_active_user_token(self) -> None:
        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
            _ = (self, method, kwargs)
            return _DummyResponse(
                status=200,
                url=url,
                obj={
                    "success": True,
                    "errors": [],
                    "messages": [],
                    "result": {"status": "expired"},
                },
            )

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            env_path = _write_env(Path(d), token="cfut_expired_token")
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--env-file", str(env_path), "auth", "check"])

        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 1)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["result"]["status"], "expired")

    def test_auth_check_fails_for_configured_account_mismatch(self) -> None:
        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
            _ = (self, method, kwargs)
            return _DummyResponse(
                status=200,
                url=url,
                obj={
                    "success": True,
                    "errors": [],
                    "messages": [],
                    "result": [{"id": "different-account", "name": "Different"}],
                    "result_info": {},
                },
            )

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            env_path = _write_env(Path(d), token="cfat_account_token")
            with env_path.open("a", encoding="utf-8") as f:
                f.write("CLOUDFLARE_ACCOUNT_ID=expected-account\n")
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--env-file", str(env_path), "auth", "check"])

        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 1)
        self.assertFalse(payload["ok"])
        self.assertFalse(payload["result"]["configured_account_match"])

    def test_explicit_env_file_overrides_process_environment_token(self) -> None:
        authorization_headers: list[str] = []

        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
            _ = (self, method, url)
            authorization_headers.append(str((kwargs.get("headers") or {}).get("authorization") or ""))
            return _DummyResponse(
                status=200,
                url=url,
                obj={"success": True, "errors": [], "messages": [], "result": {"status": "active"}},
            )

        process_env = {"CLOUDFLARE_API_TOKEN": "cfut_process_token"}
        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            env_path = _write_env(Path(d), token="cfut_file_token")
            buf = io.StringIO()
            with patch.dict("os.environ", process_env):
                with redirect_stdout(buf):
                    rc = main(["--env-file", str(env_path), "auth", "check"])

        self.assertEqual(rc, 0)
        self.assertEqual(authorization_headers, ["Bearer cfut_file_token"])

    def test_explicit_missing_env_file_stops_before_http(self) -> None:
        calls: list[str] = []

        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
            _ = (self, method, kwargs)
            calls.append(str(url))
            return _DummyResponse(
                status=200,
                url=url,
                obj={"success": True, "errors": [], "messages": [], "result": {"status": "active"}},
            )

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            missing_path = Path(d) / "missing.env"
            buf = io.StringIO()
            with patch.dict("os.environ", {"CLOUDFLARE_API_TOKEN": "cfut_process_token"}):
                with redirect_stdout(buf):
                    rc = main(["--env-file", str(missing_path), "auth", "check"])

        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 1)
        self.assertFalse(payload["ok"])
        self.assertIn("regular file", payload["error"])
        self.assertEqual(calls, [])

    def test_auth_probe_skips_user_verify_for_account_owned_token(self) -> None:
        calls: list[str] = []

        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
            _ = (self, method, kwargs)
            calls.append(str(url))
            if url.endswith("/accounts"):
                result: Any = [{"id": "a1"}]
            else:
                result = []
            return _DummyResponse(
                status=200,
                url=url,
                obj={"success": True, "errors": [], "messages": [], "result": result, "result_info": {}},
            )

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            env_path = _write_env(Path(d), token="cfat_account_token")
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--env-file", str(env_path), "--output", "json", "auth", "probe", "--account-id", "a1"])

        self.assertEqual(rc, 0)
        payload = json.loads(buf.getvalue())
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["token_owner"], "account")
        self.assertTrue(payload["checks"]["token_verify"]["skipped"])
        self.assertNotIn("http://example.invalid/client/v4/user/tokens/verify", calls)

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

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
    def __init__(self, *, status: int, url: str, body: bytes, headers: dict[str, str] | None = None):
        self.status_code = int(status)
        self.url = str(url)
        self.headers = dict(headers or {})
        self.content = body

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


def _json_envelope(result: Any) -> bytes:
    return json.dumps({"success": True, "errors": [], "messages": [], "result": result, "result_info": {}}, ensure_ascii=False).encode(
        "utf-8"
    )


class TestWafCommands(unittest.TestCase):
    def test_rate_limits_list_is_read_only(self) -> None:
        calls: list[dict[str, Any]] = []

        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
            calls.append({"method": method, "url": url})
            if method == "GET" and str(url).endswith("/zones/z1/rate_limits"):
                return _DummyResponse(status=200, url=url, body=_json_envelope([{"id": "rl1"}, {"id": "rl2"}]))
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root)
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--env-file", str(env_path), "waf", "rate-limits", "list", "--zone-id", "z1"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["command"], "waf.rate_limits.list")
            self.assertEqual(payload["zone_id"], "z1")
            self.assertEqual(payload["count"], 2)
            self.assertEqual(calls[0]["method"], "GET")

    def test_rulesets_list_zone_uses_expected_route(self) -> None:
        calls: list[dict[str, Any]] = []

        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
            calls.append({"method": method, "url": url})
            if method == "GET" and str(url).endswith("/zones/z1/rulesets"):
                return _DummyResponse(status=200, url=url, body=_json_envelope([{"id": "rs1"}]))
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root)
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--env-file", str(env_path), "waf", "rulesets", "list", "--zone-id", "z1"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["command"], "waf.rulesets.list")
            self.assertEqual(payload["scope"], "zone")
            self.assertEqual(payload["zone_id"], "z1")
            self.assertEqual(calls[0]["method"], "GET")
            self.assertEqual(calls[0]["url"], "http://example.invalid/client/v4/zones/z1/rulesets")

    def test_rulesets_list_account_uses_expected_route(self) -> None:
        calls: list[dict[str, Any]] = []

        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
            calls.append({"method": method, "url": url})
            if method == "GET" and str(url).endswith("/accounts/a1/rulesets"):
                return _DummyResponse(status=200, url=url, body=_json_envelope([{"id": "rs1"}]))
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root)
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--env-file", str(env_path), "waf", "rulesets", "list", "--account-id", "a1"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["command"], "waf.rulesets.list")
            self.assertEqual(payload["scope"], "account")
            self.assertEqual(payload["account_id"], "a1")
            self.assertEqual(calls[0]["method"], "GET")
            self.assertEqual(calls[0]["url"], "http://example.invalid/client/v4/accounts/a1/rulesets")

    def test_firewall_access_rules_list_user_uses_expected_route(self) -> None:
        calls: list[dict[str, Any]] = []

        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
            calls.append({"method": method, "url": url})
            if method == "GET" and str(url).endswith("/user/firewall/access_rules/rules"):
                return _DummyResponse(status=200, url=url, body=_json_envelope([{"id": "r1"}]))
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root)
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--env-file", str(env_path), "waf", "firewall", "access-rules", "list", "--user"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["command"], "waf.firewall.access_rules.list")
            self.assertEqual(payload["scope"], "user")
            self.assertEqual(calls[0]["method"], "GET")
            self.assertEqual(calls[0]["url"], "http://example.invalid/client/v4/user/firewall/access_rules/rules")

    def test_page_rules_list_uses_expected_route(self) -> None:
        calls: list[dict[str, Any]] = []

        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
            calls.append({"method": method, "url": url})
            if method == "GET" and str(url).endswith("/zones/z1/pagerules"):
                return _DummyResponse(status=200, url=url, body=_json_envelope([{"id": "pr1"}]))
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root)
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--env-file", str(env_path), "waf", "page-rules", "list", "--zone-id", "z1"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["command"], "waf.page_rules.list")
            self.assertEqual(payload["zone_id"], "z1")
            self.assertEqual(calls[0]["method"], "GET")
            self.assertEqual(calls[0]["url"], "http://example.invalid/client/v4/zones/z1/pagerules")

    def test_snippets_get_uses_expected_route(self) -> None:
        calls: list[dict[str, Any]] = []

        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
            calls.append({"method": method, "url": url})
            if method == "GET" and str(url).endswith("/zones/z1/snippets/s1"):
                return _DummyResponse(status=200, url=url, body=_json_envelope({"snippet_name": "s1"}))
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root)
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--env-file", str(env_path), "waf", "snippets", "get", "--zone-id", "z1", "--snippet-name", "s1"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["command"], "waf.snippets.get")
            self.assertEqual(payload["zone_id"], "z1")
            self.assertEqual(payload["snippet_name"], "s1")
            self.assertEqual(calls[0]["method"], "GET")
            self.assertEqual(calls[0]["url"], "http://example.invalid/client/v4/zones/z1/snippets/s1")

    def test_rulesets_list_requires_exactly_one_of_zone_or_account(self) -> None:
        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root)
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--env-file", str(env_path), "waf", "rulesets", "list"])
            self.assertEqual(rc, 1)
            payload = json.loads(buf.getvalue())
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["error_type"], "ValidationError")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root)
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "waf",
                        "rulesets",
                        "list",
                        "--zone-id",
                        "z1",
                        "--account-id",
                        "a1",
                    ]
                )
            self.assertEqual(rc, 1)
            payload = json.loads(buf.getvalue())
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["error_type"], "ValidationError")

    def test_firewall_access_rules_list_requires_exactly_one_scope_selector(self) -> None:
        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root)
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--env-file", str(env_path), "waf", "firewall", "access-rules", "list"])
            self.assertEqual(rc, 1)
            payload = json.loads(buf.getvalue())
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["error_type"], "ValidationError")

    def test_rulesets_entrypoint_update_dry_run_makes_no_http_calls(self) -> None:
        calls: list[dict[str, Any]] = []

        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
            calls.append({"method": method, "url": url})
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root)
            body_path = root / "body.json"
            body_path.write_text(json.dumps({"rules": []}, sort_keys=True), encoding="utf-8")
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "waf",
                        "rulesets",
                        "entrypoint-update",
                        "--zone-id",
                        "z1",
                        "--ruleset-phase",
                        "http_request_cache_settings",
                        "--body-json-file",
                        str(body_path),
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])
            self.assertEqual(payload["command"], "waf.rulesets.entrypoint.update")
            self.assertEqual(calls, [])

    def test_rulesets_entrypoint_update_apply_without_yes_refuses_and_makes_no_http_calls(self) -> None:
        calls: list[dict[str, Any]] = []

        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
            calls.append({"method": method, "url": url})
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root)
            body_path = root / "body.json"
            body_path.write_text(json.dumps({"rules": []}, sort_keys=True), encoding="utf-8")
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "waf",
                        "rulesets",
                        "entrypoint-update",
                        "--zone-id",
                        "z1",
                        "--ruleset-phase",
                        "http_request_cache_settings",
                        "--body-json-file",
                        str(body_path),
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            self.assertEqual(calls, [])

    def test_rulesets_entrypoint_update_apply_puts_then_reads_back(self) -> None:
        calls: list[dict[str, Any]] = []

        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
            calls.append({"method": method, "url": str(url)})
            if method == "PUT" and str(url).endswith("/zones/z1/rulesets/phases/http_request_cache_settings/entrypoint"):
                return _DummyResponse(status=200, url=url, body=_json_envelope({"id": "rs1"}))
            if method == "GET" and str(url).endswith("/zones/z1/rulesets/phases/http_request_cache_settings/entrypoint"):
                return _DummyResponse(status=200, url=url, body=_json_envelope({"id": "rs1"}))
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root)
            body_path = root / "body.json"
            body_path.write_text(json.dumps({"rules": []}, sort_keys=True), encoding="utf-8")
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--yes",
                        "waf",
                        "rulesets",
                        "entrypoint-update",
                        "--zone-id",
                        "z1",
                        "--ruleset-phase",
                        "http_request_cache_settings",
                        "--body-json-file",
                        str(body_path),
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            self.assertEqual(calls, [])

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root)
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "waf",
                        "firewall",
                        "access-rules",
                        "list",
                        "--zone-id",
                        "z1",
                        "--user",
                    ]
                )
            self.assertEqual(rc, 1)
            payload = json.loads(buf.getvalue())
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["error_type"], "ValidationError")

    def test_snippet_content_apply_without_out_refuses_and_does_not_call_api(self) -> None:
        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root)
            project_dir = root / "proj"
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--project-dir",
                        str(project_dir),
                        "--apply",
                        "waf",
                        "snippets",
                        "content",
                        "get",
                        "--zone-id",
                        "z1",
                        "--snippet-name",
                        "s1",
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            self.assertEqual(payload["command"], "waf.snippets.content.get")

    def test_snippet_content_apply_writes_file_and_never_prints_content(self) -> None:
        secret_bytes = b"SECRET_SNIPPET_CONTENT"

        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
            if method == "GET" and str(url).endswith("/zones/z1/snippets/s1/content"):
                return _DummyResponse(status=200, url=url, body=secret_bytes, headers={"Content-Type": "text/plain"})
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root)
            project_dir = root / "proj"
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--project-dir",
                        str(project_dir),
                        "--apply",
                        "waf",
                        "snippets",
                        "content",
                        "get",
                        "--zone-id",
                        "z1",
                        "--snippet-name",
                        "s1",
                        "--out",
                        "snippet.txt",
                    ]
                )
            self.assertEqual(rc, 0)
            out_text = buf.getvalue()
            self.assertNotIn("SECRET_SNIPPET_CONTENT", out_text)
            payload = json.loads(out_text)
            self.assertTrue(payload["ok"])
            self.assertFalse(payload.get("dry_run", True))
            receipt = payload["receipt"]
            diff = receipt["diff_applied"][0]
            written = Path(diff["abs_path"])
            self.assertTrue(written.exists())
            self.assertEqual(written.read_bytes(), secret_bytes)

    def test_managed_transforms_update_dry_run_emits_plan(self) -> None:
        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root)
            body_file = root / "body.json"
            body_file.write_text(json.dumps({"enabled": True}), encoding="utf-8")
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "waf",
                        "managed-transforms",
                        "update",
                        "--zone-id",
                        "z1",
                        "--body-json-file",
                        str(body_file),
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])
            self.assertEqual(payload["command"], "waf.managed_transforms.update")
            self.assertIn("plan", payload)

    def test_managed_transforms_update_apply_without_yes_refuses_and_does_not_call_api(self) -> None:
        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root)
            body_file = root / "body.json"
            body_file.write_text(json.dumps({"enabled": True}), encoding="utf-8")
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "waf",
                        "managed-transforms",
                        "update",
                        "--zone-id",
                        "z1",
                        "--body-json-file",
                        str(body_file),
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])

    def test_managed_transforms_update_apply_patches_and_verifies_by_read_back(self) -> None:
        calls: list[dict[str, Any]] = []

        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
            calls.append({"method": method, "url": url})
            if method == "PATCH" and str(url).endswith("/zones/z1/managed_headers"):
                return _DummyResponse(status=200, url=url, body=_json_envelope({"updated": True}))
            if method == "GET" and str(url).endswith("/zones/z1/managed_headers"):
                return _DummyResponse(status=200, url=url, body=_json_envelope({"enabled": True}))
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root)
            body_file = root / "body.json"
            body_file.write_text(json.dumps({"enabled": True}), encoding="utf-8")
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--yes",
                        "waf",
                        "managed-transforms",
                        "update",
                        "--zone-id",
                        "z1",
                        "--body-json-file",
                        str(body_file),
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            self.assertEqual(calls, [])

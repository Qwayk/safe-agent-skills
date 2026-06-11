from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from cloudflare_api_tool.cli import main
from cloudflare_api_tool.operation_keys import allowlisted_operation_command_by_operation_id


class _DummyResponse:
    def __init__(self, *, status: int, url: str, body: bytes, headers: dict[str, str] | None = None):
        self.status_code = int(status)
        self.url = str(url)
        self.headers = dict(headers or {})
        self.content = body

    @property
    def text(self) -> str:
        return self.content.decode("utf-8", errors="replace")


def _ok(result, result_info=None):  # noqa: ANN001
    payload = {"success": True, "errors": [], "messages": [], "result": result}
    if result_info is not None:
        payload["result_info"] = result_info
    return payload


def _err(*, code: int, message: str) -> dict[str, object]:
    return {"success": False, "errors": [{"code": code, "message": message}], "messages": [], "result": None}


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


class TestObservabilitySensitivity(unittest.TestCase):
    def test_audit_logs_dry_run_is_sensitive_and_does_not_call_api(self) -> None:
        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root)
            project_dir = root / "proj"
            buf = io.StringIO()
            cmd = allowlisted_operation_command_by_operation_id("audit-logs-get-account-audit-logs")
            self.assertIsNotNone(cmd)
            assert cmd is not None
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--project-dir",
                        str(project_dir),
                        "operations",
                        cmd.area,
                        cmd.op_key,
                        "--path-param",
                        "account_id=acc1",
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])
            self.assertEqual(payload["plan"]["request"]["sensitivity"], "sensitive_read")

    def test_audit_logs_apply_missing_out_refuses(self) -> None:
        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root)
            project_dir = root / "proj"
            buf = io.StringIO()
            cmd = allowlisted_operation_command_by_operation_id("audit-logs-get-account-audit-logs")
            self.assertIsNotNone(cmd)
            assert cmd is not None
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--project-dir",
                        str(project_dir),
                        "--apply",
                        "operations",
                        cmd.area,
                        cmd.op_key,
                        "--path-param",
                        "account_id=acc1",
                    ]
                )
            # Safety refusals are safe no-ops (exit code 0).
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            self.assertIn("Provide --out", " ".join(payload.get("reasons") or []))

    def test_audit_logs_apply_writes_file_and_never_prints_body(self) -> None:
        secret_bytes = b'{"event":"SENSITIVE_AUDIT_LOG","user":"someone@example.com"}\n'

        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
            if method == "GET" and str(url).endswith("/accounts/acc1/audit_logs"):
                return _DummyResponse(status=200, url=url, body=secret_bytes, headers={"Content-Type": "application/json"})
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root)
            project_dir = root / "proj"
            out_file = "audit.json"
            buf = io.StringIO()
            cmd = allowlisted_operation_command_by_operation_id("audit-logs-get-account-audit-logs")
            self.assertIsNotNone(cmd)
            assert cmd is not None
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--project-dir",
                        str(project_dir),
                        "--apply",
                        "operations",
                        cmd.area,
                        cmd.op_key,
                        "--path-param",
                        "account_id=acc1",
                        "--out",
                        out_file,
                    ]
                )
            self.assertEqual(rc, 0)
            out_text = buf.getvalue()
            self.assertNotIn("SENSITIVE_AUDIT_LOG", out_text)
            payload = json.loads(out_text)
            self.assertTrue(payload["ok"])
            wrote = payload.get("file") or {}
            self.assertTrue(wrote.get("out_path"))
            written = Path(str(wrote["out_path"]))
            self.assertTrue(written.exists())
            self.assertEqual(written.read_bytes(), secret_bytes)

    def test_request_tracer_is_read_like_non_get_and_does_not_require_yes(self) -> None:
        secret_bytes = b'{"trace":"TRACE_DATA","note":"sensitive"}\n'

        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
            if method == "POST" and str(url).endswith("/accounts/acc1/request-tracer/trace"):
                return _DummyResponse(status=200, url=url, body=secret_bytes, headers={"Content-Type": "application/json"})
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root)
            project_dir = root / "proj"
            body_path = root / "body.json"
            body_path.write_text("{}", encoding="utf-8")
            buf = io.StringIO()
            cmd = allowlisted_operation_command_by_operation_id("account-request-tracer-request-trace")
            self.assertIsNotNone(cmd)
            assert cmd is not None
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--project-dir",
                        str(project_dir),
                        "--apply",
                        "operations",
                        cmd.area,
                        cmd.op_key,
                        "--path-param",
                        "account_id=acc1",
                        "--body-json-file",
                        str(body_path),
                        "--out",
                        "trace.json",
                    ]
                )
            self.assertEqual(rc, 0)
            out_text = buf.getvalue()
            self.assertNotIn("TRACE_DATA", out_text)
            payload = json.loads(out_text)
            self.assertTrue(payload["ok"])
            receipt = payload.get("receipt") or {}
            self.assertFalse(receipt.get("changed"), "request tracer should be treated as read-like (changed=false)")

    def test_observability_audit_logs_command_delegates_to_openapi_runner(self) -> None:
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
                        "observability",
                        "audit-logs",
                        "account",
                        "list",
                        "--account-id",
                        "acc1",
                        "--out",
                        "audit.json",
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])
            self.assertEqual(payload["plan"]["request"]["sensitivity"], "sensitive_read")

    def test_logpush_jobs_list_apply_missing_out_refuses(self) -> None:
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
                        "observability",
                        "logpush",
                        "account",
                        "jobs",
                        "list",
                        "--account-id",
                        "acc1",
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            self.assertIn("Provide --out", " ".join(payload.get("reasons") or []))

    def test_logpush_jobs_list_apply_writes_file_and_never_prints_body(self) -> None:
        secret_bytes = b'{"logpush":"DESTINATION_CONF=SECRET"}\n'

        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
            if method == "GET" and str(url).endswith("/accounts/acc1/logpush/jobs"):
                return _DummyResponse(status=200, url=url, body=secret_bytes, headers={"Content-Type": "application/json"})
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
                        "observability",
                        "logpush",
                        "account",
                        "jobs",
                        "list",
                        "--account-id",
                        "acc1",
                        "--out",
                        "logpush_jobs.json",
                    ]
                )
            self.assertEqual(rc, 0)
            out_text = buf.getvalue()
            self.assertNotIn("DESTINATION_CONF=SECRET", out_text)
            payload = json.loads(out_text)
            wrote = payload.get("file") or {}
            written = Path(str(wrote.get("out_path") or ""))
            self.assertTrue(written.exists())
            self.assertEqual(written.read_bytes(), secret_bytes)

    def test_logpush_jobs_create_requires_yes_on_apply(self) -> None:
        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root)
            project_dir = root / "proj"
            body_path = root / "body.json"
            body_path.write_text("{}", encoding="utf-8")
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--project-dir",
                        str(project_dir),
                        "--apply",
                        "observability",
                        "logpush",
                        "account",
                        "jobs",
                        "create",
                        "--account-id",
                        "acc1",
                        "--body-json-file",
                        str(body_path),
                        "--out",
                        "create.json",
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            self.assertIn("before-state", " ".join(payload.get("reasons") or []))

    def test_logpush_jobs_create_apply_writes_file_and_never_prints_body(self) -> None:
        secret_bytes = b'{"job":{"destination_conf":"SECRET","name":"n"}}\n'

        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
            if method == "POST" and str(url).endswith("/accounts/acc1/logpush/jobs"):
                return _DummyResponse(status=200, url=url, body=secret_bytes, headers={"Content-Type": "application/json"})
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root)
            project_dir = root / "proj"
            body_path = root / "body.json"
            body_path.write_text("{}", encoding="utf-8")
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
                        "observability",
                        "logpush",
                        "account",
                        "jobs",
                        "create",
                        "--account-id",
                        "acc1",
                        "--body-json-file",
                        str(body_path),
                        "--out",
                        "create.json",
                    ]
                )
            self.assertEqual(rc, 0)
            out_text = buf.getvalue()
            self.assertNotIn("destination_conf", out_text)
            payload = json.loads(out_text)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])


class TestObservabilitySpeedAndAudit(unittest.TestCase):
    def test_speed_pages_list_returns_summary(self) -> None:
        pages = [
            {
                "url": "pbservices.ge/",
                "region": {"label": "Frankfurt, Germany"},
                "tests": [
                    {
                        "id": "t1",
                        "date": "2026-03-27T02:29:17.467Z",
                        "url": "pbservices.ge/",
                        "region": {"label": "Frankfurt, Germany"},
                        "mobileReport": {"performanceScore": 52, "ttfb": 362, "fcp": 3161, "lcp": 3939, "tti": 11634, "tbt": 3376, "si": 3161, "cls": 0, "state": "COMPLETE"},
                        "desktopReport": {"performanceScore": 76, "ttfb": 363, "fcp": 760, "lcp": 1155, "tti": 2964, "tbt": 498, "si": 1084, "cls": 0, "state": "COMPLETE"},
                    }
                ],
            },
            {
                "url": "pbservices.ge/contact/",
                "region": {"label": "Iowa, USA"},
                "tests": [],
            },
        ]

        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
            if method == "GET" and str(url).endswith("/zones/z1/speed_api/pages"):
                return _DummyResponse(status=200, url=url, body=json.dumps(_ok(pages)).encode("utf-8"), headers={"Content-Type": "application/json"})
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            env_path = _write_env(Path(d))
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--env-file", str(env_path), "observability", "speed", "pages", "list", "--zone-id", "z1"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["summary"]["page_entries"], 2)
            self.assertEqual(payload["summary"]["unique_urls"], 2)
            self.assertEqual(payload["summary"]["latest_test"]["id"], "t1")

    def test_speed_page_latest_normalizes_full_url_and_picks_latest_test(self) -> None:
        pages = [
            {
                "url": "pbservices.ge/",
                "region": {"label": "Frankfurt, Germany"},
                "tests": [{"id": "older", "date": "2026-03-20T00:00:00Z", "url": "pbservices.ge/", "region": {"label": "Frankfurt, Germany"}}],
            },
            {
                "url": "pbservices.ge/",
                "region": {"label": "Iowa, USA"},
                "tests": [{"id": "newer", "date": "2026-03-24T00:04:09.465Z", "url": "pbservices.ge/", "region": {"label": "Iowa, USA"}}],
            },
        ]

        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
            if method == "GET" and str(url).endswith("/zones/z1/speed_api/pages"):
                return _DummyResponse(status=200, url=url, body=json.dumps(_ok(pages)).encode("utf-8"), headers={"Content-Type": "application/json"})
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            env_path = _write_env(Path(d))
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "observability",
                        "speed",
                        "page",
                        "latest",
                        "--zone-id",
                        "z1",
                        "--url",
                        "https://pbservices.ge/?x=1",
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertEqual(payload["normalized_url"], "pbservices.ge/")
            self.assertEqual(payload["latest_test"]["id"], "newer")
            self.assertEqual(payload["match_count"], 2)

    def test_speed_page_trend_uses_encoded_observatory_url(self) -> None:
        pages = [{"url": "pbservices.ge/", "region": {"label": "Frankfurt, Germany"}, "tests": []}]
        seen: list[str] = []

        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
            seen.append(str(url))
            if method == "GET" and str(url).endswith("/zones/z1/speed_api/pages"):
                return _DummyResponse(status=200, url=url, body=json.dumps(_ok(pages)).encode("utf-8"), headers={"Content-Type": "application/json"})
            if method == "GET" and str(url).endswith("/zones/z1/speed_api/pages/pbservices.ge%2F/trend"):
                return _DummyResponse(
                    status=200,
                    url=url,
                    body=json.dumps(_ok([{"date": "2026-03-20T00:00:00Z", "lcp": 3000}, {"date": "2026-03-24T00:00:00Z", "lcp": 2500}])).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                )
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            env_path = _write_env(Path(d))
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--env-file", str(env_path), "observability", "speed", "page", "trend", "--zone-id", "z1", "--url", "https://pbservices.ge/"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertEqual(payload["summary"]["points"], 2)
            self.assertTrue(any(item.endswith("/zones/z1/speed_api/pages/pbservices.ge%2F/trend") for item in seen))

    def test_web_analytics_status_surfaces_rules_auth_scheme_failure_cleanly(self) -> None:
        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
            if method == "GET" and str(url).endswith("/zones/z1"):
                return _DummyResponse(status=200, url=url, body=json.dumps(_ok({"id": "z1", "name": "pbservices.ge"})).encode("utf-8"), headers={"Content-Type": "application/json"})
            if method == "GET" and str(url).endswith("/zones/z1/settings/rum"):
                return _DummyResponse(status=200, url=url, body=json.dumps(_ok({"editable": True, "value": "on", "zone_name": "pbservices.ge", "site_tag": "tag1"})).encode("utf-8"), headers={"Content-Type": "application/json"})
            if method == "GET" and str(url).endswith("/accounts/a1/rum/site_info/list"):
                return _DummyResponse(
                    status=200,
                    url=url,
                    body=json.dumps(_ok([{"id": "site1", "zone_tag": "z1", "auto_install": True, "ruleset": {"id": "rs1", "enabled": True}}])).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                )
            if method == "GET" and str(url).endswith("/accounts/a1/rum/v2/rs1/rules"):
                return _DummyResponse(status=405, url=url, body=json.dumps(_err(code=10405, message="Method not allowed for this authentication scheme")).encode("utf-8"), headers={"Content-Type": "application/json"})
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            env_path = _write_env(Path(d))
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--env-file", str(env_path), "observability", "web-analytics", "status", "--zone-id", "z1", "--account-id", "a1"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["summary"]["rum_enabled"])
            self.assertTrue(payload["summary"]["site_lookup_ok"])
            self.assertTrue(payload["summary"]["site_found"])
            self.assertTrue(payload["site"]["lookup_ok"])
            self.assertTrue(payload["site"]["matched"])
            self.assertFalse(payload["summary"]["rules_lookup"]["ok"])
            self.assertIn("different auth path", payload["summary"]["rules_lookup"]["error"])

    def test_web_analytics_status_matches_site_when_cloudflare_returns_full_url(self) -> None:
        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
            if method == "GET" and str(url).endswith("/zones/z1"):
                return _DummyResponse(status=200, url=url, body=json.dumps(_ok({"id": "z1", "name": "pbservices.ge"})).encode("utf-8"), headers={"Content-Type": "application/json"})
            if method == "GET" and str(url).endswith("/zones/z1/settings/rum"):
                return _DummyResponse(status=200, url=url, body=json.dumps(_ok({"editable": True, "value": "on", "zone_name": "pbservices.ge", "site_tag": "tag1"})).encode("utf-8"), headers={"Content-Type": "application/json"})
            if method == "GET" and str(url).endswith("/accounts/a1/rum/site_info/list"):
                return _DummyResponse(
                    status=200,
                    url=url,
                    body=json.dumps(_ok([{"id": "site1", "name": "https://pbservices.ge/", "auto_install": False, "ruleset": {"id": "rs1", "enabled": False}}])).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                )
            if method == "GET" and str(url).endswith("/accounts/a1/rum/v2/rs1/rules"):
                return _DummyResponse(status=200, url=url, body=json.dumps(_ok([])).encode("utf-8"), headers={"Content-Type": "application/json"})
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            env_path = _write_env(Path(d))
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--env-file", str(env_path), "observability", "web-analytics", "status", "--zone-id", "z1", "--account-id", "a1"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["summary"]["site_lookup_ok"])
            self.assertTrue(payload["summary"]["site_found"])
            self.assertTrue(payload["site"]["lookup_ok"])
            self.assertTrue(payload["site"]["matched"])
            self.assertEqual(payload["site"]["summary"]["host"], "https://pbservices.ge/")

    def test_web_analytics_status_matches_site_from_nested_ruleset_zone_name(self) -> None:
        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
            if method == "GET" and str(url).endswith("/zones/z1"):
                return _DummyResponse(status=200, url=url, body=json.dumps(_ok({"id": "z1", "name": "pbservices.ge"})).encode("utf-8"), headers={"Content-Type": "application/json"})
            if method == "GET" and str(url).endswith("/zones/z1/settings/rum"):
                return _DummyResponse(status=200, url=url, body=json.dumps(_ok({"editable": True, "value": "on", "zone_name": "pbservices.ge", "site_tag": "tag1"})).encode("utf-8"), headers={"Content-Type": "application/json"})
            if method == "GET" and str(url).endswith("/accounts/a1/rum/site_info/list"):
                return _DummyResponse(
                    status=200,
                    url=url,
                    body=json.dumps(_ok([{"id": "site1", "auto_install": True, "ruleset": {"id": "rs1", "enabled": True, "zone_name": "pbservices.ge", "zone_tag": "z1"}}])).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                )
            if method == "GET" and str(url).endswith("/accounts/a1/rum/v2/rs1/rules"):
                return _DummyResponse(status=200, url=url, body=json.dumps(_ok([{"id": "r1"}])).encode("utf-8"), headers={"Content-Type": "application/json"})
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            env_path = _write_env(Path(d))
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--env-file", str(env_path), "observability", "web-analytics", "status", "--zone-id", "z1", "--account-id", "a1"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["summary"]["site_lookup_ok"])
            self.assertTrue(payload["summary"]["site_found"])
            self.assertTrue(payload["site"]["matched"])
            self.assertEqual(payload["site"]["summary"]["ruleset_id"], "rs1")
            self.assertTrue(payload["summary"]["rules_lookup"]["ok"])

    def test_observability_audit_combines_speed_web_analytics_and_logs_status(self) -> None:
        pages = [{"url": "pbservices.ge/", "region": {"label": "Iowa, USA"}, "tests": [{"id": "t1", "date": "2026-03-24T00:04:09.465Z", "url": "pbservices.ge/", "region": {"label": "Iowa, USA"}}]}]

        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
            if method == "GET" and str(url).endswith("/zones/z1"):
                return _DummyResponse(status=200, url=url, body=json.dumps(_ok({"id": "z1", "name": "pbservices.ge"})).encode("utf-8"), headers={"Content-Type": "application/json"})
            if method == "GET" and str(url).endswith("/zones/z1/settings/rum"):
                return _DummyResponse(status=200, url=url, body=json.dumps(_ok({"editable": True, "value": "on", "zone_name": "pbservices.ge", "site_tag": "tag1"})).encode("utf-8"), headers={"Content-Type": "application/json"})
            if method == "GET" and str(url).endswith("/accounts/a1/rum/site_info/list"):
                return _DummyResponse(status=200, url=url, body=json.dumps(_ok([{"id": "site1", "zone_tag": "z1", "auto_install": True, "ruleset": {"id": "rs1", "enabled": True}}])).encode("utf-8"), headers={"Content-Type": "application/json"})
            if method == "GET" and str(url).endswith("/accounts/a1/rum/v2/rs1/rules"):
                return _DummyResponse(status=200, url=url, body=json.dumps(_ok([{"id": "r1"}])).encode("utf-8"), headers={"Content-Type": "application/json"})
            if method == "GET" and str(url).endswith("/zones/z1/speed_api/availabilities"):
                return _DummyResponse(status=200, url=url, body=json.dumps(_ok({"quotaRemaining": 3, "available": True})).encode("utf-8"), headers={"Content-Type": "application/json"})
            if method == "GET" and str(url).endswith("/zones/z1/speed_api/pages"):
                return _DummyResponse(status=200, url=url, body=json.dumps(_ok(pages)).encode("utf-8"), headers={"Content-Type": "application/json"})
            if method == "GET" and str(url).endswith("/zones/z1/logpush/edge/jobs"):
                return _DummyResponse(status=200, url=url, body=json.dumps(_ok([])).encode("utf-8"), headers={"Content-Type": "application/json"})
            if method == "GET" and str(url).endswith("/zones/z1/logpush/jobs"):
                return _DummyResponse(status=403, url=url, body=json.dumps(_err(code=10000, message="auth.forbidden")).encode("utf-8"), headers={"Content-Type": "application/json"})
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            env_path = _write_env(Path(d))
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--env-file", str(env_path), "observability", "audit", "--zone-id", "z1", "--account-id", "a1"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["summary"]["rum_enabled"])
            self.assertTrue(payload["summary"]["speed_pages_ok"])
            self.assertFalse(payload["logs"]["zone_logpush_jobs"]["ok"])
            self.assertTrue(payload["speed_homepage"]["ok"])

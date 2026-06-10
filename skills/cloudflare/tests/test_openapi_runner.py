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
from cloudflare_api_tool.operation_keys import (
    allowlisted_operation_command_by_method_path,
    allowlisted_operation_command_by_operation_id,
)
from cloudflare_api_tool.openapi_index import is_read_like_non_get_operation, load_allowlisted_operation_index


class _DummyResponse:
    def __init__(self, *, status: int, url: str, obj: Any | None, body: bytes | None = None):
        self.status_code = int(status)
        self.url = str(url)
        if body is not None:
            self.content = body
        else:
            self.content = (json.dumps(obj, ensure_ascii=False) if obj is not None else "").encode("utf-8")
        self.headers: dict[str, str] = {}


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


def _ops_argv_for_operation_id(operation_id: str) -> list[str]:
    c = allowlisted_operation_command_by_operation_id(operation_id)
    if not c:
        raise AssertionError(f"Operation not found in allowlist: {operation_id}")
    return ["operations", c.area, c.op_key]


def _ops_argv_for_method_path(*, method: str, path_template: str) -> list[str]:
    c = allowlisted_operation_command_by_method_path(method=method, path_template=path_template)
    if not c:
        raise AssertionError(f"Operation not found in allowlist: {method} {path_template}")
    return ["operations", c.area, c.op_key]


class TestOperationsCommands(unittest.TestCase):
    def test_operations_list_returns_results(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = _write_env(Path(d))
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--env-file", str(env_path), "operations", "list", "--contains", "workers/scripts", "--limit", "5", "--include-sensitive"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertGreaterEqual(payload["count"], 1)

    def test_operations_list_includes_waiting_room_endpoints(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = _write_env(Path(d))
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "operations",
                        "list",
                        "--contains",
                        "waiting_rooms",
                        "--limit",
                        "50",
                        "--include-sensitive",
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertGreaterEqual(payload["count"], 1)
            operation_ids = [o.get("operation_id") for o in payload.get("operations") or []]
            self.assertIn("waiting-room-list-waiting-rooms-account", operation_ids)
            self.assertIn("waiting-room-list-waiting-rooms", operation_ids)

    def test_allowlist_includes_pages_projects(self) -> None:
        idx = load_allowlisted_operation_index()
        spec = idx.get("pages-project-get-projects")
        self.assertIsNotNone(spec)

    def test_allowlist_includes_images_operations(self) -> None:
        idx = load_allowlisted_operation_index()
        self.assertIsNotNone(idx.get("cloudflare-images-list-images"))
        self.assertIsNotNone(idx.get("cloudflare-images-variants-list-variants"))

    def test_allowlist_includes_ai_gateway_operation_ids(self) -> None:
        idx = load_allowlisted_operation_index()
        for op_id in [
            "aig-config-list-gateway",
            "aig-config-list-gateway-dynamic-routes",
            "aig-config-list-gateway-logs",
            "aig-config-list-dataset",
            "aig-config-list-providers",
            "aig-config-create-providers",
        ]:
            self.assertIsNotNone(idx.get(op_id), f"missing AI Gateway opId in allowlist: {op_id}")

    def test_allowlist_includes_vectorize_operation_ids(self) -> None:
        idx = load_allowlisted_operation_index()
        for op_id in [
            "vectorize-list-vectorize-indexes",
            "vectorize-query-vector",
            "vectorize-upsert-vector",
        ]:
            self.assertIsNotNone(idx.get(op_id), f"missing Vectorize opId in allowlist: {op_id}")

    def test_allowlist_includes_autorag_operation_ids(self) -> None:
        idx = load_allowlisted_operation_index()
        for op_id in [
            "autorag-config-ai-search",
            "autorag-config-search",
            "autorag-config-sync",
            "autorag-config-files",
            "autorag-config-list-jobs",
            "autorag-config-get-job",
            "autorag-config-list-job-logs",
        ]:
            self.assertIsNotNone(idx.get(op_id), f"missing AutoRAG opId in allowlist: {op_id}")

    def test_allowlist_includes_ai_search_operation_ids(self) -> None:
        idx = load_allowlisted_operation_index()
        for op_id in [
            # Instances
            "ai-search-list-instances",
            # Jobs/logs
            "ai-search-instance-list-job-logs",
            # Tokens
            "ai-search-create-tokens",
            "ai-search-update-tokens",
            # Search/chat (read-like POSTs)
            "ai-search-instance-search",
        ]:
            self.assertIsNotNone(idx.get(op_id), f"missing AI Search opId in allowlist: {op_id}")

    def test_allowlist_includes_workers_ai_operation_ids(self) -> None:
        idx = load_allowlisted_operation_index()
        for op_id in [
            "workers-ai-search-model",
            "workers-ai-create-finetune",
            "workers-ai-post-run-model",
        ]:
            self.assertIsNotNone(idx.get(op_id), f"missing Workers AI opId in allowlist: {op_id}")

    def test_allowlist_includes_email_security_operation_ids(self) -> None:
        idx = load_allowlisted_operation_index()
        for op_id in [
            "email_security_investigate",
            "email_security_list_allow_policies",
            "dlp-email-scanner-list-all-rules",
            "radar-get-email-security-summary",
        ]:
            self.assertIsNotNone(idx.get(op_id), f"missing Email Security opId in allowlist: {op_id}")

    def test_allowlist_includes_radar_http_and_dns_operation_ids(self) -> None:
        idx = load_allowlisted_operation_index()
        for op_id in [
            # Radar HTTP (Phase 17)
            "radar-get-http-summary",
            "radar-get-http-timeseries",
            "radar-get-http-top-locations-by-http-requests",
            # Radar DNS (Phase 17)
            "radar-get-dns-summary",
            "radar-get-dns-timeseries",
            "radar-get-dns-top-locations",
        ]:
            self.assertIsNotNone(idx.get(op_id), f"missing Radar HTTP/DNS opId in allowlist: {op_id}")

    def test_allowlist_marks_email_security_endpoints_as_sensitive_read(self) -> None:
        idx = load_allowlisted_operation_index()

        spec_investigate = idx.get_by_method_path(method="GET", path_template="/accounts/{account_id}/email-security/investigate")
        self.assertIsNotNone(spec_investigate)
        assert spec_investigate is not None
        self.assertEqual(spec_investigate.sensitivity, "sensitive_read")

        spec_settings = idx.get_by_method_path(
            method="GET", path_template="/accounts/{account_id}/email-security/settings/allow_policies"
        )
        self.assertIsNotNone(spec_settings)
        assert spec_settings is not None
        self.assertEqual(spec_settings.sensitivity, "sensitive_read")

        spec_dlp = idx.get_by_method_path(method="GET", path_template="/accounts/{account_id}/dlp/email/rules")
        self.assertIsNotNone(spec_dlp)
        assert spec_dlp is not None
        self.assertEqual(spec_dlp.sensitivity, "sensitive_read")

        spec_radar = idx.get_by_method_path(method="GET", path_template="/radar/email/security/summary/{dimension}")
        self.assertIsNotNone(spec_radar)
        assert spec_radar is not None
        self.assertEqual(spec_radar.sensitivity, "sensitive_read")

    def test_allowlist_marks_radar_http_and_dns_endpoints_as_sensitive_read(self) -> None:
        idx = load_allowlisted_operation_index()

        spec_http = idx.get_by_method_path(method="GET", path_template="/radar/http/summary/{dimension}")
        self.assertIsNotNone(spec_http)
        assert spec_http is not None
        self.assertEqual(spec_http.sensitivity, "sensitive_read")

        spec_dns = idx.get_by_method_path(method="GET", path_template="/radar/dns/summary/{dimension}")
        self.assertIsNotNone(spec_dns)
        assert spec_dns is not None
        self.assertEqual(spec_dns.sensitivity, "sensitive_read")

    def test_operations_list_hides_ai_gateway_logs_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = _write_env(Path(d))

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "operations", "list",
                        "--contains",
                        "/ai-gateway/gateways/{gateway_id}/logs",
                        "--limit",
                        "50",
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["count"], 0)

            buf2 = io.StringIO()
            with redirect_stdout(buf2):
                rc2 = main(
                    [
                        "--env-file",
                        str(env_path),
                        "operations", "list",
                        "--contains",
                        "/ai-gateway/gateways/{gateway_id}/logs",
                        "--limit",
                        "50",
                        "--include-sensitive",
                    ]
                )
            self.assertEqual(rc2, 0)
            payload2 = json.loads(buf2.getvalue())
            self.assertTrue(payload2["ok"])
            self.assertGreaterEqual(payload2["count"], 1)

    def test_operations_list_hides_radar_http_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = _write_env(Path(d))

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--env-file", str(env_path), "operations", "list", "--contains", "/radar/http/", "--limit", "50"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["count"], 0)

            buf2 = io.StringIO()
            with redirect_stdout(buf2):
                rc2 = main(
                    [
                        "--env-file",
                        str(env_path),
                        "operations", "list",
                        "--contains",
                        "/radar/http/",
                        "--limit",
                        "50",
                        "--include-sensitive",
                    ]
                )
            self.assertEqual(rc2, 0)
            payload2 = json.loads(buf2.getvalue())
            self.assertTrue(payload2["ok"])
            self.assertGreaterEqual(payload2["count"], 1)

    def test_operations_list_hides_radar_dns_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = _write_env(Path(d))

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--env-file", str(env_path), "operations", "list", "--contains", "/radar/dns/", "--limit", "50"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["count"], 0)

            buf2 = io.StringIO()
            with redirect_stdout(buf2):
                rc2 = main(
                    [
                        "--env-file",
                        str(env_path),
                        "operations", "list",
                        "--contains",
                        "/radar/dns/",
                        "--limit",
                        "50",
                        "--include-sensitive",
                    ]
                )
            self.assertEqual(rc2, 0)
            payload2 = json.loads(buf2.getvalue())
            self.assertTrue(payload2["ok"])
            self.assertGreaterEqual(payload2["count"], 1)

    def test_operations_list_hides_vectorize_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = _write_env(Path(d))

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--env-file", str(env_path), "operations", "list", "--contains", "vectorize", "--limit", "50"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["count"], 0)

            buf2 = io.StringIO()
            with redirect_stdout(buf2):
                rc2 = main(
                    [
                        "--env-file",
                        str(env_path),
                        "operations", "list",
                        "--contains",
                        "vectorize",
                        "--limit",
                        "50",
                        "--include-sensitive",
                    ]
                )
            self.assertEqual(rc2, 0)
            payload2 = json.loads(buf2.getvalue())
            self.assertTrue(payload2["ok"])
            self.assertGreaterEqual(payload2["count"], 1)

    def test_operations_list_hides_autorag_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = _write_env(Path(d))

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--env-file", str(env_path), "operations", "list", "--contains", "autorag", "--limit", "50"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["count"], 0)

            buf2 = io.StringIO()
            with redirect_stdout(buf2):
                rc2 = main(
                    [
                        "--env-file",
                        str(env_path),
                        "operations", "list",
                        "--contains",
                        "autorag",
                        "--limit",
                        "50",
                        "--include-sensitive",
                    ]
                )
            self.assertEqual(rc2, 0)
            payload2 = json.loads(buf2.getvalue())
            self.assertTrue(payload2["ok"])
            self.assertGreaterEqual(payload2["count"], 7)

    def test_operations_list_hides_ai_search_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = _write_env(Path(d))

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--env-file", str(env_path), "operations", "list", "--contains", "ai-search", "--limit", "50"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["count"], 0)

            buf2 = io.StringIO()
            with redirect_stdout(buf2):
                rc2 = main(
                    [
                        "--env-file",
                        str(env_path),
                        "operations", "list",
                        "--contains",
                        "ai-search",
                        "--limit",
                        "50",
                        "--include-sensitive",
                    ]
                )
            self.assertEqual(rc2, 0)
            payload2 = json.loads(buf2.getvalue())
            self.assertTrue(payload2["ok"])
            self.assertGreaterEqual(payload2["count"], 1)

    def test_operations_list_hides_workers_ai_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = _write_env(Path(d))

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--env-file", str(env_path), "operations", "list", "--contains", "workers-ai", "--limit", "50"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["count"], 0)

            buf2 = io.StringIO()
            with redirect_stdout(buf2):
                rc2 = main(
                    [
                        "--env-file",
                        str(env_path),
                        "operations", "list",
                        "--contains",
                        "workers-ai",
                        "--limit",
                        "50",
                        "--include-sensitive",
                    ]
                )
            self.assertEqual(rc2, 0)
            payload2 = json.loads(buf2.getvalue())
            self.assertTrue(payload2["ok"])
            self.assertGreaterEqual(payload2["count"], 1)

    def test_operations_list_hides_email_security_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = _write_env(Path(d))

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--env-file", str(env_path), "operations", "list", "--contains", "email-security", "--limit", "50"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["count"], 0)

            buf2 = io.StringIO()
            with redirect_stdout(buf2):
                rc2 = main(
                    [
                        "--env-file",
                        str(env_path),
                        "operations", "list",
                        "--contains",
                        "email-security",
                        "--limit",
                        "50",
                        "--include-sensitive",
                    ]
                )
            self.assertEqual(rc2, 0)
            payload2 = json.loads(buf2.getvalue())
            self.assertTrue(payload2["ok"])
            self.assertGreaterEqual(payload2["count"], 1)

    def test_operations_call_ai_gateway_logs_is_sensitive_read_in_plan(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = _write_env(Path(d))
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        *_ops_argv_for_operation_id("aig-config-list-gateway-logs"),
                        "--path-param",
                        "account_id=acc1",
                        "--path-param",
                        "gateway_id=gw1",
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])
            self.assertEqual(payload["plan"]["request"]["sensitivity"], "sensitive_read")

    def test_operations_call_email_security_investigate_is_sensitive_read_in_plan(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = _write_env(Path(d))
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        *_ops_argv_for_operation_id("email_security_investigate"),
                        "--path-param",
                        "account_id=acc1",
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])
            self.assertEqual(payload["plan"]["request"]["sensitivity"], "sensitive_read")

    def test_allowlist_marks_autorag_endpoints_as_sensitive_read(self) -> None:
        idx = load_allowlisted_operation_index()
        for method, path in [
            ("POST", "/accounts/{account_id}/autorag/rags/{id}/ai-search"),
            ("POST", "/accounts/{account_id}/autorag/rags/{id}/search"),
            ("PATCH", "/accounts/{account_id}/autorag/rags/{id}/sync"),
            ("GET", "/accounts/{account_id}/autorag/rags/{id}/files"),
            ("GET", "/accounts/{account_id}/autorag/rags/{id}/jobs"),
            ("GET", "/accounts/{account_id}/autorag/rags/{id}/jobs/{job_id}"),
            ("GET", "/accounts/{account_id}/autorag/rags/{id}/jobs/{job_id}/logs"),
        ]:
            spec = idx.get_by_method_path(method=method, path_template=path)
            self.assertIsNotNone(spec)
            assert spec is not None
            self.assertEqual(spec.sensitivity, "sensitive_read")

    def test_allowlist_marks_ai_search_endpoints_as_sensitive(self) -> None:
        idx = load_allowlisted_operation_index()

        spec_list = idx.get_by_method_path(method="GET", path_template="/accounts/{account_id}/ai-search/instances")
        self.assertIsNotNone(spec_list)
        assert spec_list is not None
        self.assertEqual(spec_list.sensitivity, "sensitive_read")

        spec_search = idx.get_by_method_path(method="POST", path_template="/accounts/{account_id}/ai-search/instances/{id}/search")
        self.assertIsNotNone(spec_search)
        assert spec_search is not None
        self.assertEqual(spec_search.sensitivity, "sensitive_read")

        spec_token_create = idx.get_by_method_path(method="POST", path_template="/accounts/{account_id}/ai-search/tokens")
        self.assertIsNotNone(spec_token_create)
        assert spec_token_create is not None
        self.assertEqual(spec_token_create.sensitivity, "sensitive_write_result")

        spec_namespace_search = idx.get_by_method_path(
            method="POST",
            path_template="/accounts/{account_id}/ai-search/namespaces/{name}/search",
        )
        self.assertIsNotNone(spec_namespace_search)
        assert spec_namespace_search is not None
        self.assertEqual(spec_namespace_search.sensitivity, "sensitive_read")

        spec_namespace_chat = idx.get_by_method_path(
            method="POST",
            path_template="/accounts/{account_id}/ai-search/namespaces/{name}/chat/completions",
        )
        self.assertIsNotNone(spec_namespace_chat)
        assert spec_namespace_chat is not None
        self.assertEqual(spec_namespace_chat.sensitivity, "sensitive_read")

    def test_namespaced_ai_search_search_and_chat_are_read_like_posts(self) -> None:
        idx = load_allowlisted_operation_index()
        for path in [
            "/accounts/{account_id}/ai-search/namespaces/{name}/search",
            "/accounts/{account_id}/ai-search/namespaces/{name}/chat/completions",
            "/accounts/{account_id}/ai-search/namespaces/{name}/instances/{id}/search",
            "/accounts/{account_id}/ai-search/namespaces/{name}/instances/{id}/chat/completions",
        ]:
            spec = idx.get_by_method_path(method="POST", path_template=path)
            self.assertIsNotNone(spec, msg=f"missing allowlist op: POST {path}")
            assert spec is not None
            self.assertTrue(is_read_like_non_get_operation(spec), msg=f"expected read-like POST: {path}")

    def test_allowlist_marks_live_browser_rendering_and_custom_pages_as_sensitive_reads(self) -> None:
        idx = load_allowlisted_operation_index()
        for method, path in [
            ("GET", "/accounts/{account_id}/browser-rendering/devtools/browser"),
            ("POST", "/accounts/{account_id}/browser-rendering/devtools/browser"),
            ("GET", "/accounts/{account_id}/custom_pages/assets"),
            ("PUT", "/zones/{zone_id}/custom_pages/{identifier}"),
        ]:
            spec = idx.get_by_method_path(method=method, path_template=path)
            self.assertIsNotNone(spec, msg=f"missing allowlist op: {method} {path}")
            assert spec is not None
            self.assertEqual(spec.sensitivity, "sensitive_read", msg=f"unexpected sensitivity for {method} {path}")

    def test_allowlist_marks_workers_ai_endpoints_as_sensitive_read(self) -> None:
        idx = load_allowlisted_operation_index()
        for method, path in [
            ("GET", "/accounts/{account_id}/ai/models/search"),
            ("POST", "/accounts/{account_id}/ai/finetunes"),
            ("POST", "/accounts/{account_id}/ai/run/{model_name}"),
        ]:
            spec = idx.get_by_method_path(method=method, path_template=path)
            self.assertIsNotNone(spec)
            assert spec is not None
            self.assertEqual(spec.sensitivity, "sensitive_read")

    def test_operations_call_vectorize_query_is_sensitive_read_in_plan(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = _write_env(root)
            body = root / "body.json"
            body.write_text('{"vector":[0.1,0.2,0.3],"topK":3}\n', encoding="utf-8")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        *_ops_argv_for_operation_id("vectorize-query-vector"),
                        "--path-param",
                        "account_id=acc1",
                        "--path-param",
                        "index_name=idx1",
                        "--body-json-file",
                        str(body),
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])
            self.assertEqual(payload["plan"]["request"]["sensitivity"], "sensitive_read")

    def test_operations_call_ai_gateway_provider_config_write_is_sensitive_write_result_in_plan(self) -> None:
        def fake_request(_session, method, url, **kwargs):  # noqa: ANN001
            if method == "GET" and str(url).endswith("/accounts/acc1/ai-gateway/gateways/gw1/provider_configs"):
                return _DummyResponse(status=200, url=url, obj=_ok([{"id": "pc1"}]))
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            env_path = _write_env(Path(d))
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        *_ops_argv_for_operation_id("aig-config-create-providers"),
                        "--path-param",
                        "account_id=acc1",
                        "--path-param",
                        "gateway_id=gw1",
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])
            self.assertEqual(payload["plan"]["request"]["sensitivity"], "sensitive_write_result")

    def test_operations_call_pages_deployment_logs_is_sensitive_read_in_plan(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = _write_env(Path(d))
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        *_ops_argv_for_operation_id("pages-deployment-get-deployment-logs"),
                        "--path-param",
                        "account_id=acc1",
                        "--path-param",
                        "project_name=proj1",
                        "--path-param",
                        "deployment_id=dep1",
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])
            self.assertEqual(payload["plan"]["request"]["sensitivity"], "sensitive_read")

    def test_allowlist_marks_images_sensitive_endpoints_as_sensitive_read(self) -> None:
        idx = load_allowlisted_operation_index()
        for method, path in [
            ("GET", "/accounts/{account_id}/images/v1/{image_id}/blob"),
            ("POST", "/accounts/{account_id}/images/v2/direct_upload"),
            ("GET", "/accounts/{account_id}/images/v1/keys"),
            ("PUT", "/accounts/{account_id}/images/v1/keys/{signing_key_name}"),
            ("DELETE", "/accounts/{account_id}/images/v1/keys/{signing_key_name}"),
        ]:
            spec = idx.get_by_method_path(method=method, path_template=path)
            self.assertIsNotNone(spec)
            assert spec is not None
            self.assertEqual(spec.sensitivity, "sensitive_read")

    def test_operations_list_hides_images_sensitive_endpoints_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = _write_env(Path(d))

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--env-file", str(env_path), "operations", "list", "--contains", "/images/v1/keys", "--limit", "50"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["count"], 0)

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--env-file", str(env_path), "operations", "list", "--contains", "/images/v1/keys", "--limit", "50", "--include-sensitive"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertGreaterEqual(payload["count"], 1)

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--env-file", str(env_path), "operations", "list", "--contains", "direct_upload", "--limit", "50"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["count"], 0)

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--env-file", str(env_path), "operations", "list", "--contains", "direct_upload", "--limit", "50", "--include-sensitive"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertGreaterEqual(payload["count"], 1)

    def test_operations_call_pages_refuses_without_out_on_apply(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = _write_env(Path(d))
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--apply",
                        *_ops_argv_for_operation_id("pages-project-get-projects"),
                        "--path-param",
                        "account_id=acc1",
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])

    def test_operations_call_email_security_refuses_without_out_on_apply(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = _write_env(Path(d))
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--apply",
                        *_ops_argv_for_operation_id("email_security_investigate"),
                        "--path-param",
                        "account_id=acc1",
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])

    def test_operations_email_security_raw_apply_writes_file_and_never_prints_content(self) -> None:
        secret_bytes = b"RAW_EMAIL_SECRET\\nFrom: user@example.com\\n"

        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
            if method == "GET" and str(url).endswith("/accounts/acc1/email-security/investigate/pf1/raw"):
                return _DummyResponse(status=200, url=url, obj=None, body=secret_bytes)
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
                        *_ops_argv_for_operation_id("email_security_get_message_raw"),
                        "--path-param",
                        "account_id=acc1",
                        "--path-param",
                        "postfix_id=pf1",
                        "--out",
                        "raw.eml",
                    ]
                )
            self.assertEqual(rc, 0)
            out_text = buf.getvalue()
            self.assertNotIn("RAW_EMAIL_SECRET", out_text)
            payload = json.loads(out_text)
            self.assertTrue(payload["ok"])
            file_obj = payload.get("file") or {}
            written = Path(file_obj.get("out_path") or "")
            self.assertTrue(written.exists())
            self.assertEqual(written.read_bytes(), secret_bytes)

    def test_operations_call_images_refuses_without_out_on_apply(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = _write_env(Path(d))
            # Blob endpoint (image bytes) requires file output.
            buf1 = io.StringIO()
            with redirect_stdout(buf1):
                rc1 = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--apply",
                        *_ops_argv_for_operation_id("cloudflare-images-base-image"),
                        "--path-param",
                        "account_id=acc1",
                        "--path-param",
                        "image_id=img1",
                    ]
                )
            self.assertEqual(rc1, 0)
            payload1 = json.loads(buf1.getvalue())
            self.assertTrue(payload1["ok"])
            self.assertTrue(payload1["refused"])

            # Direct upload (read-like POST) returns a time-limited upload URL; requires file output.
            buf2 = io.StringIO()
            with redirect_stdout(buf2):
                rc2 = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--apply",
                        *_ops_argv_for_operation_id("cloudflare-images-create-authenticated-direct-upload-url-v-2"),
                        "--path-param",
                        "account_id=acc1",
                    ]
                )
            self.assertEqual(rc2, 0)
            payload2 = json.loads(buf2.getvalue())
            self.assertTrue(payload2["ok"])
            self.assertTrue(payload2["refused"])

            # Signing keys are sensitive and ack-gated; even with ack, missing --out must refuse.
            buf3 = io.StringIO()
            with redirect_stdout(buf3):
                rc3 = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--ack-irreversible",
                        *_ops_argv_for_operation_id("cloudflare-images-keys-list-signing-keys"),
                        "--path-param",
                        "account_id=acc1",
                    ]
                )
            self.assertEqual(rc3, 0)
            payload3 = json.loads(buf3.getvalue())
            self.assertTrue(payload3["ok"])
            self.assertTrue(payload3["refused"])

    def test_operations_call_ai_gateway_logs_refuses_without_out_on_apply(self) -> None:
        def fake_request(_session, method, url, **kwargs):  # noqa: ANN001
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
                        *_ops_argv_for_operation_id("aig-config-list-gateway-logs"),
                        "--path-param",
                        "account_id=acc1",
                        "--path-param",
                        "gateway_id=gw1",
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])

    def test_operations_call_ai_search_sensitive_read_refuses_without_out_on_apply(self) -> None:
        def fake_request(_session, method, url, **kwargs):  # noqa: ANN001
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
                        *_ops_argv_for_operation_id("ai-search-instance-list-job-logs"),
                        "--path-param",
                        "account_id=acc1",
                        "--path-param",
                        "id=inst1",
                        "--path-param",
                        "job_id=job1",
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])

    def test_operations_call_ai_search_read_like_post_writes_file_without_yes_and_without_leaking(self) -> None:
        sentinel = "AI_SEARCH_RESULT_SENTINEL"

        def fake_request(_session, method, url, **kwargs):  # noqa: ANN001
            if method == "POST" and str(url).endswith("/accounts/acc1/ai-search/instances/inst1/search"):
                body = json.dumps(_ok({"answer": sentinel}), ensure_ascii=False).encode("utf-8")
                return _DummyResponse(status=200, url=url, obj=None, body=body)
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root)
            body = root / "body.json"
            body.write_text('{"query":"hello"}\n', encoding="utf-8")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--project-dir",
                        str(root),
                        "--apply",
                        *_ops_argv_for_operation_id("ai-search-instance-search"),
                        "--path-param",
                        "account_id=acc1",
                        "--path-param",
                        "id=inst1",
                        "--body-json-file",
                        str(body),
                        "--out",
                        "out/ai_search_search.json",
                    ]
                )
            self.assertEqual(rc, 0)
            out_text = buf.getvalue()
            payload = json.loads(out_text)
            self.assertTrue(payload["ok"])
            self.assertFalse(payload["changed"])
            self.assertNotIn(sentinel, out_text)

            out_file = root / "out" / "ai_search_search.json"
            self.assertTrue(out_file.exists())
            self.assertIn(sentinel, out_file.read_text(encoding="utf-8"))

    def test_operations_call_ai_search_token_create_refused_missing_ack_irreversible(self) -> None:
        def fake_request(_session, method, url, **kwargs):  # noqa: ANN001
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root)
            body = root / "body.json"
            body.write_text("{}", encoding="utf-8")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--project-dir",
                        str(root),
                        "--apply",
                        "--yes",
                        *_ops_argv_for_operation_id("ai-search-create-tokens"),
                        "--path-param",
                        "account_id=acc1",
                        "--body-json-file",
                        str(body),
                        "--out",
                        "out/token_create.json",
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])

    def test_operations_call_ai_search_token_update_refused_missing_ack_irreversible(self) -> None:
        def fake_request(_session, method, url, **kwargs):  # noqa: ANN001
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root)
            body = root / "body.json"
            body.write_text("{}", encoding="utf-8")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--project-dir",
                        str(root),
                        "--apply",
                        "--yes",
                        *_ops_argv_for_operation_id("ai-search-update-tokens"),
                        "--path-param",
                        "account_id=acc1",
                        "--path-param",
                        "id=tok1",
                        "--body-json-file",
                        str(body),
                        "--out",
                        "out/token_update.json",
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])

    def test_operations_call_ai_search_token_create_writes_file_without_leaking(self) -> None:
        sentinel = "AI_SEARCH_TOKEN_SECRET_SENTINEL"

        def fake_request(_session, method, url, **kwargs):  # noqa: ANN001
            if method == "GET" and str(url).endswith("/accounts/acc1/ai-search/tokens"):
                body = json.dumps(_ok([{"id": "tok1"}]), ensure_ascii=False).encode("utf-8")
                return _DummyResponse(status=200, url=url, obj=None, body=body)
            if method == "POST" and str(url).endswith("/accounts/acc1/ai-search/tokens"):
                body = json.dumps(_ok({"token": sentinel}), ensure_ascii=False).encode("utf-8")
                return _DummyResponse(status=200, url=url, obj=None, body=body)
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root)
            body = root / "body.json"
            body.write_text("{}", encoding="utf-8")
            out_file = root / "out" / "token_create.json"

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--project-dir",
                        str(root),
                        "--apply",
                        "--yes",
                        "--ack-irreversible",
                        *_ops_argv_for_operation_id("ai-search-create-tokens"),
                        "--path-param",
                        "account_id=acc1",
                        "--body-json-file",
                        str(body),
                        "--out",
                        str(out_file),
                    ]
                )
            self.assertEqual(rc, 0)
            out_text = buf.getvalue()
            payload = json.loads(out_text)
            self.assertTrue(payload["ok"])
            self.assertFalse(payload.get("refused", False))
            self.assertNotIn(sentinel, out_text)
            self.assertTrue(out_file.exists())
            self.assertIn(sentinel, out_file.read_text(encoding="utf-8"))

    def test_operations_call_ai_gateway_provider_config_write_requires_ack_irreversible(self) -> None:
        def fake_request(_session, method, url, **kwargs):  # noqa: ANN001
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root)
            body = root / "body.json"
            body.write_text("{}", encoding="utf-8")
            out_file = root / "out.json"
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--project-dir",
                        str(root),
                        "--apply",
                        "--yes",
                        *_ops_argv_for_operation_id("aig-config-create-providers"),
                        "--path-param",
                        "account_id=acc1",
                        "--path-param",
                        "gateway_id=gw1",
                        "--body-json-file",
                        str(body),
                        "--out",
                        str(out_file),
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])

    def test_operations_call_ai_gateway_provider_config_write_writes_file_without_leaking(self) -> None:
        sentinel = "AIG_PROVIDER_CONFIG_SECRET_SENTINEL"

        def fake_request(_session, method, url, **kwargs):  # noqa: ANN001
            if method == "GET" and str(url).endswith("/accounts/acc1/ai-gateway/gateways/gw1/provider_configs"):
                body = json.dumps(_ok([{"id": "pc1"}]), ensure_ascii=False).encode("utf-8")
                return _DummyResponse(status=200, url=url, obj=None, body=body)
            if method == "POST" and str(url).endswith("/accounts/acc1/ai-gateway/gateways/gw1/provider_configs"):
                body = json.dumps(_ok({"secret": sentinel}), ensure_ascii=False).encode("utf-8")
                return _DummyResponse(status=200, url=url, obj=None, body=body)
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root)
            body = root / "body.json"
            body.write_text("{}", encoding="utf-8")
            out_file = root / "out" / "provider_config_put.json"

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--project-dir",
                        str(root),
                        "--apply",
                        "--yes",
                        "--ack-irreversible",
                        *_ops_argv_for_operation_id("aig-config-create-providers"),
                        "--path-param",
                        "account_id=acc1",
                        "--path-param",
                        "gateway_id=gw1",
                        "--body-json-file",
                        str(body),
                        "--out",
                        str(out_file),
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertFalse(payload.get("refused"))
            self.assertTrue(out_file.exists())
            self.assertIn(sentinel, out_file.read_text(encoding="utf-8"))
            self.assertNotIn(sentinel, buf.getvalue())
            self.assertNotIn(sentinel, json.dumps(payload, ensure_ascii=False))

    def test_operations_call_images_signing_key_put_requires_ack_irreversible(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = _write_env(root)
            body = root / "body.json"
            body.write_text("{}", encoding="utf-8")
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--yes",
                        *_ops_argv_for_operation_id("cloudflare-images-keys-add-signing-key"),
                        "--path-param",
                        "account_id=acc1",
                        "--path-param",
                        "signing_key_name=k1",
                        "--body-json-file",
                        str(body),
                        "--out",
                        "signing_key_put.json",
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])

    def test_operations_call_images_signing_key_get_requires_ack_irreversible(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = _write_env(root)
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--project-dir",
                        str(root),
                        "--apply",
                        *_ops_argv_for_operation_id("cloudflare-images-keys-list-signing-keys"),
                        "--path-param",
                        "account_id=acc1",
                        "--out",
                        "signing_keys.json",
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])

    def test_operations_call_images_signing_key_delete_requires_ack_irreversible(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = _write_env(root)
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--project-dir",
                        str(root),
                        "--apply",
                        "--yes",
                        *_ops_argv_for_operation_id("cloudflare-images-keys-delete-signing-key"),
                        "--path-param",
                        "account_id=acc1",
                        "--path-param",
                        "signing_key_name=k1",
                        "--out",
                        "signing_key_delete.json",
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])

    def test_allowlist_marks_snippet_content_as_sensitive_read(self) -> None:
        idx = load_allowlisted_operation_index()
        spec = idx.get_by_method_path(method="GET", path_template="/zones/{zone_id}/snippets/{snippet_name}/content")
        self.assertIsNotNone(spec)
        assert spec is not None
        self.assertEqual(spec.sensitivity, "sensitive_read")

    def test_allowlist_marks_custom_hostnames_as_sensitive_read(self) -> None:
        idx = load_allowlisted_operation_index()
        spec = idx.get_by_method_path(method="GET", path_template="/zones/{zone_id}/custom_hostnames")
        self.assertIsNotNone(spec)
        assert spec is not None
        self.assertEqual(spec.sensitivity, "sensitive_read")

    def test_allowlist_marks_ssl_tls_as_sensitive_read(self) -> None:
        idx = load_allowlisted_operation_index()
        spec = idx.get_by_method_path(method="GET", path_template="/zones/{zone_id}/ssl/certificate_packs")
        self.assertIsNotNone(spec)
        assert spec is not None
        self.assertEqual(spec.sensitivity, "sensitive_read")

    def test_allowlist_marks_zaraz_zone_settings_as_sensitive_read(self) -> None:
        idx = load_allowlisted_operation_index()
        spec = idx.get_by_method_path(method="GET", path_template="/zones/{zone_id}/settings/zaraz/config")
        self.assertIsNotNone(spec)
        assert spec is not None
        self.assertEqual(spec.sensitivity, "sensitive_read")

    def test_allowlist_marks_registrar_domains_as_sensitive_read(self) -> None:
        idx = load_allowlisted_operation_index()
        for method, path in [
            ("GET", "/accounts/{account_id}/registrar/domains"),
            ("GET", "/accounts/{account_id}/registrar/domains/{domain_name}"),
            ("PUT", "/accounts/{account_id}/registrar/domains/{domain_name}"),
        ]:
            spec = idx.get_by_method_path(method=method, path_template=path)
            self.assertIsNotNone(spec)
            assert spec is not None
            self.assertEqual(spec.sensitivity, "sensitive_read")

    def test_allowlist_marks_turnstile_widgets_sensitivity(self) -> None:
        idx = load_allowlisted_operation_index()

        list_spec = idx.get_by_method_path(method="GET", path_template="/accounts/{account_id}/challenges/widgets")
        self.assertIsNotNone(list_spec)
        assert list_spec is not None
        self.assertEqual(list_spec.sensitivity, "sensitive_read")

        create_spec = idx.get_by_method_path(method="POST", path_template="/accounts/{account_id}/challenges/widgets")
        self.assertIsNotNone(create_spec)
        assert create_spec is not None
        self.assertEqual(create_spec.sensitivity, "sensitive_write_result")

        rotate_spec = idx.get_by_method_path(
            method="POST", path_template="/accounts/{account_id}/challenges/widgets/{sitekey}/rotate_secret"
        )
        self.assertIsNotNone(rotate_spec)
        assert rotate_spec is not None
        self.assertEqual(rotate_spec.sensitivity, "sensitive_write_result")

    def test_allowlist_marks_email_routing_as_sensitive_read(self) -> None:
        idx = load_allowlisted_operation_index()
        for method, path in [
            ("GET", "/accounts/{account_id}/email/routing/addresses"),
            ("POST", "/accounts/{account_id}/email/routing/addresses"),
            ("GET", "/zones/{zone_id}/email/routing"),
            ("POST", "/zones/{zone_id}/email/routing/enable"),
            ("GET", "/zones/{zone_id}/email/routing/rules/catch_all"),
            ("PUT", "/zones/{zone_id}/email/routing/rules/catch_all"),
        ]:
            spec = idx.get_by_method_path(method=method, path_template=path)
            self.assertIsNotNone(spec)
            assert spec is not None
            self.assertEqual(spec.sensitivity, "sensitive_read")

    def test_allowlist_marks_workers_telemetry_as_sensitive_read(self) -> None:
        idx = load_allowlisted_operation_index()
        for method, path in [
            ("POST", "/accounts/{account_id}/workers/observability/telemetry/query"),
            ("POST", "/accounts/{account_id}/workers/observability/telemetry/keys"),
            ("POST", "/accounts/{account_id}/workers/observability/telemetry/values"),
        ]:
            spec = idx.get_by_method_path(method=method, path_template=path)
            self.assertIsNotNone(spec)
            assert spec is not None
            self.assertEqual(spec.sensitivity, "sensitive_read")

    def test_allowlist_marks_workflows_instance_detail_as_sensitive_read(self) -> None:
        idx = load_allowlisted_operation_index()
        spec = idx.get_by_method_path(
            method="GET", path_template="/accounts/{account_id}/workflows/{workflow_name}/instances/{instance_id}"
        )
        self.assertIsNotNone(spec)
        assert spec is not None
        self.assertEqual(spec.sensitivity, "sensitive_read")

    def test_allowlist_includes_pages_endpoints_and_marks_sensitive_read(self) -> None:
        idx = load_allowlisted_operation_index()
        for method, path in [
            ("GET", "/accounts/{account_id}/pages/projects"),
            ("GET", "/accounts/{account_id}/pages/projects/{project_name}/deployments/{deployment_id}/history/logs"),
        ]:
            spec = idx.get_by_method_path(method=method, path_template=path)
            self.assertIsNotNone(spec)
            assert spec is not None
            self.assertEqual(spec.sensitivity, "sensitive_read")

    def test_allowlist_marks_account_members_and_writes_as_sensitive(self) -> None:
        idx = load_allowlisted_operation_index()

        for method, path in [
            ("GET", "/accounts/{account_id}/members"),
            ("GET", "/accounts/{account_id}/members/{member_id}"),
        ]:
            spec = idx.get_by_method_path(method=method, path_template=path)
            self.assertIsNotNone(spec)
            assert spec is not None
            self.assertEqual(spec.sensitivity, "sensitive_read")

        for method, path in [
            ("POST", "/accounts/{account_id}/members"),
            ("PUT", "/accounts/{account_id}/members/{member_id}"),
            ("DELETE", "/accounts/{account_id}/members/{member_id}"),
        ]:
            spec = idx.get_by_method_path(method=method, path_template=path)
            self.assertIsNotNone(spec)
            assert spec is not None
            self.assertEqual(spec.sensitivity, "sensitive_write_result")

    def test_operations_list_includes_zero_trust_dlp(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = _write_env(Path(d))
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--env-file", str(env_path), "operations", "list", "--contains", "/dlp/", "--limit", "5"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertGreaterEqual(payload["count"], 1)

    def test_operations_list_hides_pii_endpoints_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = _write_env(Path(d))

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--env-file", str(env_path), "operations", "list", "--contains", "/zt_risk_scoring/summary", "--limit", "5"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["count"], 0)

            buf2 = io.StringIO()
            with redirect_stdout(buf2):
                rc2 = main(
                    [
                        "--env-file",
                        str(env_path),
                        "operations", "list",
                        "--contains",
                        "/zt_risk_scoring/summary",
                        "--limit",
                        "5",
                        "--include-sensitive",
                    ]
                )
            self.assertEqual(rc2, 0)
            payload2 = json.loads(buf2.getvalue())
            self.assertTrue(payload2["ok"])
            self.assertGreaterEqual(payload2["count"], 1)

    def test_operations_call_pages_get_is_plan_only_without_apply(self) -> None:
        def fake_request(_session, method, url, **kwargs):  # noqa: ANN001
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root)

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        *_ops_argv_for_method_path(method="GET", path_template="/accounts/{account_id}/pages/projects"),
                        "--path-param",
                        "account_id=acc1",
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])

    def test_operations_call_pages_get_refuses_without_out_on_apply(self) -> None:
        def fake_request(_session, method, url, **kwargs):  # noqa: ANN001
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root)

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--apply",
                        *_ops_argv_for_method_path(method="GET", path_template="/accounts/{account_id}/pages/projects"),
                        "--path-param",
                        "account_id=acc1",
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])

    def test_operations_call_pages_rollback_requires_ack_irreversible(self) -> None:
        def fake_request(_session, method, url, **kwargs):  # noqa: ANN001
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root)
            out_file = root / "out" / "pages_rollback.json"

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--project-dir",
                        str(root),
                        "--apply",
                        "--yes",
                        *_ops_argv_for_method_path(method="POST", path_template="/accounts/{account_id}/pages/projects/{project_name}/deployments/{deployment_id}/rollback"),
                        "--path-param",
                        "account_id=acc1",
                        "--path-param",
                        "project_name=p1",
                        "--path-param",
                        "deployment_id=d1",
                        "--out",
                        str(out_file),
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])

    def test_operations_call_pages_rollback_verifies_via_read_back_get_without_leaking(self) -> None:
        sentinel = "PAGES_ROLLBACK_RESPONSE_SHOULD_NOT_PRINT"

        seen: list[tuple[str, str]] = []

        def fake_request(_session, method, url, **kwargs):  # noqa: ANN001
            seen.append((str(method), str(url)))
            if method == "POST" and str(url).endswith("/accounts/acc1/pages/projects/p1/deployments/d1/rollback"):
                body = json.dumps(_ok({"status": "ok", "note": sentinel}), ensure_ascii=False).encode("utf-8")
                return _DummyResponse(status=200, url=url, obj=None, body=body)
            if method == "GET" and str(url).endswith("/accounts/acc1/pages/projects/p1/deployments/d1"):
                body = json.dumps(_ok({"deployment": {"id": "d1", "logs": sentinel}}), ensure_ascii=False).encode("utf-8")
                return _DummyResponse(status=200, url=url, obj=None, body=body)
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root)
            out_file = root / "out" / "pages_rollback.json"

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--project-dir",
                        str(root),
                        "--apply",
                        "--yes",
                        "--ack-irreversible",
                        *_ops_argv_for_method_path(method="POST", path_template="/accounts/{account_id}/pages/projects/{project_name}/deployments/{deployment_id}/rollback"),
                        "--path-param",
                        "account_id=acc1",
                        "--path-param",
                        "project_name=p1",
                        "--path-param",
                        "deployment_id=d1",
                        "--out",
                        str(out_file),
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertFalse(payload.get("refused"))
            self.assertTrue(out_file.exists())
            self.assertIn(sentinel, out_file.read_text(encoding="utf-8"))
            self.assertNotIn(sentinel, buf.getvalue())
            self.assertNotIn(sentinel, json.dumps(payload, ensure_ascii=False))

            verification = (payload.get("receipt") or {}).get("verification") or {}
            self.assertEqual(verification.get("method"), "read_back_get_pages_deployment")
            evidence = verification.get("evidence")
            if evidence is not None:
                self.assertIsInstance(evidence, dict)
                self.assertTrue(set(evidence.keys()).issubset({"http_status", "size_bytes", "sha256"}))
                self.assertNotIn(sentinel, json.dumps(evidence, ensure_ascii=False))
            self.assertFalse("rollback_plan" in payload.get("receipt", {}), "operations receipts currently should not include rollback plans")
            self.assertIn(("POST", "http://example.invalid/client/v4/accounts/acc1/pages/projects/p1/deployments/d1/rollback"), seen)
            self.assertIn(("GET", "http://example.invalid/client/v4/accounts/acc1/pages/projects/p1/deployments/d1"), seen)

    def test_operations_list_hides_observability_sensitive_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = _write_env(Path(d))
            for needle in ["/logpush/", "/audit_logs", "request-tracer/trace"]:
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = main(["--env-file", str(env_path), "operations", "list", "--contains", needle, "--limit", "10"])
                self.assertEqual(rc, 0)
                payload = json.loads(buf.getvalue())
                self.assertTrue(payload["ok"])
                self.assertEqual(payload["count"], 0, f"expected {needle} to be hidden without --include-sensitive")

                buf2 = io.StringIO()
                with redirect_stdout(buf2):
                    rc2 = main(
                        [
                            "--env-file",
                            str(env_path),
                            "operations", "list",
                            "--contains",
                            needle,
                            "--limit",
                            "10",
                            "--include-sensitive",
                        ]
                    )
                self.assertEqual(rc2, 0)
                payload2 = json.loads(buf2.getvalue())
                self.assertTrue(payload2["ok"])
                self.assertGreaterEqual(payload2["count"], 1, f"expected {needle} to appear with --include-sensitive")

    def test_operations_list_hides_email_routing_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = _write_env(Path(d))

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--env-file", str(env_path), "operations", "list", "--contains", "email/routing", "--limit", "10"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["count"], 0)

            buf2 = io.StringIO()
            with redirect_stdout(buf2):
                rc2 = main(
                    [
                        "--env-file",
                        str(env_path),
                        "operations", "list",
                        "--contains",
                        "email/routing",
                        "--limit",
                        "10",
                        "--include-sensitive",
                    ]
                )
            self.assertEqual(rc2, 0)
            payload2 = json.loads(buf2.getvalue())
            self.assertTrue(payload2["ok"])
            self.assertGreaterEqual(payload2["count"], 1)

    def test_operations_list_hides_account_members_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = _write_env(Path(d))

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--env-file", str(env_path), "operations", "list", "--contains", "account-members-list-members", "--limit", "20"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["count"], 0)

            buf2 = io.StringIO()
            with redirect_stdout(buf2):
                rc2 = main(
                    [
                        "--env-file",
                        str(env_path),
                        "operations", "list",
                        "--contains",
                        "account-members-list-members",
                        "--limit",
                        "20",
                        "--include-sensitive",
                    ]
                )
            self.assertEqual(rc2, 0)
            payload2 = json.loads(buf2.getvalue())
            self.assertTrue(payload2["ok"])
            self.assertGreaterEqual(payload2["count"], 1)

    def test_operations_list_includes_dns(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = _write_env(Path(d))
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--env-file", str(env_path), "operations", "list", "--contains", "/dns_records", "--limit", "5"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertGreaterEqual(payload["count"], 1)

    def test_operations_list_includes_dns_firewall(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = _write_env(Path(d))
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--env-file", str(env_path), "operations", "list", "--contains", "dns_firewall", "--limit", "5", "--include-sensitive"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertGreaterEqual(payload["count"], 1)

    def test_operations_list_includes_workflows(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = _write_env(Path(d))
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--env-file", str(env_path), "operations", "list", "--contains", "workflows", "--limit", "50"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            ops = payload.get("operations") or []
            self.assertTrue(
                any((o or {}).get("operation_id") == "wor-list-workflows" for o in ops),
                "expected wor-list-workflows to be present in allowlisted operations list",
            )

    def test_operations_call_workflows_instance_describe_is_sensitive_read_in_plan(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = _write_env(Path(d))
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        *_ops_argv_for_operation_id("wor-describe-workflow-instance"),
                        "--path-param",
                        "account_id=acc1",
                        "--path-param",
                        "workflow_name=wf1",
                        "--path-param",
                        "instance_id=inst1",
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])
            self.assertEqual(payload["plan"]["request"]["sensitivity"], "sensitive_read")

    def test_operations_call_workflows_instance_describe_refuses_without_out_on_apply(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = _write_env(Path(d))
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--apply",
                        *_ops_argv_for_operation_id("wor-describe-workflow-instance"),
                        "--path-param",
                        "account_id=acc1",
                        "--path-param",
                        "workflow_name=wf1",
                        "--path-param",
                        "instance_id=inst1",
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])

    def test_operations_call_refuses_pii_read_without_out(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = _write_env(Path(d))
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--apply",
                        *_ops_argv_for_operation_id("dlp-risk-score-summary-get"),
                        "--path-param",
                        "account_id=acc1",
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])

    def test_operations_call_dns_export_requires_out_on_apply(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = _write_env(Path(d))
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--apply",
                        *_ops_argv_for_operation_id("dns-records-for-a-zone-export-dns-records"),
                        "--path-param",
                        "zone_id=zone1",
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])

    def test_operations_call_zaraz_config_requires_out_on_apply(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = _write_env(Path(d))
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--apply",
                        *_ops_argv_for_operation_id("get-zones-zone_identifier-zaraz-config"),
                        "--path-param",
                        "zone_id=zone1",
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])

    def test_operations_call_kv_bulk_get_requires_out_and_is_read_like(self) -> None:
        sentinel = "KV_VALUE_SHOULD_NOT_PRINT"

        def fake_request(_session, method, url, **kwargs):  # noqa: ANN001
            if method == "POST" and str(url).endswith("/accounts/acc1/storage/kv/namespaces/ns1/bulk/get"):
                body = json.dumps(_ok({"k": sentinel}), ensure_ascii=False).encode("utf-8")
                return _DummyResponse(status=200, url=url, obj=None, body=body)
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root)

            # Missing --out
            buf1 = io.StringIO()
            with redirect_stdout(buf1):
                rc1 = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--apply",
                        *_ops_argv_for_operation_id("workers-kv-namespace-get-multiple-key-value-pairs"),
                        "--path-param",
                        "account_id=acc1",
                        "--path-param",
                        "namespace_id=ns1",
                    ]
                )
            self.assertEqual(rc1, 0)
            payload1 = json.loads(buf1.getvalue())
            self.assertTrue(payload1["ok"])
            self.assertTrue(payload1["refused"])

            # With --out (no --yes): succeeds, writes file, and does not leak value to stdout/receipt.
            out_file = root / "out" / "kv.json"
            buf2 = io.StringIO()
            with redirect_stdout(buf2):
                rc2 = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--project-dir",
                        str(root),
                        "--apply",
                        *_ops_argv_for_operation_id("workers-kv-namespace-get-multiple-key-value-pairs"),
                        "--path-param",
                        "account_id=acc1",
                        "--path-param",
                        "namespace_id=ns1",
                        "--out",
                        str(out_file),
                    ]
                )
            self.assertEqual(rc2, 0)
            payload2 = json.loads(buf2.getvalue())
            self.assertTrue(payload2["ok"])
            self.assertFalse(payload2["dry_run"])
            self.assertFalse(payload2["changed"])
            self.assertTrue(out_file.exists())
            self.assertIn(sentinel, out_file.read_text(encoding="utf-8"))
            self.assertNotIn(sentinel, buf2.getvalue())
            self.assertNotIn(sentinel, json.dumps(payload2, ensure_ascii=False))

    def test_operations_call_vectorize_query_requires_out_and_is_read_like(self) -> None:
        sentinel = "VECTORIZE_QUERY_RESULT_SHOULD_NOT_PRINT"

        def fake_request(_session, method, url, **kwargs):  # noqa: ANN001
            if method == "POST" and str(url).endswith("/accounts/acc1/vectorize/v2/indexes/idx1/query"):
                body = json.dumps(_ok({"result": sentinel}), ensure_ascii=False).encode("utf-8")
                return _DummyResponse(status=200, url=url, obj=None, body=body)
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root)
            body = root / "body.json"
            body.write_text('{"vector":[0.1,0.2,0.3],"topK":3}\n', encoding="utf-8")

            # Missing --out should refuse (and not call HTTP).
            buf1 = io.StringIO()
            with redirect_stdout(buf1):
                rc1 = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--apply",
                        *_ops_argv_for_operation_id("vectorize-query-vector"),
                        "--path-param",
                        "account_id=acc1",
                        "--path-param",
                        "index_name=idx1",
                        "--body-json-file",
                        str(body),
                    ]
                )
            self.assertEqual(rc1, 0)
            payload1 = json.loads(buf1.getvalue())
            self.assertTrue(payload1["ok"])
            self.assertTrue(payload1["refused"])

            # With --out (no --yes): succeeds, changed=false, and does not leak response to stdout/receipt.
            out_file = root / "out" / "vectorize_query.json"
            buf2 = io.StringIO()
            with redirect_stdout(buf2):
                rc2 = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--project-dir",
                        str(root),
                        "--apply",
                        *_ops_argv_for_operation_id("vectorize-query-vector"),
                        "--path-param",
                        "account_id=acc1",
                        "--path-param",
                        "index_name=idx1",
                        "--body-json-file",
                        str(body),
                        "--out",
                        str(out_file),
                    ]
                )
            self.assertEqual(rc2, 0)
            payload2 = json.loads(buf2.getvalue())
            self.assertTrue(payload2["ok"])
            self.assertFalse(payload2["dry_run"])
            self.assertFalse(payload2["changed"])
            self.assertTrue(out_file.exists())
            self.assertIn(sentinel, out_file.read_text(encoding="utf-8"))
            self.assertNotIn(sentinel, buf2.getvalue())
            self.assertNotIn(sentinel, json.dumps(payload2, ensure_ascii=False))

    def test_operations_call_workers_ai_run_requires_out_and_is_read_like(self) -> None:
        sentinel = "WORKERS_AI_RUN_RESULT_SHOULD_NOT_PRINT"

        def fake_request(_session, method, url, **kwargs):  # noqa: ANN001
            if method == "POST" and str(url).endswith("/accounts/acc1/ai/run/@cf/baai/bge-base-en-v1.5"):
                body = json.dumps(_ok({"result": sentinel}), ensure_ascii=False).encode("utf-8")
                return _DummyResponse(status=200, url=url, obj=None, body=body)
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root)
            body = root / "body.json"
            body.write_text("{}", encoding="utf-8")

            # Missing --out should refuse (and not call HTTP).
            buf1 = io.StringIO()
            with redirect_stdout(buf1):
                rc1 = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--apply",
                        *_ops_argv_for_operation_id("workers-ai-post-run-model"),
                        "--path-param",
                        "account_id=acc1",
                        "--path-param",
                        "model_name=@cf/baai/bge-base-en-v1.5",
                        "--body-json-file",
                        str(body),
                    ]
                )
            self.assertEqual(rc1, 0)
            payload1 = json.loads(buf1.getvalue())
            self.assertTrue(payload1["ok"])
            self.assertTrue(payload1["refused"])

            # With --out (no --yes): succeeds, changed=false, and does not leak response to stdout/receipt.
            out_file = root / "out" / "workers_ai_run.json"
            buf2 = io.StringIO()
            with redirect_stdout(buf2):
                rc2 = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--project-dir",
                        str(root),
                        "--apply",
                        *_ops_argv_for_operation_id("workers-ai-post-run-model"),
                        "--path-param",
                        "account_id=acc1",
                        "--path-param",
                        "model_name=@cf/baai/bge-base-en-v1.5",
                        "--body-json-file",
                        str(body),
                        "--out",
                        str(out_file),
                    ]
                )
            self.assertEqual(rc2, 0)
            payload2 = json.loads(buf2.getvalue())
            self.assertTrue(payload2["ok"])
            self.assertFalse(payload2["dry_run"])
            self.assertFalse(payload2["changed"])
            self.assertIn("receipt", payload2)
            self.assertFalse(payload2["receipt"]["changed"])
            self.assertTrue(out_file.exists())
            self.assertIn(sentinel, out_file.read_text(encoding="utf-8"))
            self.assertNotIn(sentinel, buf2.getvalue())
            self.assertNotIn(sentinel, json.dumps(payload2, ensure_ascii=False))

    def test_operations_call_workers_ai_finetune_create_refuses_without_yes_and_does_not_call_http(self) -> None:
        def fake_request(_session, method, url, **kwargs):  # noqa: ANN001
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root)
            body = root / "body.json"
            body.write_text("{}", encoding="utf-8")
            out_file = root / "out" / "workers_ai_finetune_create.json"

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--project-dir",
                        str(root),
                        "--apply",
                        *_ops_argv_for_operation_id("workers-ai-create-finetune"),
                        "--path-param",
                        "account_id=acc1",
                        "--body-json-file",
                        str(body),
                        "--out",
                        str(out_file),
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])

    def test_operations_call_vectorize_upsert_requires_yes(self) -> None:
        def fake_request(_session, method, url, **kwargs):  # noqa: ANN001
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root)
            body = root / "body.json"
            body.write_text('{"vectors":[{"id":"doc1","values":[0.1,0.2,0.3]}]}\n', encoding="utf-8")

            # With --out but without --yes refuses.
            out_file = root / "out" / "vectorize_upsert.json"
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--project-dir",
                        str(root),
                        "--apply",
                        *_ops_argv_for_operation_id("vectorize-upsert-vector"),
                        "--path-param",
                        "account_id=acc1",
                        "--path-param",
                        "index_name=idx1",
                        "--body-json-file",
                        str(body),
                        "--out",
                        str(out_file),
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])

    def test_operations_call_ssl_analyze_is_read_like_non_get_and_does_not_require_yes(self) -> None:
        secret_bytes = b'{"analysis":"CERT_DATA_SHOULD_NOT_PRINT"}\n'

        def fake_request(_session, method, url, **kwargs):  # noqa: ANN001
            if method == "POST" and str(url).endswith("/zones/zone1/ssl/analyze"):
                return _DummyResponse(status=200, url=url, obj=None, body=secret_bytes)
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
                        *_ops_argv_for_operation_id("analyze-certificate-analyze-certificate"),
                        "--path-param",
                        "zone_id=zone1",
                        "--out",
                        "analyze.json",
                    ]
                )
            self.assertEqual(rc, 0)
            out_text = buf.getvalue()
            self.assertNotIn("CERT_DATA_SHOULD_NOT_PRINT", out_text)
            payload = json.loads(out_text)
            self.assertTrue(payload["ok"])
            self.assertFalse(payload.get("changed"), "ssl analyze should be treated as read-like (changed=false)")

    def test_operations_call_waiting_room_preview_is_read_like_non_get_and_does_not_require_yes(self) -> None:
        def fake_request(_session, method, url, **kwargs):  # noqa: ANN001
            if method == "POST" and str(url).endswith("/zones/zone1/waiting_rooms/preview"):
                return _DummyResponse(status=200, url=url, obj=_ok("preview"))
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root)

            # Plan
            buf1 = io.StringIO()
            with redirect_stdout(buf1):
                rc1 = main(
                    [
                        "--env-file",
                        str(env_path),
                        *_ops_argv_for_operation_id("waiting-room-create-a-custom-waiting-room-page-preview"),
                        "--path-param",
                        "zone_id=zone1",
                    ]
                )
            self.assertEqual(rc1, 0)
            payload1 = json.loads(buf1.getvalue())
            self.assertTrue(payload1["ok"])
            self.assertTrue(payload1["dry_run"])
            self.assertIn(
                "This endpoint uses a non-GET read-like operation (no state changes expected).",
                payload1.get("plan", {}).get("risk_reasons", []),
            )

            # Apply (no --yes)
            buf2 = io.StringIO()
            with redirect_stdout(buf2):
                rc2 = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--apply",
                        *_ops_argv_for_operation_id("waiting-room-create-a-custom-waiting-room-page-preview"),
                        "--path-param",
                        "zone_id=zone1",
                    ]
                )
            self.assertEqual(rc2, 0)
            payload2 = json.loads(buf2.getvalue())
            self.assertTrue(payload2["ok"])
            self.assertFalse(payload2.get("refused"))
            self.assertFalse(payload2.get("changed"))
            self.assertIn("receipt", payload2)
            self.assertFalse(payload2["receipt"]["changed"])

    def test_operations_call_queues_pull_requires_out_and_is_read_like(self) -> None:
        sentinel = "QUEUE_MESSAGE_BODY_SHOULD_NOT_PRINT"

        def fake_request(_session, method, url, **kwargs):  # noqa: ANN001
            if method == "POST" and str(url).endswith("/accounts/acc1/queues/q1/messages/pull"):
                body = json.dumps(_ok({"messages": [{"body": sentinel}]}), ensure_ascii=False).encode("utf-8")
                return _DummyResponse(status=200, url=url, obj=None, body=body)
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root)

            # Missing --out
            buf1 = io.StringIO()
            with redirect_stdout(buf1):
                rc1 = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--apply",
                        *_ops_argv_for_operation_id("queues-pull-messages"),
                        "--path-param",
                        "account_id=acc1",
                        "--path-param",
                        "queue_id=q1",
                    ]
                )
            self.assertEqual(rc1, 0)
            payload1 = json.loads(buf1.getvalue())
            self.assertTrue(payload1["ok"])
            self.assertTrue(payload1["refused"])

            out_file = root / "out" / "queues_pull.json"
            buf2 = io.StringIO()
            with redirect_stdout(buf2):
                rc2 = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--project-dir",
                        str(root),
                        "--apply",
                        *_ops_argv_for_operation_id("queues-pull-messages"),
                        "--path-param",
                        "account_id=acc1",
                        "--path-param",
                        "queue_id=q1",
                        "--out",
                        str(out_file),
                    ]
                )
            self.assertEqual(rc2, 0)
            payload2 = json.loads(buf2.getvalue())
            self.assertTrue(payload2["ok"])
            self.assertFalse(payload2["dry_run"])
            self.assertFalse(payload2["changed"])
            self.assertTrue(out_file.exists())
            self.assertIn(sentinel, out_file.read_text(encoding="utf-8"))
            self.assertNotIn(sentinel, buf2.getvalue())
            self.assertNotIn(sentinel, json.dumps(payload2, ensure_ascii=False))

    def test_operations_call_autorag_search_requires_out_and_is_read_like(self) -> None:
        sentinel = "AUTORAG_SEARCH_RESULT_SHOULD_NOT_PRINT"

        def fake_request(_session, method, url, **kwargs):  # noqa: ANN001
            if method == "POST" and str(url).endswith("/accounts/acc1/autorag/rags/rag1/search"):
                body = json.dumps(_ok({"chunks": [{"content": sentinel}]}), ensure_ascii=False).encode("utf-8")
                return _DummyResponse(status=200, url=url, obj=None, body=body)
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root)

            # Missing --out
            buf1 = io.StringIO()
            with redirect_stdout(buf1):
                rc1 = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--apply",
                        *_ops_argv_for_operation_id("autorag-config-search"),
                        "--path-param",
                        "account_id=acc1",
                        "--path-param",
                        "id=rag1",
                    ]
                )
            self.assertEqual(rc1, 0)
            payload1 = json.loads(buf1.getvalue())
            self.assertTrue(payload1["ok"])
            self.assertTrue(payload1["refused"])

            # With --out (no --yes): succeeds, writes file, and does not leak value to stdout/receipt.
            out_file = root / "out" / "autorag_search.json"
            buf2 = io.StringIO()
            with redirect_stdout(buf2):
                rc2 = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--project-dir",
                        str(root),
                        "--apply",
                        *_ops_argv_for_operation_id("autorag-config-search"),
                        "--path-param",
                        "account_id=acc1",
                        "--path-param",
                        "id=rag1",
                        "--out",
                        str(out_file),
                    ]
                )
            self.assertEqual(rc2, 0)
            payload2 = json.loads(buf2.getvalue())
            self.assertTrue(payload2["ok"])
            self.assertFalse(payload2.get("refused"))
            self.assertFalse(payload2.get("changed"))
            self.assertTrue(out_file.exists())
            self.assertIn(sentinel, out_file.read_text(encoding="utf-8"))
            self.assertNotIn(sentinel, buf2.getvalue())
            self.assertNotIn(sentinel, json.dumps(payload2, ensure_ascii=False))

    def test_operations_call_autorag_ai_search_requires_out_and_is_read_like(self) -> None:
        sentinel = "AUTORAG_AI_SEARCH_RESULT_SHOULD_NOT_PRINT"

        def fake_request(_session, method, url, **kwargs):  # noqa: ANN001
            if method == "POST" and str(url).endswith("/accounts/acc1/autorag/rags/rag1/ai-search"):
                body = json.dumps(_ok({"answer": sentinel}), ensure_ascii=False).encode("utf-8")
                return _DummyResponse(status=200, url=url, obj=None, body=body)
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root)

            # Missing --out
            buf1 = io.StringIO()
            with redirect_stdout(buf1):
                rc1 = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--apply",
                        *_ops_argv_for_operation_id("autorag-config-ai-search"),
                        "--path-param",
                        "account_id=acc1",
                        "--path-param",
                        "id=rag1",
                    ]
                )
            self.assertEqual(rc1, 0)
            payload1 = json.loads(buf1.getvalue())
            self.assertTrue(payload1["ok"])
            self.assertTrue(payload1["refused"])

            # With --out (no --yes): succeeds, writes file, and does not leak value to stdout/receipt.
            out_file = root / "out" / "autorag_ai_search.json"
            buf2 = io.StringIO()
            with redirect_stdout(buf2):
                rc2 = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--project-dir",
                        str(root),
                        "--apply",
                        *_ops_argv_for_operation_id("autorag-config-ai-search"),
                        "--path-param",
                        "account_id=acc1",
                        "--path-param",
                        "id=rag1",
                        "--out",
                        str(out_file),
                    ]
                )
            self.assertEqual(rc2, 0)
            payload2 = json.loads(buf2.getvalue())
            self.assertTrue(payload2["ok"])
            self.assertFalse(payload2.get("refused"))
            self.assertFalse(payload2.get("changed"))
            self.assertTrue(out_file.exists())
            self.assertIn(sentinel, out_file.read_text(encoding="utf-8"))
            self.assertNotIn(sentinel, buf2.getvalue())
            self.assertNotIn(sentinel, json.dumps(payload2, ensure_ascii=False))

    def test_operations_call_autorag_sync_refuses_without_yes_and_does_not_call_http(self) -> None:
        def fake_request(_session, method, url, **kwargs):  # noqa: ANN001
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root)
            out_file = root / "out" / "autorag_sync.json"

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--project-dir",
                        str(root),
                        "--apply",
                        *_ops_argv_for_operation_id("autorag-config-sync"),
                        "--path-param",
                        "account_id=acc1",
                        "--path-param",
                        "id=rag1",
                        "--out",
                        str(out_file),
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])

    def test_operations_call_hyperdrive_create_and_patch_are_file_only_sensitive(self) -> None:
        sentinel = "HYPERDRIVE_SECRET_SHOULD_NOT_PRINT"

        def fake_request(_session, method, url, **kwargs):  # noqa: ANN001
            if method == "GET" and str(url).endswith("/accounts/acc1/hyperdrive/configs"):
                body = json.dumps(_ok([{"id": "h1"}]), ensure_ascii=False).encode("utf-8")
                return _DummyResponse(status=200, url=url, obj=None, body=body)
            if method == "POST" and str(url).endswith("/accounts/acc1/hyperdrive/configs"):
                body = json.dumps(_ok({"connectionString": sentinel}), ensure_ascii=False).encode("utf-8")
                return _DummyResponse(status=200, url=url, obj=None, body=body)
            if method == "PATCH" and str(url).endswith("/accounts/acc1/hyperdrive/configs/h1"):
                body = json.dumps(_ok({"connectionString": sentinel}), ensure_ascii=False).encode("utf-8")
                return _DummyResponse(status=200, url=url, obj=None, body=body)
            if method == "GET" and str(url).endswith("/accounts/acc1/hyperdrive/configs/h1"):
                body = json.dumps(_ok({"id": "h1"}), ensure_ascii=False).encode("utf-8")
                return _DummyResponse(status=200, url=url, obj=None, body=body)
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root)

            out_create = root / "out" / "hyperdrive_create.json"
            out_patch = root / "out" / "hyperdrive_patch.json"

            # Create: missing --out.
            buf1 = io.StringIO()
            with redirect_stdout(buf1):
                rc1 = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--yes",
                        *_ops_argv_for_operation_id("create-hyperdrive"),
                        "--path-param",
                        "account_id=acc1",
                    ]
                )
            self.assertEqual(rc1, 0)
            payload1 = json.loads(buf1.getvalue())
            self.assertTrue(payload1["ok"])
            self.assertTrue(payload1["refused"])

            # Create: with --out but without --yes (write gate).
            buf2 = io.StringIO()
            with redirect_stdout(buf2):
                rc2 = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--project-dir",
                        str(root),
                        "--apply",
                        *_ops_argv_for_operation_id("create-hyperdrive"),
                        "--path-param",
                        "account_id=acc1",
                        "--out",
                        str(out_create),
                    ]
                )
            self.assertEqual(rc2, 0)
            payload2 = json.loads(buf2.getvalue())
            self.assertTrue(payload2["ok"])
            self.assertTrue(payload2["refused"])

            # Create: with --out + --yes succeeds and does not leak sentinel.
            buf3 = io.StringIO()
            with redirect_stdout(buf3):
                rc3 = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--project-dir",
                        str(root),
                        "--apply",
                        "--yes",
                        *_ops_argv_for_operation_id("create-hyperdrive"),
                        "--path-param",
                        "account_id=acc1",
                        "--out",
                        str(out_create),
                    ]
                )
            self.assertEqual(rc3, 0)
            payload3 = json.loads(buf3.getvalue())
            self.assertTrue(payload3["ok"])
            self.assertTrue(payload3["changed"])
            self.assertTrue(out_create.exists())
            self.assertIn(sentinel, out_create.read_text(encoding="utf-8"))
            self.assertNotIn(sentinel, buf3.getvalue())
            self.assertNotIn(sentinel, json.dumps(payload3, ensure_ascii=False))

            # Patch: with --out but without --yes refuses.
            buf4 = io.StringIO()
            with redirect_stdout(buf4):
                rc4 = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--project-dir",
                        str(root),
                        "--apply",
                        *_ops_argv_for_operation_id("patch-hyperdrive"),
                        "--path-param",
                        "account_id=acc1",
                        "--path-param",
                        "hyperdrive_id=h1",
                        "--out",
                        str(out_patch),
                    ]
                )
            self.assertEqual(rc4, 0)
            payload4 = json.loads(buf4.getvalue())
            self.assertTrue(payload4["ok"])
            self.assertTrue(payload4["refused"])

            # Patch: with --out + --yes succeeds and does not leak sentinel.
            buf5 = io.StringIO()
            with redirect_stdout(buf5):
                rc5 = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--project-dir",
                        str(root),
                        "--apply",
                        "--yes",
                        *_ops_argv_for_operation_id("patch-hyperdrive"),
                        "--path-param",
                        "account_id=acc1",
                        "--path-param",
                        "hyperdrive_id=h1",
                        "--out",
                        str(out_patch),
                    ]
                )
            self.assertEqual(rc5, 0)
            payload5 = json.loads(buf5.getvalue())
            self.assertTrue(payload5["ok"])
            self.assertTrue(payload5["changed"])
            self.assertTrue(out_patch.exists())
            self.assertIn(sentinel, out_patch.read_text(encoding="utf-8"))
            self.assertNotIn(sentinel, buf5.getvalue())
            self.assertNotIn(sentinel, json.dumps(payload5, ensure_ascii=False))

    def test_operations_call_d1_import_is_file_only_sensitive(self) -> None:
        sentinel = "D1_IMPORT_SHOULD_NOT_PRINT"

        def fake_request(_session, method, url, **kwargs):  # noqa: ANN001
            if method == "POST" and str(url).endswith("/accounts/acc1/d1/database/db1/import"):
                body = json.dumps(_ok({"imported": True, "sample": sentinel}), ensure_ascii=False).encode("utf-8")
                return _DummyResponse(status=200, url=url, obj=None, body=body)
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root)
            out_file = root / "out" / "d1_import.json"

            # Missing --out.
            buf1 = io.StringIO()
            with redirect_stdout(buf1):
                rc1 = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--yes",
                        *_ops_argv_for_operation_id("d1-import-database"),
                        "--path-param",
                        "account_id=acc1",
                        "--path-param",
                        "database_id=db1",
                    ]
                )
            self.assertEqual(rc1, 0)
            payload1 = json.loads(buf1.getvalue())
            self.assertTrue(payload1["ok"])
            self.assertTrue(payload1["refused"])

            # With --out but without --yes refuses.
            buf2 = io.StringIO()
            with redirect_stdout(buf2):
                rc2 = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--project-dir",
                        str(root),
                        "--apply",
                        *_ops_argv_for_operation_id("d1-import-database"),
                        "--path-param",
                        "account_id=acc1",
                        "--path-param",
                        "database_id=db1",
                        "--out",
                        str(out_file),
                    ]
                )
            self.assertEqual(rc2, 0)
            payload2 = json.loads(buf2.getvalue())
            self.assertTrue(payload2["ok"])
            self.assertTrue(payload2["refused"])

            # With --out + --yes still refuses because this database write has no before-state path yet.
            buf3 = io.StringIO()
            with redirect_stdout(buf3):
                rc3 = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--project-dir",
                        str(root),
                        "--apply",
                        "--yes",
                        *_ops_argv_for_operation_id("d1-import-database"),
                        "--path-param",
                        "account_id=acc1",
                        "--path-param",
                        "database_id=db1",
                        "--out",
                        str(out_file),
                    ]
                )
            self.assertEqual(rc3, 0)
            payload3 = json.loads(buf3.getvalue())
            self.assertTrue(payload3["ok"])
            self.assertTrue(payload3["refused"])
            self.assertFalse(out_file.exists())
            self.assertNotIn(sentinel, buf3.getvalue())
            self.assertNotIn(sentinel, json.dumps(payload3, ensure_ascii=False))

    def test_operations_call_pipelines_validate_sql_is_read_like_file_only(self) -> None:
        sentinel = "PIPELINES_VALIDATE_SQL_SHOULD_NOT_PRINT"

        def fake_request(_session, method, url, **kwargs):  # noqa: ANN001
            if method == "POST" and str(url).endswith("/accounts/acc1/pipelines/v1/validate_sql"):
                body = json.dumps(_ok({"valid": True, "diagnostics": {"echo": sentinel}}), ensure_ascii=False).encode("utf-8")
                return _DummyResponse(status=200, url=url, obj=None, body=body)
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root)
            out_file = root / "out" / "validate_sql.json"

            # Missing --out.
            buf1 = io.StringIO()
            with redirect_stdout(buf1):
                rc1 = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--apply",
                        *_ops_argv_for_operation_id("postV4AccountsByAccount_idPipelinesV1Validate_sql"),
                        "--path-param",
                        "account_id=acc1",
                    ]
                )
            self.assertEqual(rc1, 0)
            payload1 = json.loads(buf1.getvalue())
            self.assertTrue(payload1["ok"])
            self.assertTrue(payload1["refused"])

            # With --out (no --yes): succeeds, changed=false, and does not leak sentinel.
            buf2 = io.StringIO()
            with redirect_stdout(buf2):
                rc2 = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--project-dir",
                        str(root),
                        "--apply",
                        *_ops_argv_for_operation_id("postV4AccountsByAccount_idPipelinesV1Validate_sql"),
                        "--path-param",
                        "account_id=acc1",
                        "--out",
                        str(out_file),
                    ]
                )
            self.assertEqual(rc2, 0)
            payload2 = json.loads(buf2.getvalue())
            self.assertTrue(payload2["ok"])
            self.assertFalse(payload2["dry_run"])
            self.assertFalse(payload2["changed"])
            self.assertTrue(out_file.exists())
            self.assertIn(sentinel, out_file.read_text(encoding="utf-8"))
            self.assertNotIn(sentinel, buf2.getvalue())
            self.assertNotIn(sentinel, json.dumps(payload2, ensure_ascii=False))

    def test_operations_call_r2_temp_creds_requires_ack_irreversible(self) -> None:
        sentinel = "TEMP_CREDENTIAL_SECRET"

        def fake_request(_session, method, url, **kwargs):  # noqa: ANN001
            if method == "POST" and str(url).endswith("/accounts/acc1/r2/temp-access-credentials"):
                body = json.dumps(_ok({"accessKeyId": "AKIA", "secretAccessKey": sentinel}), ensure_ascii=False).encode("utf-8")
                return _DummyResponse(status=200, url=url, obj=None, body=body)
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root)
            out_file = root / "out" / "temp_creds.json"

            # Missing --ack-irreversible
            buf1 = io.StringIO()
            with redirect_stdout(buf1):
                rc1 = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--project-dir",
                        str(root),
                        "--apply",
                        "--yes",
                        *_ops_argv_for_operation_id("r2-create-temp-access-credentials"),
                        "--path-param",
                        "account_id=acc1",
                        "--out",
                        str(out_file),
                    ]
                )
            self.assertEqual(rc1, 0)
            payload1 = json.loads(buf1.getvalue())
            self.assertTrue(payload1["ok"])
            self.assertTrue(payload1["refused"])

            # Missing --yes (write gate)
            buf2 = io.StringIO()
            with redirect_stdout(buf2):
                rc2 = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--project-dir",
                        str(root),
                        "--apply",
                        "--ack-irreversible",
                        *_ops_argv_for_operation_id("r2-create-temp-access-credentials"),
                        "--path-param",
                        "account_id=acc1",
                        "--out",
                        str(out_file),
                    ]
                )
            self.assertEqual(rc2, 0)
            payload2 = json.loads(buf2.getvalue())
            self.assertTrue(payload2["ok"])
            self.assertTrue(payload2["refused"])

            # With --out + --ack-irreversible + --yes still refuses because this write has no before-state path yet.
            buf3 = io.StringIO()
            with redirect_stdout(buf3):
                rc3 = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--project-dir",
                        str(root),
                        "--apply",
                        "--yes",
                        "--ack-irreversible",
                        *_ops_argv_for_operation_id("r2-create-temp-access-credentials"),
                        "--path-param",
                        "account_id=acc1",
                        "--out",
                        str(out_file),
                    ]
                )
            self.assertEqual(rc3, 0)
            payload3 = json.loads(buf3.getvalue())
            self.assertTrue(payload3["ok"])
            self.assertTrue(payload3["refused"])
            self.assertFalse(out_file.exists())
            self.assertNotIn(sentinel, buf3.getvalue())
            self.assertNotIn(sentinel, json.dumps(payload3, ensure_ascii=False))

    def test_operations_call_tsig_create_safety_gates_and_secret_safety(self) -> None:
        sentinel = "SUPERSECRET"

        def fake_request(_session, method, url, **kwargs):  # noqa: ANN001
            if method == "POST" and str(url).endswith("/accounts/acc1/secondary_dns/tsigs"):
                body = json.dumps(_ok({"id": "ts1", "tsig_secret": sentinel}), ensure_ascii=False).encode("utf-8")
                return _DummyResponse(status=200, url=url, obj=None, body=body)
            if method == "GET" and str(url).endswith("/accounts/acc1/secondary_dns/tsigs/ts1"):
                body = json.dumps(_ok({"id": "ts1"}), ensure_ascii=False).encode("utf-8")
                return _DummyResponse(status=200, url=url, obj=None, body=body)
            if method == "GET" and "/accounts/acc1/secondary_dns/tsigs" in str(url):
                body = json.dumps(_ok({"ok": True}), ensure_ascii=False).encode("utf-8")
                return _DummyResponse(status=200, url=url, obj=None, body=body)
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root)
            body_path = root / "body.json"
            body_path.write_text(json.dumps({"name": "k", "secret": "v"}, sort_keys=True), encoding="utf-8")

            # Missing --out
            buf1 = io.StringIO()
            with redirect_stdout(buf1):
                rc1 = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--yes",
                        "--ack-irreversible",
                        *_ops_argv_for_operation_id("secondary-dns-(-tsig)-create-tsig"),
                        "--path-param",
                        "account_id=acc1",
                        "--body-json-file",
                        str(body_path),
                    ]
                )
            self.assertEqual(rc1, 0)
            payload1 = json.loads(buf1.getvalue())
            self.assertTrue(payload1["ok"])
            self.assertTrue(payload1["refused"])

            # Missing --ack-irreversible
            out_file = root / "out" / "tsig.json"
            buf2 = io.StringIO()
            with redirect_stdout(buf2):
                rc2 = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--project-dir",
                        str(root),
                        "--apply",
                        "--yes",
                        *_ops_argv_for_operation_id("secondary-dns-(-tsig)-create-tsig"),
                        "--path-param",
                        "account_id=acc1",
                        "--body-json-file",
                        str(body_path),
                        "--out",
                        str(out_file),
                    ]
                )
            self.assertEqual(rc2, 0)
            payload2 = json.loads(buf2.getvalue())
            self.assertTrue(payload2["ok"])
            self.assertTrue(payload2["refused"])

            # Missing --yes (write gate)
            buf3 = io.StringIO()
            with redirect_stdout(buf3):
                rc3 = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--project-dir",
                        str(root),
                        "--apply",
                        "--ack-irreversible",
                        *_ops_argv_for_operation_id("secondary-dns-(-tsig)-create-tsig"),
                        "--path-param",
                        "account_id=acc1",
                        "--body-json-file",
                        str(body_path),
                        "--out",
                        str(out_file),
                    ]
                )
            self.assertEqual(rc3, 0)
            payload3 = json.loads(buf3.getvalue())
            self.assertTrue(payload3["ok"])
            self.assertTrue(payload3["refused"])

            # With --out + --ack-irreversible + --yes: succeeds, writes file, and does not leak secret to stdout/receipt.
            buf4 = io.StringIO()
            with redirect_stdout(buf4):
                rc4 = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--project-dir",
                        str(root),
                        "--apply",
                        "--yes",
                        "--ack-irreversible",
                        *_ops_argv_for_operation_id("secondary-dns-(-tsig)-create-tsig"),
                        "--path-param",
                        "account_id=acc1",
                        "--body-json-file",
                        str(body_path),
                        "--out",
                        str(out_file),
                    ]
                )
            self.assertEqual(rc4, 0)
            payload4 = json.loads(buf4.getvalue())
            self.assertTrue(payload4["ok"])
            self.assertFalse(payload4["dry_run"])
            self.assertTrue(out_file.exists())
            self.assertNotIn(sentinel, buf4.getvalue())
            self.assertNotIn(sentinel, json.dumps(payload4, ensure_ascii=False))

    def test_operations_list_hides_workers_assets_upload_session_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = _write_env(Path(d))

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--env-file", str(env_path), "operations", "list", "--contains", "assets-upload-session", "--limit", "10"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["count"], 0)

            buf2 = io.StringIO()
            with redirect_stdout(buf2):
                rc2 = main(
                    [
                        "--env-file",
                        str(env_path),
                        "operations", "list",
                        "--contains",
                        "assets-upload-session",
                        "--limit",
                        "10",
                        "--include-sensitive",
                    ]
                )
            self.assertEqual(rc2, 0)
            payload2 = json.loads(buf2.getvalue())
            self.assertTrue(payload2["ok"])
            self.assertGreaterEqual(payload2["count"], 1)

    def test_operations_call_refuses_assets_upload_session_without_out_and_ack(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = _write_env(Path(d))
            body_path = Path(d) / "b.json"
            body_path.write_text("{}", encoding="utf-8")
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--yes",
                        *_ops_argv_for_operation_id("namespace-worker-script-update-create-assets-upload-session"),
                        "--path-param",
                        "account_id=acc1",
                        "--path-param",
                        "dispatch_namespace=ns1",
                        "--path-param",
                        "script_name=s1",
                        "--body-json-file",
                        str(body_path),
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            self.assertEqual(payload["refusal_type"], "SafetyError")

    def test_operations_call_dry_run_write_captures_before_state_in_plan(self) -> None:
        calls: list[tuple[str, str]] = []

        def fake_request(_session, method, url, **kwargs):  # noqa: ANN001
            calls.append((str(method), str(url)))
            if method == "GET" and str(url).endswith("/accounts/acc1/access/apps"):
                return _DummyResponse(status=200, url=url, obj=_ok([{"id": "app1"}]))
            raise AssertionError(f"unexpected HTTP call in dry-run: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            env_path = _write_env(Path(d))
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        *_ops_argv_for_method_path(method="POST", path_template="/accounts/{account_id}/access/apps"),
                        "--path-param",
                        "account_id=acc1",
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])
            self.assertIn("plan", payload)
            self.assertIn("before_state", payload["plan"])
            self.assertEqual(payload["plan"]["before_state"]["path_resolved"], "/accounts/acc1/access/apps")
            self.assertTrue(Path(payload["plan"]["before_state_path"]).exists())
            self.assertEqual(len(calls), 1)
            self.assertEqual(calls[0][0], "GET")

    def test_operations_call_dry_run_write_without_before_state_marks_apply_blocked(self) -> None:
        def fake_request(_session, method, url, **kwargs):  # noqa: ANN001
            raise AssertionError(f"unexpected HTTP call in dry-run: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            env_path = _write_env(Path(d))
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        *_ops_argv_for_operation_id("RequestReview"),
                        "--path-param",
                        "account_id=acc1",
                        "--path-param",
                        "report_id=rep1",
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])
            before_state = payload["plan"]["before_state"]
            self.assertFalse(before_state["saved"])
            self.assertIn("No matching GET endpoint", before_state["reason"])
            self.assertIn("ack-no-snapshot", " ".join(payload["plan"]["notes"]))

    def test_operations_call_apply_write_without_before_state_refuses_before_http(self) -> None:
        def fake_request(_session, method, url, **kwargs):  # noqa: ANN001
            raise AssertionError(f"unexpected HTTP write: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root)
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--project-dir",
                        str(root),
                        "--apply",
                        "--yes",
                        *_ops_argv_for_operation_id("RequestReview"),
                        "--path-param",
                        "account_id=acc1",
                        "--path-param",
                        "report_id=rep1",
                        "--out",
                        "out/request-review.json",
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            self.assertEqual(payload["refusal_type"], "SafetyError")
            self.assertIn("before-state snapshot", payload["reasons"][0])
            self.assertIn("ack-no-snapshot", payload["reasons"][0])

    def test_operations_call_get_executes_without_apply(self) -> None:
        def fake_request(_session, method, url, **kwargs):  # noqa: ANN001
            if method == "GET" and str(url).endswith("/accounts/acc1/workers/scripts"):
                return _DummyResponse(status=200, url=url, obj=_ok([{"id": "s1"}]))
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            env_path = _write_env(Path(d))
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        *_ops_argv_for_operation_id("worker-script-list-workers"),
                        "--path-param",
                        "account_id=acc1",
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertIn("result", payload)
            self.assertEqual(payload["command"], "operations.call")

    def test_operations_call_dry_run_write_requires_token_for_before_state(self) -> None:
        def fake_request(_session, method, url, **kwargs):  # noqa: ANN001
            raise AssertionError(f"unexpected HTTP call in dry-run: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            # env file without token
            env_path = root / ".env"
            env_path.write_text(
                "\n".join(
                    [
                        "CLOUDFLARE_API_BASE_URL=http://example.invalid/client/v4",
                        "CLOUDFLARE_TIMEOUT_S=30",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        *_ops_argv_for_method_path(method="POST", path_template="/accounts/{account_id}/access/apps"),
                        "--path-param",
                        "account_id=acc1",
                    ]
                )
            self.assertEqual(rc, 1)
            payload = json.loads(buf.getvalue())
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["error_type"], "ValidationError")
            self.assertIn("Missing CLOUDFLARE_API_TOKEN", payload["error"])

    def test_operations_call_sensitive_read_requires_out_on_apply(self) -> None:
        def fake_request(_session, method, url, **kwargs):  # noqa: ANN001
            if method == "GET" and str(url).endswith("/accounts/acc1/workers/scripts/s1"):
                return _DummyResponse(status=200, url=url, obj=None, body=b"console.log('hi')\n")
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root)

            # Apply without --out should refuse safely.
            buf1 = io.StringIO()
            with redirect_stdout(buf1):
                rc1 = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--apply",
                        *_ops_argv_for_operation_id("worker-script-download-worker"),
                        "--path-param",
                        "account_id=acc1",
                        "--path-param",
                        "script_name=s1",
                    ]
                )
            self.assertEqual(rc1, 0)
            payload1 = json.loads(buf1.getvalue())
            self.assertTrue(payload1["ok"])
            self.assertTrue(payload1["refused"])

            # Apply with --out writes file and does not print content.
            out_file = root / "out" / "script.js"
            buf2 = io.StringIO()
            with redirect_stdout(buf2):
                rc2 = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--project-dir",
                        str(root),
                        "--apply",
                        *_ops_argv_for_operation_id("worker-script-download-worker"),
                        "--path-param",
                        "account_id=acc1",
                        "--path-param",
                        "script_name=s1",
                        "--out",
                        str(out_file),
                    ]
                )
            self.assertEqual(rc2, 0)
            payload2 = json.loads(buf2.getvalue())
            self.assertTrue(payload2["ok"])
            self.assertFalse(payload2["dry_run"])
            self.assertTrue(out_file.exists())
            self.assertNotIn("console.log", buf2.getvalue())

    def test_operations_call_radar_http_refuses_missing_out_on_apply(self) -> None:
        def fake_request(_session, method, url, **kwargs):  # noqa: ANN001
            raise AssertionError(f"unexpected HTTP call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root)

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--apply",
                        *_ops_argv_for_operation_id("radar-get-http-summary"),
                        "--path-param",
                        "dimension=http_requests",
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])

    def test_operations_call_refuses_unknown_endpoint(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = _write_env(Path(d))
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "operations",
                        "workers_platform",
                        "not-a-real-operation",
                    ]
                )
            self.assertEqual(rc, 1)
            payload = json.loads(buf.getvalue())
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["error_type"], "ValidationError")

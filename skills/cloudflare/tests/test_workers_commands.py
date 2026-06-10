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


class TestWorkersCommands(unittest.TestCase):
    def test_account_id_defaults_are_used_when_omitted(self) -> None:
        calls: list[str] = []

        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
            calls.append(str(url))
            return _DummyResponse(status=200, url=url, obj={"success": True, "errors": [], "messages": [], "result": {}})

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root)

            # Set local default (no API call).
            sink = io.StringIO()
            with redirect_stdout(sink):
                _ = main(["--env-file", str(env_path), "accounts", "set-default", "--account-id", "acc_default"])

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--env-file", str(env_path), "workers", "subdomain", "get"])
            self.assertEqual(rc, 0)
            self.assertTrue(calls)
            self.assertEqual(calls[0], "http://example.invalid/client/v4/accounts/acc_default/workers/subdomain")

    def test_scripts_get_uses_settings_endpoint(self) -> None:
        calls: list[dict[str, Any]] = []

        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
            calls.append({"method": method, "url": url, "params": kwargs.get("params")})
            return _DummyResponse(
                status=200,
                url=url,
                obj={"success": True, "errors": [], "messages": [], "result": {"name": "w"}},
            )

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            env_path = _write_env(Path(d))
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "workers",
                        "scripts",
                        "get",
                        "--account-id",
                        "acc1",
                        "--script-name",
                        "hello",
                    ]
                )
            self.assertEqual(rc, 0)
            self.assertTrue(calls)
            self.assertEqual(calls[0]["method"], "GET")
            self.assertEqual(
                calls[0]["url"],
                "http://example.invalid/client/v4/accounts/acc1/workers/scripts/hello/settings",
            )
            self.assertNotEqual(
                calls[0]["url"],
                "http://example.invalid/client/v4/accounts/acc1/workers/scripts/hello",
            )

    def test_kv_metadata_get_never_uses_values_endpoint(self) -> None:
        calls: list[str] = []

        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
            calls.append(str(url))
            return _DummyResponse(
                status=200,
                url=url,
                obj={"success": True, "errors": [], "messages": [], "result": {"metadata": {"k": "v"}}},
            )

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            env_path = _write_env(Path(d))
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "workers",
                        "kv",
                        "keys",
                        "metadata-get",
                        "--account-id",
                        "acc1",
                        "--namespace-id",
                        "ns1",
                        "--key-name",
                        "k1",
                    ]
                )
            self.assertEqual(rc, 0)
            self.assertTrue(calls)
            self.assertIn("/metadata/k1", calls[0])
            self.assertNotIn("/values/", calls[0])

    def test_kv_keys_list_all_uses_cursor_pagination(self) -> None:
        calls: list[dict[str, Any]] = []

        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
            params = kwargs.get("params") or {}
            calls.append({"url": str(url), "params": dict(params)})
            cur = params.get("cursor")
            if not cur:
                obj = {
                    "success": True,
                    "errors": [],
                    "messages": [],
                    "result": [{"name": "a"}],
                    "result_info": {"cursors": {"after": "NEXT"}},
                }
            else:
                obj = {"success": True, "errors": [], "messages": [], "result": [{"name": "b"}], "result_info": {}}
            return _DummyResponse(status=200, url=url, obj=obj)

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            env_path = _write_env(Path(d))
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "workers",
                        "kv",
                        "keys",
                        "list",
                        "--account-id",
                        "acc1",
                        "--namespace-id",
                        "ns1",
                        "--all",
                        "--max-rows",
                        "10",
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["count"], 2)
            self.assertEqual(len(calls), 2)
            self.assertNotIn("cursor", calls[0]["params"])
            self.assertEqual(calls[1]["params"]["cursor"], "NEXT")

    def test_dispatch_scripts_get_uses_settings_not_content(self) -> None:
        calls: list[str] = []

        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
            calls.append(str(url))
            return _DummyResponse(status=200, url=url, obj={"success": True, "errors": [], "messages": [], "result": {}})

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            env_path = _write_env(Path(d))
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "workers",
                        "dispatch",
                        "scripts",
                        "get",
                        "--account-id",
                        "acc1",
                        "--dispatch-namespace",
                        "ns",
                        "--script-name",
                        "s1",
                    ]
                )
            self.assertEqual(rc, 0)
            self.assertTrue(calls)
            self.assertIn("/settings", calls[0])
            self.assertNotIn("/content", calls[0])

    def test_account_settings_and_placement_regions_paths(self) -> None:
        calls: list[str] = []

        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
            calls.append(str(url))
            return _DummyResponse(status=200, url=url, obj={"success": True, "errors": [], "messages": [], "result": {}})

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            env_path = _write_env(Path(d))
            sink = io.StringIO()
            with redirect_stdout(sink):
                _ = main(["--env-file", str(env_path), "workers", "account-settings", "get", "--account-id", "acc1"])
            with redirect_stdout(sink):
                _ = main(["--env-file", str(env_path), "workers", "placement", "regions", "list", "--account-id", "acc1"])
            self.assertEqual(calls[0], "http://example.invalid/client/v4/accounts/acc1/workers/account-settings")
            self.assertEqual(calls[1], "http://example.invalid/client/v4/accounts/acc1/workers/placement/regions")

    def test_platforms_list_and_get_paths(self) -> None:
        calls: list[str] = []

        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
            calls.append(str(url))
            return _DummyResponse(status=200, url=url, obj={"success": True, "errors": [], "messages": [], "result": []})

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            env_path = _write_env(Path(d))
            sink = io.StringIO()
            with redirect_stdout(sink):
                _ = main(["--env-file", str(env_path), "workers", "platforms", "list", "--account-id", "acc1"])
            with redirect_stdout(sink):
                _ = main(
                    [
                        "--env-file",
                        str(env_path),
                        "workers",
                        "platforms",
                        "get",
                        "--account-id",
                        "acc1",
                        "--worker-id",
                        "w1",
                    ]
                )
            self.assertEqual(calls[0], "http://example.invalid/client/v4/accounts/acc1/workers/workers")
            self.assertEqual(calls[1], "http://example.invalid/client/v4/accounts/acc1/workers/workers/w1")

    def test_services_env_settings_get_path(self) -> None:
        calls: list[str] = []

        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
            calls.append(str(url))
            return _DummyResponse(status=200, url=url, obj={"success": True, "errors": [], "messages": [], "result": {}})

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            env_path = _write_env(Path(d))
            sink = io.StringIO()
            with redirect_stdout(sink):
                _ = main(
                    [
                        "--env-file",
                        str(env_path),
                        "workers",
                        "services",
                        "env",
                        "settings",
                        "get",
                        "--account-id",
                        "acc1",
                        "--service-name",
                        "svc1",
                        "--environment-name",
                        "prod",
                    ]
                )
            self.assertEqual(
                calls[0],
                "http://example.invalid/client/v4/accounts/acc1/workers/services/svc1/environments/prod/settings",
            )

    def test_scripts_extras_paths(self) -> None:
        calls: list[str] = []

        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
            calls.append(str(url))
            return _DummyResponse(status=200, url=url, obj={"success": True, "errors": [], "messages": [], "result": []})

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            env_path = _write_env(Path(d))
            sink = io.StringIO()
            with redirect_stdout(sink):
                _ = main(
                    [
                        "--env-file",
                        str(env_path),
                        "workers",
                        "scripts",
                        "schedules",
                        "get",
                        "--account-id",
                        "acc1",
                        "--script-name",
                        "hello",
                    ]
                )
            with redirect_stdout(sink):
                _ = main(
                    [
                        "--env-file",
                        str(env_path),
                        "workers",
                        "scripts",
                        "script-settings",
                        "get",
                        "--account-id",
                        "acc1",
                        "--script-name",
                        "hello",
                    ]
                )
            with redirect_stdout(sink):
                _ = main(
                    [
                        "--env-file",
                        str(env_path),
                        "workers",
                        "scripts",
                        "usage-model",
                        "get",
                        "--account-id",
                        "acc1",
                        "--script-name",
                        "hello",
                    ]
                )
            with redirect_stdout(sink):
                _ = main(
                    [
                        "--env-file",
                        str(env_path),
                        "workers",
                        "scripts",
                        "subdomain",
                        "get",
                        "--account-id",
                        "acc1",
                        "--script-name",
                        "hello",
                    ]
                )
            with redirect_stdout(sink):
                _ = main(
                    [
                        "--env-file",
                        str(env_path),
                        "workers",
                        "scripts",
                        "secrets",
                        "list",
                        "--account-id",
                        "acc1",
                        "--script-name",
                        "hello",
                    ]
                )
            with redirect_stdout(sink):
                _ = main(
                    [
                        "--env-file",
                        str(env_path),
                        "workers",
                        "scripts",
                        "secrets",
                        "get",
                        "--account-id",
                        "acc1",
                        "--script-name",
                        "hello",
                        "--secret-name",
                        "s1",
                    ]
                )
            self.assertEqual(calls[0], "http://example.invalid/client/v4/accounts/acc1/workers/scripts/hello/schedules")
            self.assertEqual(
                calls[1],
                "http://example.invalid/client/v4/accounts/acc1/workers/scripts/hello/script-settings",
            )
            self.assertEqual(calls[2], "http://example.invalid/client/v4/accounts/acc1/workers/scripts/hello/usage-model")
            self.assertEqual(calls[3], "http://example.invalid/client/v4/accounts/acc1/workers/scripts/hello/subdomain")
            self.assertEqual(calls[4], "http://example.invalid/client/v4/accounts/acc1/workers/scripts/hello/secrets")
            self.assertEqual(calls[5], "http://example.invalid/client/v4/accounts/acc1/workers/scripts/hello/secrets/s1")

    def test_dispatch_scripts_extras_path(self) -> None:
        calls: list[str] = []

        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
            calls.append(str(url))
            return _DummyResponse(status=200, url=url, obj={"success": True, "errors": [], "messages": [], "result": []})

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            env_path = _write_env(Path(d))
            sink = io.StringIO()
            with redirect_stdout(sink):
                _ = main(
                    [
                        "--env-file",
                        str(env_path),
                        "workers",
                        "dispatch",
                        "scripts",
                        "bindings",
                        "list",
                        "--account-id",
                        "acc1",
                        "--dispatch-namespace",
                        "ns1",
                        "--script-name",
                        "s1",
                    ]
                )
            self.assertEqual(
                calls[0],
                "http://example.invalid/client/v4/accounts/acc1/workers/dispatch/namespaces/ns1/scripts/s1/bindings",
            )

    def test_builds_and_pipelines_paths(self) -> None:
        calls: list[str] = []

        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
            calls.append(str(url))
            return _DummyResponse(status=200, url=url, obj={"success": True, "errors": [], "messages": [], "result": []})

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            env_path = _write_env(Path(d))
            sink = io.StringIO()
            with redirect_stdout(sink):
                _ = main(
                    [
                        "--env-file",
                        str(env_path),
                        "workers",
                        "builds",
                        "list",
                        "--account-id",
                        "acc1",
                        "--external-script-id",
                        "ext1",
                    ]
                )
            with redirect_stdout(sink):
                _ = main(["--env-file", str(env_path), "workers", "pipelines", "list", "--account-id", "acc1"])
            with redirect_stdout(sink):
                _ = main(
                    [
                        "--env-file",
                        str(env_path),
                        "workers",
                        "pipelines",
                        "legacy",
                        "get",
                        "--account-id",
                        "acc1",
                        "--pipeline-name",
                        "p1",
                    ]
                )
            self.assertEqual(calls[0], "http://example.invalid/client/v4/accounts/acc1/builds/workers/ext1/builds")
            self.assertEqual(calls[1], "http://example.invalid/client/v4/accounts/acc1/pipelines/v1/pipelines")
            self.assertEqual(calls[2], "http://example.invalid/client/v4/accounts/acc1/pipelines/p1")

    def test_routes_list_path(self) -> None:
        calls: list[str] = []

        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
            calls.append(str(url))
            return _DummyResponse(status=200, url=url, obj={"success": True, "errors": [], "messages": [], "result": []})

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            env_path = _write_env(Path(d))
            sink = io.StringIO()
            with redirect_stdout(sink):
                _ = main(["--env-file", str(env_path), "workers", "routes", "list", "--zone-id", "z1"])
            self.assertEqual(calls[0], "http://example.invalid/client/v4/zones/z1/workers/routes")

    def test_versions_and_deployments_and_tails_paths(self) -> None:
        calls: list[str] = []

        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
            calls.append(str(url))
            return _DummyResponse(status=200, url=url, obj={"success": True, "errors": [], "messages": [], "result": []})

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            env_path = _write_env(Path(d))
            sink = io.StringIO()
            with redirect_stdout(sink):
                _ = main(
                    [
                        "--env-file",
                        str(env_path),
                        "workers",
                        "versions",
                        "list",
                        "--account-id",
                        "acc1",
                        "--script-name",
                        "s",
                    ]
                )
            with redirect_stdout(sink):
                _ = main(
                    [
                        "--env-file",
                        str(env_path),
                        "workers",
                        "deployments",
                        "get",
                        "--account-id",
                        "acc1",
                        "--script-name",
                        "s",
                        "--deployment-id",
                        "d1",
                    ]
                )
            with redirect_stdout(sink):
                _ = main(
                    [
                        "--env-file",
                        str(env_path),
                        "workers",
                        "tails",
                        "list",
                        "--account-id",
                        "acc1",
                        "--script-name",
                        "s",
                    ]
                )
            self.assertEqual(calls[0], "http://example.invalid/client/v4/accounts/acc1/workers/scripts/s/versions")
            self.assertEqual(
                calls[1],
                "http://example.invalid/client/v4/accounts/acc1/workers/scripts/s/deployments/d1",
            )
            self.assertEqual(calls[2], "http://example.invalid/client/v4/accounts/acc1/workers/scripts/s/tails")

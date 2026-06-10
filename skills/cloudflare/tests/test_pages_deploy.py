from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from cloudflare_api_tool.cli import main
from cloudflare_api_tool.cloudflare import CloudflareResult
from cloudflare_api_tool.errors import ToolError
from cloudflare_api_tool.http import HttpResponse


def _write_env(root: Path, *, token: str = "T") -> Path:
    env = root / ".env"
    env.write_text(
        "\n".join(
            [
                "CLOUDFLARE_API_BASE_URL=http://example.invalid/client/v4",
                f"CLOUDFLARE_API_TOKEN={token}",
                "CLOUDFLARE_API_ACCOUNT_ID=acc1",
                "CLOUDFLARE_TIMEOUT_S=30",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return env


class TestPagesDeployCommand(unittest.TestCase):
    def _base_args(self, project_dir: Path, env_path: Path) -> list[str]:
        return [
            "--output",
            "json",
            "--env-file",
            str(env_path),
            "--project-dir",
            str(project_dir),
            "pages",
            "deploy",
            "--account-id",
            "acc1",
            "--project-name",
            "site",
            "--source-dir",
            str(project_dir / "build"),
        ]

    def _create_static_dir(self, root: Path) -> Path:
        build = root / "build"
        build.mkdir(parents=True, exist_ok=True)
        (build / "index.html").write_text("hello", encoding="utf-8")
        (build / "_headers").write_text("/*\n  X-Test: yes\n", encoding="utf-8")
        return build

    def test_plan_emits_safe_plan(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            env = _write_env(tmp_path)
            static_dir = self._create_static_dir(tmp_path)
            buf = io.StringIO()
            args = self._base_args(tmp_path, env)
            with patch("cloudflare_api_tool.cloudflare.CloudflareClient.get_json") as mock_get_json:
                with redirect_stdout(buf):
                    rc = main(args)
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload.get("ok"))
            self.assertTrue(payload.get("dry_run"))
            mock_get_json.assert_not_called()
            selector = payload["plan"].get("selector", {})
            self.assertEqual(selector.get("source_dir"), str(static_dir))
            self.assertEqual(selector.get("target_environment"), "production")
            self.assertEqual(selector.get("production_branch"), "main")
            self.assertIn("direct-upload asset flow", payload["plan"]["risk_reasons"][0])
            self.assertIn("Dry-run is local only", payload["plan"]["notes"][0])

    def test_apply_uploads_assets_and_reads_back_deployment(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            env = _write_env(tmp_path)
            static_dir = self._create_static_dir(tmp_path)
            out_file = tmp_path / "deploy.json"

            get_json_calls: list[str] = []
            request_raw_calls: list[tuple[str, str, dict[str, object]]] = []

            def fake_get_json(self, path, **kwargs):  # noqa: ANN001
                del kwargs
                get_json_calls.append(path)
                if path == "/accounts/acc1/pages/projects/site":
                    return CloudflareResult(result={"production_branch": "main"}, result_info=None)
                if path == "/accounts/acc1/pages/projects/site/upload-token":
                    return CloudflareResult(result={"jwt": "aaa.eyJtYXhfZmlsZV9jb3VudF9hbGxvd2VkIjoyMH0.ccc"}, result_info=None)
                if path == "/accounts/acc1/pages/projects/site/deployments/dep1":
                    return CloudflareResult(
                        result={
                            "id": "dep1",
                            "environment": "preview",
                            "latest_stage": {"name": "deploy", "status": "success"},
                        },
                        result_info=None,
                    )
                raise AssertionError(f"unexpected get_json path: {path}")

            def fake_request_raw(self, method, path, **kwargs):  # noqa: ANN001
                request_raw_calls.append((method, path, kwargs))
                if path == "/pages/assets/upload":
                    return HttpResponse(status=200, headers={}, body=b'{"success":true,"result":null}', url="http://example.invalid/upload", duration_ms=10, attempts=1)
                if path == "/pages/assets/upsert-hashes":
                    return HttpResponse(status=200, headers={}, body=b'{"success":true,"result":null}', url="http://example.invalid/upsert", duration_ms=10, attempts=1)
                if path == "/accounts/acc1/pages/projects/site/deployments":
                    body = (
                        b'{"success":true,"result":{"id":"dep1","environment":"preview","url":"https://dep1.pages.dev"}}'
                    )
                    return HttpResponse(status=200, headers={}, body=body, url="http://example.invalid/deploy", duration_ms=10, attempts=1)
                raise AssertionError(f"unexpected request_raw path: {path}")

            def fake_request_json(self, method, path, **kwargs):  # noqa: ANN001
                if method == "POST" and path == "/pages/assets/check-missing":
                    body = kwargs.get("json_body") or {}
                    hashes = body.get("hashes") if isinstance(body, dict) else None
                    return CloudflareResult(result=list(hashes or []), result_info=None)
                raise AssertionError(f"unexpected request_json call: {method} {path}")

            with (
                patch("cloudflare_api_tool.cloudflare.CloudflareClient.get_json", new=fake_get_json),
                patch("cloudflare_api_tool.cloudflare.CloudflareClient.request_json", new=fake_request_json),
                patch("cloudflare_api_tool.cloudflare.CloudflareClient.request_raw", new=fake_request_raw),
            ):
                buf = io.StringIO()
                args = [
                    "--apply",
                    "--yes",
                    "--ack-no-snapshot",
                    "--output",
                    "json",
                    "--env-file",
                    str(env),
                    "--project-dir",
                    str(tmp_path),
                    "pages",
                    "deploy",
                    "--account-id",
                    "acc1",
                    "--project-name",
                    "site",
                    "--branch",
                    "preview-proof",
                    "--source-dir",
                    str(static_dir),
                    "--out",
                    str(out_file),
                ]
                with redirect_stdout(buf):
                    rc = main(args)

            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertFalse(payload.get("refused", False))
            self.assertTrue(out_file.exists())

            self.assertIn("/accounts/acc1/pages/projects/site", get_json_calls)
            self.assertIn("/accounts/acc1/pages/projects/site/upload-token", get_json_calls)
            self.assertTrue(any(path == "/accounts/acc1/pages/projects/site/deployments" for _, path, _ in request_raw_calls))

    def test_apply_creates_project_when_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            env = _write_env(tmp_path)
            static_dir = self._create_static_dir(tmp_path)
            out_file = tmp_path / "deploy.json"

            request_json_calls: list[tuple[str, str, dict[str, object]]] = []

            def fake_get_json(self, path, **kwargs):  # noqa: ANN001
                del kwargs
                if path == "/accounts/acc1/pages/projects/site":
                    raise ToolError("Cloudflare API error for GET /accounts/acc1/pages/projects/site: HTTP 404: project not found")
                if path == "/accounts/acc1/pages/projects/site/upload-token":
                    return CloudflareResult(result={"jwt": "aaa.eyJtYXhfZmlsZV9jb3VudF9hbGxvd2VkIjoyMH0.ccc"}, result_info=None)
                if path == "/accounts/acc1/pages/projects/site/deployments/dep2":
                    return CloudflareResult(
                        result={
                            "id": "dep2",
                            "environment": "production",
                            "latest_stage": {"name": "deploy", "status": "success"},
                        },
                        result_info=None,
                    )
                raise AssertionError(f"unexpected get_json path: {path}")

            def fake_request_json(self, method, path, **kwargs):  # noqa: ANN001
                request_json_calls.append((method, path, kwargs))
                if method == "POST" and path == "/accounts/acc1/pages/projects":
                    body = kwargs.get("json_body") or {}
                    return CloudflareResult(
                        result={
                            "name": body.get("name"),
                            "production_branch": body.get("production_branch"),
                        },
                        result_info=None,
                    )
                if method == "POST" and path == "/pages/assets/check-missing":
                    body = kwargs.get("json_body") or {}
                    hashes = body.get("hashes") if isinstance(body, dict) else None
                    return CloudflareResult(result=list(hashes or []), result_info=None)
                raise AssertionError(f"unexpected request_json call: {method} {path}")

            def fake_request_raw(self, method, path, **kwargs):  # noqa: ANN001
                if path == "/pages/assets/upload":
                    return HttpResponse(status=200, headers={}, body=b'{"success":true,"result":null}', url="http://example.invalid/upload", duration_ms=10, attempts=1)
                if path == "/pages/assets/upsert-hashes":
                    return HttpResponse(status=200, headers={}, body=b'{"success":true,"result":null}', url="http://example.invalid/upsert", duration_ms=10, attempts=1)
                if path == "/accounts/acc1/pages/projects/site/deployments":
                    body = (
                        b'{"success":true,"result":{"id":"dep2","environment":"production","url":"https://dep2.pages.dev"}}'
                    )
                    return HttpResponse(status=200, headers={}, body=body, url="http://example.invalid/deploy", duration_ms=10, attempts=1)
                raise AssertionError(f"unexpected request_raw path: {path}")

            with (
                patch("cloudflare_api_tool.cloudflare.CloudflareClient.get_json", new=fake_get_json),
                patch("cloudflare_api_tool.cloudflare.CloudflareClient.request_json", new=fake_request_json),
                patch("cloudflare_api_tool.cloudflare.CloudflareClient.request_raw", new=fake_request_raw),
            ):
                buf = io.StringIO()
                args = [
                    "--apply",
                    "--yes",
                    "--ack-no-snapshot",
                    "--output",
                    "json",
                    "--env-file",
                    str(env),
                    "--project-dir",
                    str(tmp_path),
                    "pages",
                    "deploy",
                    "--account-id",
                    "acc1",
                    "--project-name",
                    "site",
                    "--production-branch",
                    "main",
                    "--source-dir",
                    str(static_dir),
                    "--out",
                    str(out_file),
                ]
                with redirect_stdout(buf):
                    rc = main(args)

            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertFalse(payload.get("refused", False))
            self.assertTrue(out_file.exists())
            self.assertTrue(any(path == "/accounts/acc1/pages/projects" for _, path, _ in request_json_calls))

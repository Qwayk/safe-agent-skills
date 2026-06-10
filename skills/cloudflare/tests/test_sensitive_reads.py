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


class TestSensitiveReads(unittest.TestCase):
    def test_scripts_download_dry_run_does_not_call_api(self) -> None:
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
                        "workers",
                        "scripts",
                        "download",
                        "--account-id",
                        "acc1",
                        "--script-name",
                        "hello",
                        "--out",
                        "hello.js",
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])

    def test_scripts_download_apply_writes_file_and_never_prints_content(self) -> None:
        secret_bytes = b"// SECRET_WORKER_CODE\\nconsole.log('hi')\\n"

        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
            if method == "GET" and str(url).endswith("/accounts/acc1/workers/scripts/hello"):
                return _DummyResponse(status=200, url=url, body=secret_bytes, headers={"Content-Type": "application/javascript"})
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
                        "workers",
                        "scripts",
                        "download",
                        "--account-id",
                        "acc1",
                        "--script-name",
                        "hello",
                        "--out",
                        "hello.js",
                    ]
                )
            self.assertEqual(rc, 0)
            out_text = buf.getvalue()
            self.assertNotIn("SECRET_WORKER_CODE", out_text)
            payload = json.loads(out_text)
            self.assertTrue(payload["ok"])
            receipt = payload["receipt"]
            diff = receipt["diff_applied"][0]
            self.assertEqual(diff["bytes_written"], len(secret_bytes))
            written = Path(diff["abs_path"])
            self.assertTrue(written.exists())
            self.assertEqual(written.read_bytes(), secret_bytes)

    def test_kv_values_apply_writes_file_and_never_prints_value(self) -> None:
        secret_bytes = b"SUPER_SECRET_VALUE"

        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
            if method == "GET" and str(url).endswith("/accounts/acc1/storage/kv/namespaces/ns1/values/k1"):
                return _DummyResponse(status=200, url=url, body=secret_bytes, headers={"Content-Type": "application/octet-stream"})
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
                        "workers",
                        "kv",
                        "values",
                        "get",
                        "--account-id",
                        "acc1",
                        "--namespace-id",
                        "ns1",
                        "--key-name",
                        "k1",
                        "--out",
                        "kv.bin",
                    ]
                )
            self.assertEqual(rc, 0)
            out_text = buf.getvalue()
            self.assertNotIn("SUPER_SECRET_VALUE", out_text)
            payload = json.loads(out_text)
            self.assertTrue(payload["ok"])
            diff = payload["receipt"]["diff_applied"][0]
            written = Path(diff["abs_path"])
            self.assertTrue(written.exists())
            self.assertEqual(written.read_bytes(), secret_bytes)

    def test_operations_images_blob_apply_writes_file_and_never_prints_bytes(self) -> None:
        secret_bytes = b"SECRET_IMAGE_BYTES\x00\x01\x02"

        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
            if method == "GET" and str(url).endswith("/accounts/acc1/images/v1/img1/blob"):
                return _DummyResponse(status=200, url=url, body=secret_bytes, headers={"Content-Type": "application/octet-stream"})
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root)
            project_dir = root / "proj"
            buf = io.StringIO()
            cmd = allowlisted_operation_command_by_operation_id("cloudflare-images-base-image")
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
                        "--path-param",
                        "image_id=img1",
                        "--out",
                        "img.bin",
                    ]
                )
            self.assertEqual(rc, 0)
            out_text = buf.getvalue()
            self.assertNotIn("SECRET_IMAGE_BYTES", out_text)
            payload = json.loads(out_text)
            self.assertTrue(payload["ok"])
            file_obj = payload.get("file") or {}
            written = Path(file_obj.get("out_path") or "")
            self.assertTrue(written.exists())
            self.assertEqual(written.read_bytes(), secret_bytes)

    def test_operations_images_direct_upload_apply_requires_no_yes_and_never_prints_url(self) -> None:
        secret_marker = "UPLOAD_URL_SECRET"
        body = json.dumps(
            {
                "success": True,
                "errors": [],
                "messages": [],
                "result": {"uploadURL": f"https://example.invalid/{secret_marker}"},
            }
        ).encode("utf-8")

        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
            if method == "POST" and str(url).endswith("/accounts/acc1/images/v2/direct_upload"):
                return _DummyResponse(status=200, url=url, body=body, headers={"Content-Type": "application/json"})
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root)
            project_dir = root / "proj"
            buf = io.StringIO()
            cmd = allowlisted_operation_command_by_operation_id("cloudflare-images-create-authenticated-direct-upload-url-v-2")
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
                        "direct_upload.json",
                    ]
                )
            self.assertEqual(rc, 0)
            out_text = buf.getvalue()
            self.assertNotIn(secret_marker, out_text)
            payload = json.loads(out_text)
            self.assertTrue(payload["ok"])
            file_obj = payload.get("file") or {}
            written = Path(file_obj.get("out_path") or "")
            self.assertTrue(written.exists())
            self.assertEqual(written.read_bytes(), body)

    def test_scripts_download_http_error_does_not_write_file(self) -> None:
        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
            if method == "GET" and str(url).endswith("/accounts/acc1/workers/scripts/hello"):
                # Typical Cloudflare error envelope.
                body = json.dumps({"success": False, "errors": [{"code": 10000, "message": "Denied"}], "messages": [], "result": None}).encode(
                    "utf-8"
                )
                return _DummyResponse(status=403, url=url, body=body, headers={"Content-Type": "application/json"})
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root)
            project_dir = root / "proj"
            out_file = project_dir / "hello.js"
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--project-dir",
                        str(project_dir),
                        "--apply",
                        "workers",
                        "scripts",
                        "download",
                        "--account-id",
                        "acc1",
                        "--script-name",
                        "hello",
                        "--out",
                        "hello.js",
                    ]
                )
            self.assertEqual(rc, 1)
            self.assertFalse(out_file.exists())

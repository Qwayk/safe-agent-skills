from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
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


class TestRegistrarCommands(unittest.TestCase):
    def test_registrar_domains_list_is_dry_run_and_does_not_call_api(self) -> None:
        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root)
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--env-file", str(env_path), "registrar", "domains", "list", "--account-id", "acct1"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])

    def test_registrar_domains_list_apply_missing_out_refuses_and_does_not_call_api(self) -> None:
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
                        "registrar",
                        "domains",
                        "list",
                        "--account-id",
                        "acct1",
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])

    def test_registrar_domains_list_apply_writes_file_and_does_not_print_body(self) -> None:
        secret_bytes = b'{"domain":"example.com","registrant":"SECRET_REGISTRANT_SHOULD_NOT_PRINT"}\n'

        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = _write_env(root)
            project_dir = root / "proj"

            def fake_request(self, method, url, **kwargs):  # noqa: ANN001
                if method == "GET" and str(url).endswith("/accounts/acct1/registrar/domains"):
                    return _DummyResponse(status=200, url=url, body=secret_bytes)
                raise AssertionError(f"unexpected call: {method} {url}")

            with patch("requests.Session.request", new=fake_request):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = main(
                        [
                            "--env-file",
                            str(env_path),
                            "--project-dir",
                            str(project_dir),
                            "--apply",
                            "registrar",
                            "domains",
                            "list",
                            "--account-id",
                            "acct1",
                            "--out",
                            "domains.json",
                        ]
                    )
                self.assertEqual(rc, 0)
                out_text = buf.getvalue()
                self.assertNotIn("SECRET_REGISTRANT_SHOULD_NOT_PRINT", out_text)
                payload = json.loads(out_text)
                self.assertTrue(payload["ok"])
                out_path = project_dir / "domains.json"
                self.assertTrue(out_path.exists())
                self.assertEqual(out_path.read_bytes(), secret_bytes)

    def test_registrar_domains_get_apply_writes_file_and_does_not_print_body(self) -> None:
        secret_bytes = b'{"domain":"example.com","registrant":"SECRET_REGISTRANT_SHOULD_NOT_PRINT"}\n'

        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = _write_env(root)
            project_dir = root / "proj"

            def fake_request(self, method, url, **kwargs):  # noqa: ANN001
                if method == "GET" and str(url).endswith("/accounts/acct1/registrar/domains/example.com"):
                    return _DummyResponse(status=200, url=url, body=secret_bytes)
                raise AssertionError(f"unexpected call: {method} {url}")

            with patch("requests.Session.request", new=fake_request):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = main(
                        [
                            "--env-file",
                            str(env_path),
                            "--project-dir",
                            str(project_dir),
                            "--apply",
                            "registrar",
                            "domains",
                            "get",
                            "--account-id",
                            "acct1",
                            "--domain-name",
                            "example.com",
                            "--out",
                            "domain.json",
                        ]
                    )
                self.assertEqual(rc, 0)
                out_text = buf.getvalue()
                self.assertNotIn("SECRET_REGISTRANT_SHOULD_NOT_PRINT", out_text)
                payload = json.loads(out_text)
                self.assertTrue(payload["ok"])
                out_path = project_dir / "domain.json"
                self.assertTrue(out_path.exists())
                self.assertEqual(out_path.read_bytes(), secret_bytes)

    def test_registrar_domains_update_apply_missing_yes_refuses_and_does_not_call_api(self) -> None:
        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root)
            project_dir = root / "proj"
            body_path = root / "body.json"
            body_path.write_text('{"auto_renew":true}\n', encoding="utf-8")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--project-dir",
                        str(project_dir),
                        "--apply",
                        "registrar",
                        "domains",
                        "update",
                        "--account-id",
                        "acct1",
                        "--domain-name",
                        "example.com",
                        "--body-json-file",
                        str(body_path),
                        "--out",
                        "update.json",
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])

    def test_registrar_domains_update_apply_writes_file_and_does_not_print_body(self) -> None:
        secret_bytes = b'{"domain":"example.com","registrant":"SECRET_REGISTRANT_SHOULD_NOT_PRINT"}\n'

        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = _write_env(root)
            project_dir = root / "proj"
            body_path = root / "body.json"
            body_path.write_text('{"auto_renew":true}\n', encoding="utf-8")

            def fake_request(self, method, url, **kwargs):  # noqa: ANN001
                if method == "PUT" and str(url).endswith("/accounts/acct1/registrar/domains/example.com"):
                    return _DummyResponse(status=200, url=url, body=secret_bytes)
                if method == "GET" and str(url).endswith("/accounts/acct1/registrar/domains/example.com"):
                    # Read-back verification (must not leak to stdout; not written to the output file).
                    body = json.dumps(
                        {"success": True, "errors": [], "messages": [], "result": {"domain": "example.com"}},
                        ensure_ascii=False,
                    ).encode("utf-8")
                    return _DummyResponse(status=200, url=url, body=body)
                raise AssertionError(f"unexpected call: {method} {url}")

            with patch("requests.Session.request", new=fake_request):
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
                            "registrar",
                            "domains",
                            "update",
                            "--account-id",
                            "acct1",
                            "--domain-name",
                            "example.com",
                            "--body-json-file",
                            str(body_path),
                            "--out",
                            "update.json",
                        ]
                    )
                self.assertEqual(rc, 0)
                out_text = buf.getvalue()
                self.assertNotIn("SECRET_REGISTRANT_SHOULD_NOT_PRINT", out_text)
                payload = json.loads(out_text)
                self.assertTrue(payload["ok"])
                self.assertTrue(payload["refused"])
                out_path = project_dir / "update.json"
                self.assertFalse(out_path.exists())

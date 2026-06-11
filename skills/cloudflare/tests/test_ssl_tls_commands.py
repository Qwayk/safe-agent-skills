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


class TestSslTlsCommands(unittest.TestCase):
    def test_ssl_tls_analyze_apply_requires_out_but_not_yes(self) -> None:
        secret_bytes = b'{"analysis":"SECRET_ANALYSIS_SHOULD_NOT_PRINT"}\n'

        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
            if method == "POST" and str(url).endswith("/zones/zone1/ssl/analyze"):
                return _DummyResponse(status=200, url=url, body=secret_bytes)
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = _write_env(root)
            project_dir = root / "proj"

            # Missing --out refuses safely (no API calls).
            def fake_request_never(self, method, url, **kwargs):  # noqa: ANN001
                raise AssertionError(f"unexpected call: {method} {url}")

            with patch("requests.Session.request", new=fake_request_never):
                buf1 = io.StringIO()
                with redirect_stdout(buf1):
                    rc1 = main(
                        [
                            "--env-file",
                            str(env_path),
                            "--project-dir",
                            str(project_dir),
                            "--apply",
                            "ssl-tls",
                            "analyze",
                            "--zone-id",
                            "zone1",
                        ]
                    )
                self.assertEqual(rc1, 0)
                payload1 = json.loads(buf1.getvalue())
                self.assertTrue(payload1["ok"])
                self.assertTrue(payload1["refused"])

            # With --out succeeds without --yes and reports changed=false.
            with patch("requests.Session.request", new=fake_request):
                buf2 = io.StringIO()
                with redirect_stdout(buf2):
                    rc2 = main(
                        [
                            "--env-file",
                            str(env_path),
                            "--project-dir",
                            str(project_dir),
                            "--apply",
                            "ssl-tls",
                            "analyze",
                            "--zone-id",
                            "zone1",
                            "--out",
                            "analyze.json",
                        ]
                    )
                self.assertEqual(rc2, 0)
                out_text = buf2.getvalue()
                self.assertNotIn("SECRET_ANALYSIS_SHOULD_NOT_PRINT", out_text)
                payload2 = json.loads(out_text)
                self.assertTrue(payload2["ok"])
                self.assertFalse(payload2.get("changed"), "ssl-tls analyze should be read-like (changed=false)")
                out_path = project_dir / "analyze.json"
                self.assertTrue(out_path.exists())
                self.assertEqual(out_path.read_bytes(), secret_bytes)

    def test_ssl_tls_certificate_packs_restart_is_dry_run_and_apply_requires_out(self) -> None:
        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
            if method == "GET" and str(url).endswith("/zones/zone1/ssl/certificate_packs/pack1"):
                body = json.dumps({"success": True, "errors": [], "messages": [], "result": {"id": "pack1", "status": "pending_validation"}}).encode("utf-8")
                return _DummyResponse(status=200, url=url, body=body)
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root)
            project_dir = root / "proj"

            body_path = root / "body.json"
            body_path.write_text('{"validation_method":"txt"}\n', encoding="utf-8")

            # Dry-run saves before-state when a matching read path exists.
            buf1 = io.StringIO()
            with redirect_stdout(buf1):
                rc1 = main(
                    [
                        "--env-file",
                        str(env_path),
                        "ssl-tls",
                        "certificate-packs",
                        "restart",
                        "--zone-id",
                        "zone1",
                        "--certificate-pack-id",
                        "pack1",
                        "--body-json-file",
                        str(body_path),
                    ]
                )
            self.assertEqual(rc1, 0)
            payload1 = json.loads(buf1.getvalue())
            self.assertTrue(payload1["ok"])
            self.assertTrue(payload1["dry_run"])
            self.assertTrue(payload1["plan"]["before_state"]["saved"])

            # Apply without --out refuses safely (no network).
            buf2 = io.StringIO()
            with redirect_stdout(buf2):
                rc2 = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--project-dir",
                        str(project_dir),
                        "--apply",
                        "--yes",
                        "ssl-tls",
                        "certificate-packs",
                        "restart",
                        "--zone-id",
                        "zone1",
                        "--certificate-pack-id",
                        "pack1",
                        "--body-json-file",
                        str(body_path),
                    ]
                )
            self.assertEqual(rc2, 0)
            payload2 = json.loads(buf2.getvalue())
            self.assertTrue(payload2["ok"])
            self.assertTrue(payload2["refused"])

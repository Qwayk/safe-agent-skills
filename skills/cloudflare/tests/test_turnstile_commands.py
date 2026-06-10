from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from cloudflare_api_tool.cli import main


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


class _DummyResponse:
    def __init__(self, *, status: int, url: str, body: bytes):
        self.status_code = int(status)
        self.url = str(url)
        self.content = bytes(body)
        self.headers: dict[str, str] = {}


class TestTurnstileCommands(unittest.TestCase):
    def test_turnstile_widgets_list_is_dry_run_and_does_not_call_api(self) -> None:
        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
            raise AssertionError(f"unexpected call: {method} {url}")

        with tempfile.TemporaryDirectory() as d, patch("requests.Session.request", new=fake_request):
            root = Path(d)
            env_path = _write_env(root)
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--env-file", str(env_path), "turnstile", "widgets", "list", "--account-id", "acc1"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])

    def test_turnstile_widgets_list_apply_missing_out_refuses_and_does_not_call_api(self) -> None:
        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
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
                        "--project-dir",
                        str(root),
                        "--apply",
                        "turnstile",
                        "widgets",
                        "list",
                        "--account-id",
                        "acc1",
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])

    def test_turnstile_widgets_create_apply_missing_yes_refuses_and_does_not_call_api(self) -> None:
        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
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
                        "turnstile",
                        "widgets",
                        "create",
                        "--account-id",
                        "acc1",
                        "--body-json-file",
                        str(body),
                        "--out",
                        "out.json",
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])

    def test_turnstile_widgets_rotate_secret_apply_missing_ack_refuses_and_does_not_call_api(self) -> None:
        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
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
                        "--project-dir",
                        str(root),
                        "--apply",
                        "--yes",
                        "turnstile",
                        "widgets",
                        "rotate-secret",
                        "--account-id",
                        "acc1",
                        "--sitekey",
                        "sk1",
                        "--out",
                        "out.json",
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])

    def test_turnstile_widgets_create_apply_writes_file_and_does_not_print_secret(self) -> None:
        secret = "TOP_SECRET_SHOULD_NOT_PRINT"
        response_body = json.dumps({"success": True, "result": {"secret": secret}}, ensure_ascii=False).encode("utf-8")

        def fake_request(self, method, url, **kwargs):  # noqa: ANN001
            return _DummyResponse(status=200, url=url, body=response_body)

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
                        "--ack-irreversible",
                        "turnstile",
                        "widgets",
                        "create",
                        "--account-id",
                        "acc1",
                        "--body-json-file",
                        str(body),
                        "--out",
                        "out.json",
                    ]
                )
            self.assertEqual(rc, 0)
            stdout = buf.getvalue()
            self.assertNotIn(secret, stdout)

            payload = json.loads(stdout)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            out_file = root / "out.json"
            self.assertFalse(out_file.exists())

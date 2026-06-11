from __future__ import annotations

import io
import json as jsonlib
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from mercury_api_tool.cli import main


class _FakeResponse:
    def __init__(self, *, url: str, status_code: int, body: bytes):
        self.url = url
        self.status_code = status_code
        self.content = body
        self.headers = {"content-type": "application/json;charset=utf-8"}

    @property
    def text(self) -> str:
        return self.content.decode("utf-8", errors="replace")


class TestSignedUrlRedaction(unittest.TestCase):
    def test_attachment_metadata_does_not_emit_signed_url(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(
                "MERCURY_API_BASE_URL=https://api.mercury.com/api/v1\n"
                "MERCURY_API_TOKEN=secret-token:TEST_TOKEN_DO_NOT_LEAK\n"
                "MERCURY_AUTH_SCHEME=bearer\n"
                "MERCURY_TIMEOUT_S=30\n",
                encoding="utf-8",
            )

            signed_url = "https://files.example.com/download?sig=abc123"

            def _fake_request(self, method, url, headers=None, params=None, json=None, data=None, timeout=None):  # noqa: ANN001
                if url.endswith("/ar/attachments/att_123"):
                    body = jsonlib.dumps({"id": "att_123", "fileName": "invoice.pdf", "url": signed_url}).encode(
                        "utf-8"
                    )
                    return _FakeResponse(url=url, status_code=200, body=body)
                if url.endswith("/ar/invoices/inv_123/attachments"):
                    body = jsonlib.dumps(
                        [
                            {"id": "att_a", "fileName": "a.pdf", "url": signed_url},
                            {"id": "att_b", "fileName": "b.pdf", "url": signed_url},
                        ]
                    ).encode("utf-8")
                    return _FakeResponse(url=url, status_code=200, body=body)
                raise AssertionError(f"Unexpected URL: {url}")

            with patch("mercury_api_tool.http.requests.Session.request", new=_fake_request):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = main(
                        [
                            "--output",
                            "json",
                            "--env-file",
                            str(env_path),
                            "invoices",
                            "attachment",
                            "--attachment-id",
                            "att_123",
                        ]
                    )
                self.assertEqual(rc, 0)
                payload = jsonlib.loads(buf.getvalue())
                self.assertTrue(payload["ok"])
                attachment = payload["attachment"]
                self.assertNotIn("url", attachment)
                self.assertTrue(attachment.get("url_redacted"))

                buf2 = io.StringIO()
                with redirect_stdout(buf2):
                    rc2 = main(
                        [
                            "--output",
                            "json",
                            "--env-file",
                            str(env_path),
                            "invoices",
                            "attachments",
                            "--invoice-id",
                            "inv_123",
                        ]
                    )
                self.assertEqual(rc2, 0)
                payload2 = jsonlib.loads(buf2.getvalue())
                self.assertTrue(payload2["ok"])
                attachments = payload2["attachments"]
                self.assertIsInstance(attachments, list)
                for a in attachments:
                    self.assertNotIn("url", a)
                    self.assertTrue(a.get("url_redacted"))

                out_path = root / "download.bin"
                buf3 = io.StringIO()
                with redirect_stdout(buf3):
                    rc3 = main(
                        [
                            "--output",
                            "json",
                            "--env-file",
                            str(env_path),
                            "invoices",
                            "download-attachment",
                            "--attachment-id",
                            "att_123",
                            "--out",
                            str(out_path),
                        ]
                    )
                self.assertEqual(rc3, 0)
                payload3 = jsonlib.loads(buf3.getvalue())
                self.assertTrue(payload3["ok"])
                self.assertTrue(payload3["dry_run"])
                combined = jsonlib.dumps(payload3)
                self.assertNotIn(signed_url, combined)

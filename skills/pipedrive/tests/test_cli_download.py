from __future__ import annotations

import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from qwayk_pipedrive_safe_agent_cli.cli import main


class _Response:
    def __init__(self, status: int, headers: dict[str, str], body: bytes = b"", url: str = "https://api.test.pipedrive.com") -> None:
        self.status = status
        self.headers = headers
        self.body = body
        self.url = url


class _HttpClient:
    def __init__(self, responses: list[_Response] | None = None):
        self.calls: list[tuple[str, str, dict[str, str] | None, dict[str, object] | None, bool]] = []
        self._responses = list(responses or [])

    def request(
        self,
        method: str,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        params: dict[str, object] | None = None,
        allow_redirects: bool = True,
        stream: bool = False,
        **kwargs: object,
    ) -> _Response:
        self.calls.append((method, url, headers, params, bool(allow_redirects)))
        if self._responses:
            return self._responses.pop(0)
        return _Response(
            status=302,
            headers={"location": "https://downloads.test.pipedrive.com/file.zip", "content-length": "123", "content-type": "application/octet-stream"},
        )


def _write_env(path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write("PIPEDRIVE_API_DOMAIN=test-company\n")
        f.write("PIPEDRIVE_API_TOKEN=token-xyz\n")


class TestDownloadMetadataOnly(unittest.TestCase):
    def test_files_download_does_not_follow_redirect_or_download(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = os.path.join(td, ".env")
            _write_env(env_path)
            client = _HttpClient()

            buf = io.StringIO()
            with patch("qwayk_pipedrive_safe_agent_cli.cli.HttpClient", return_value=client):
                with redirect_stdout(buf):
                    rc = main(["--output", "json", "--env-file", env_path, "files", "download", "--id", "123"])

            self.assertEqual(rc, 0)
            self.assertEqual(len(client.calls), 1)
            method, _url, _headers, _params, allow_redirects = client.calls[0]
            self.assertEqual(method, "HEAD")
            self.assertFalse(allow_redirects)
            payload = json.loads(buf.getvalue())
            self.assertEqual(payload["http"]["method"], "HEAD")
            self.assertEqual(payload["data"]["download"], "redirect-metadata-only")
            self.assertEqual(payload["data"]["content_type"], "application/octet-stream")
            self.assertEqual(payload["http"]["status"], 302)

    def test_files_download_falls_back_to_get_when_head_is_not_allowed(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = os.path.join(td, ".env")
            _write_env(env_path)
            client = _HttpClient(
                responses=[
                    _Response(status=405, headers={}),
                    _Response(
                        status=200,
                        headers={"content-length": "456", "content-type": "application/pdf"},
                    ),
                ]
            )

            buf = io.StringIO()
            with patch("qwayk_pipedrive_safe_agent_cli.cli.HttpClient", return_value=client):
                with redirect_stdout(buf):
                    rc = main(["--output", "json", "--env-file", env_path, "files", "download", "--id", "123"])

            self.assertEqual(rc, 0)
            self.assertEqual(len(client.calls), 2)
            first_method, _url, _headers, _params, first_allow_redirects = client.calls[0]
            second_method, _url, _headers, _params, second_allow_redirects = client.calls[1]
            self.assertEqual(first_method, "HEAD")
            self.assertEqual(second_method, "GET")
            self.assertFalse(first_allow_redirects)
            self.assertFalse(second_allow_redirects)
            payload = json.loads(buf.getvalue())
            self.assertEqual(payload["http"]["method"], "GET")
            self.assertEqual(payload["data"]["download"], "metadata-only")
            self.assertEqual(payload["data"]["content_type"], "application/pdf")
            self.assertEqual(payload["http"]["status"], 200)

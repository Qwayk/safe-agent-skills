from __future__ import annotations

import os
import tempfile
import unittest
from unittest import mock

from pinterest_api_tool.http import DownloadExceededError, HttpClient


class _FakeStreamResponse:
    def __init__(self, *, status_code: int, url: str, chunks: list[bytes]) -> None:
        self.status_code = int(status_code)
        self.url = url
        self.headers = {"Content-Type": "application/octet-stream"}
        self._chunks = list(chunks)

    @property
    def text(self) -> str:  # noqa: D401
        return ""

    def iter_content(self, chunk_size: int = 8192):  # noqa: ANN001
        _ = chunk_size
        for c in self._chunks:
            yield c


class TestReportJobsDownloadCaps(unittest.TestCase):
    def test_download_writes_file_and_returns_metadata(self) -> None:
        http = HttpClient(timeout_s=30.0, verbose=False, user_agent="ua")
        resp = _FakeStreamResponse(status_code=200, url="https://example.com/file.bin", chunks=[b"a", b"bcd"])

        with tempfile.TemporaryDirectory() as td:
            out_path = os.path.join(td, "out.bin")
            with mock.patch.object(
                type(http._session),  # noqa: SLF001
                "request",
                return_value=resp,
            ):
                res = http.download_to_file(
                    "https://example.com/file.bin",
                    max_bytes=10,
                    dest_path=out_path,
                )

            self.assertEqual(res.status, 200)
            self.assertEqual(res.bytes_written, 4)
            self.assertTrue(os.path.exists(out_path))
            with open(out_path, "rb") as f:
                self.assertEqual(f.read(), b"abcd")

    def test_download_exceeds_max_bytes_and_fails_safely(self) -> None:
        http = HttpClient(timeout_s=30.0, verbose=False, user_agent="ua")
        resp = _FakeStreamResponse(status_code=200, url="https://example.com/file.bin", chunks=[b"x" * 9])

        with tempfile.TemporaryDirectory() as td:
            out_path = os.path.join(td, "out.bin")
            with mock.patch.object(
                type(http._session),  # noqa: SLF001
                "request",
                return_value=resp,
            ):
                with self.assertRaises(DownloadExceededError):
                    http.download_to_file(
                        "https://example.com/file.bin",
                        max_bytes=5,
                        dest_path=out_path,
                    )

            self.assertFalse(os.path.exists(out_path))

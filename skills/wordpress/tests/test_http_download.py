import hashlib
import os
import tempfile
import unittest

from wordpress_api_tool.http import HttpClient


class _FakeResponse:
    def __init__(self, *, chunks: list[bytes], content_type: str = "image/jpeg"):
        self.status_code = 200
        self.headers = {"content-type": content_type}
        self._chunks = chunks

    def raise_for_status(self) -> None:
        return None

    def iter_content(self, *, chunk_size: int):
        yield from self._chunks


class _FakeResponseError(_FakeResponse):
    def iter_content(self, *, chunk_size: int):
        yield b"abc"
        raise RuntimeError("boom")


class HttpDownloadTests(unittest.TestCase):
    def test_download_to_file_is_atomic_on_success(self) -> None:
        http = HttpClient(timeout_s=1.0, verbose=False)

        def fake_get(url, *, stream, timeout, headers):
            return _FakeResponse(chunks=[b"abc", b"def"])

        http._session.get = fake_get  # type: ignore[assignment]

        with tempfile.TemporaryDirectory() as td:
            out_path = os.path.join(td, "out.bin")
            meta = http.download_to_file("https://example.test/file", out_path=out_path)

            with open(out_path, "rb") as f:
                data = f.read()

            self.assertEqual(data, b"abcdef")
            self.assertFalse(os.path.exists(out_path + ".part"))
            self.assertEqual(meta["bytes"], 6)
            self.assertEqual(meta["sha256"], hashlib.sha256(b"abcdef").hexdigest())

    def test_download_to_file_cleans_partial_on_error(self) -> None:
        http = HttpClient(timeout_s=1.0, verbose=False)

        def fake_get(url, *, stream, timeout, headers):
            return _FakeResponseError(chunks=[b"abc"])

        http._session.get = fake_get  # type: ignore[assignment]

        with tempfile.TemporaryDirectory() as td:
            out_path = os.path.join(td, "out.bin")
            with self.assertRaises(RuntimeError):
                http.download_to_file("https://example.test/file", out_path=out_path)

            self.assertFalse(os.path.exists(out_path))
            self.assertFalse(os.path.exists(out_path + ".part"))

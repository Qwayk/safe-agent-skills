from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from meta_ads_api_tool.assets import download_assets, safe_asset_filename


class _StubResp:
    def __init__(self, body: bytes):
        self.body = body


class _StubHttp:
    def __init__(self, body: bytes):
        self._body = body
        self.calls: list[str] = []

    def request(self, method: str, url: str, *, headers=None, params=None, retries=0):  # type: ignore[override]
        self.calls.append(f"{method} {url}")
        return _StubResp(self._body)


class TestAssetsDownload(unittest.TestCase):
    def test_safe_asset_filename_is_stable(self) -> None:
        url = "https://cdn.example.com/path/to/file.jpg?x=1"
        a = safe_asset_filename(url)
        b = safe_asset_filename(url)
        self.assertEqual(a, b)
        self.assertTrue(a.endswith(".jpg"))

    def test_download_assets_skips_existing_when_if_missing(self) -> None:
        url = "https://cdn.example.com/a.png"
        items = [{"creative_id": "cr_1", "url": url, "kind": "image_url", "url_sha256": "sha"}]
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "assets"
            out.mkdir(parents=True, exist_ok=True)
            fname = safe_asset_filename(url)
            (out / fname).write_bytes(b"old")

            errors: list[dict] = []
            res = download_assets(http=_StubHttp(b"new"), items=items, out_dir=out, overwrite="if_missing", errors=errors)
            self.assertEqual(len(res), 1)
            self.assertEqual(res[0].status, "skipped_exists")
            self.assertEqual(errors, [])
            self.assertEqual((out / fname).read_bytes(), b"old")

    def test_download_assets_overwrites_when_always(self) -> None:
        url = "https://cdn.example.com/a.png"
        items = [{"creative_id": "cr_1", "url": url, "kind": "image_url", "url_sha256": "sha"}]
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "assets"
            out.mkdir(parents=True, exist_ok=True)
            fname = safe_asset_filename(url)
            (out / fname).write_bytes(b"old")

            errors: list[dict] = []
            http = _StubHttp(b"new")
            res = download_assets(http=http, items=items, out_dir=out, overwrite="always", errors=errors)
            self.assertEqual(len(res), 1)
            self.assertEqual(res[0].status, "downloaded")
            self.assertEqual(errors, [])
            self.assertEqual((out / fname).read_bytes(), b"new")
            self.assertEqual(len(http.calls), 1)


# Awin Publisher — enhanced-download error detection tests
from __future__ import annotations

import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

import requests

from awin_publisher_safe_agent_cli.cli import main


def _bytes_response(
    method: str,
    url: str,
    body_bytes: bytes,
    *,
    status: int = 200,
    content_type: str = "application/x-ndjson",
) -> requests.Response:
    response = requests.Response()
    response.status_code = status
    response._content = body_bytes
    response.headers["content-type"] = content_type
    response.url = url
    return response


def _run_cli(body_bytes: bytes, status: int = 200, *, previous: bytes | None = None) -> tuple[int, dict, bytes | None]:
    token = "TOKEN_TEST"
    with patch("awin_publisher_safe_agent_cli.http.requests.Session.request") as mocked:
        mocked.side_effect = lambda method, url, headers=None, params=None, **kw: _bytes_response(
            method, url, body_bytes, status=status, content_type="application/x-ndjson"
        )
        with tempfile.TemporaryDirectory() as td:
            env_file = os.path.join(td, ".env")
            out_path = Path(td) / "feed.jsonl"
            if previous is not None:
                out_path.write_bytes(previous)
            with open(env_file, "w", encoding="utf-8") as f:
                f.write(f"AWIN_API_TOKEN={token}\n")
            stdout_buf = io.StringIO()
            with redirect_stdout(stdout_buf):
                rc = main([
                    "--output", "json",
                    "--env-file", env_file,
                    "feeds", "enhanced-download",
                    "--publisher-id", "100",
                    "--advertiser-id", "200",
                    "--locale", "en_GB",
                    "--out", str(out_path),
                    "--overwrite",
                ])
            out = json.loads(stdout_buf.getvalue())
            saved = out_path.read_bytes() if out_path.exists() else None
            return rc, out, saved


class TestEnhancedDownloadErrorDetection(unittest.TestCase):
    """Correction 1: detect an Awin error object in the final JSONL line."""

    def test_final_line_error_object_refuses_success(self) -> None:
        error_body = b'{"product":"item1"}\n{"errors":[{"code":"ERR","message":"Something went wrong"}]}\n'
        rc, out, file_existed = _run_cli(error_body, 200)
        self.assertEqual(rc, 1)
        self.assertFalse(out["ok"])
        self.assertFalse(file_existed)

    def test_final_line_error_with_top_level_error_key(self) -> None:
        error_body = b'{"title":"Product row"}\n{"error":"Invalid advertiser","errorCode":"ADV_ERROR"}\n'
        rc, out, file_existed = _run_cli(error_body, 200)
        self.assertEqual(rc, 1)
        self.assertFalse(out["ok"])
        self.assertFalse(file_existed)

    def test_clean_download_with_no_error_still_succeeds(self) -> None:
        clean_body = b'{"productId":"item1","price":"10.00"}\n{"productId":"item2","price":"20.00"}\n'
        rc, out, file_existed = _run_cli(clean_body, 200)
        self.assertEqual(rc, 0)
        self.assertTrue(out["ok"])
        self.assertEqual(file_existed, clean_body)

    def test_invalid_download_keeps_the_previous_file(self) -> None:
        previous = b'{"product_basic":{"id":"previous"}}\n'
        for status, body in (
            (200, b'{"product_basic":{"id":"1"}}\n{"error":500,"message":"Interrupted"}\n\n'),
            (200, b'{"product_basic":\n{"product_basic":{"id":"2"}}\n'),
            (200, b'{"product_basic":{"id":"1"}}\n{"product_basic":'),
            (200, b'<html>Unavailable</html>'),
            (200, b'\n'),
            (206, b'{"product_basic":{"id":"1"}}\n'),
        ):
            with self.subTest(status=status, body=body):
                rc, out, saved = _run_cli(body, status, previous=previous)
                self.assertEqual(rc, 1)
                self.assertFalse(out["ok"])
                self.assertEqual(saved, previous)


class TestEnhancedDownload404Guidance(unittest.TestCase):
    """Correction 2: return clear feed-specific guidance on a 404."""

    def test_404_returns_clear_guidance_with_feed_list_hint(self) -> None:
        not_found_body = b"Not Found"
        rc, out, _file = _run_cli(not_found_body, 404)
        self.assertEqual(rc, 1)
        self.assertFalse(out["ok"])
        error_text = out.get("error", "")
        self.assertIn("Feed not available", error_text)
        self.assertIn("200", error_text)
        self.assertIn("en_GB", error_text)
        self.assertIn("feed list", error_text)
        self.assertIn("publisher 100", error_text)
        self.assertIn("/downloading-a-list-of-your-product-feeds", error_text)

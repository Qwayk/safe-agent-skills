from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from freepik_api_tool.commands.download import run_download
from freepik_api_tool.config import Config
from freepik_api_tool.freepik_api import FreepikApi


class TestDownloadOverwriteGuard(unittest.TestCase):
    def test_apply_refuses_before_file_overwrite_or_download(self) -> None:
        cfg = Config(
            base_url="https://api.freepik.com/v1",
            api_key="k",
            timeout_s=1.0,
            auth_header="x-freepik-api-key",
            auth_prefix="",
            accept_language=None,
            image_size=None,
            download_url_jsonpath=None,
            license_url_jsonpath=None,
        )

        with tempfile.TemporaryDirectory() as td:
            out_dir = Path(td) / "out"
            out_dir.mkdir(parents=True, exist_ok=True)
            inv_path = Path(td) / "inv.csv"

            rid = "123"
            fmt = "jpg"
            existing_path = out_dir / f"{rid}--file.jpg"
            existing_path.write_bytes(b"already here")

            args = SimpleNamespace(
                id=rid,
                format=fmt,
                out_dir=str(out_dir),
                inventory=str(inv_path),
                force=False,
                image_size=None,
                post_slug="",
                ghost_id="",
                usage_role="",
                download_url_jsonpath=None,
                license_url_jsonpath=None,
            )

            ctx = {
                "cfg": cfg,
                "timeout_s": 1.0,
                "verbose": False,
                "apply": True,
                "audit": Mock(),
            }

            detail = {
                "data": {
                    "id": rid,
                    "is_ai_generated": False,
                    "has_prompt": False,
                    "license": "https://www.freepik.com/license/free/123.pdf",
                }
            }
            download_payload = {"data": {"url": "https://download.example/file.jpg", "filename": "file.jpg"}}

            with patch.object(FreepikApi, "get_resource", autospec=True, return_value=detail), patch.object(
                FreepikApi, "download_by_id_and_format", autospec=True, return_value=download_payload
            ) as mock_download, patch("freepik_api_tool.commands.download.HttpClient.download_to_path") as mock_dl:
                result = run_download(args, ctx)

            self.assertTrue(result["refused"])
            self.assertIn("before-state", result["reasons"][0])
            mock_download.assert_not_called()
            mock_dl.assert_not_called()

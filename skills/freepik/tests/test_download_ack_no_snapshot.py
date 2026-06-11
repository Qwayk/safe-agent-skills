from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from freepik_api_tool.commands.download import run_download
from freepik_api_tool.config import Config
from freepik_api_tool.freepik_api import FreepikApi
from freepik_api_tool.http import HttpClient


class TestDownloadAckNoSnapshot(unittest.TestCase):
    def test_apply_with_ack_writes_file_and_inventory_row(self) -> None:
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

        detail = {
            "data": {
                "id": "123456",
                "title": "Example asset name",
                "name": "Example asset name",
                "type": "photo",
                "url": "https://www.freepik.com/free-photo/example_123456.htm",
                "preview": {"url": "https://img.freepik.com/free-photo/example-preview.jpg"},
                "author": {"name": "Example author"},
                "licenses": [{"url": "https://www.freepik.com/license/free/123456.pdf"}],
                "is_ai_generated": False,
                "has_prompt": False,
                "tags": [{"name": "recipe"}, {"name": "food photo"}],
            }
        }
        download_payload = {"data": {"url": "https://download.example/file.jpg", "filename": "file.jpg"}}

        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            out_dir = tmp / "downloads"
            inv_path = tmp / "licensed-downloads-ledger.csv"
            args = SimpleNamespace(
                id="123456",
                format="jpg",
                out_dir=str(out_dir),
                inventory=str(inv_path),
                force=False,
                image_size=None,
                post_slug="summer-pasta",
                ghost_id="42",
                usage_role="featured",
                download_url_jsonpath=None,
                license_url_jsonpath=None,
            )
            ctx = {
                "cfg": cfg,
                "timeout_s": 1.0,
                "verbose": False,
                "apply": True,
                "ack_no_snapshot": True,
                "audit": Mock(),
                "project_dir": tmp,
            }

            def _fake_download_to_path(
                self: HttpClient, url: str, path: Path, retries: int = 2  # noqa: ARG001
            ) -> None:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(b"abc")

            with patch.object(FreepikApi, "get_resource", autospec=True, return_value=detail), patch.object(
                FreepikApi, "download_by_id_and_format", autospec=True, return_value=download_payload
            ) as mock_download, patch.object(
                HttpClient,
                "download_to_path",
                autospec=True,
                side_effect=_fake_download_to_path,
            ) as mock_binary_download:
                result = run_download(args, ctx)

            self.assertTrue(result["ok"])
            self.assertEqual(result["before_state"]["status"], "no_snapshot_available")
            self.assertEqual(result["before_state"]["approval_required"], "--ack-no-snapshot")
            self.assertTrue(result["no_snapshot_approval"]["acknowledged"])
            self.assertEqual(result["verification"]["mode"], "download-and-inventory")
            self.assertEqual(result["verification"]["file_count"], 1)

            rows = result["rows"]
            self.assertEqual(len(rows), 1)
            row = rows[0]
            self.assertEqual(row["resource_id"], "123456")
            self.assertEqual(row["file_name"], "123456--file.jpg")
            self.assertTrue(Path(row["file_path"]).exists())
            self.assertEqual(
                row["sha256"],
                "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad",
            )

            self.assertTrue(inv_path.exists())
            with inv_path.open(newline="", encoding="utf-8") as f:
                saved_rows = list(csv.DictReader(f))
            self.assertEqual(len(saved_rows), 1)
            self.assertEqual(saved_rows[0]["resource_id"], "123456")
            self.assertEqual(saved_rows[0]["file_name"], "123456--file.jpg")
            self.assertEqual(saved_rows[0]["post_slug"], "summer-pasta")

            mock_download.assert_called_once()
            mock_binary_download.assert_called_once()

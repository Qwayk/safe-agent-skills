import tempfile
import unittest
from pathlib import Path
from typing import Any

from ghost_api_tool.config import Config
from ghost_api_tool.ghost_api import GhostAdminApi
from ghost_api_tool.http import HttpClient


class UploadNameTests(unittest.TestCase):
    def test_upload_name_is_sanitized(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "test.jpg"
            p.write_bytes(b"abc")

            cfg = Config(
                admin_api_url="https://example.com/ghost/api/admin/",
                admin_api_key="id:deadbeef",
                accept_version="v5.0",
                timeout_s=30.0,
            )
            api = GhostAdminApi(cfg=cfg, http=HttpClient(timeout_s=1.0, verbose=False, user_agent="test"))

            captured: dict[str, Any] = {}

            def fake_request(method, path, *, params=None, json_body=None, files=None, data=None):
                captured["files"] = files

                class _Resp:
                    def json(self):
                        return {}

                return _Resp()

            api.request = fake_request  # type: ignore[method-assign]

            api.upload_image(file_path=str(p), purpose="image", ref=None, upload_name="../evil.jpg")
            files = captured.get("files")
            assert isinstance(files, dict)
            self.assertEqual(files["file"][0], "evil.jpg")

            api.upload_image(file_path=str(p), purpose="image", ref=None, upload_name=r"foo\\bar.jpg")
            files = captured.get("files")
            assert isinstance(files, dict)
            self.assertEqual(files["file"][0], "bar.jpg")

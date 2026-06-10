import os
import tempfile
import unittest

from ghost_api_tool.config import Config
from ghost_api_tool.ghost_api import GhostAdminApi
from ghost_api_tool.http import HttpClient, HttpResponse


class ThemesWebhooksApiTests(unittest.TestCase):
    def _make_api(self) -> GhostAdminApi:
        cfg = Config(
            admin_api_url="https://example.com/ghost/api/admin/",
            admin_api_key="id:deadbeef",
            accept_version="v5.0",
            timeout_s=30.0,
        )
        return GhostAdminApi(cfg=cfg, http=HttpClient(timeout_s=1.0, verbose=False, user_agent="test"))

    def test_themes_activate_calls_put_themes_name_activate(self) -> None:
        api = self._make_api()
        captured: dict[str, object] = {}

        def fake_request(method, path, *, params=None, json_body=None, files=None, data=None):
            captured["method"] = method
            captured["path"] = path

            class _Resp:
                def json(self):
                    return {"themes": [{"name": "x", "active": True}]}

            return _Resp()

        api.request = fake_request  # type: ignore[method-assign]
        res = api.themes_activate("casper")
        self.assertEqual(captured["method"], "PUT")
        self.assertEqual(captured["path"], "/themes/casper/activate")
        self.assertEqual(res, {"themes": [{"name": "x", "active": True}]})

    def test_themes_upload_calls_post_themes_upload_with_file(self) -> None:
        api = self._make_api()
        captured: dict[str, object] = {}

        with tempfile.TemporaryDirectory() as td:
            p = os.path.join(td, "theme.zip")
            with open(p, "wb") as f:
                f.write(b"zipbytes")

            def fake_request(method, path, *, params=None, json_body=None, files=None, data=None):
                captured["method"] = method
                captured["path"] = path
                captured["files_keys"] = sorted(list(files.keys())) if isinstance(files, dict) else None

                class _Resp:
                    def json(self):
                        return {"themes": [{"name": "t1"}]}

                return _Resp()

            api.request = fake_request  # type: ignore[method-assign]
            res = api.themes_upload(file_path=p, upload_name=None)
            self.assertEqual(captured["method"], "POST")
            self.assertEqual(captured["path"], "/themes/upload")
            self.assertEqual(captured["files_keys"], ["file"])
            self.assertEqual(res, {"themes": [{"name": "t1"}]})

    def test_webhooks_create_calls_post_webhooks(self) -> None:
        api = self._make_api()
        captured: dict[str, object] = {}

        def fake_request(method, path, *, params=None, json_body=None, files=None, data=None):
            captured["method"] = method
            captured["path"] = path
            captured["json_body"] = json_body

            class _Resp:
                def json(self):
                    return {"webhooks": [{"id": "w1"}]}

            return _Resp()

        api.request = fake_request  # type: ignore[method-assign]
        res = api.webhooks_create({"webhooks": [{"event": "post.added"}]})
        self.assertEqual(captured["method"], "POST")
        self.assertEqual(captured["path"], "/webhooks/")
        self.assertEqual(captured["json_body"], {"webhooks": [{"event": "post.added"}]})
        self.assertEqual(res, {"webhooks": [{"id": "w1"}]})

    def test_webhooks_delete_calls_delete_webhooks_id(self) -> None:
        api = self._make_api()
        captured: dict[str, object] = {}

        def fake_request(method, path, *, params=None, json_body=None, files=None, data=None):
            captured["method"] = method
            captured["path"] = path
            return HttpResponse(status=204, headers={}, body=b"", url="x")

        api.request = fake_request  # type: ignore[method-assign]
        resp = api.webhooks_delete("w1")
        self.assertEqual(captured["method"], "DELETE")
        self.assertEqual(captured["path"], "/webhooks/w1/")
        self.assertEqual(resp.status, 204)


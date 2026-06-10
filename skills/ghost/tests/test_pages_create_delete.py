import unittest

from ghost_api_tool.config import Config
from ghost_api_tool.ghost_api import GhostAdminApi
from ghost_api_tool.http import HttpClient, HttpResponse


class PagesCreateDeleteTests(unittest.TestCase):
    def _make_api(self) -> GhostAdminApi:
        cfg = Config(
            admin_api_url="https://example.com/ghost/api/admin/",
            admin_api_key="id:deadbeef",
            accept_version="v5.0",
            timeout_s=30.0,
        )
        return GhostAdminApi(cfg=cfg, http=HttpClient(timeout_s=1.0, verbose=False, user_agent="test"))

    def test_pages_create_calls_post_pages(self) -> None:
        api = self._make_api()
        captured: dict[str, object] = {}

        def fake_request(method, path, *, params=None, json_body=None, files=None, data=None):
            captured["method"] = method
            captured["path"] = path
            captured["params"] = params
            captured["json_body"] = json_body

            class _Resp:
                def json(self):
                    return {"pages": [{"id": "123"}]}

            return _Resp()

        api.request = fake_request  # type: ignore[method-assign]

        res = api.pages_create({"pages": [{"title": "Test"}]}, params={"source": "html"})

        self.assertEqual(captured["method"], "POST")
        self.assertEqual(captured["path"], "/pages/")
        self.assertEqual(captured["params"], {"source": "html"})
        self.assertEqual(res, {"pages": [{"id": "123"}]})

    def test_pages_delete_calls_delete_page_id(self) -> None:
        api = self._make_api()
        captured: dict[str, object] = {}

        def fake_request(method, path, *, params=None, json_body=None, files=None, data=None):
            captured["method"] = method
            captured["path"] = path
            return HttpResponse(status=204, headers={}, body=b"", url="https://example.com/ghost/api/admin/pages/123/")

        api.request = fake_request  # type: ignore[method-assign]

        resp = api.pages_delete("123")

        self.assertEqual(captured["method"], "DELETE")
        self.assertEqual(captured["path"], "/pages/123/")
        self.assertEqual(resp.status, 204)


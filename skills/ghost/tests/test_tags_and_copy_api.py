import unittest

from ghost_api_tool.config import Config
from ghost_api_tool.ghost_api import GhostAdminApi
from ghost_api_tool.http import HttpClient


class TagsAndCopyApiTests(unittest.TestCase):
    def _make_api(self) -> GhostAdminApi:
        cfg = Config(
            admin_api_url="https://example.com/ghost/api/admin/",
            admin_api_key="id:deadbeef",
            accept_version="v5.0",
            timeout_s=30.0,
        )
        return GhostAdminApi(cfg=cfg, http=HttpClient(timeout_s=1.0, verbose=False, user_agent="test"))

    def test_tags_create_calls_post_tags(self) -> None:
        api = self._make_api()
        captured: dict[str, object] = {}

        def fake_request(method, path, *, params=None, json_body=None, files=None, data=None):
            captured["method"] = method
            captured["path"] = path
            captured["json_body"] = json_body

            class _Resp:
                def json(self):
                    return {"tags": [{"id": "t1"}]}

            return _Resp()

        api.request = fake_request  # type: ignore[method-assign]

        res = api.tags_create({"tags": [{"name": "X"}]})
        self.assertEqual(captured["method"], "POST")
        self.assertEqual(captured["path"], "/tags/")
        self.assertEqual(captured["json_body"], {"tags": [{"name": "X"}]})
        self.assertEqual(res, {"tags": [{"id": "t1"}]})

    def test_tags_update_calls_put_tags_id(self) -> None:
        api = self._make_api()
        captured: dict[str, object] = {}

        def fake_request(method, path, *, params=None, json_body=None, files=None, data=None):
            captured["method"] = method
            captured["path"] = path
            captured["json_body"] = json_body

            class _Resp:
                def json(self):
                    return {"tags": [{"id": "t1"}]}

            return _Resp()

        api.request = fake_request  # type: ignore[method-assign]

        res = api.tags_update("t1", {"tags": [{"name": "Y"}]})
        self.assertEqual(captured["method"], "PUT")
        self.assertEqual(captured["path"], "/tags/t1/")
        self.assertEqual(captured["json_body"], {"tags": [{"name": "Y"}]})
        self.assertEqual(res, {"tags": [{"id": "t1"}]})

    def test_posts_copy_calls_post_posts_id_copy(self) -> None:
        api = self._make_api()
        captured: dict[str, object] = {}

        def fake_request(method, path, *, params=None, json_body=None, files=None, data=None):
            captured["method"] = method
            captured["path"] = path

            class _Resp:
                def json(self):
                    return {"posts": [{"id": "p2"}]}

            return _Resp()

        api.request = fake_request  # type: ignore[method-assign]

        res = api.posts_copy("p1")
        self.assertEqual(captured["method"], "POST")
        self.assertEqual(captured["path"], "/posts/p1/copy")
        self.assertEqual(res, {"posts": [{"id": "p2"}]})

    def test_pages_copy_calls_post_pages_id_copy(self) -> None:
        api = self._make_api()
        captured: dict[str, object] = {}

        def fake_request(method, path, *, params=None, json_body=None, files=None, data=None):
            captured["method"] = method
            captured["path"] = path

            class _Resp:
                def json(self):
                    return {"pages": [{"id": "pg2"}]}

            return _Resp()

        api.request = fake_request  # type: ignore[method-assign]

        res = api.pages_copy("pg1")
        self.assertEqual(captured["method"], "POST")
        self.assertEqual(captured["path"], "/pages/pg1/copy")
        self.assertEqual(res, {"pages": [{"id": "pg2"}]})


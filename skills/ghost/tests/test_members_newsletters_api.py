import unittest

from ghost_api_tool.config import Config
from ghost_api_tool.ghost_api import GhostAdminApi
from ghost_api_tool.http import HttpClient, HttpResponse


class MembersNewslettersApiTests(unittest.TestCase):
    def _make_api(self) -> GhostAdminApi:
        cfg = Config(
            admin_api_url="https://example.com/ghost/api/admin/",
            admin_api_key="id:deadbeef",
            accept_version="v5.0",
            timeout_s=30.0,
        )
        return GhostAdminApi(cfg=cfg, http=HttpClient(timeout_s=1.0, verbose=False, user_agent="test"))

    def test_members_browse_calls_get_members(self) -> None:
        api = self._make_api()
        captured: dict[str, object] = {}

        def fake_request(method, path, *, params=None, json_body=None, files=None, data=None):
            captured["method"] = method
            captured["path"] = path
            captured["params"] = params

            class _Resp:
                def json(self):
                    return {"members": []}

            return _Resp()

        api.request = fake_request  # type: ignore[method-assign]

        res = api.members_browse(params={"limit": 1})
        self.assertEqual(captured["method"], "GET")
        self.assertEqual(captured["path"], "/members/")
        self.assertEqual(captured["params"], {"limit": 1})
        self.assertEqual(res, {"members": []})

    def test_members_update_calls_put_member_id(self) -> None:
        api = self._make_api()
        captured: dict[str, object] = {}

        def fake_request(method, path, *, params=None, json_body=None, files=None, data=None):
            captured["method"] = method
            captured["path"] = path
            captured["json_body"] = json_body

            class _Resp:
                def json(self):
                    return {"members": [{"id": "m1"}]}

            return _Resp()

        api.request = fake_request  # type: ignore[method-assign]

        res = api.members_update("m1", {"members": [{"name": "X"}]})
        self.assertEqual(captured["method"], "PUT")
        self.assertEqual(captured["path"], "/members/m1/")
        self.assertEqual(captured["json_body"], {"members": [{"name": "X"}]})
        self.assertEqual(res, {"members": [{"id": "m1"}]})

    def test_newsletters_browse_calls_get_newsletters(self) -> None:
        api = self._make_api()
        captured: dict[str, object] = {}

        def fake_request(method, path, *, params=None, json_body=None, files=None, data=None):
            captured["method"] = method
            captured["path"] = path
            captured["params"] = params

            class _Resp:
                def json(self):
                    return {"newsletters": []}

            return _Resp()

        api.request = fake_request  # type: ignore[method-assign]

        res = api.newsletters_browse(params={"limit": 50})
        self.assertEqual(captured["method"], "GET")
        self.assertEqual(captured["path"], "/newsletters/")
        self.assertEqual(captured["params"], {"limit": 50})
        self.assertEqual(res, {"newsletters": []})

    def test_newsletters_read_by_id_calls_get_newsletter(self) -> None:
        api = self._make_api()
        captured: dict[str, object] = {}

        def fake_request(method, path, *, params=None, json_body=None, files=None, data=None):
            captured["method"] = method
            captured["path"] = path
            return HttpResponse(status=200, headers={}, body=b'{"newsletters":[{"id":"n1"}]}', url="x")

        api.request = fake_request  # type: ignore[method-assign]

        res = api.newsletters_read_by_id("n1")
        self.assertEqual(captured["method"], "GET")
        self.assertEqual(captured["path"], "/newsletters/n1/")
        self.assertEqual(res, {"newsletters": [{"id": "n1"}]})


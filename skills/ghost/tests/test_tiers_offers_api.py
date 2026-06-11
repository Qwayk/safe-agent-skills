import unittest

from ghost_api_tool.config import Config
from ghost_api_tool.ghost_api import GhostAdminApi
from ghost_api_tool.http import HttpClient


class TiersOffersApiTests(unittest.TestCase):
    def _make_api(self) -> GhostAdminApi:
        cfg = Config(
            admin_api_url="https://example.com/ghost/api/admin/",
            admin_api_key="id:deadbeef",
            accept_version="v5.0",
            timeout_s=30.0,
        )
        return GhostAdminApi(cfg=cfg, http=HttpClient(timeout_s=1.0, verbose=False, user_agent="test"))

    def test_tiers_browse_calls_get_tiers(self) -> None:
        api = self._make_api()
        captured: dict[str, object] = {}

        def fake_request(method, path, *, params=None, json_body=None, files=None, data=None):
            captured["method"] = method
            captured["path"] = path
            captured["params"] = params

            class _Resp:
                def json(self):
                    return {"tiers": []}

            return _Resp()

        api.request = fake_request  # type: ignore[method-assign]
        res = api.tiers_browse(params={"limit": 1})
        self.assertEqual(captured["method"], "GET")
        self.assertEqual(captured["path"], "/tiers/")
        self.assertEqual(captured["params"], {"limit": 1})
        self.assertEqual(res, {"tiers": []})

    def test_tiers_update_calls_put_tiers_id(self) -> None:
        api = self._make_api()
        captured: dict[str, object] = {}

        def fake_request(method, path, *, params=None, json_body=None, files=None, data=None):
            captured["method"] = method
            captured["path"] = path
            captured["json_body"] = json_body

            class _Resp:
                def json(self):
                    return {"tiers": [{"id": "tr1"}]}

            return _Resp()

        api.request = fake_request  # type: ignore[method-assign]
        res = api.tiers_update("tr1", {"tiers": [{"name": "X"}]})
        self.assertEqual(captured["method"], "PUT")
        self.assertEqual(captured["path"], "/tiers/tr1/")
        self.assertEqual(captured["json_body"], {"tiers": [{"name": "X"}]})
        self.assertEqual(res, {"tiers": [{"id": "tr1"}]})

    def test_offers_browse_calls_get_offers(self) -> None:
        api = self._make_api()
        captured: dict[str, object] = {}

        def fake_request(method, path, *, params=None, json_body=None, files=None, data=None):
            captured["method"] = method
            captured["path"] = path
            captured["params"] = params

            class _Resp:
                def json(self):
                    return {"offers": []}

            return _Resp()

        api.request = fake_request  # type: ignore[method-assign]
        res = api.offers_browse(params={"limit": 1})
        self.assertEqual(captured["method"], "GET")
        self.assertEqual(captured["path"], "/offers/")
        self.assertEqual(captured["params"], {"limit": 1})
        self.assertEqual(res, {"offers": []})

    def test_offers_create_calls_post_offers(self) -> None:
        api = self._make_api()
        captured: dict[str, object] = {}

        def fake_request(method, path, *, params=None, json_body=None, files=None, data=None):
            captured["method"] = method
            captured["path"] = path
            captured["json_body"] = json_body

            class _Resp:
                def json(self):
                    return {"offers": [{"id": "o1"}]}

            return _Resp()

        api.request = fake_request  # type: ignore[method-assign]
        res = api.offers_create({"offers": [{"name": "X"}]})
        self.assertEqual(captured["method"], "POST")
        self.assertEqual(captured["path"], "/offers/")
        self.assertEqual(captured["json_body"], {"offers": [{"name": "X"}]})
        self.assertEqual(res, {"offers": [{"id": "o1"}]})


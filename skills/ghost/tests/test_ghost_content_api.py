import unittest

from ghost_api_tool.config import ContentConfig
from ghost_api_tool.ghost_content_api import GhostContentApi
from ghost_api_tool.http import HttpClient


class GhostContentApiTests(unittest.TestCase):
    def test_posts_browse_adds_key_param_and_accept_version(self) -> None:
        cfg = ContentConfig(
            content_api_url="https://example.com/ghost/api/content/",
            content_api_key="deadbeef",
            accept_version="v5.0",
            timeout_s=30.0,
        )
        api = GhostContentApi(cfg=cfg, http=HttpClient(timeout_s=1.0, verbose=False, user_agent="test"))
        captured: dict[str, object] = {}

        def fake_request(method, url, *, headers=None, params=None, json_body=None, files=None, data=None, retries=0, retry_on=(429, 500, 502, 503, 504)):  # type: ignore[no-untyped-def]
            captured["method"] = method
            captured["url"] = url
            captured["headers"] = headers
            captured["params"] = params

            class _Resp:
                def json(self):
                    return {"posts": []}

            return _Resp()

        api._http.request = fake_request  # type: ignore[method-assign]
        res = api.posts_browse(params={"limit": 1})
        self.assertEqual(res, {"posts": []})
        self.assertEqual(captured["method"], "GET")
        self.assertEqual(captured["url"], "https://example.com/ghost/api/content/posts/")
        self.assertEqual(captured["headers"], {"Accept-Version": "v5.0"})
        self.assertEqual(captured["params"], {"limit": 1, "key": "deadbeef"})


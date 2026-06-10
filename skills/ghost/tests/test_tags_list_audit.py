import unittest

from ghost_api_tool.commands import tag as tag_cmd
from ghost_api_tool.config import Config
from ghost_api_tool.ghost_api import GhostAdminApi
from ghost_api_tool.http import HttpClient


class TagsBrowseTests(unittest.TestCase):
    def test_tags_browse_calls_get_tags(self) -> None:
        cfg = Config(
            admin_api_url="https://example.com/ghost/api/admin/",
            admin_api_key="id:deadbeef",
            accept_version="v5.0",
            timeout_s=30.0,
        )
        api = GhostAdminApi(cfg=cfg, http=HttpClient(timeout_s=1.0, verbose=False, user_agent="test"))

        captured: dict[str, object] = {}

        def fake_request(method, path, *, params=None, json_body=None, files=None, data=None):
            captured["method"] = method
            captured["path"] = path
            captured["params"] = params

            class _Resp:
                def json(self):
                    return {"tags": []}

            return _Resp()

        api.request = fake_request  # type: ignore[method-assign]
        res = api.tags_browse(params={"limit": 1})
        self.assertEqual(captured["method"], "GET")
        self.assertEqual(captured["path"], "/tags/")
        self.assertEqual(captured["params"], {"limit": 1})
        self.assertEqual(res, {"tags": []})

    def test_tags_delete_calls_delete_tag_id(self) -> None:
        cfg = Config(
            admin_api_url="https://example.com/ghost/api/admin/",
            admin_api_key="id:deadbeef",
            accept_version="v5.0",
            timeout_s=30.0,
        )
        api = GhostAdminApi(cfg=cfg, http=HttpClient(timeout_s=1.0, verbose=False, user_agent="test"))

        captured: dict[str, object] = {}

        def fake_request(method, path, *, params=None, json_body=None, files=None, data=None):
            captured["method"] = method
            captured["path"] = path
            from ghost_api_tool.http import HttpResponse

            return HttpResponse(status=204, headers={}, body=b"", url="https://example.com/ghost/api/admin/tags/123/")

        api.request = fake_request  # type: ignore[method-assign]
        resp = api.tags_delete("123")
        self.assertEqual(captured["method"], "DELETE")
        self.assertEqual(captured["path"], "/tags/123/")
        self.assertEqual(resp.status, 204)


class _FakeApi:
    def __init__(self, pages):
        self._pages = pages
        self._calls: list[dict[str, object]] = []

    def tags_browse(self, *, params=None):
        params = params or {}
        self._calls.append(dict(params))
        page = int(params.get("page", 1))
        return self._pages[page - 1]

    def tags_delete(self, tag_id: str):
        from ghost_api_tool.http import HttpResponse

        return HttpResponse(status=204, headers={}, body=b"", url=f"https://example.com/ghost/api/admin/tags/{tag_id}/")

    def tags_read_by_id(self, tag_id: str, *, params=None):
        raise RuntimeError(f"HTTP 404 for GET https://example.com/ghost/api/admin/tags/{tag_id}/\\nNot found")


class _CaptureOut:
    def __init__(self):
        self.last = None

    def print(self, obj):
        self.last = obj


class TagsCommandsTests(unittest.TestCase):
    def test_browse_all_paginates(self) -> None:
        api = _FakeApi(
            pages=[
                {
                    "tags": [{"id": "1"}, {"id": "2"}],
                    "meta": {"pagination": {"page": 1, "limit": 2, "pages": 2, "total": 3, "next": 2, "prev": None}},
                },
                {
                    "tags": [{"id": "3"}],
                    "meta": {"pagination": {"page": 2, "limit": 2, "pages": 2, "total": 3, "next": None, "prev": 1}},
                },
            ]
        )
        tags, meta = tag_cmd._browse_all(api, params={"limit": 2})
        self.assertEqual([t["id"] for t in tags], ["1", "2", "3"])
        self.assertEqual(meta["pagination"]["pages"], 2)
        self.assertEqual(len(api._calls), 2)

    def test_tag_audit_finds_duplicates_and_zero_posts(self) -> None:
        api = _FakeApi(
            pages=[
                {
                    "tags": [
                        {"id": "a1", "name": "Appetizers", "slug": "appetizers", "visibility": "public", "count": {"posts": 0}},
                        {"id": "a2", "name": "Appetizers", "slug": "appetizers-1", "visibility": "public", "count": {"posts": 2}},
                        {"id": "a3", "name": "Appetizers", "slug": "appetizers-2", "visibility": "public", "count": {"posts": 1}},
                        {"id": "i1", "name": "#Import 2025-12-14 09:45", "slug": "hash-import", "visibility": "internal", "count": {"posts": 0}},
                    ],
                    "meta": {"pagination": {"page": 1, "limit": 100, "pages": 1, "total": 4, "next": None, "prev": None}},
                }
            ]
        )
        out = _CaptureOut()
        ctx = {"_api": api, "out": out}

        class _Args:
            exclude_empty = False

        rc = tag_cmd.cmd_tag_audit(_Args(), ctx)
        self.assertEqual(rc, 0)
        self.assertIsInstance(out.last, dict)
        self.assertEqual(out.last["summary"]["total"], 4)
        self.assertEqual(out.last["summary"]["zero_post"], 2)  # includes both the 0-post public tag and the import tag
        self.assertEqual(out.last["summary"]["duplicate_name_groups"], 1)
        self.assertEqual(out.last["candidates"]["duplicate_name_groups"][0]["name"], "Appetizers")
        self.assertEqual(out.last["candidates"]["duplicate_name_groups"][0]["tags"][0]["slug"], "appetizers-1")
        self.assertEqual(len(out.last["candidates"]["internal_suspects"]), 1)

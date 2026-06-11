import unittest

from ghost_api_tool.commands.content import (
    cmd_content_posts_get,
    cmd_content_posts_list,
)
from ghost_api_tool.errors import ValidationError


class _Out:
    def __init__(self) -> None:
        self.items = []

    def print(self, obj):
        self.items.append(obj)


class ContentCommandsTests(unittest.TestCase):
    def test_posts_list_fetch_all_pages_includes_fetched_summary(self):
        calls = []

        class FakeApi:
            def posts_browse(self, *, params=None):
                calls.append(dict(params or {}))
                page = int((params or {}).get("page") or 1)
                if page == 1:
                    return {
                        "posts": [{"id": "p1"}],
                        "meta": {"pagination": {"page": 1, "limit": 1, "pages": 2, "total": 2, "next": 2, "prev": None}},
                    }
                return {
                    "posts": [{"id": "p2"}],
                    "meta": {"pagination": {"page": 2, "limit": 1, "pages": 2, "total": 2, "next": None, "prev": 1}},
                }

        class Args:
            limit = 1
            page = None
            filter = None
            fields = None
            include = None
            order = None
            formats = None

        out = _Out()
        ctx = {"out": out, "_content_api": FakeApi()}
        rc = cmd_content_posts_list(Args(), ctx)
        self.assertEqual(rc, 0)
        self.assertEqual(len(out.items), 1)
        obj = out.items[0]
        self.assertEqual(obj.get("kind"), "content.posts.list")
        self.assertEqual(obj.get("fetched", {}).get("total"), 2)
        self.assertEqual(len(obj.get("posts") or []), 2)
        self.assertEqual(calls[0]["page"], 1)
        self.assertEqual(calls[1]["page"], 2)

    def test_posts_get_requires_exactly_one_selector(self):
        class FakeApi:
            pass

        class Args:
            id = "p1"
            slug = "welcome"
            fields = None
            include = None
            formats = None

        out = _Out()
        ctx = {"out": out, "_content_api": FakeApi()}
        with self.assertRaises(ValidationError):
            _ = cmd_content_posts_get(Args(), ctx)

    def test_posts_get_by_slug_passes_params(self):
        captured = {}

        class FakeApi:
            def posts_read_by_slug(self, slug, *, params=None):
                captured["slug"] = slug
                captured["params"] = params
                return {"posts": [{"slug": slug}]}

        class Args:
            id = None
            slug = "welcome"
            fields = "id,title"
            include = "tags,authors"
            formats = "html"

        out = _Out()
        ctx = {"out": out, "_content_api": FakeApi()}
        rc = cmd_content_posts_get(Args(), ctx)
        self.assertEqual(rc, 0)
        self.assertEqual(captured["slug"], "welcome")
        self.assertEqual(captured["params"], {"fields": "id,title", "include": "tags,authors", "formats": "html"})
        obj = out.items[0]
        self.assertEqual(obj.get("kind"), "content.posts.get")
        self.assertEqual(obj.get("selector"), {"slug": "welcome"})


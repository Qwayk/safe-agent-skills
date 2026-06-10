import unittest
from typing import cast

from wordpress_api_tool.commands.post import post_set_status_core
from wordpress_api_tool.wp_api import WordPressApi


class _StubApi:
    def __init__(self, post):
        self._post = dict(post)
        self.updated = []

    def post_by_slug(self, *, post_type: str, slug: str):
        return dict(self._post)

    def post_by_id(self, *, post_type: str, post_id: int):
        return dict(self._post)

    def update_post_status(self, *, post_type: str, post_id: int, status: str):
        self.updated.append((post_type, post_id, status))
        self._post["status"] = status
        return dict(self._post)


class PostSetStatusTests(unittest.TestCase):
    def test_refuses_without_selector(self):
        api = _StubApi({"id": 1, "slug": "x", "status": "draft"})
        with self.assertRaises(RuntimeError):
            post_set_status_core(
                cast(WordPressApi, api),
                post_type="posts",
                slug=None,
                post_id=None,
                to_status="publish",
                require_current=None,
                apply=False,
            )

    def test_refuses_with_both_selectors(self):
        api = _StubApi({"id": 1, "slug": "x", "status": "draft"})
        with self.assertRaises(RuntimeError):
            post_set_status_core(
                cast(WordPressApi, api),
                post_type="posts",
                slug="x",
                post_id=1,
                to_status="publish",
                require_current=None,
                apply=False,
            )

    def test_dry_run_returns_change(self):
        api = _StubApi({"id": 1, "slug": "x", "status": "draft", "link": "l"})
        res = post_set_status_core(
            cast(WordPressApi, api),
            post_type="posts",
            slug="x",
            post_id=None,
            to_status="publish",
            require_current="draft",
            apply=False,
        )
        self.assertEqual(res["changes"]["status"]["before"], "draft")
        self.assertEqual(res["changes"]["status"]["after"], "publish")
        self.assertNotIn("verified", res)
        self.assertEqual(api.updated, [])

    def test_apply_updates_and_verifies(self):
        api = _StubApi({"id": 1, "slug": "x", "status": "draft", "link": "l"})
        res = post_set_status_core(
            cast(WordPressApi, api),
            post_type="posts",
            slug="x",
            post_id=None,
            to_status="publish",
            require_current="draft",
            apply=True,
        )
        self.assertEqual(api.updated, [("posts", 1, "publish")])
        self.assertTrue(res["verified"])

    def test_require_current_refuses(self):
        api = _StubApi({"id": 1, "slug": "x", "status": "publish", "link": "l"})
        res = post_set_status_core(
            cast(WordPressApi, api),
            post_type="posts",
            slug="x",
            post_id=None,
            to_status="draft",
            require_current="draft",
            apply=True,
        )
        self.assertTrue(res.get("refused"))
        self.assertEqual(api.updated, [])

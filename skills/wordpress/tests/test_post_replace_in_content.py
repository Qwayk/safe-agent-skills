import unittest
from typing import cast

from wordpress_api_tool.commands.post import post_replace_in_content_core
from wordpress_api_tool.wp_api import WordPressApi


class _StubApi:
    def __init__(self, post):
        self._post = dict(post)
        self.updated = []

    def post_by_slug(self, *, post_type: str, slug: str):
        return dict(self._post)

    def post_by_id(self, *, post_type: str, post_id: int):
        return dict(self._post)

    def update_post_content(self, *, post_type: str, post_id: int, content_raw: str):
        self.updated.append((post_type, post_id, content_raw))
        self._post["content"] = {"raw": content_raw}
        return dict(self._post)


class PostReplaceInContentTests(unittest.TestCase):
    def test_refuses_without_selector(self):
        api = _StubApi({"id": 1, "slug": "x", "content": {"raw": "a"}})
        with self.assertRaises(RuntimeError):
            post_replace_in_content_core(
                cast(WordPressApi, api),
                post_type="posts",
                slug=None,
                post_id=None,
                from_text="a",
                to_text="b",
                expected_count=1,
                max_replacements=1,
                include_diff=False,
                apply=False,
            )

    def test_refuses_with_both_selectors(self):
        api = _StubApi({"id": 1, "slug": "x", "content": {"raw": "a"}})
        with self.assertRaises(RuntimeError):
            post_replace_in_content_core(
                cast(WordPressApi, api),
                post_type="posts",
                slug="x",
                post_id=1,
                from_text="a",
                to_text="b",
                expected_count=1,
                max_replacements=1,
                include_diff=False,
                apply=False,
            )

    def test_refuses_on_count_mismatch(self):
        api = _StubApi({"id": 1, "slug": "x", "content": {"raw": "aaa"}})
        with self.assertRaises(RuntimeError):
            post_replace_in_content_core(
                cast(WordPressApi, api),
                post_type="posts",
                slug="x",
                post_id=None,
                from_text="a",
                to_text="b",
                expected_count=2,
                max_replacements=2,
                include_diff=False,
                apply=False,
            )

    def test_dry_run_includes_diff_when_requested(self):
        api = _StubApi({"id": 1, "slug": "x", "content": {"raw": "hello tel:old"}})
        res = post_replace_in_content_core(
            cast(WordPressApi, api),
            post_type="posts",
            slug="x",
            post_id=None,
            from_text="tel:old",
            to_text="tel:new",
            expected_count=1,
            max_replacements=1,
            include_diff=True,
            apply=False,
        )
        self.assertTrue(res["changed"])
        diff = res["changes"]["content_raw"]["diff"]
        self.assertIsInstance(diff, str)
        self.assertIn("tel:old", diff)
        self.assertIn("tel:new", diff)
        self.assertEqual(api.updated, [])

    def test_apply_updates_and_verifies(self):
        api = _StubApi({"id": 1, "slug": "x", "content": {"raw": 'href="tel:bad"'}})
        res = post_replace_in_content_core(
            cast(WordPressApi, api),
            post_type="posts",
            slug="x",
            post_id=None,
            from_text='href="tel:bad"',
            to_text='href="tel:good"',
            expected_count=1,
            max_replacements=1,
            include_diff=False,
            apply=True,
        )
        self.assertEqual(len(api.updated), 1)
        self.assertTrue(res["verified"])
        self.assertEqual(res["verify"]["remaining_source_occurrences"], 0)

    def test_apply_allows_partial_replace_when_expected(self):
        api = _StubApi({"id": 1, "slug": "x", "content": {"raw": "a a"}})
        res = post_replace_in_content_core(
            cast(WordPressApi, api),
            post_type="posts",
            slug="x",
            post_id=None,
            from_text="a",
            to_text="b",
            expected_count=2,
            max_replacements=1,
            include_diff=False,
            apply=True,
        )
        self.assertTrue(res["verified"])
        self.assertEqual(res["verify"]["remaining_source_occurrences"], 1)
        self.assertEqual(res["verify"]["expected_remaining_source_occurrences"], 1)

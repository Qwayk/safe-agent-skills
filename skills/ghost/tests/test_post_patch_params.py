import unittest
from typing import cast

from ghost_api_tool.ghost_api import GhostAdminApi
from ghost_api_tool.post_patch import apply_post_patch


class _FakeApi:
    def __init__(self):
        self.post = {
            "id": "p1",
            "updated_at": "2022-06-05T20:52:37.000Z",
            "status": "draft",
        }
        self.update_calls = []

    def posts_read_by_slug(self, slug, *, params=None):
        return {"posts": [dict(self.post)]}

    def posts_read_by_id(self, post_id, *, params=None):
        return {"posts": [dict(self.post)]}

    def posts_update(self, post_id, payload, *, params=None):
        self.update_calls.append({"id": post_id, "payload": payload, "params": params})
        patch = payload["posts"][0]
        for k, v in patch.items():
            if k == "updated_at":
                continue
            self.post[k] = v
        return {"posts": [dict(self.post)]}


class PostPatchParamsTests(unittest.TestCase):
    def test_apply_post_patch_forwards_params(self):
        api = _FakeApi()
        apply_post_patch(
            cast(GhostAdminApi, api),
            slug="x",
            post_id=None,
            patch={"status": "published"},
            apply=True,
            params={"newsletter": "weekly-newsletter"},
        )
        self.assertEqual(api.update_calls[0]["params"], {"newsletter": "weekly-newsletter"})

    def test_apply_post_patch_merges_source_with_params(self):
        api = _FakeApi()
        apply_post_patch(
            cast(GhostAdminApi, api),
            slug="x",
            post_id=None,
            patch={"status": "published"},
            apply=True,
            params={"newsletter": "weekly-newsletter"},
            source="html",
        )
        self.assertEqual(
            api.update_calls[0]["params"], {"newsletter": "weekly-newsletter", "source": "html"}
        )

import unittest
from typing import Any, cast

from ghost_api_tool.ghost_api import GhostAdminApi
from ghost_api_tool.post_patch import apply_post_patch


class _FakeApi:
    def __init__(self):
        self.post: dict[str, Any] = {
            "id": "p1",
            "updated_at": "2022-06-05T20:52:37.000Z",
            "status": "draft",
            "tags": [],
            "authors": [],
        }

    def posts_read_by_slug(self, slug, *, params=None):
        return {"posts": [dict(self.post)]}

    def posts_read_by_id(self, post_id, *, params=None):
        return {"posts": [dict(self.post)]}

    def posts_update(self, post_id, payload, *, params=None):
        patch = payload["posts"][0]
        for k, v in patch.items():
            if k == "updated_at":
                continue
            self.post[k] = v

        # Simulate Ghost expanding tag/author objects in responses.
        if "tags" in self.post:
            expanded = []
            for item in self.post["tags"]:
                if isinstance(item, str):
                    expanded.append({"id": f"t-{item}", "name": item, "slug": item.lower().replace(" ", "-")})
                else:
                    name = item.get("name") or "unknown"
                    expanded.append({"id": f"t-{name}", "name": name, "slug": name.lower().replace(" ", "-")})
            self.post["tags"] = expanded

        if "authors" in self.post:
            expanded = []
            for item in self.post["authors"]:
                if isinstance(item, str):
                    expanded.append({"id": f"a-{item}", "email": item, "slug": item.split("@")[0]})
                else:
                    email = item.get("email") or "x@example.com"
                    expanded.append({"id": item.get("id", f"a-{email}"), "email": email, "slug": email.split("@")[0]})
            self.post["authors"] = expanded

        return {"posts": [dict(self.post)]}


class PostPatchVerifyRelationsTests(unittest.TestCase):
    def test_tags_verify_by_name(self):
        api = _FakeApi()
        plan = apply_post_patch(
            cast(GhostAdminApi, api),
            slug="x",
            post_id=None,
            patch={"tags": [{"name": "A"}, {"name": "#hidden"}]},
            apply=True,
            require_current="draft",
        )
        self.assertFalse(plan.refused)
        self.assertEqual([t["name"] for t in plan.after["tags"]], ["A", "#hidden"])

    def test_authors_verify_by_email(self):
        api = _FakeApi()
        plan = apply_post_patch(
            cast(GhostAdminApi, api),
            slug="x",
            post_id=None,
            patch={"authors": ["a@example.com"]},
            apply=True,
            require_current="draft",
        )
        self.assertFalse(plan.refused)
        self.assertEqual(plan.after["authors"][0]["email"], "a@example.com")

    def test_authors_noop_when_ids_match(self):
        api = _FakeApi()
        _ = apply_post_patch(
            cast(GhostAdminApi, api),
            slug="x",
            post_id=None,
            patch={"authors": ["a@example.com"]},
            apply=True,
            require_current="draft",
        )
        # Re-applying the same author by id should be a no-op even though Ghost expands author objects.
        plan = apply_post_patch(
            cast(GhostAdminApi, api),
            slug="x",
            post_id=None,
            patch={"authors": [{"id": "a-a@example.com"}]},
            apply=False,
            require_current="draft",
        )
        self.assertFalse(plan.refused)
        self.assertEqual(plan.changes, [])

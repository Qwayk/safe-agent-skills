import unittest

from ghost_api_tool.authors_audit import audit_authors


class TestAuthorsAudit(unittest.TestCase):
    def test_audit_authors_primary_and_any(self) -> None:
        users = [
            {"id": "u1", "name": "Ghost Admin", "slug": "ghost-admin", "roles": [{"name": "Owner"}]},
            {"id": "u2", "name": "Primary Author", "slug": "primary-author", "roles": [{"name": "Administrator"}]},
            {"id": "u3", "name": "Editor One", "slug": "editor-one", "roles": [{"name": "Editor"}]},
        ]
        posts = [
            {
                "id": "p1",
                "slug": "a",
                "title": "A",
                "status": "published",
                "primary_author": {"id": "u1", "name": "Ghost Admin", "slug": "ghost-admin"},
                "authors": [{"id": "u1", "name": "Ghost Admin"}, {"id": "u2", "name": "Primary Author"}],
            },
            {
                "id": "p2",
                "slug": "b",
                "title": "B",
                "status": "published",
                "primary_author": {"id": "u2", "name": "Primary Author", "slug": "primary-author"},
                "authors": [{"id": "u2", "name": "Primary Author"}],
            },
            {
                "id": "p3",
                "slug": "c",
                "title": "C",
                "status": "draft",
                # No primary_author field; fallback to authors[0]
                "authors": [{"id": "u1", "name": "Ghost Admin"}],
            },
        ]

        res = audit_authors(users=users, posts=posts, primary_author_name="Primary Author", ghost_admin_name="Ghost Admin")

        self.assertEqual(len(res.primary_author_users_min), 1)
        self.assertEqual(res.primary_author_users_min[0]["id"], "u2")
        self.assertTrue(any(u["id"] == "u1" for u in res.ghost_admin_users_min))

        # Primary author = Ghost Admin: p1 and p3
        self.assertEqual({p["id"] for p in res.posts_primary_author_ghost_admin}, {"p1", "p3"})

        # Any author includes Ghost Admin: p1 and p3
        self.assertEqual({p["id"] for p in res.posts_any_author_ghost_admin}, {"p1", "p3"})

        # Counts
        primary_counts = {r["user_id"]: r["posts_count"] for r in res.counts_primary_author}
        any_counts = {r["user_id"]: r["posts_count"] for r in res.counts_any_author}
        self.assertEqual(primary_counts["u1"], 2)
        self.assertEqual(primary_counts["u2"], 1)
        self.assertEqual(any_counts["u1"], 2)
        self.assertEqual(any_counts["u2"], 2)

    def test_fallback_ghost_admin_contains(self) -> None:
        users = [
            {"id": "u1", "name": "Ghost Owner", "slug": "ghost-owner"},
        ]
        posts = [
            {
                "id": "p1",
                "slug": "a",
                "title": "A",
                "status": "published",
                "authors": [{"id": "u1", "name": "Ghost Owner"}],
            }
        ]
        res = audit_authors(users=users, posts=posts, primary_author_name="Primary Author", ghost_admin_name="Ghost Admin")
        self.assertEqual(len(res.ghost_admin_users_min), 0)
        self.assertEqual(len(res.ghost_admin_candidates_min), 1)
        self.assertEqual(res.ghost_admin_candidates_min[0]["id"], "u1")


if __name__ == "__main__":
    unittest.main()

import unittest

from ghost_api_tool.commands.page import cmd_page_copy
from ghost_api_tool.commands.post import cmd_post_copy


class _Out:
    def __init__(self) -> None:
        self.items = []

    def print(self, obj):
        self.items.append(obj)


class _Audit:
    def write(self, *_args, **_kwargs) -> None:
        return None


class CopyCommandsVerificationTests(unittest.TestCase):
    def test_post_copy_dry_run_uses_before_state_without_crashing(self) -> None:
        class FakeApi:
            def posts_read_by_id(self, post_id, params=None):
                assert post_id == "p1"
                return {"posts": [{"id": "p1", "slug": "from", "title": "From", "status": "draft"}]}

        class Args:
            slug = None
            id = "p1"

        out = _Out()
        ctx = {"apply": False, "out": out, "_api": FakeApi()}
        rc = cmd_post_copy(Args(), ctx)
        self.assertEqual(rc, 0)
        self.assertEqual(out.items[0]["copy"]["from_id"], "p1")

    def test_page_copy_dry_run_uses_before_state_without_crashing(self) -> None:
        class FakeApi:
            def pages_read_by_id(self, page_id, params=None):
                assert page_id == "pg1"
                return {"pages": [{"id": "pg1", "slug": "from", "title": "From", "status": "draft"}]}

        class Args:
            slug = None
            id = "pg1"

        out = _Out()
        ctx = {"apply": False, "out": out, "_api": FakeApi()}
        rc = cmd_page_copy(Args(), ctx)
        self.assertEqual(rc, 0)
        self.assertEqual(out.items[0]["copy"]["from_id"], "pg1")

    def test_post_copy_reads_back_and_requires_draft(self) -> None:
        class FakeApi:
            def __init__(self) -> None:
                self.read_ids: list[str] = []

            def posts_read_by_id(self, post_id, params=None):
                self.read_ids.append(post_id)
                if post_id == "p1":
                    return {"posts": [{"id": "p1", "slug": "from", "title": "From", "status": "draft"}]}
                if post_id == "p2":
                    return {"posts": [{"id": "p2", "slug": "copy", "title": "Copy", "status": "draft"}]}
                raise AssertionError(f"unexpected post_id: {post_id}")

            def posts_copy(self, post_id):
                assert post_id == "p1"
                return {"posts": [{"id": "p2"}]}

        class Args:
            slug = None
            id = "p1"

        api = FakeApi()
        out = _Out()
        ctx = {"apply": True, "out": out, "_api": api, "audit": _Audit()}
        rc = cmd_post_copy(Args(), ctx)
        self.assertEqual(rc, 0)
        self.assertEqual(api.read_ids, ["p1", "p2"])
        self.assertEqual(out.items[0]["from_id"], "p1")
        self.assertEqual(out.items[0]["to_id"], "p2")
        self.assertEqual(out.items[0]["status"], "draft")

    def test_post_copy_raises_when_read_back_is_not_draft(self) -> None:
        class FakeApi:
            def posts_read_by_id(self, post_id, params=None):
                if post_id == "p1":
                    return {"posts": [{"id": "p1", "slug": "from", "title": "From", "status": "draft"}]}
                if post_id == "p2":
                    return {"posts": [{"id": "p2", "slug": "copy", "title": "Copy", "status": "published"}]}
                raise AssertionError(f"unexpected post_id: {post_id}")

            def posts_copy(self, post_id):
                assert post_id == "p1"
                return {"posts": [{"id": "p2"}]}

        class Args:
            slug = None
            id = "p1"

        ctx = {"apply": True, "out": _Out(), "_api": FakeApi(), "audit": _Audit()}
        with self.assertRaises(RuntimeError):
            cmd_post_copy(Args(), ctx)

    def test_page_copy_reads_back_and_requires_draft(self) -> None:
        class FakeApi:
            def __init__(self) -> None:
                self.read_ids: list[str] = []

            def pages_read_by_id(self, page_id, params=None):
                self.read_ids.append(page_id)
                if page_id == "pg1":
                    return {"pages": [{"id": "pg1", "slug": "from", "title": "From", "status": "draft"}]}
                if page_id == "pg2":
                    return {"pages": [{"id": "pg2", "slug": "copy", "title": "Copy", "status": "draft"}]}
                raise AssertionError(f"unexpected page_id: {page_id}")

            def pages_copy(self, page_id):
                assert page_id == "pg1"
                return {"pages": [{"id": "pg2"}]}

        class Args:
            slug = None
            id = "pg1"

        api = FakeApi()
        out = _Out()
        ctx = {"apply": True, "out": out, "_api": api, "audit": _Audit()}
        rc = cmd_page_copy(Args(), ctx)
        self.assertEqual(rc, 0)
        self.assertEqual(api.read_ids, ["pg1", "pg2"])
        self.assertEqual(out.items[0]["from_id"], "pg1")
        self.assertEqual(out.items[0]["to_id"], "pg2")
        self.assertEqual(out.items[0]["status"], "draft")

    def test_page_copy_raises_when_read_back_is_not_draft(self) -> None:
        class FakeApi:
            def pages_read_by_id(self, page_id, params=None):
                if page_id == "pg1":
                    return {"pages": [{"id": "pg1", "slug": "from", "title": "From", "status": "draft"}]}
                if page_id == "pg2":
                    return {"pages": [{"id": "pg2", "slug": "copy", "title": "Copy", "status": "published"}]}
                raise AssertionError(f"unexpected page_id: {page_id}")

            def pages_copy(self, page_id):
                assert page_id == "pg1"
                return {"pages": [{"id": "pg2"}]}

        class Args:
            slug = None
            id = "pg1"

        ctx = {"apply": True, "out": _Out(), "_api": FakeApi(), "audit": _Audit()}
        with self.assertRaises(RuntimeError):
            cmd_page_copy(Args(), ctx)

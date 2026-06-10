import unittest

from ghost_api_tool.commands.tag import _merge_tag_refs


class TagMergeTests(unittest.TestCase):
    def test_merge_replaces_from_with_to(self):
        tags = [{"id": "a", "slug": "from"}, {"id": "x", "slug": "keep"}]
        out, changed = _merge_tag_refs(tags, from_id="a", to_id="b")
        self.assertTrue(changed)
        self.assertEqual([t["id"] for t in out], ["b", "x"])

    def test_merge_removes_from_when_to_already_present(self):
        tags = [{"id": "x", "slug": "keep"}, {"id": "a", "slug": "from"}, {"id": "b", "slug": "to"}]
        out, changed = _merge_tag_refs(tags, from_id="a", to_id="b")
        self.assertTrue(changed)
        self.assertEqual([t["id"] for t in out], ["x", "b"])

    def test_merge_noop_when_from_missing(self):
        tags = [{"id": "x", "slug": "keep"}]
        out, changed = _merge_tag_refs(tags, from_id="a", to_id="b")
        self.assertFalse(changed)
        self.assertIs(out, tags)

    def test_merge_dedupes_to(self):
        tags = [{"id": "a"}, {"id": "b"}, {"id": "b"}]
        out, changed = _merge_tag_refs(tags, from_id="a", to_id="b")
        self.assertTrue(changed)
        self.assertEqual([t["id"] for t in out], ["b"])


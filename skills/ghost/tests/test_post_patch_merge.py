import unittest

from ghost_api_tool.diffutil import diff_dict


class PatchMergeTests(unittest.TestCase):
    def test_diff_dict(self):
        before = {"title": "A", "status": "draft"}
        after = {"title": "B", "status": "draft"}
        changes = diff_dict(before, after, keys=["title", "status"])
        self.assertEqual(len(changes), 1)
        self.assertEqual(changes[0]["field"], "title")

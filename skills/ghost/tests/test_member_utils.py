import unittest

from ghost_api_tool.member_utils import merge_labels, parse_delimited_list, redact_email, slugify_label


class MemberUtilsTests(unittest.TestCase):
    def test_slugify_label(self) -> None:
        self.assertEqual(slugify_label("VIP"), "vip")
        self.assertEqual(slugify_label("New  Label!"), "new-label")
        self.assertEqual(slugify_label("  --Hello--  "), "hello")

    def test_parse_delimited_list(self) -> None:
        self.assertEqual(parse_delimited_list("a,b;c|d"), ["a", "b", "c", "d"])
        self.assertEqual(parse_delimited_list(""), [])
        self.assertEqual(parse_delimited_list(None), [])
        self.assertEqual(parse_delimited_list("A, a"), ["A"])

    def test_redact_email(self) -> None:
        self.assertEqual(redact_email("user@example.com"), "u***@e***")
        self.assertEqual(redact_email("x@d.com"), "x***@d***")
        self.assertEqual(redact_email("not-an-email"), "***")

    def test_merge_labels_add_remove(self) -> None:
        existing = [{"id": "1", "name": "VIP", "slug": "vip"}, {"id": "2", "name": "Old", "slug": "old"}]
        merged = merge_labels(existing=existing, add=["New"], remove=["old"])
        slugs = sorted([x["slug"] for x in merged])
        self.assertEqual(slugs, ["new", "vip"])

    def test_merge_labels_replace(self) -> None:
        existing = [{"id": "1", "name": "VIP", "slug": "vip"}]
        merged = merge_labels(existing=existing, replace=["A", "B"])
        slugs = sorted([x["slug"] for x in merged])
        self.assertEqual(slugs, ["a", "b"])


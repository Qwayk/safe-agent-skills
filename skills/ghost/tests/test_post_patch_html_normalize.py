import unittest

from ghost_api_tool.post_patch import _normalize_html_for_verification


class TestPostPatchHtmlNormalize(unittest.TestCase):
    def test_ignores_heading_ids(self) -> None:
        a = '<h2 id="x">Title</h2>'
        b = "<h2>Title</h2>"
        self.assertEqual(
            _normalize_html_for_verification(a, internal_hosts=set()),
            _normalize_html_for_verification(b, internal_hosts=set()),
        )

    def test_unescapes_ampersand(self) -> None:
        a = "<p>A &amp; B</p>"
        b = "<p>A & B</p>"
        self.assertEqual(
            _normalize_html_for_verification(a, internal_hosts=set()),
            _normalize_html_for_verification(b, internal_hosts=set()),
        )

    def test_strips_anchor_rel_and_target(self) -> None:
        a = '<p><a href="https://x" rel="nofollow sponsored" target="_blank">X</a></p>'
        b = '<p><a href="https://x">X</a></p>'
        self.assertEqual(
            _normalize_html_for_verification(a, internal_hosts=set()),
            _normalize_html_for_verification(b, internal_hosts=set()),
        )

    def test_normalizes_internal_absolute_urls(self) -> None:
        internal = {"mysite.example", "www.mysite.example"}
        a = '<a href="https://mysite.example/disclaimer/">D</a><img src="https://www.mysite.example/x.jpg">'
        b = '<a href="/disclaimer/">D</a><img src="/x.jpg">'
        self.assertEqual(
            _normalize_html_for_verification(a, internal_hosts=internal),
            _normalize_html_for_verification(b, internal_hosts=internal),
        )

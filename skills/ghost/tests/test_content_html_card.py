import unittest

from ghost_api_tool.content_html_card import extract_html_card, set_figcaptions_by_src


class HtmlCardTests(unittest.TestCase):
    def test_refuses_without_html_card(self):
        rep, out = set_figcaptions_by_src("<p>x</p>", captions_by_src={"a": "b"}, include_diff=False)
        self.assertTrue(rep.refused)
        self.assertEqual(out, "<p>x</p>")

    def test_updates_figcaption_by_src(self):
        html = (
            "<!--kg-card-begin: html-->"
            '<figure><img src="https://example.com/a.jpg"/></figure>'
            "<!--kg-card-end: html-->"
        )
        rep, out = set_figcaptions_by_src(html, captions_by_src={"https://example.com/a.jpg": "Cap"}, include_diff=True)
        self.assertFalse(rep.refused)
        self.assertEqual(rep.matched_images, 1)
        self.assertEqual(rep.updated_figcaptions, 1)
        self.assertIn("<figcaption>Cap</figcaption>", out)
        self.assertIsNotNone(rep.diff)

    def test_preserves_figcaption_attributes(self):
        html = (
            "<!--kg-card-begin: html-->"
            '<figure><img src="https://example.com/a.jpg"/>'
            '<figcaption class="kg-caption">Old</figcaption></figure>'
            "<!--kg-card-end: html-->"
        )
        rep, out = set_figcaptions_by_src(
            html, captions_by_src={"https://example.com/a.jpg": "New"}, include_diff=False
        )
        self.assertFalse(rep.refused)
        self.assertIn('<figcaption class="kg-caption">New</figcaption>', out)

    def test_extract_html_card(self):
        html = "<!--kg-card-begin: html--><p>Hi</p><!--kg-card-end: html-->"
        self.assertEqual(extract_html_card(html), "<p>Hi</p>")

    def test_extract_html_card_refuses_multiple(self):
        html = (
            "<!--kg-card-begin: html--><p>One</p><!--kg-card-end: html-->"
            "<!--kg-card-begin: html--><p>Two</p><!--kg-card-end: html-->"
        )
        self.assertIsNone(extract_html_card(html))

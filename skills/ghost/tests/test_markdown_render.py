import unittest

from ghost_api_tool.markdown_render import render_markdown

try:
    import markdown  # type: ignore[import-untyped]  # noqa: F401
except ModuleNotFoundError:
    markdown = None


@unittest.skipIf(markdown is None, "markdown dependency not installed")
class MarkdownRenderTests(unittest.TestCase):
    def test_strips_leading_h1(self) -> None:
        r = render_markdown("# My Title\n\nHello **world**.")
        self.assertEqual(r.dropped_h1, "My Title")
        self.assertNotIn("<h1", r.html)
        self.assertIn("<strong>world</strong>", r.html)

    def test_renders_tables(self) -> None:
        r = render_markdown(
            "# Title\n\n| A | B |\n|---|---|\n| 1 | 2 |\n",
        )
        self.assertIn("<table", r.html)

    def test_preserves_raw_html_blocks(self) -> None:
        r = render_markdown("# Title\n\n<div id=\"consumer-privacy-footer-wrapper\"></div>\n")
        self.assertIn("consumer-privacy-footer-wrapper", r.html)

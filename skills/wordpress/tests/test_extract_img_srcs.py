import unittest

from wordpress_api_tool.extract import extract_img_srcs_from_html


class ExtractImgSrcTests(unittest.TestCase):
    def test_extract_img_src_and_srcset(self):
        html = (
            '<p><img src="https://example.com/a.jpg" '
            'srcset="https://example.com/a-1.jpg 1x, https://example.com/a-2.jpg 2x"/></p>'
        )
        out = extract_img_srcs_from_html(html)
        self.assertIn("https://example.com/a.jpg", out)
        self.assertIn("https://example.com/a-1.jpg", out)
        self.assertIn("https://example.com/a-2.jpg", out)

    def test_dedupes(self):
        html = '<img src="x"/><img src="x"/>'
        out = extract_img_srcs_from_html(html)
        self.assertEqual(out, ["x"])


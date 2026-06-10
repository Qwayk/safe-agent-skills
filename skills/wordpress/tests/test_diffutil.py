import unittest

from wordpress_api_tool.diffutil import caption_text_from_media, title_text_from_media


class DiffUtilTests(unittest.TestCase):
    def test_caption_text_prefers_raw(self):
        media = {"caption": {"raw": "x", "rendered": "y"}}
        self.assertEqual(caption_text_from_media(media), "x")

    def test_title_text_prefers_raw(self):
        media = {"title": {"raw": "x", "rendered": "y"}}
        self.assertEqual(title_text_from_media(media), "x")


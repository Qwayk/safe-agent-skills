import unittest

from wordpress_api_tool.edit_content import update_gutenberg_image_captions


class PlanLikeBehaviorTests(unittest.TestCase):
    def test_dry_run_generates_diff(self):
        raw = (
            '<!-- wp:image {"id":123} -->'
            "<figure><img src='x'/></figure>"
            "<!-- /wp:image -->"
        )
        rep, out = update_gutenberg_image_captions(
            raw,
            caption_text="Cap",
            caption_html=None,
            alt_text=None,
            only_ids=None,
            include_diff=True,
        )
        self.assertNotEqual(out, raw)
        self.assertIsNotNone(rep.diff)


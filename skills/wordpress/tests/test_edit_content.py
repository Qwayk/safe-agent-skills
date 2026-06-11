import unittest

from wordpress_api_tool.edit_content import update_gutenberg_image_captions


class EditContentTests(unittest.TestCase):
    def test_updates_figcaption_and_alt(self):
        raw = (
            '<!-- wp:image {"id":123} -->'
            '<figure><img src="x" alt="old"/><figcaption>Old</figcaption></figure>'
            "<!-- /wp:image -->"
        )
        rep, out = update_gutenberg_image_captions(
            raw,
            caption_text='New "cap"',
            caption_html=None,
            alt_text='new "alt"',
            only_ids={123},
            include_diff=True,
        )
        self.assertEqual(rep.updated_blocks, 1)
        self.assertIn('<figcaption>New "cap"</figcaption>', out)
        self.assertIn('alt="new &quot;alt&quot;"', out)
        self.assertIsNotNone(rep.diff)

    def test_refuses_without_id(self):
        raw = '<!-- wp:image {} --><figure><img src="x"/></figure><!-- /wp:image -->'
        rep, out = update_gutenberg_image_captions(
            raw,
            caption_text="Cap",
            caption_html=None,
            alt_text=None,
            only_ids=None,
            include_diff=False,
        )
        self.assertEqual(rep.refused_blocks, 1)
        self.assertEqual(out, raw)

    def test_falls_back_to_wp_image_class_id(self):
        raw = (
            "<!-- wp:image {} -->"
            '<figure><img class="wp-image-123" src="x"/><figcaption>Old</figcaption></figure>'
            "<!-- /wp:image -->"
        )
        rep, out = update_gutenberg_image_captions(
            raw,
            caption_text=None,
            caption_html=None,
            alt_text=None,
            caption_text_by_id={123: "Cap"},
            only_ids=None,
            include_diff=False,
        )
        self.assertEqual(rep.refused_blocks, 0)
        self.assertEqual(rep.updated_blocks, 1)
        self.assertIn("<figcaption>Cap</figcaption>", out)

    def test_skips_unidentifiable_image_blocks_in_mapping_mode(self):
        raw = (
            "<!-- wp:image {} -->"
            '<figure><img src="https://example.com/external.jpg" alt=""/></figure>'
            "<!-- /wp:image -->"
        )
        rep, out = update_gutenberg_image_captions(
            raw,
            caption_text=None,
            caption_html=None,
            alt_text=None,
            caption_text_by_id={123: "Cap"},
            only_ids=None,
            include_diff=False,
        )
        self.assertEqual(rep.refused_blocks, 0)
        self.assertEqual(rep.updated_blocks, 0)
        self.assertEqual(out, raw)

    def test_updates_alt_with_single_quotes(self):
        raw = (
            '<!-- wp:image {"id":123} -->'
            "<figure><img src='x' alt='old'></figure>"
            "<!-- /wp:image -->"
        )
        rep, out = update_gutenberg_image_captions(
            raw,
            caption_text=None,
            caption_html=None,
            alt_text="new",
            only_ids={123},
            include_diff=False,
        )
        self.assertEqual(rep.updated_blocks, 1)
        self.assertIn('alt="new"', out)

    def test_caption_map_updates_multiple_ids(self):
        raw = (
            '<!-- wp:image {"id":1} -->'
            "<figure><img src='a'/><figcaption>Old A</figcaption></figure>"
            "<!-- /wp:image -->"
            '<!-- wp:image {"id":2} -->'
            "<figure><img src='b'/><figcaption>Old B</figcaption></figure>"
            "<!-- /wp:image -->"
        )
        rep, out = update_gutenberg_image_captions(
            raw,
            caption_text=None,
            caption_html=None,
            alt_text=None,
            caption_text_by_id={1: "Cap A", 2: "Cap B"},
            only_ids=None,
            include_diff=True,
        )
        self.assertEqual(rep.updated_blocks, 2)
        self.assertIn("<figcaption>Cap A</figcaption>", out)
        self.assertIn("<figcaption>Cap B</figcaption>", out)
        self.assertIsNotNone(rep.diff)

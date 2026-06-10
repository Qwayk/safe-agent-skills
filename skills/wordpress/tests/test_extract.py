import unittest

from wordpress_api_tool.extract import extract_attachment_ids_from_post_content


class ExtractTests(unittest.TestCase):
    def test_extracts_from_img_class(self):
        raw = '<p><img class="wp-image-123 size-full" src="x"></p>'
        ids = extract_attachment_ids_from_post_content(raw)
        self.assertEqual([i.attachment_id for i in ids], [123])
        self.assertIn("img_class", ids[0].sources)

    def test_extracts_from_wp_image_block(self):
        raw = '<!-- wp:image {"id":456} --><figure>...</figure><!-- /wp:image -->'
        ids = extract_attachment_ids_from_post_content(raw)
        self.assertEqual([i.attachment_id for i in ids], [456])
        self.assertIn("wp_image_block", ids[0].sources)


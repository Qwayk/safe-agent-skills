from __future__ import annotations

import json
import unittest

from ghost_api_tool.commands.post_images import _ledger_rows_for_post


class TestPostImagesExportLedger(unittest.TestCase):
    def test_ledger_rows_includes_featured_and_body_images(self) -> None:
        lexical_doc = {
            "root": {
                "type": "root",
                "version": 1,
                "children": [
                    {
                        "type": "extended-heading",
                        "version": 1,
                        "tag": "h2",
                        "children": [{"type": "extended-text", "version": 1, "text": "Instructions"}],
                    },
                    {
                        "type": "image",
                        "version": 1,
                        "src": "https://example.com/body.jpg",
                        "alt": "Body alt",
                        "caption": "Body caption (stock image; for illustration only).",
                        "title": "",
                        "href": "",
                        "cardWidth": "regular",
                        "width": None,
                        "height": None,
                    },
                ],
            }
        }
        post = {
            "id": "post123",
            "slug": "my-post",
            "title": "My Post",
            "status": "published",
            "feature_image": "https://example.com/feat.jpg",
            "feature_image_alt": "Feat alt",
            "feature_image_caption": "Feat caption (stock image; for illustration only).",
            "primary_tag": {"slug": "recipes"},
            "tags": [{"slug": "recipes"}, {"slug": "bread"}],
            "lexical": json.dumps(lexical_doc),
        }
        rows, warnings = _ledger_rows_for_post(post)
        self.assertEqual(warnings, [])
        self.assertEqual([r.image_kind for r in rows], ["featured", "body"])
        self.assertEqual(rows[0].image_url, "https://example.com/feat.jpg")
        self.assertEqual(rows[1].image_url, "https://example.com/body.jpg")
        self.assertEqual(rows[0].primary_tag_slug, "recipes")
        self.assertEqual(rows[0].tags_slugs, "recipes|bread")
        self.assertEqual(rows[1].context_heading, "Instructions")

    def test_ledger_rows_handles_bad_lexical(self) -> None:
        post = {
            "id": "post123",
            "slug": "my-post",
            "title": "My Post",
            "status": "published",
            "feature_image": "https://example.com/feat.jpg",
            "lexical": "not-json",
        }
        rows, warnings = _ledger_rows_for_post(post)
        # Featured row should still be present.
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].image_kind, "featured")
        self.assertTrue(warnings)


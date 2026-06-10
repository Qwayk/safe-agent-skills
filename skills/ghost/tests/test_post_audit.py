import unittest

from ghost_api_tool.post_audit import audit_post


class PostAuditTests(unittest.TestCase):
    def test_audit_flags_slug_suffix_and_missing_meta(self):
        post = {
            "slug": "hello-693feda73bdf05001bf2504e",
            "meta_description": "",
            "feature_image": None,
            "lexical": {
                "root": {
                    "type": "root",
                    "version": 1,
                    "children": [
                        {"type": "image", "version": 1, "src": "https://mysite.example/wp-content/uploads/a.jpg"},
                        {"type": "image", "version": 1, "src": "https://mysite.example/wp-content/uploads/a.jpg"},
                    ],
                }
            },
        }
        rep = audit_post(post, legacy_hosts=["mysite.example"])
        self.assertFalse(rep["ready_to_publish"])
        issues = rep["issues"]
        self.assertTrue(any(i["type"] == "slug" for i in issues))
        self.assertTrue(any(i["type"] == "meta" for i in issues))
        self.assertTrue(any(i["type"] == "body_images" and "duplicates" in i for i in issues))
        self.assertTrue(any(i["type"] == "body_images" and "WordPress uploads" in i["message"] for i in issues))

    def test_audit_flags_html_list_cards(self):
        post = {
            "slug": "ok-slug",
            "meta_description": "ok",
            "feature_image": None,
            "lexical": {
                "root": {
                    "type": "root",
                    "version": 1,
                    "children": [
                        {"type": "extended-heading", "version": 1, "children": [{"type": "extended-text", "version": 1, "text": "Intro"}]},
                        {
                            "type": "list",
                            "version": 1,
                            "listType": "bullet",
                            "children": [
                                {"type": "listitem", "version": 1, "value": 1, "children": [{"type": "extended-text", "version": 1, "text": "Item one"}]}
                            ],
                        },
                        {
                            "type": "html",
                            "version": 1,
                            "html": '<ul start="2"><!-- wp:list-item --><li><strong>Item two</strong> — Second</li><!-- /wp:list-item --></ul>',
                        },
                    ],
                }
            },
        }
        rep = audit_post(post, legacy_hosts=["mysite.example"])
        self.assertFalse(rep["ready_to_publish"])
        self.assertTrue(any(i["type"] == "content_structure" for i in rep["issues"]))

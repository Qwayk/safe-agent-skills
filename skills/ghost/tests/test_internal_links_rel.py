import unittest

from ghost_api_tool.internal_links import extract_links_from_lexical


def _doc(children):
    return {
        "root": {
            "type": "root",
            "version": 1,
            "children": children,
            "direction": None,
            "format": "",
            "indent": 0,
        }
    }


class TestInternalLinksRel(unittest.TestCase):
    def test_extract_links_includes_rel_for_lexical_links_only(self) -> None:
        doc = _doc(
            [
                {
                    "type": "paragraph",
                    "version": 1,
                    "children": [
                        {
                            "type": "link",
                            "version": 1,
                            "url": "https://example.com",
                            "rel": "nofollow sponsored",
                            "children": [{"type": "extended-text", "version": 1, "text": "X"}],
                        }
                    ],
                }
            ]
        )
        occ = extract_links_from_lexical(
            doc,
            source_id="1",
            source_slug="s",
            source_title="t",
            source_status="draft",
        )
        self.assertEqual(len(occ), 1)
        self.assertEqual(occ[0].origin, "lexical_link")
        self.assertEqual(occ[0].rel, "nofollow sponsored")


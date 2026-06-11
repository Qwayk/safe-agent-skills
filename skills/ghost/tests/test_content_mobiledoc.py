import unittest

from ghost_api_tool.content_mobiledoc import dedupe_image_cards


class TestContentMobiledoc(unittest.TestCase):
    def test_dedupe_image_cards_keeps_first(self) -> None:
        mob = {
            "version": "0.3.1",
            "atoms": [],
            "cards": [
                ["markdown", {"markdown": "intro"}],
                ["image", {"src": "https://example.com/a.jpg", "alt": None, "caption": None}],
                ["image", {"src": "https://example.com/b.jpg"}],
                ["image", {"src": "https://example.com/a.jpg"}],  # dup
                ["image", {"src": "https://example.com/b.jpg"}],  # dup
                ["image", {"src": "https://example.com/c.jpg"}],
            ],
            "markups": [],
            "sections": [
                [10, 1],
                [10, 2],
                [10, 3],  # dup a
                [10, 4],  # dup b
                [10, 5],
            ],
        }

        rep, new_obj, result = dedupe_image_cards(mob, include_diff=False)
        self.assertFalse(rep.refused)
        self.assertTrue(rep.changed)
        self.assertEqual(result.removed, 2)

        cards = new_obj["cards"]
        image_srcs = [c[1]["src"] for c in cards if isinstance(c, list) and c and c[0] == "image"]
        self.assertEqual(image_srcs, ["https://example.com/a.jpg", "https://example.com/b.jpg", "https://example.com/c.jpg"])

        # Sections referencing removed cards are dropped and remaining card indices are re-mapped
        self.assertEqual(new_obj["sections"], [[10, 1], [10, 2], [10, 3]])

        # Idempotent: running again yields no changes
        rep2, new2, result2 = dedupe_image_cards(new_obj, include_diff=False)
        self.assertFalse(rep2.refused)
        self.assertFalse(rep2.changed)
        self.assertEqual(result2.removed, 0)


if __name__ == "__main__":
    unittest.main()

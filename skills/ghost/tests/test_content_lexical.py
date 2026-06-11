import unittest

from ghost_api_tool.content_lexical import (
    build_replace_many_map_for_missing_captions,
    convert_html_list_cards_to_native_lists,
    delete_images_by_src,
    insert_link_paragraph_after_heading_section_end,
    fix_link_whitespace,
    fix_bullet_lists_split_by_html_ul_cards,
    fix_numbered_list_split_by_html_ol_after_heading,
    fix_numbered_paragraphs_to_list_after_heading,
    clear_heading_bold,
    linkify_text_in_paragraph,
    insert_image_after_heading,
    list_images,
    move_top_level_image_before_heading,
    replace_first_image_after_heading,
    replace_image_src,
    replace_images_by_src_map,
    set_paid_rel_on_amazon_links,
    set_paid_rel_on_links,
    set_image_meta_by_src,
    sync_top_level_images_before_headings,
    unlink_links_by_url,
    unlink_links_by_url_after_heading,
    delete_linked_list_items_by_url_after_heading,
    unlink_internal_links_in_image_captions,
    insert_internal_links_section_before_heading,
)


def _heading(text: str):
    return {
        "type": "extended-heading",
        "version": 1,
        "children": [{"type": "extended-text", "version": 1, "text": text}],
    }


def _image(src: str, *, alt: str = "", caption: str = "", title: str = ""):
    return {
        "type": "image",
        "version": 1,
        "src": src,
        "alt": alt,
        "caption": caption,
        "title": title,
        "width": 100,
        "height": 50,
        "cardWidth": "regular",
        "href": None,
    }


def _doc(children):
    return {"root": {"type": "root", "version": 1, "children": children}}


def _para(text: str):
    return {"type": "paragraph", "version": 1, "children": [{"type": "extended-text", "version": 1, "text": text}]}


def _link(url: str, text: str):
    return {
        "type": "link",
        "version": 1,
        "url": url,
        "children": [{"type": "extended-text", "version": 1, "text": text}],
    }


def _list(items: list[str]):
    children = []
    value = 1
    for text in items:
        children.append(
            {
                "type": "listitem",
                "version": 1,
                "value": value,
                "children": [{"type": "extended-text", "version": 1, "text": text}],
            }
        )
        value += 1
    return {"type": "list", "version": 1, "listType": "bullet", "tag": "ul", "children": children}


class LexicalContentTests(unittest.TestCase):
    def test_clear_heading_bold_removes_partial_bold(self):
        doc = _doc(
            [
                {
                    "type": "extended-heading",
                    "version": 1,
                    "tag": "h3",
                    "children": [
                        {"type": "extended-text", "version": 1, "text": "1. ", "format": 1},
                        {"type": "extended-text", "version": 1, "text": "Avoid skipping meals", "format": 0},
                    ],
                },
                _para("Body"),
            ]
        )
        rep, out = clear_heading_bold(doc, include_diff=False)
        self.assertFalse(rep.refused)
        self.assertTrue(rep.changed)
        self.assertEqual(rep.matched, 1)
        # Ensure the bold bit was cleared.
        children = out["root"]["children"][0]["children"]
        self.assertEqual(children[0].get("format"), 0)
        self.assertEqual(children[1].get("format"), 0)

        # Idempotence.
        rep2, out2 = clear_heading_bold(out, include_diff=False)
        self.assertFalse(rep2.refused)
        self.assertFalse(rep2.changed)
        self.assertEqual(rep2.matched, 0)
        self.assertEqual(out2, out)

    def test_list_images_includes_context_heading(self):
        doc = _doc([_heading("Ingredients"), _image("a"), _heading("Other"), _image("b")])
        imgs = list_images(doc)
        self.assertEqual(len(imgs), 2)
        self.assertEqual(imgs[0].src, "a")
        self.assertEqual(imgs[0].context_heading, "Ingredients")
        self.assertEqual(imgs[0].title, "")
        self.assertEqual(imgs[1].src, "b")
        self.assertEqual(imgs[1].context_heading, "Other")
        self.assertEqual(imgs[1].title, "")

    def test_replace_image_src_wraps_plain_caption(self):
        doc = _doc([_heading("Ingredients"), _image("old", caption="Old caption")])
        rep, out = replace_image_src(
            doc,
            old_src="old",
            new_src="new",
            alt=None,
            caption="New caption",
            title=None,
            include_diff=False,
        )
        self.assertFalse(rep.refused)
        self.assertTrue(rep.changed)
        img = out["root"]["children"][1]
        self.assertEqual(img["src"], "new")
        self.assertIn("New caption", img["caption"])
        self.assertIn("white-space: pre-wrap", img["caption"])

    def test_replace_image_src_refuses_multiple_matches(self):
        doc = _doc([_image("same"), _image("same")])
        rep, out = replace_image_src(
            doc,
            old_src="same",
            new_src="new",
            alt=None,
            caption=None,
            title=None,
            include_diff=False,
        )
        self.assertTrue(rep.refused)
        self.assertEqual(rep.matched, 2)
        self.assertIs(out, doc)

    def test_replace_image_src_treats_new_src_as_already_replaced(self):
        doc = _doc([_image("new", alt="old alt", caption="old cap")])
        rep, out = replace_image_src(
            doc,
            old_src="old",
            new_src="new",
            alt="new alt",
            caption="new cap",
            title=None,
            include_diff=False,
        )
        self.assertFalse(rep.refused)
        self.assertEqual(rep.matched, 1)
        self.assertIn("already replaced", " ".join(rep.reasons).lower())
        img = out["root"]["children"][0]
        self.assertEqual(img["src"], "new")
        self.assertEqual(img["alt"], "new alt")
        self.assertIn("new cap", img["caption"])

    def test_move_top_level_image_before_heading_moves_card(self):
        doc = _doc([_heading("Ingredients"), _image("a"), {"type": "paragraph", "version": 1, "children": []}, _heading("Instructions")])
        rep, out = move_top_level_image_before_heading(
            doc,
            src="a",
            heading="Instructions",
            heading_occurrence=None,
            include_diff=False,
        )
        self.assertFalse(rep.refused)
        self.assertTrue(rep.changed)
        children = out["root"]["children"]
        # Image should now be immediately before the Instructions heading.
        self.assertEqual(children[-2]["type"], "image")
        self.assertEqual(children[-2]["src"], "a")
        self.assertEqual(children[-1]["type"], "extended-heading")

    def test_fix_numbered_paragraphs_to_list_after_heading_converts(self):
        doc = _doc([_heading("Instructions"), _para("1. First step"), _para("2. Second step"), _heading("Notes")])
        rep, out = fix_numbered_paragraphs_to_list_after_heading(
            doc,
            heading="Instructions",
            heading_occurrence=None,
            include_diff=False,
        )
        self.assertFalse(rep.refused)
        self.assertTrue(rep.changed)
        self.assertEqual(rep.matched, 2)
        children = out["root"]["children"]
        self.assertEqual(children[1]["type"], "list")
        self.assertEqual(children[1]["listType"], "number")
        self.assertEqual(children[1]["tag"], "ol")
        self.assertEqual(children[1]["children"][0]["children"][0]["text"], "First step")
        self.assertEqual(children[1]["children"][1]["children"][0]["text"], "Second step")

    def test_fix_numbered_paragraphs_to_list_after_heading_refuses_nonconsecutive(self):
        doc = _doc([_heading("Instructions"), _para("1. First step"), _para("3. Third step")])
        rep, out = fix_numbered_paragraphs_to_list_after_heading(
            doc,
            heading="Instructions",
            heading_occurrence=None,
            include_diff=False,
        )
        self.assertTrue(rep.refused)
        self.assertIs(out, doc)

    def test_fix_numbered_paragraphs_to_list_after_heading_noop_when_already_list(self):
        doc = _doc(
            [
                _heading("Instructions"),
                {
                    "type": "list",
                    "version": 1,
                    "listType": "number",
                    "tag": "ol",
                    "start": 1,
                    "format": "",
                    "indent": 0,
                    "direction": None,
                    "children": [
                        {
                            "type": "listitem",
                            "version": 1,
                            "value": 1,
                            "format": "",
                            "indent": 0,
                            "direction": None,
                            "children": [{"type": "extended-text", "version": 1, "text": "Step"}],
                        }
                    ],
                },
            ]
        )
        rep, out = fix_numbered_paragraphs_to_list_after_heading(
            doc,
            heading="Instructions",
            heading_occurrence=None,
            include_diff=False,
        )
        self.assertFalse(rep.refused)
        self.assertFalse(rep.changed)
        self.assertIs(out, doc)

    def test_sync_top_level_images_before_headings_removes_and_inserts(self):
        doc = _doc(
            [
                _heading("Intro"),
                _image("old1", alt="old", caption="old"),
                {"type": "html", "version": 1, "html": "<figure><img src='x'></figure>"},
                _heading("Ingredients"),
                {"type": "paragraph", "version": 1, "children": [{"type": "extended-text", "version": 1, "text": "hi"}]},
                _heading("Instructions"),
                {
                    "type": "list",
                    "version": 1,
                    "listType": "number",
                    "children": [
                        {"type": "listitem", "version": 1, "value": 1, "children": [{"type": "extended-text", "version": 1, "text": "Step 1"}]}
                    ],
                },
                _heading("Variations"),
                _image("old2", alt="old", caption="old"),
            ]
        )
        placements = [
            {"heading": "Instructions", "src": "https://example.com/new1.jpg", "alt": "a", "caption": "cap1"},
            {"heading": "Variations", "src": "https://example.com/new2.jpg", "alt": "b", "caption": "cap2"},
        ]
        rep, out = sync_top_level_images_before_headings(
            doc, placements=placements, fix_split_numbered_lists=False, include_diff=False
        )
        self.assertFalse(rep.refused)
        self.assertTrue(rep.changed)
        imgs = [n for n in out["root"]["children"] if isinstance(n, dict) and n.get("type") == "image"]
        self.assertEqual([i["src"] for i in imgs], ["https://example.com/new1.jpg", "https://example.com/new2.jpg"])

        children = out["root"]["children"]
        for idx, node in enumerate(children):
            if isinstance(node, dict) and node.get("type") == "extended-heading" and node["children"][0]["text"] == "Instructions":
                self.assertEqual(children[idx - 1]["type"], "image")
                self.assertEqual(children[idx - 1]["src"], "https://example.com/new1.jpg")
            if isinstance(node, dict) and node.get("type") == "extended-heading" and node["children"][0]["text"] == "Variations":
                self.assertEqual(children[idx - 1]["type"], "image")
                self.assertEqual(children[idx - 1]["src"], "https://example.com/new2.jpg")

        rep2, out2 = sync_top_level_images_before_headings(
            out, placements=placements, fix_split_numbered_lists=False, include_diff=False
        )
        self.assertFalse(rep2.refused)
        self.assertFalse(rep2.changed)
        self.assertEqual(out2, out)

    def test_sync_top_level_images_before_headings_allows_empty_placements_remove_only(self):
        doc = _doc([_heading("Intro"), _image("old1"), _heading("Instructions"), _image("old2")])
        rep, out = sync_top_level_images_before_headings(doc, placements=[], fix_split_numbered_lists=False, include_diff=False)
        self.assertFalse(rep.refused)
        self.assertTrue(rep.changed)
        imgs = [n for n in out["root"]["children"] if isinstance(n, dict) and n.get("type") == "image"]
        self.assertEqual(imgs, [])
        rep2, out2 = sync_top_level_images_before_headings(out, placements=[], fix_split_numbered_lists=False, include_diff=False)
        self.assertFalse(rep2.refused)
        self.assertFalse(rep2.changed)
        self.assertEqual(out2, out)

    def test_fix_numbered_list_split_by_html_ol_after_heading_merges(self):
        # Step 1 is a Lexical list, steps 2+ are split into HTML cards (common importer artifact).
        doc = _doc(
            [
                _heading("Instructions"),
                {
                    "type": "list",
                    "version": 1,
                    "listType": "number",
                    "start": 1,
                    "tag": "ol",
                    "children": [
                        {
                            "type": "listitem",
                            "version": 1,
                            "value": 1,
                            "children": [{"type": "extended-text", "version": 1, "text": "Step one"}],
                        }
                    ],
                },
                {"type": "html", "version": 1, "html": '<ol start="2"><li>Step two</li></ol>'},
                {"type": "html", "version": 1, "html": '<ol start="3"><li>Step three</li></ol>'},
                _heading("Next"),
            ]
        )
        rep, out = fix_numbered_list_split_by_html_ol_after_heading(
            doc,
            heading="Instructions",
            heading_occurrence=None,
            include_diff=False,
        )
        self.assertFalse(rep.refused)
        self.assertTrue(rep.changed)
        children = out["root"]["children"]
        # HTML cards should be removed.
        self.assertNotIn("html", [c.get("type") for c in children if isinstance(c, dict)])
        # List should have 3 items now.
        lst = children[1]
        self.assertEqual(lst["type"], "list")
        self.assertEqual(len(lst["children"]), 3)
        self.assertEqual(lst["children"][1]["value"], 2)
        self.assertEqual(lst["children"][1]["children"][0]["text"], "Step two")
        self.assertEqual(lst["children"][2]["value"], 3)
        self.assertEqual(lst["children"][2]["children"][0]["text"], "Step three")

    def test_fix_numbered_list_split_by_html_ol_after_heading_merges_consecutive_list_nodes(self):
        # Some imports create many separate Lexical list nodes, each with a single item and start=N.
        doc = _doc(
            [
                _heading("Instructions"),
                {
                    "type": "list",
                    "version": 1,
                    "listType": "number",
                    "start": 1,
                    "tag": "ol",
                    "children": [
                        {
                            "type": "listitem",
                            "version": 1,
                            "value": 1,
                            "children": [{"type": "extended-text", "version": 1, "text": "Step one"}],
                        }
                    ],
                },
                {
                    "type": "list",
                    "version": 1,
                    "listType": "number",
                    "start": 2,
                    "tag": "ol",
                    "children": [
                        {
                            "type": "listitem",
                            "version": 1,
                            "value": 2,
                            "children": [{"type": "extended-text", "version": 1, "text": "Step two"}],
                        }
                    ],
                },
                {
                    "type": "list",
                    "version": 1,
                    "listType": "number",
                    "start": 3,
                    "tag": "ol",
                    "children": [
                        {
                            "type": "listitem",
                            "version": 1,
                            "value": 3,
                            "children": [{"type": "extended-text", "version": 1, "text": "Step three"}],
                        }
                    ],
                },
                _heading("Next"),
            ]
        )
        rep, out = fix_numbered_list_split_by_html_ol_after_heading(
            doc,
            heading="Instructions",
            heading_occurrence=None,
            include_diff=False,
        )
        self.assertFalse(rep.refused)
        self.assertTrue(rep.changed)
        children = out["root"]["children"]
        lst = children[1]
        self.assertEqual(lst["type"], "list")
        self.assertEqual(len(lst["children"]), 3)
        self.assertEqual(lst["children"][1]["value"], 2)
        self.assertEqual(lst["children"][1]["children"][0]["text"], "Step two")
        self.assertEqual(lst["children"][2]["value"], 3)
        self.assertEqual(lst["children"][2]["children"][0]["text"], "Step three")

    def test_fix_bullet_lists_split_by_html_ul_cards_merges_and_preserves_bold_title(self):
        doc = _doc(
            [
                _heading("Intro"),
                {
                    "type": "list",
                    "version": 1,
                    "listType": "bullet",
                    "children": [
                        {
                            "type": "listitem",
                            "version": 1,
                            "value": 1,
                            "format": "",
                            "indent": 0,
                            "direction": None,
                            "children": [
                                {"type": "extended-text", "version": 1, "text": "Item one", "format": 1, "detail": 0, "mode": "normal", "style": ""},
                                {"type": "extended-text", "version": 1, "text": " — First", "format": 0, "detail": 0, "mode": "normal", "style": ""},
                            ],
                        }
                    ],
                },
                {
                    "type": "html",
                    "version": 1,
                    "html": '<ul start="2"><!-- wp:list-item --><li><strong>Item two</strong> — Second</li><!-- /wp:list-item --></ul>',
                },
                {
                    "type": "html",
                    "version": 1,
                    "html": '<ul start="3"><!-- wp:list-item --><li><strong>Item three</strong> — Third</li><!-- /wp:list-item --></ul>',
                },
                _heading("Next"),
            ]
        )
        rep, out = fix_bullet_lists_split_by_html_ul_cards(doc, include_diff=False)
        self.assertFalse(rep.refused)
        self.assertTrue(rep.changed)
        self.assertEqual(rep.matched, 2)
        children = out["root"]["children"]
        self.assertNotIn("html", [c.get("type") for c in children if isinstance(c, dict)])
        lst = children[1]
        self.assertEqual(lst["type"], "list")
        self.assertEqual(lst["listType"], "bullet")
        self.assertEqual(len(lst["children"]), 3)
        self.assertEqual(lst["children"][1]["value"], 2)
        self.assertEqual(lst["children"][2]["value"], 3)
        item2_nodes = lst["children"][1]["children"]
        self.assertEqual(item2_nodes[0]["text"], "Item two")
        self.assertEqual(item2_nodes[0]["format"], 1)
        self.assertEqual(item2_nodes[1]["text"], " — Second")
        self.assertEqual(item2_nodes[1]["format"], 0)

        rep2, out2 = fix_bullet_lists_split_by_html_ul_cards(out, include_diff=False)
        self.assertFalse(rep2.refused)
        self.assertFalse(rep2.changed)
        self.assertEqual(out2, out)

    def test_fix_bullet_lists_split_by_html_ul_cards_refuses_unsupported_tags(self):
        doc = _doc(
            [
                {
                    "type": "list",
                    "version": 1,
                    "listType": "bullet",
                    "children": [
                        {
                            "type": "listitem",
                            "version": 1,
                            "value": 1,
                            "children": [{"type": "extended-text", "version": 1, "text": "Item one", "format": 0}],
                        }
                    ],
                },
                {
                    "type": "html",
                    "version": 1,
                    "html": '<ul start="2"><li><strong>Item two</strong> <a href="https://example.com">link</a></li></ul>',
                },
            ]
        )
        rep, out = fix_bullet_lists_split_by_html_ul_cards(doc, include_diff=False)
        self.assertTrue(rep.refused)
        self.assertIs(out, doc)

    def test_convert_html_list_cards_to_native_lists_converts_ol_and_ul_cards(self):
        doc = _doc(
            [
                {
                    "type": "list",
                    "version": 1,
                    "listType": "bullet",
                    "children": [
                        {"type": "listitem", "version": 1, "value": 1, "children": [{"type": "extended-text", "version": 1, "text": "Item one"}]}
                    ],
                },
                {"type": "html", "version": 1, "html": '<ul><!-- wp:list-item --><li>Item two</li><!-- /wp:list-item --></ul>'},
                _image("x"),
                {
                    "type": "html",
                    "version": 1,
                    "html": '<ol start="2"><!-- wp:list-item --><li><strong>Step two</strong> — do it</li><!-- /wp:list-item --></ol>',
                },
            ]
        )
        rep, out = convert_html_list_cards_to_native_lists(doc, include_diff=False)
        self.assertFalse(rep.refused)
        self.assertTrue(rep.changed)
        self.assertEqual(rep.matched, 2)
        children = out["root"]["children"]
        # The <ul> card should be merged into the preceding bullet list.
        self.assertEqual(children[0]["type"], "list")
        self.assertEqual(children[0]["listType"], "bullet")
        self.assertEqual(len(children[0]["children"]), 2)
        self.assertEqual(children[0]["children"][1]["children"][0]["text"], "Item two")
        # The <ol> card should become a native ordered list (kept separate due to image in between).
        lst = children[2]
        self.assertEqual(lst["type"], "list")
        self.assertEqual(lst["listType"], "number")
        self.assertEqual(lst["start"], 2)
        self.assertEqual(lst["children"][0]["value"], 2)
        self.assertEqual(lst["children"][0]["children"][0]["text"], "Step two")
        self.assertEqual(lst["children"][0]["children"][0]["format"], 1)
        self.assertEqual(lst["children"][0]["children"][1]["text"], " — do it")

        rep2, out2 = convert_html_list_cards_to_native_lists(out, include_diff=False)
        self.assertFalse(rep2.refused)
        self.assertFalse(rep2.changed)
        self.assertEqual(out2, out)

    def test_convert_html_list_cards_to_native_lists_converts_nested_ul_to_indented_items(self):
        doc = _doc(
            [
                {
                    "type": "html",
                    "version": 1,
                    "html": (
                        "<ul><!-- wp:list-item -->"
                        "<li>Intro text:<!-- wp:list --><ul>"
                        "<!-- wp:list-item --><li>Sub 1</li><!-- /wp:list-item -->"
                        "<!-- wp:list-item --><li>Sub 2</li><!-- /wp:list-item -->"
                        "</ul><!-- /wp:list --></li>"
                        "<!-- /wp:list-item --></ul>"
                    ),
                }
            ]
        )
        rep, out = convert_html_list_cards_to_native_lists(doc, include_diff=False)
        self.assertFalse(rep.refused)
        self.assertTrue(rep.changed)
        self.assertEqual(rep.matched, 1)
        lst = out["root"]["children"][0]
        self.assertEqual(lst["type"], "list")
        self.assertEqual(lst["listType"], "bullet")
        items = lst["children"]
        self.assertEqual(len(items), 3)
        self.assertEqual(items[0]["children"][0]["text"], "Intro text:")
        self.assertEqual(items[0].get("indent"), 0)
        self.assertEqual(items[1]["children"][0]["text"], "Sub 1")
        self.assertEqual(items[1].get("indent"), 1)
        self.assertEqual(items[2]["children"][0]["text"], "Sub 2")
        self.assertEqual(items[2].get("indent"), 1)

    def test_convert_html_list_cards_to_native_lists_refuses_ol_missing_start(self):
        doc = _doc([{"type": "html", "version": 1, "html": '<ol><!-- wp:list-item --><li>Step</li><!-- /wp:list-item --></ol>'}])
        rep, out = convert_html_list_cards_to_native_lists(doc, include_diff=False)
        self.assertTrue(rep.refused)
        self.assertIs(out, doc)

    def test_set_image_meta_updates_single_match(self):
        doc = _doc([_image("a", alt="x", caption="")])
        rep, out = set_image_meta_by_src(
            doc,
            src="a",
            alt="new alt",
            caption="Cap",
            title="T",
            include_diff=False,
        )
        self.assertFalse(rep.refused)
        self.assertTrue(rep.changed)
        img = out["root"]["children"][0]
        self.assertEqual(img["alt"], "new alt")
        self.assertIn("Cap", img["caption"])
        self.assertEqual(img["title"], "T")

    def test_replace_after_heading_refuses_multiple_headings_without_occurrence(self):
        doc = _doc([_heading("Ingredients"), _image("a"), _heading("Ingredients"), _image("b")])
        rep, out = replace_first_image_after_heading(
            doc,
            heading="Ingredients",
            new_src="x",
            expect_old_src=None,
            alt=None,
            caption=None,
            title=None,
            nth_after_heading=1,
            heading_occurrence=None,
            include_diff=False,
        )
        self.assertTrue(rep.refused)
        self.assertIs(out, doc)

    def test_replace_after_heading_replaces_nth_image(self):
        doc = _doc([_heading("Ingredients"), _image("a"), _image("b"), _image("c")])
        rep, out = replace_first_image_after_heading(
            doc,
            heading="Ingredients",
            new_src="x",
            expect_old_src=None,
            alt=None,
            caption=None,
            title=None,
            nth_after_heading=2,
            heading_occurrence=1,
            include_diff=False,
        )
        self.assertFalse(rep.refused)
        self.assertTrue(rep.changed)
        self.assertEqual(out["root"]["children"][2]["src"], "x")
        self.assertEqual(out["root"]["children"][1]["src"], "a")

    def test_replace_after_heading_refuses_when_expected_old_src_mismatch(self):
        doc = _doc([_heading("Ingredients"), _image("a")])
        rep, out = replace_first_image_after_heading(
            doc,
            heading="Ingredients",
            new_src="x",
            expect_old_src="expected",
            alt=None,
            caption=None,
            title=None,
            nth_after_heading=1,
            heading_occurrence=1,
            include_diff=False,
        )
        self.assertTrue(rep.refused)
        self.assertIs(out, doc)

    def test_replace_after_heading_expected_old_src_allows_already_new_src(self):
        doc = _doc([_heading("Ingredients"), _image("x", alt="old", caption="")])
        rep, out = replace_first_image_after_heading(
            doc,
            heading="Ingredients",
            new_src="x",
            expect_old_src="expected",
            alt="NEW",
            caption="CAP",
            title=None,
            nth_after_heading=1,
            heading_occurrence=1,
            include_diff=False,
        )
        self.assertFalse(rep.refused)
        self.assertTrue(rep.changed)
        self.assertIn("treating as applied", " ".join(rep.reasons).lower())
        img = out["root"]["children"][1]
        self.assertEqual(img["src"], "x")
        self.assertEqual(img["alt"], "NEW")
        self.assertIn("CAP", img["caption"])

    def test_insert_after_heading_requires_template_src(self):
        doc = _doc([_heading("Ingredients"), _image("a")])
        rep, out = insert_image_after_heading(
            doc,
            heading="Ingredients",
            src="x",
            alt=None,
            caption=None,
            title=None,
            template_src=None,
            heading_occurrence=1,
            include_diff=False,
        )
        self.assertTrue(rep.refused)
        self.assertIs(out, doc)

    def test_insert_after_heading_clones_template(self):
        doc = _doc([_heading("Ingredients"), _image("template", alt="a", caption="c"), _heading("Other")])
        rep, out = insert_image_after_heading(
            doc,
            heading="Ingredients",
            src="x",
            alt="ALT",
            caption="CAP",
            title="TITLE",
            template_src="template",
            heading_occurrence=1,
            include_diff=False,
        )
        self.assertFalse(rep.refused)
        self.assertTrue(rep.changed)
        # Inserted right after the heading (index 1).
        inserted = out["root"]["children"][1]
        self.assertEqual(inserted["src"], "x")
        self.assertEqual(inserted["alt"], "ALT")
        self.assertEqual(inserted["title"], "TITLE")
        self.assertIn("CAP", inserted["caption"])

    def test_insert_after_heading_is_idempotent(self):
        doc = _doc([_heading("Ingredients"), _image("x"), _image("template"), _heading("Other")])
        rep, out = insert_image_after_heading(
            doc,
            heading="Ingredients",
            src="x",
            alt="ALT",
            caption="CAP",
            title="TITLE",
            template_src="template",
            heading_occurrence=1,
            include_diff=False,
        )
        self.assertFalse(rep.refused)
        self.assertTrue(rep.changed)

        rep2, out2 = insert_image_after_heading(
            out,
            heading="Ingredients",
            src="x",
            alt="ALT",
            caption="CAP",
            title="TITLE",
            template_src="template",
            heading_occurrence=1,
            include_diff=False,
        )
        self.assertFalse(rep2.refused)
        self.assertFalse(rep2.changed)
        self.assertIs(out2, out)

    def test_delete_image_by_src_refuses_multiple_without_all(self):
        doc = _doc([_image("x"), _image("x")])
        rep, out = delete_images_by_src(doc, src="x", allow_multiple=False, include_diff=False)
        self.assertTrue(rep.refused)
        self.assertEqual(rep.matched, 2)
        self.assertIs(out, doc)

    def test_delete_image_by_src_deletes_all(self):
        doc = _doc([_heading("Ingredients"), _image("x"), _image("y"), _image("x")])
        rep, out = delete_images_by_src(doc, src="x", allow_multiple=True, include_diff=False)
        self.assertFalse(rep.refused)
        self.assertTrue(rep.changed)
        imgs = [n for n in out["root"]["children"] if isinstance(n, dict) and n.get("type") == "image"]
        self.assertEqual([i["src"] for i in imgs], ["y"])

    def test_replace_many_replaces_multiple_images_in_one_pass(self):
        doc = _doc([_image("a"), _image("b")])
        rep, out, items = replace_images_by_src_map(
            doc,
            mapping={"a": {"new_src": "A", "alt": "ALT A", "caption": "CAP A"}, "b": "B"},
            include_diff=False,
        )
        self.assertFalse(rep.refused)
        self.assertTrue(rep.changed)
        self.assertEqual(rep.matched, 2)
        self.assertEqual(len(items), 2)
        self.assertEqual(out["root"]["children"][0]["src"], "A")
        self.assertEqual(out["root"]["children"][0]["alt"], "ALT A")
        self.assertIn("CAP A", out["root"]["children"][0]["caption"])
        self.assertEqual(out["root"]["children"][1]["src"], "B")

    def test_replace_many_refuses_on_ambiguous_old_src(self):
        doc = _doc([_image("same"), _image("same")])
        rep, out, _ = replace_images_by_src_map(doc, mapping={"same": "new"}, include_diff=False)
        self.assertTrue(rep.refused)
        self.assertIs(out, doc)

    def test_replace_many_treats_new_src_as_already_replaced(self):
        doc = _doc([_image("new", alt="old")])
        rep, out, items = replace_images_by_src_map(
            doc,
            mapping={"old": {"new_src": "new", "alt": "NEW ALT"}},
            include_diff=False,
        )
        self.assertFalse(rep.refused)
        self.assertTrue(rep.changed)
        self.assertEqual(items[0].matched, 1)
        self.assertIn("already replaced", " ".join(items[0].reasons).lower())
        self.assertEqual(out["root"]["children"][0]["alt"], "NEW ALT")

    def test_build_replace_many_map_for_missing_captions(self):
        doc = _doc([_image("a", alt="A", caption=""), _image("b", alt="B", caption="CAP")])
        m = build_replace_many_map_for_missing_captions(doc, include_all=False)
        self.assertEqual(set(m.keys()), {"a"})
        self.assertEqual(m["a"]["new_src"], "a")
        self.assertEqual(m["a"]["alt"], "A")
        self.assertEqual(m["a"]["caption"], "")

    def test_build_replace_many_map_include_all_prefills_existing_caption(self):
        doc = _doc([_image("a", alt="A", caption=""), _image("b", alt="B", caption="CAP")])
        m = build_replace_many_map_for_missing_captions(doc, include_all=True)
        self.assertEqual(set(m.keys()), {"a", "b"})
        self.assertEqual(m["a"]["caption"], "")
        self.assertEqual(m["b"]["caption"], "CAP")

    def test_fix_link_whitespace_moves_leading_space_outside_link(self):
        doc = _doc(
            [
                {
                    "type": "paragraph",
                    "version": 1,
                    "children": [
                        {"type": "extended-text", "version": 1, "text": "See"},
                        _link("https://example.com", " PETA"),
                        {"type": "extended-text", "version": 1, "text": "now"},
                    ],
                }
            ]
        )
        rep, out = fix_link_whitespace(doc, include_diff=False)
        self.assertFalse(rep.refused)
        self.assertTrue(rep.changed)
        self.assertEqual(rep.matched, 1)
        children = out["root"]["children"][0]["children"]
        self.assertEqual(children[1]["text"], " ")
        self.assertEqual(children[2]["type"], "link")
        self.assertEqual(children[2]["url"], "https://example.com")
        self.assertEqual(children[2]["children"][0]["text"], "PETA")

    def test_linkify_text_in_paragraph_wraps_anchor(self):
        doc = _doc([_para("This mentions arthritis and joint pain."), _para("Other paragraph.")])
        rep, out = linkify_text_in_paragraph(
            doc,
            paragraph_contains="mentions arthritis",
            paragraph_occurrence=None,
            anchor_text="arthritis",
            anchor_occurrence=None,
            url="https://mysite.example/arthritis-fighting-foods/",
            include_list_items=False,
            include_diff=False,
        )
        self.assertFalse(rep.refused)
        self.assertTrue(rep.changed)
        children = out["root"]["children"][0]["children"]
        self.assertEqual(children[0]["text"], "This mentions ")
        self.assertEqual(children[1]["type"], "link")
        self.assertEqual(children[1]["url"], "https://mysite.example/arthritis-fighting-foods/")
        self.assertEqual(children[1]["children"][0]["text"], "arthritis")
        self.assertEqual(children[2]["text"], " and joint pain.")

        # Idempotence.
        rep2, out2 = linkify_text_in_paragraph(
            out,
            paragraph_contains="mentions arthritis",
            paragraph_occurrence=None,
            anchor_text="arthritis",
            anchor_occurrence=None,
            url="https://mysite.example/arthritis-fighting-foods/",
            include_list_items=False,
            include_diff=False,
        )
        self.assertFalse(rep2.refused)
        self.assertFalse(rep2.changed)
        self.assertEqual(out2, out)

    def test_linkify_text_in_paragraph_refuses_ambiguous_paragraph(self):
        doc = _doc([_para("Gut health matters."), _para("More gut health.")])
        rep, out = linkify_text_in_paragraph(
            doc,
            paragraph_contains="gut health",
            paragraph_occurrence=None,
            anchor_text="gut",
            anchor_occurrence=None,
            url="https://mysite.example/the-gut-brain-connection/",
            include_list_items=False,
            include_diff=False,
        )
        self.assertTrue(rep.refused)
        self.assertIs(out, doc)

    def test_linkify_text_in_paragraph_refuses_ambiguous_anchor(self):
        doc = _doc([_para("arthritis arthritis")])
        rep, out = linkify_text_in_paragraph(
            doc,
            paragraph_contains="arthritis arthritis",
            paragraph_occurrence=None,
            anchor_text="arthritis",
            anchor_occurrence=None,
            url="https://mysite.example/arthritis-fighting-foods/",
            include_list_items=False,
            include_diff=False,
        )
        self.assertTrue(rep.refused)
        self.assertIs(out, doc)

    def test_linkify_text_in_paragraph_allows_list_items_when_enabled(self):
        doc = _doc([_list(["Supports blood pressure for heart health."])])
        rep, out = linkify_text_in_paragraph(
            doc,
            paragraph_contains="Supports blood pressure",
            paragraph_occurrence=None,
            anchor_text="blood pressure",
            anchor_occurrence=None,
            url="https://mysite.example/foods-that-naturally-lower-your-blood-pressure/",
            include_list_items=True,
            include_diff=False,
        )
        self.assertFalse(rep.refused)
        self.assertTrue(rep.changed)
        children = out["root"]["children"][0]["children"][0]["children"]
        self.assertEqual(children[0]["text"], "Supports ")
        self.assertEqual(children[1]["type"], "link")
        self.assertEqual(children[1]["url"], "https://mysite.example/foods-that-naturally-lower-your-blood-pressure/")
        self.assertEqual(children[1]["children"][0]["text"], "blood pressure")
        self.assertEqual(children[2]["text"], " for heart health.")

    def test_insert_link_paragraph_after_heading_section_end_inserts_before_next_h2(self):
        doc = _doc(
            [
                _heading("Intro"),
                _para("One"),
                _heading("Conclusion"),
                _para("Wrap up."),
                {"type": "extended-heading", "version": 1, "tag": "h3", "children": [{"type": "extended-text", "version": 1, "text": "Extra"}]},
                _para("More."),
                _heading("Next"),
            ]
        )
        rep, out = insert_link_paragraph_after_heading_section_end(
            doc,
            heading="Conclusion",
            heading_occurrence=None,
            link_text="tapioca flour substitutes",
            url="https://mysite.example/tapioca-flour-substitutes/",
            include_diff=False,
        )
        self.assertFalse(rep.refused)
        self.assertTrue(rep.changed)
        children = out["root"]["children"]
        # Should insert before the next h2 ("Next"), after all Conclusion section content (including h3).
        self.assertEqual(children[-2]["type"], "paragraph")
        self.assertEqual(children[-2]["children"][0]["type"], "link")
        self.assertEqual(children[-2]["children"][0]["url"], "https://mysite.example/tapioca-flour-substitutes/")
        self.assertEqual(children[-2]["children"][0]["children"][0]["text"], "tapioca flour substitutes")
        self.assertEqual(children[-1]["type"], "extended-heading")

        rep2, out2 = insert_link_paragraph_after_heading_section_end(
            out,
            heading="Conclusion",
            heading_occurrence=None,
            link_text="tapioca flour substitutes",
            url="https://mysite.example/tapioca-flour-substitutes/",
            include_diff=False,
        )
        self.assertFalse(rep2.refused)
        self.assertFalse(rep2.changed)
        self.assertEqual(out2, out)

    def test_fix_link_whitespace_moves_trailing_space_outside_link(self):
        doc = _doc(
            [
                {
                    "type": "paragraph",
                    "version": 1,
                    "children": [
                        {"type": "extended-text", "version": 1, "text": "See"},
                        _link("https://example.com", "PETA "),
                        {"type": "extended-text", "version": 1, "text": "now"},
                    ],
                }
            ]
        )
        rep, out = fix_link_whitespace(doc, include_diff=False)
        self.assertFalse(rep.refused)
        self.assertTrue(rep.changed)
        self.assertEqual(rep.matched, 1)
        children = out["root"]["children"][0]["children"]
        self.assertEqual(children[1]["type"], "link")
        self.assertEqual(children[1]["children"][0]["text"], "PETA")
        self.assertEqual(children[2]["text"], " ")

    def test_fix_link_whitespace_removes_whitespace_only_link(self):
        doc = _doc(
            [
                {
                    "type": "paragraph",
                    "version": 1,
                    "children": [
                        {"type": "extended-text", "version": 1, "text": "A"},
                        _link("https://example.com", " "),
                        {"type": "extended-text", "version": 1, "text": "B"},
                    ],
                }
            ]
        )
        rep, out = fix_link_whitespace(doc, include_diff=False)
        self.assertFalse(rep.refused)
        self.assertTrue(rep.changed)
        self.assertEqual(rep.matched, 1)
        children = out["root"]["children"][0]["children"]
        self.assertEqual([c.get("type") for c in children], ["extended-text", "extended-text", "extended-text"])
        self.assertEqual(children[1]["text"], " ")

    def test_set_paid_rel_on_amazon_links_adds_sponsored_and_nofollow(self):
        doc = _doc(
            [
                {
                    "type": "paragraph",
                    "version": 1,
                    "children": [
                        {
                            "type": "link",
                            "version": 1,
                            "url": "https://amzn.to/abc123",
                            "rel": "noreferrer noopener",
                            "children": [{"type": "extended-text", "version": 1, "text": "Amazon"}],
                        }
                    ],
                }
            ]
        )
        rep, out = set_paid_rel_on_amazon_links(doc, include_diff=False)
        self.assertFalse(rep.refused)
        self.assertTrue(rep.changed)
        self.assertEqual(rep.matched, 1)
        link = out["root"]["children"][0]["children"][0]
        self.assertIn("sponsored", link["rel"].split())
        self.assertIn("nofollow", link["rel"].split())

    def test_set_paid_rel_on_amazon_links_no_change_for_non_amazon(self):
        doc = _doc(
            [
                {
                    "type": "paragraph",
                    "version": 1,
                    "children": [
                        {
                            "type": "link",
                            "version": 1,
                            "url": "https://example.com/x",
                            "rel": "noreferrer noopener",
                            "children": [{"type": "extended-text", "version": 1, "text": "Example"}],
                        }
                    ],
                }
            ]
        )
        rep, out = set_paid_rel_on_amazon_links(doc, include_diff=False)
        self.assertFalse(rep.refused)
        self.assertFalse(rep.changed)
        self.assertEqual(out, doc)

    def test_set_paid_rel_on_links_host_mode(self):
        doc = _doc(
            [
                {
                    "type": "paragraph",
                    "version": 1,
                    "children": [
                        {
                            "type": "link",
                            "version": 1,
                            "url": "https://www.hellofresh.com/x",
                            "rel": "noopener",
                            "children": [{"type": "extended-text", "version": 1, "text": "HF"}],
                        },
                        {
                            "type": "link",
                            "version": 1,
                            "url": "https://example.com/y",
                            "children": [{"type": "extended-text", "version": 1, "text": "Example"}],
                        },
                    ],
                }
            ]
        )

        def match(u: str) -> bool:
            return "hellofresh.com" in u

        rep, out = set_paid_rel_on_links(
            doc,
            match_url=match,
            required_tokens=["noreferrer", "noopener", "sponsored", "nofollow"],
            include_diff=False,
        )
        self.assertFalse(rep.refused)
        self.assertTrue(rep.changed)
        self.assertEqual(rep.matched, 1)

        a = out["root"]["children"][0]["children"][0]
        b = out["root"]["children"][0]["children"][1]
        self.assertIn("noopener", a["rel"].split())
        self.assertIn("sponsored", a["rel"].split())
        self.assertIn("nofollow", a["rel"].split())
        self.assertNotIn("rel", b)

    def test_set_paid_rel_on_links_token_dedupe_preserves_order(self):
        doc = _doc(
            [
                {
                    "type": "paragraph",
                    "version": 1,
                    "children": [
                        {
                            "type": "link",
                            "version": 1,
                            "url": "https://example.com/x",
                            "rel": "noopener NoOpEnEr",
                            "children": [{"type": "extended-text", "version": 1, "text": "X"}],
                        }
                    ],
                }
            ]
        )

        rep, out = set_paid_rel_on_links(
            doc,
            match_url=lambda u: True,
            required_tokens=["noopener", "sponsored"],
            include_diff=False,
        )
        self.assertTrue(rep.changed)
        rel = out["root"]["children"][0]["children"][0]["rel"]
        self.assertEqual(rel, "noopener sponsored")

    def test_unlink_links_by_url_unwraps_keep_text(self):
        doc = _doc(
            [
                _para("Before "),
                _link("https://example.com/a", "A"),
                _para(" and "),
                _link("https://example.com/b", "B"),
            ]
        )
        rep, out = unlink_links_by_url(doc, urls=["https://example.com/a"], include_diff=False)
        self.assertFalse(rep.refused)
        self.assertTrue(rep.changed)
        self.assertEqual(rep.matched, 1)
        children = out["root"]["children"]
        self.assertEqual(children[1]["type"], "extended-text")
        self.assertEqual(children[1]["text"], "A")
        self.assertEqual(children[3]["type"], "link")
        self.assertEqual(children[3]["url"], "https://example.com/b")

        rep2, out2 = unlink_links_by_url(out, urls=["https://example.com/a"], include_diff=False)
        self.assertFalse(rep2.refused)
        self.assertFalse(rep2.changed)
        self.assertEqual(rep2.matched, 0)
        self.assertIs(out2, out)

    def test_unlink_links_by_url_removes_link_when_no_children(self):
        doc = _doc(
            [
                {"type": "link", "version": 1, "url": "https://example.com/a", "children": []},
                _para("x"),
            ]
        )
        rep, out = unlink_links_by_url(doc, urls=[" https://example.com/a "], include_diff=False)
        self.assertFalse(rep.refused)
        self.assertTrue(rep.changed)
        self.assertEqual(rep.matched, 1)
        self.assertEqual(len(out["root"]["children"]), 1)
        self.assertEqual(out["root"]["children"][0]["type"], "paragraph")

    def test_unlink_internal_links_in_image_captions_unwraps_anchor(self):
        doc = _doc(
            [
                _image(
                    "x",
                    caption='<span>See <a href=\"https://mysite.example/hello/\">Hello</a> and <a href=\"https://example.com/x\">X</a></span>',
                )
            ]
        )
        rep, out = unlink_internal_links_in_image_captions(doc, internal_hosts={"mysite.example"}, include_diff=False)
        self.assertFalse(rep.refused)
        self.assertTrue(rep.changed)
        self.assertEqual(rep.matched, 1)
        cap = out["root"]["children"][0]["caption"]
        self.assertIn("Hello", cap)
        self.assertNotIn("href=\"https://mysite.example/hello/\"", cap)
        self.assertIn("href=\"https://example.com/x\"", cap)

        rep2, out2 = unlink_internal_links_in_image_captions(out, internal_hosts={"mysite.example"}, include_diff=False)
        self.assertFalse(rep2.refused)
        self.assertFalse(rep2.changed)
        self.assertIs(out2, out)

    def test_insert_internal_links_section_before_heading_inserts_before_conclusion_and_skips_self(self):
        doc = _doc([_heading("Intro"), _para("x"), _heading("Conclusion"), _para("end")])
        links = [
            ("A", "https://mysite.example/a/"),
            ("B", "https://mysite.example/b/"),
        ]
        rep, out = insert_internal_links_section_before_heading(
            doc,
            before_heading="Conclusion",
            section_heading="More blood type diet guides",
            intro_text="Want another blood type?",
            links=links,
            skip_url="https://mysite.example/a/",
            include_diff=False,
        )
        self.assertFalse(rep.refused)
        self.assertTrue(rep.changed)
        self.assertEqual(rep.matched, 1)
        children = out["root"]["children"]
        # Inserted right before Conclusion heading => index 2 becomes new heading
        self.assertEqual(children[2]["type"], "extended-heading")
        self.assertIn("More blood type diet guides", children[2]["children"][0]["text"])
        self.assertEqual(children[3]["type"], "paragraph")
        self.assertEqual(children[4]["type"], "list")
        # Conclusion should now be later
        self.assertEqual(children[5]["type"], "extended-heading")
        self.assertIn("Conclusion", children[5]["children"][0]["text"])

        # Idempotence: running again should no-op
        rep2, out2 = insert_internal_links_section_before_heading(
            out,
            before_heading="Conclusion",
            section_heading="More blood type diet guides",
            intro_text="Want another blood type?",
            links=links,
            skip_url="https://mysite.example/a/",
            include_diff=False,
        )
        self.assertFalse(rep2.refused)
        self.assertFalse(rep2.changed)
        self.assertIs(out2, out)

    def test_unlink_links_by_url_after_heading_only_affects_section_after_heading(self):
        url = "https://mysite.example/top-supplements-for-lowering-cortisol-levels/"
        # Same link appears both before and after Conclusion.
        h2_more = {
            "type": "extended-heading",
            "version": 1,
            "tag": "h2",
            "children": [{"type": "extended-text", "version": 1, "text": "More cortisol guides"}],
        }
        h2_conc = {
            "type": "extended-heading",
            "version": 1,
            "tag": "h2",
            "children": [{"type": "extended-text", "version": 1, "text": "Conclusion"}],
        }
        para_before = {"type": "paragraph", "version": 1, "children": [_link(url, "supplements")]}
        para_after = {"type": "paragraph", "version": 1, "children": [_link(url, "supplements")]}
        doc = _doc([h2_more, para_before, h2_conc, _para("In summary, "), para_after, _para(" are optional.")])
        rep, out = unlink_links_by_url_after_heading(doc, after_heading="Conclusion", urls=[url], include_diff=False)
        self.assertFalse(rep.refused)
        self.assertTrue(rep.changed)
        self.assertEqual(rep.matched, 1)

        # Link before Conclusion should still be present.
        before_links_rep, _ = unlink_links_by_url_after_heading(out, after_heading="More cortisol guides", urls=[url], include_diff=False)
        self.assertFalse(before_links_rep.refused)
        self.assertTrue(before_links_rep.changed)
        self.assertEqual(before_links_rep.matched, 1)

        # Idempotence: running again for Conclusion should be a no-op.
        rep2, out2 = unlink_links_by_url_after_heading(out, after_heading="Conclusion", urls=[url], include_diff=False)
        self.assertFalse(rep2.refused)
        self.assertFalse(rep2.changed)
        self.assertEqual(rep2.matched, 0)
        self.assertIs(out2, out)

    def test_delete_linked_list_items_by_url_after_heading_removes_list_item_only(self):
        u_keep = "https://mysite.example/foods-for-plaque-arteries/"
        u_drop = "https://mysite.example/johnstone-river-almonds-health-benefits/"

        h2_more = {
            "type": "extended-heading",
            "version": 1,
            "tag": "h2",
            "children": [{"type": "extended-text", "version": 1, "text": "More heart health guides"}],
        }
        h2_conc = {
            "type": "extended-heading",
            "version": 1,
            "tag": "h2",
            "children": [{"type": "extended-text", "version": 1, "text": "Conclusion"}],
        }
        ul = {
            "type": "list",
            "version": 1,
            "listType": "bullet",
            "tag": "ul",
            "children": [
                {"type": "listitem", "version": 1, "value": 1, "children": [_link(u_keep, "Foods for plaque")]},
                {"type": "listitem", "version": 1, "value": 2, "children": [_link(u_drop, "Johnstone River almonds")]},
            ],
        }
        doc = _doc([_para("Intro"), h2_more, _para("Here are our other guides:"), ul, h2_conc, _para("End")])

        rep, out = delete_linked_list_items_by_url_after_heading(
            doc,
            after_heading="More heart health guides",
            urls=[u_drop],
            include_diff=False,
        )
        self.assertFalse(rep.refused)
        self.assertTrue(rep.changed)
        self.assertEqual(rep.matched, 1)

        children = out["root"]["children"]
        # Section heading and intro should remain.
        self.assertEqual(children[1]["type"], "extended-heading")
        self.assertEqual(children[1]["tag"], "h2")
        self.assertIn("More heart health guides", children[1]["children"][0]["text"])
        self.assertEqual(children[3]["type"], "list")
        self.assertEqual(len(children[3]["children"]), 1)
        self.assertEqual(children[3]["children"][0]["children"][0]["url"], u_keep)

        # Idempotence: running again should no-op.
        rep2, out2 = delete_linked_list_items_by_url_after_heading(
            out,
            after_heading="More heart health guides",
            urls=[u_drop],
            include_diff=False,
        )
        self.assertFalse(rep2.refused)
        self.assertFalse(rep2.changed)
        self.assertEqual(rep2.matched, 0)
        self.assertIs(out2, out)

    def test_delete_linked_list_items_by_url_after_heading_removes_entire_section_when_empty(self):
        u_drop1 = "https://mysite.example/a/"
        u_drop2 = "https://mysite.example/b/"

        h2_more = {
            "type": "extended-heading",
            "version": 1,
            "tag": "h2",
            "children": [{"type": "extended-text", "version": 1, "text": "More heart health guides"}],
        }
        h2_conc = {
            "type": "extended-heading",
            "version": 1,
            "tag": "h2",
            "children": [{"type": "extended-text", "version": 1, "text": "Conclusion"}],
        }
        ul = {
            "type": "list",
            "version": 1,
            "listType": "bullet",
            "tag": "ul",
            "children": [
                {"type": "listitem", "version": 1, "value": 1, "children": [_link(u_drop1, "A")]},
                {"type": "listitem", "version": 1, "value": 2, "children": [_link(u_drop2, "B")]},
            ],
        }
        doc = _doc([_para("Intro"), h2_more, _para("Here are our other guides:"), ul, h2_conc, _para("End")])

        rep, out = delete_linked_list_items_by_url_after_heading(
            doc,
            after_heading="More heart health guides",
            urls=[u_drop1, u_drop2],
            include_diff=False,
        )
        self.assertFalse(rep.refused)
        self.assertTrue(rep.changed)
        self.assertEqual(rep.matched, 2)

        # Entire section removed => children should be: Intro, Conclusion, End.
        children = out["root"]["children"]
        self.assertEqual(children[0]["type"], "paragraph")
        self.assertEqual(children[1]["type"], "extended-heading")
        self.assertEqual(children[1]["tag"], "h2")
        self.assertIn("Conclusion", children[1]["children"][0]["text"])

        # Verification/idempotence: running again should be a no-op (and should not refuse).
        rep2, out2 = delete_linked_list_items_by_url_after_heading(
            out,
            after_heading="More heart health guides",
            urls=[u_drop1, u_drop2],
            include_diff=False,
        )
        self.assertFalse(rep2.refused)
        self.assertFalse(rep2.changed)
        self.assertEqual(rep2.matched, 0)
        self.assertIs(out2, out)

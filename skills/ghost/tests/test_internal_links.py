import unittest

from ghost_api_tool.internal_links import classify_target, extract_links_from_lexical, internal_hosts_from_site_url


def _doc(children):
    return {"root": {"type": "root", "version": 1, "children": children}}


def _link(url: str, text: str):
    return {
        "type": "link",
        "version": 1,
        "url": url,
        "children": [{"type": "extended-text", "version": 1, "text": text}],
    }


def _html_card(html: str):
    return {"type": "html", "version": 1, "html": html}


class InternalLinksTests(unittest.TestCase):
    def test_extract_links_from_lexical_finds_link_nodes(self):
        doc = _doc([{"type": "paragraph", "version": 1, "children": [_link("https://example.com/a", "Example")]}])
        occ = extract_links_from_lexical(
            doc,
            source_id="p1",
            source_slug="s1",
            source_title="t1",
            source_status="published",
        )
        self.assertEqual(len(occ), 1)
        self.assertEqual(occ[0].url, "https://example.com/a")
        self.assertEqual(occ[0].anchor_text, "Example")
        self.assertEqual(occ[0].origin, "lexical_link")

    def test_extract_links_from_lexical_finds_html_anchor(self):
        doc = _doc([_html_card('<p>See <a href="https://example.com/x">X</a></p>')])
        occ = extract_links_from_lexical(
            doc,
            source_id="p1",
            source_slug="s1",
            source_title="t1",
            source_status="published",
        )
        self.assertEqual(len(occ), 1)
        self.assertEqual(occ[0].url, "https://example.com/x")
        self.assertEqual(occ[0].anchor_text, "X")
        self.assertEqual(occ[0].origin, "html_card")

    def test_classify_target_internal_relative(self):
        internal_hosts = {"example-site.ghost.io"}
        ok, ref = classify_target("/my-post/", internal_hosts=internal_hosts)
        self.assertTrue(ok)
        self.assertEqual(ref.slug, "my-post")
        self.assertEqual(ref.kind, "post_or_page")

    def test_classify_target_internal_absolute(self):
        internal_hosts = {"example-site.ghost.io"}
        ok, ref = classify_target("https://example-site.ghost.io/my-post/", internal_hosts=internal_hosts)
        self.assertTrue(ok)
        self.assertEqual(ref.slug, "my-post")

    def test_internal_hosts_from_site_url(self):
        hosts = internal_hosts_from_site_url("https://example-site.ghost.io/", extra_hosts=["www.example.com"])
        self.assertIn("example-site.ghost.io", hosts)
        self.assertIn("www.example.com", hosts)

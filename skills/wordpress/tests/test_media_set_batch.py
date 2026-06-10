import unittest
from typing import cast

from wordpress_api_tool.commands.media import media_set_batch_core
from wordpress_api_tool.wp_api import WordPressApi


class _StubApi:
    def __init__(self, media_items):
        self._media = {m["id"]: dict(m) for m in media_items}
        self.updated = []

    def media_by_include(self, ids):
        out = []
        for i in ids:
            m = self._media.get(int(i))
            if m:
                out.append(dict(m))
        return out

    def update_media(self, *, media_id: int, caption, alt_text, title):
        self.updated.append((int(media_id), caption, alt_text, title))
        m = self._media[int(media_id)]
        if caption is not None:
            m["caption"] = {"raw": caption, "rendered": caption}
        if alt_text is not None:
            m["alt_text"] = alt_text
        if title is not None:
            m["title"] = {"raw": title, "rendered": title}
        return dict(m)


class MediaSetBatchTests(unittest.TestCase):
    def test_dry_run_reports_changes(self):
        api = _StubApi(
            [
                {"id": 1, "caption": {"raw": "old"}, "alt_text": "a", "title": {"raw": "t"}, "source_url": "u"},
                {"id": 2, "caption": {"raw": "same"}, "alt_text": "", "title": {"raw": ""}, "source_url": "u2"},
            ]
        )
        res = media_set_batch_core(
            cast(WordPressApi, api),
            updates=[{"id": "1", "caption": "new", "alt_text": None, "title": None}, {"id": "2", "caption": "same", "alt_text": None, "title": None}],
            apply=False,
        )
        self.assertFalse(res["apply"])
        self.assertEqual(res["errors"], 0)
        self.assertEqual(res["results"][0]["changed"], True)
        self.assertEqual(res["results"][1]["changed"], False)
        self.assertEqual(api.updated, [])

    def test_apply_updates_and_verifies(self):
        api = _StubApi(
            [
                {"id": 1, "caption": {"raw": "old"}, "alt_text": "a", "title": {"raw": "t"}, "source_url": "u"},
            ]
        )
        res = media_set_batch_core(
            cast(WordPressApi, api),
            updates=[{"id": "1", "caption": "new", "alt_text": None, "title": None}],
            apply=True,
        )
        self.assertTrue(res["apply"])
        self.assertEqual(res["errors"], 0)
        self.assertEqual(api.updated, [(1, "new", None, None)])
        self.assertTrue(res["results"][0]["verified"])

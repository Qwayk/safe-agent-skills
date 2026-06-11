import unittest

from ghost_api_tool.link_candidates import pick_hub_shortlist_post_ids, tag_candidate_rows


class LinkCandidatesTests(unittest.TestCase):
    def test_pick_hub_shortlist_prefers_higher_reading_time(self):
        posts = [
            {"id": "a", "word_count_est": 200, "published_at": "2020-01-01T00:00:00.000Z", "title": "A"},
            {"id": "b", "word_count_est": 900, "published_at": "2020-01-01T00:00:00.000Z", "title": "B"},
            {"id": "c", "word_count_est": 500, "published_at": "2020-01-01T00:00:00.000Z", "title": "C"},
        ]
        self.assertEqual(pick_hub_shortlist_post_ids(posts, limit=2, metric_key="word_count_est"), {"b", "c"})

    def test_tag_candidate_rows_marks_hub_shortlist(self):
        posts = [
            {
                "id": "p1",
                "slug": "s1",
                "title": "T1",
                "url": "https://example.com/s1/",
                "status": "published",
                "published_at": "2020-01-01T00:00:00.000Z",
                "updated_at": "2020-01-02T00:00:00.000Z",
                "word_count_est": 800,
                "reading_time_est": 4,
            }
        ]
        rows = tag_candidate_rows(tag_slug="nutrition", posts=posts, hub_shortlist_post_ids={"p1"})
        self.assertEqual(rows[0]["tag_slug"], "nutrition")
        self.assertEqual(rows[0]["post_id"], "p1")
        self.assertEqual(rows[0]["hub_shortlist"], "true")

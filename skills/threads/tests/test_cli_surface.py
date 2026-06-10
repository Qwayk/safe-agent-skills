from __future__ import annotations

from unittest import TestCase

from threads_api_tool.cli import build_parser
from threads_api_tool.errors import ValidationError


class TestCLICommandSurface(TestCase):
    def _parse(self, args: list[str]):
        return build_parser().parse_args(args)

    def test_posts_list_public_uses_username_arg(self) -> None:
        args = self._parse(["posts", "list-public", "--username", "alice"])
        self.assertEqual(args.username, "alice")

    def test_search_keyword_uses_q_argument(self) -> None:
        args = self._parse(["search", "keyword", "--q", "cats"])
        self.assertEqual(args.q, "cats")

    def test_topic_tag_search_defaults_search_mode_to_TAG(self) -> None:
        args = self._parse(["search", "topic-tag", "--topic-tag", "travel"])
        self.assertEqual(args.search_mode, "TAG")

    def test_topic_tag_search_rejects_query_alias(self) -> None:
        with self.assertRaises(ValidationError):
            self._parse(["search", "topic-tag", "--topic-tag", "travel", "--query", "travel"])

    def test_locations_search_query_uses_q_argument(self) -> None:
        args = self._parse(["locations", "search-query", "--q", "rome"])
        self.assertEqual(args.q, "rome")

    def test_locations_search_query_does_not_expose_limit(self) -> None:
        with self.assertRaises(ValidationError):
            self._parse(["locations", "search-query", "--q", "rome", "--limit", "5"])

    def test_locations_search_coordinates_does_not_expose_radius_km(self) -> None:
        with self.assertRaises(ValidationError):
            self._parse(["locations", "search-coordinates", "--latitude", "1", "--longitude", "2", "--radius-km", "5"])

    def test_locations_get_supports_fields(self) -> None:
        args = self._parse(["locations", "get", "--location-id", "loc-1", "--fields", "id,name"])
        self.assertEqual(args.fields, "id,name")

    def test_replies_hide_uses_hide_argument(self) -> None:
        args = self._parse(["replies", "hide", "--threads-reply-id", "r1", "--hide", "true"])
        self.assertEqual(args.hide, "true")

    def test_replies_pending_decide_uses_approve_argument(self) -> None:
        args = self._parse(["replies", "pending", "decide", "--threads-reply-id", "r1", "--approve", "false"])
        self.assertEqual(args.approve, "false")

    def test_posts_status_is_exposed_read_command(self) -> None:
        args = self._parse(["posts", "status", "--threads-container-id", "c1"])
        self.assertEqual(args.threads_container_id, "c1")

    def test_replies_pending_list_is_exposed_read_command(self) -> None:
        args = self._parse(["replies", "pending", "list", "--threads-media-id", "m1"])
        self.assertEqual(args.threads_media_id, "m1")

    def test_replies_list_user_is_not_exposed(self) -> None:
        with self.assertRaises(ValidationError):
            self._parse(["replies", "list-user"])

    def test_posts_create_text_supports_text_spoiler_ranges_and_reply_approvals(self) -> None:
        args = self._parse(
            [
                "posts",
                "create-text",
                "--text",
                "hello",
                "--text-spoiler-range",
                "0:2",
                "--text-spoiler-range",
                "2:3",
                "--enable-reply-approvals",
            ],
        )
        self.assertEqual(args.text_spoiler_ranges, ["0:2", "2:3"])
        self.assertTrue(args.enable_reply_approvals)

    def test_posts_create_text_supports_repeatable_poll_options(self) -> None:
        args = self._parse(
            [
                "posts",
                "create-text",
                "--text",
                "hello",
                "--poll-option",
                "a",
                "--poll-option",
                "b",
            ],
        )
        self.assertEqual(args.poll_options, ["a", "b"])

    def test_posts_list_ghost_is_not_exposed(self) -> None:
        with self.assertRaises(ValidationError):
            self._parse(["posts", "list-ghost"])

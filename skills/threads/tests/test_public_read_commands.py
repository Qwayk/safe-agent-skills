from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from threads_api_tool.commands import insights as insights_cmd
from threads_api_tool.commands import locations as locations_cmd
from threads_api_tool.commands import mentions as mentions_cmd
from threads_api_tool.commands import oembed as oembed_cmd
from threads_api_tool.commands import posts as posts_cmd
from threads_api_tool.commands import profiles as profiles_cmd
from threads_api_tool.commands import replies as replies_cmd
from threads_api_tool.commands import search as search_cmd
from threads_api_tool.output import Output


class _NoopAudit:
    def write(self, *_args, **_kwargs) -> None:
        return None


class TestPublicReadCommands(unittest.TestCase):
    def _ctx(self, *, default_user_id: str = "default-user") -> dict:
        cfg = SimpleNamespace(
            base_url="http://example.invalid",
            api_version="v1.0",
            token="dummy-token",
            app_id="app-id",
            app_secret="app-secret",
            redirect_uri="https://callback.local",
            default_user_id=default_user_id,
            timeout_s=30.0,
        )
        return {
            "cfg": cfg,
            "out": Output(mode="json"),
            "audit": _NoopAudit(),
            "tool": "threads-api-tool",
            "tool_version": "0.1.0",
            "command_str": "threads-api-tool read-test",
            "env_file": str(Path("/tmp/.env")),
            "timeout_s": 30,
            "verbose": False,
            "apply": False,
            "yes": False,
            "plan_out": None,
            "plan_in": None,
            "receipt_out": None,
            "ack_irreversible": False,
            "run_id": None,
            "artifacts_dir": None,
            "runs_index_path": None,
        }

    def _run(self, func, args, *, patch_target: str, fake: Mock, ctx: dict | None = None) -> dict:
        buf = io.StringIO()
        with patch(patch_target, return_value=fake):
            with redirect_stdout(buf):
                rc = func(args, ctx or self._ctx())
        self.assertEqual(rc, 0)
        payload = json.loads(buf.getvalue())
        self.assertTrue(payload["ok"])
        return payload

    def test_profiles_and_posts_read_handlers(self) -> None:
        fake = Mock()
        fake.get_me.return_value = {"id": "me-1"}
        payload = self._run(
            profiles_cmd.cmd_profiles_me,
            SimpleNamespace(fields="id,username"),
            patch_target="threads_api_tool.commands.profiles._client",
            fake=fake,
        )
        fake.get_me.assert_called_once_with(fields="id,username")
        self.assertEqual(payload["command"], "profiles.me")

        fake = Mock()
        fake.get_profile.return_value = {"id": "user-1"}
        payload = self._run(
            profiles_cmd.cmd_profiles_get,
            SimpleNamespace(threads_user_id=None, fields="id"),
            patch_target="threads_api_tool.commands.profiles._client",
            fake=fake,
        )
        fake.get_profile.assert_called_once_with(threads_user_id="default-user", fields="id")
        self.assertEqual(payload["command"], "profiles.get")

        fake = Mock()
        fake.lookup_profile.return_value = {"id": "user-2"}
        payload = self._run(
            profiles_cmd.cmd_profiles_lookup,
            SimpleNamespace(username="alice", fields="id,username"),
            patch_target="threads_api_tool.commands.profiles._client",
            fake=fake,
        )
        fake.lookup_profile.assert_called_once_with(username="alice", fields="id,username")
        self.assertEqual(payload["command"], "profiles.lookup")

        fake = Mock()
        fake.list_owned_posts.return_value = {"data": []}
        payload = self._run(
            posts_cmd.cmd_posts_list_owned,
            SimpleNamespace(
                threads_user_id=None,
                fields="id,text",
                limit=5,
                before="before-1",
                after="after-1",
                since="since-1",
                until="until-1",
                reverse=True,
            ),
            patch_target="threads_api_tool.commands.posts._client",
            fake=fake,
        )
        fake.list_owned_posts.assert_called_once_with(
            threads_user_id="default-user",
            params={
                "fields": "id,text",
                "limit": 5,
                "before": "before-1",
                "after": "after-1",
                "since": "since-1",
                "until": "until-1",
                "reverse": True,
            },
        )
        self.assertEqual(payload["command"], "posts.list-owned")

        fake = Mock()
        fake.list_public_posts.return_value = {"data": []}
        payload = self._run(
            posts_cmd.cmd_posts_list_public,
            SimpleNamespace(
                username="alice",
                fields="id",
                limit=3,
                before="",
                after="",
                since="",
                until="",
                reverse=False,
            ),
            patch_target="threads_api_tool.commands.posts._client",
            fake=fake,
        )
        fake.list_public_posts.assert_called_once_with(
            username="alice",
            params={"fields": "id", "limit": 3},
        )
        self.assertEqual(payload["command"], "posts.list-public")

        fake = Mock()
        fake.get_post.return_value = {"id": "media-1"}
        payload = self._run(
            posts_cmd.cmd_posts_get,
            SimpleNamespace(threads_media_id="media-1", fields="id,text"),
            patch_target="threads_api_tool.commands.posts._client",
            fake=fake,
        )
        fake.get_post.assert_called_once_with(
            threads_media_id="media-1",
            params={"fields": "id,text"},
        )
        self.assertEqual(payload["command"], "posts.get")

        fake = Mock()
        fake.posting_limits.return_value = {"quota_usage": 1}
        payload = self._run(
            posts_cmd.cmd_posts_limits,
            SimpleNamespace(threads_user_id=None),
            patch_target="threads_api_tool.commands.posts._client",
            fake=fake,
        )
        fake.posting_limits.assert_called_once_with(threads_user_id="default-user")
        self.assertEqual(payload["command"], "posts.limits")

        fake = Mock()
        fake.post_status.return_value = {"id": "container-1", "status": "FINISHED"}
        payload = self._run(
            posts_cmd.cmd_posts_status,
            SimpleNamespace(threads_container_id="container-1", fields="id,status"),
            patch_target="threads_api_tool.commands.posts._client",
            fake=fake,
        )
        fake.post_status.assert_called_once_with(threads_container_id="container-1", fields="id,status")
        self.assertEqual(payload["command"], "posts.status")

    def test_replies_mentions_and_insights_handlers(self) -> None:
        fake = Mock()
        fake.list_replies.return_value = {"data": []}
        payload = self._run(
            replies_cmd.cmd_replies_list,
            SimpleNamespace(
                threads_media_id="media-1",
                fields="id",
                limit=5,
                before="before-1",
                after="after-1",
                since="since-1",
                until="until-1",
                reverse=True,
            ),
            patch_target="threads_api_tool.commands.replies._client",
            fake=fake,
        )
        fake.list_replies.assert_called_once_with(
            threads_media_id="media-1",
            params={
                "fields": "id",
                "limit": 5,
                "before": "before-1",
                "after": "after-1",
                "since": "since-1",
                "until": "until-1",
                "reverse": True,
            },
        )
        self.assertEqual(payload["command"], "replies.list")

        fake = Mock()
        fake.reply_conversation.return_value = {"data": []}
        payload = self._run(
            replies_cmd.cmd_replies_conversation,
            SimpleNamespace(
                threads_media_id="media-1",
                fields="id",
                limit=2,
                before="",
                after="",
                since="",
                until="",
                reverse=True,
            ),
            patch_target="threads_api_tool.commands.replies._client",
            fake=fake,
        )
        fake.reply_conversation.assert_called_once_with(
            threads_media_id="media-1",
            params={"fields": "id", "limit": 2},
        )
        self.assertEqual(payload["command"], "replies.conversation")

        fake = Mock()
        fake.list_pending_replies.return_value = {"data": []}
        payload = self._run(
            replies_cmd.cmd_replies_pending_list,
            SimpleNamespace(
                threads_media_id="media-1",
                fields="id",
                limit=4,
                before="before-1",
                after="after-1",
                since="",
                until="",
                reverse=False,
            ),
            patch_target="threads_api_tool.commands.replies._client",
            fake=fake,
        )
        fake.list_pending_replies.assert_called_once_with(
            threads_media_id="media-1",
            params={"fields": "id", "limit": 4, "before": "before-1", "after": "after-1"},
        )
        self.assertEqual(payload["command"], "replies.pending_list")

        fake = Mock()
        fake.list_mentions.return_value = {"data": []}
        payload = self._run(
            mentions_cmd.cmd_mentions_list,
            SimpleNamespace(
                threads_user_id=None,
                fields="id",
                limit=5,
                before="before-1",
                after="after-1",
                since="since-1",
                until="until-1",
                reverse=False,
            ),
            patch_target="threads_api_tool.commands.mentions._client",
            fake=fake,
        )
        fake.list_mentions.assert_called_once_with(
            threads_user_id="default-user",
            params={
                "fields": "id",
                "limit": 5,
                "before": "before-1",
                "after": "after-1",
                "since": "since-1",
                "until": "until-1",
            },
        )
        self.assertEqual(payload["command"], "mentions.list")

        fake = Mock()
        fake.media_insights.return_value = {"data": []}
        payload = self._run(
            insights_cmd.cmd_insights_media,
            SimpleNamespace(
                threads_media_id="media-1",
                fields="views",
                since="2026-01-01",
                until="2026-01-31",
                limit=None,
                before="",
                after="",
                reverse=False,
                period="day",
                metric="views,likes",
            ),
            patch_target="threads_api_tool.commands.insights._client",
            fake=fake,
        )
        fake.media_insights.assert_called_once_with(
            threads_media_id="media-1",
            params={
                "fields": "views",
                "since": "2026-01-01",
                "until": "2026-01-31",
                "metric": "views,likes",
                "period": "day",
            },
        )
        self.assertEqual(payload["command"], "insights.media")

        fake = Mock()
        fake.user_insights.return_value = {"data": []}
        payload = self._run(
            insights_cmd.cmd_insights_user,
            SimpleNamespace(
                threads_user_id=None,
                fields="followers_count",
                since="2026-01-01",
                until="2026-01-31",
                limit=None,
                before="",
                after="",
                reverse=False,
                period="lifetime",
                metric="followers_count",
            ),
            patch_target="threads_api_tool.commands.insights._client",
            fake=fake,
        )
        fake.user_insights.assert_called_once_with(
            threads_user_id="default-user",
            params={
                "fields": "followers_count",
                "since": "2026-01-01",
                "until": "2026-01-31",
                "metric": "followers_count",
                "period": "lifetime",
            },
        )
        self.assertEqual(payload["command"], "insights.user")

    def test_search_locations_and_oembed_handlers(self) -> None:
        fake = Mock()
        fake.search_keyword.return_value = {"data": []}
        payload = self._run(
            search_cmd.cmd_search_keyword,
            SimpleNamespace(
                q="cats",
                fields="id,text",
                limit=5,
                before="",
                after="",
                since="",
                until="",
                reverse=False,
                search_type="TOP",
                search_mode="KEYWORD",
                media_type="TEXT",
            ),
            patch_target="threads_api_tool.commands.search._client",
            fake=fake,
        )
        fake.search_keyword.assert_called_once_with(
            query="cats",
            params={
                "fields": "id,text",
                "limit": 5,
                "search_mode": "KEYWORD",
                "search_type": "TOP",
                "media_type": "TEXT",
                "q": "cats",
            },
        )
        self.assertEqual(payload["command"], "search.keyword")

        fake = Mock()
        fake.search_topic_tag.return_value = {"data": []}
        payload = self._run(
            search_cmd.cmd_search_topic_tag,
            SimpleNamespace(
                topic_tag="travel",
                fields="id,text",
                limit=3,
                before="",
                after="",
                since="",
                until="",
                reverse=False,
                search_type="TOP",
                search_mode="TAG",
                media_type="TEXT",
            ),
            patch_target="threads_api_tool.commands.search._client",
            fake=fake,
        )
        fake.search_topic_tag.assert_called_once_with(
            topic_tag="travel",
            params={
                "fields": "id,text",
                "limit": 3,
                "search_mode": "TAG",
                "search_type": "TOP",
                "media_type": "TEXT",
                "q": "travel",
            },
        )
        self.assertEqual(payload["command"], "search.topic-tag")

        fake = Mock()
        fake.recently_searched_keywords.return_value = {"recently_searched_keywords": ["travel"]}
        payload = self._run(
            search_cmd.cmd_search_recent_keywords,
            SimpleNamespace(),
            patch_target="threads_api_tool.commands.search._client",
            fake=fake,
        )
        fake.recently_searched_keywords.assert_called_once_with()
        self.assertEqual(payload["command"], "search.recent-keywords")

        fake = Mock()
        fake.search_locations_query.return_value = {"data": []}
        payload = self._run(
            locations_cmd.cmd_locations_search_query,
            SimpleNamespace(q="rome", fields="id,name", limit=99, reverse=True),
            patch_target="threads_api_tool.commands.locations._client",
            fake=fake,
        )
        fake.search_locations_query.assert_called_once_with(
            q="rome",
            params={"fields": "id,name"},
        )
        self.assertEqual(payload["command"], "locations.search-query")

        fake = Mock()
        fake.search_locations_coordinates.return_value = {"data": []}
        payload = self._run(
            locations_cmd.cmd_locations_search_coordinates,
            SimpleNamespace(latitude="47.6", longitude="-122.3", fields="id,name"),
            patch_target="threads_api_tool.commands.locations._client",
            fake=fake,
        )
        fake.search_locations_coordinates.assert_called_once_with(
            latitude=47.6,
            longitude=-122.3,
            params={"fields": "id,name"},
        )
        self.assertEqual(payload["command"], "locations.search-coordinates")

        fake = Mock()
        fake.get_location.return_value = {"id": "loc-1"}
        payload = self._run(
            locations_cmd.cmd_locations_get,
            SimpleNamespace(location_id="loc-1", fields="id,name"),
            patch_target="threads_api_tool.commands.locations._client",
            fake=fake,
        )
        fake.get_location.assert_called_once_with(location_id="loc-1", fields="id,name")
        self.assertEqual(payload["command"], "locations.get")

        fake = Mock()
        fake.oembed.return_value = {"html": "<blockquote>...</blockquote>"}
        payload = self._run(
            oembed_cmd.cmd_oembed_get,
            SimpleNamespace(url="https://threads.net/@user/post/1", fields="html", maxwidth=420),
            patch_target="threads_api_tool.commands.oembed._client",
            fake=fake,
        )
        fake.oembed.assert_called_once_with(
            url="https://threads.net/@user/post/1",
            params={"fields": "html", "maxwidth": 420},
        )
        self.assertEqual(payload["command"], "oembed.get")

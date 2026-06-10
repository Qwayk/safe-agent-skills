from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest import mock

from instagram_api_tool.commands import auth, comments, insights, live_media, media, mentions, messages, stories, tags, users
from instagram_api_tool.output import Output


class _AuditStub:
    def write(self, event: str, payload: dict) -> None:
        self.last = (event, payload)


class _FakeClient:
    def __init__(self) -> None:
        self.calls: list[tuple] = []

    def build_login_url(self, **kwargs):
        self.calls.append(("build_login_url", kwargs))
        return "https://example.invalid/oauth"

    def get_me(self, fields=None):
        self.calls.append(("get_me", fields))
        return {"id": "me"}

    def get(self, path, params=None):
        self.calls.append(("get", path, params))
        return {"path": path, "params": params}

    def post(self, path, params=None, json_body=None, data=None):
        self.calls.append(("post", path, params, json_body, data))
        return {"id": "ok"}

    def delete(self, path, params=None):
        self.calls.append(("delete", path, params))
        return {"success": True}


class TestCommandFamilies(unittest.TestCase):
    def _ctx(self, **overrides):
        ctx = {
            "cfg": SimpleNamespace(base_url="https://graph.instagram.com"),
            "env_file": ".env",
            "timeout_s": 30.0,
            "verbose": False,
            "apply": False,
            "yes": False,
            "ack_irreversible": False,
            "plan_out": None,
            "plan_in": None,
            "receipt_out": None,
            "tool": "instagram-api-tool",
            "tool_version": "0.1.0",
            "command_str": "test-command",
            "audit": _AuditStub(),
            "out": Output(mode="json"),
        }
        ctx.update(overrides)
        return ctx

    def _run(self, func, args, ctx):
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = func(args, ctx)
        return rc, json.loads(buf.getvalue())

    def test_auth_family_uses_login_url_builder(self) -> None:
        fake = _FakeClient()
        with mock.patch.object(auth, "_client", return_value=fake):
            rc, payload = self._run(
                auth.cmd_auth_login_url,
                SimpleNamespace(scope="instagram_business_basic", state="abc123"),
                self._ctx(),
            )
        self.assertEqual(rc, 0)
        self.assertEqual(payload["login_url"], "https://example.invalid/oauth")
        self.assertEqual(
            fake.calls,
            [
                (
                    "build_login_url",
                    {
                        "scope": "instagram_business_basic",
                        "state": "abc123",
                        "response_type": "code",
                    },
                )
            ],
        )

    def test_users_family_passes_id_and_fields(self) -> None:
        fake = _FakeClient()
        with mock.patch.object(users, "_client", return_value=fake):
            rc, payload = self._run(
                users.cmd_users_get,
                SimpleNamespace(ig_user_id="17841400000000000", fields="username,account_type"),
                self._ctx(),
            )
        self.assertEqual(rc, 0)
        self.assertEqual(payload["result"]["path"], "/17841400000000000")
        self.assertEqual(payload["result"]["params"], {"fields": "username,account_type"})

    def test_media_family_refuses_apply_before_provider_call(self) -> None:
        fake = _FakeClient()
        with mock.patch.object(media, "_client", return_value=fake):
            rc, payload = self._run(
                media.cmd_media_create_container,
                SimpleNamespace(
                    ig_user_id="17841400000000000",
                    media_type="IMAGE",
                    image_url="https://example.invalid/image.jpg",
                    video_url=None,
                    children=None,
                    caption="Caption",
                    fields=None,
                ),
                self._ctx(apply=True),
            )
        self.assertEqual(rc, 0)
        self.assertFalse(payload["dry_run"])
        self.assertTrue(payload["refused"])
        self.assertEqual(fake.calls, [])
        self.assertEqual(payload["plan"]["before_state"]["status"], "no_snapshot_available")

    def test_comments_family_reads_comment_list(self) -> None:
        fake = _FakeClient()
        with mock.patch.object(comments, "_client", return_value=fake):
            rc, payload = self._run(
                comments.cmd_comments_list,
                SimpleNamespace(media_id="17900000000000000", fields="id,text"),
                self._ctx(),
            )
        self.assertEqual(rc, 0)
        self.assertEqual(payload["result"]["path"], "/17900000000000000/comments")
        self.assertEqual(payload["result"]["params"], {"fields": "id,text"})

    def test_mentions_family_builds_field_selector(self) -> None:
        fake = _FakeClient()
        with mock.patch.object(mentions, "_client", return_value=fake):
            rc, payload = self._run(
                mentions.cmd_mentions_media_get,
                SimpleNamespace(ig_user_id="17841400000000000", media_id="17900000000000000"),
                self._ctx(),
            )
        self.assertEqual(rc, 0)
        self.assertEqual(payload["result"]["path"], "/17841400000000000")
        self.assertEqual(
            payload["result"]["params"],
            {"fields": "mentioned_media.media_id(17900000000000000)"},
        )

    def test_insights_family_builds_metric_params(self) -> None:
        fake = _FakeClient()
        with mock.patch.object(insights, "_client", return_value=fake):
            rc, payload = self._run(
                insights.cmd_insights_account_get,
                SimpleNamespace(
                    ig_user_id="17841400000000000",
                    metric="impressions,reach",
                    period="day",
                    breakdown="follow_type",
                ),
                self._ctx(),
            )
        self.assertEqual(rc, 0)
        self.assertEqual(payload["result"]["path"], "/17841400000000000/insights")
        self.assertEqual(
            payload["result"]["params"],
            {"metric": "impressions,reach", "period": "day", "breakdown": "follow_type"},
        )

    def test_messages_family_refuses_apply_before_provider_call(self) -> None:
        fake = _FakeClient()
        with mock.patch.object(messages, "_client", return_value=fake):
            rc, payload = self._run(
                messages.cmd_messages_send,
                SimpleNamespace(
                    ig_user_id="17841400000000000",
                    recipient_id="123456789",
                    message="Hello",
                ),
                self._ctx(apply=True, yes=True),
            )
        self.assertEqual(rc, 0)
        self.assertFalse(payload["dry_run"])
        self.assertTrue(payload["refused"])
        self.assertEqual(fake.calls, [])
        self.assertEqual(payload["plan"]["before_state"]["status"], "no_snapshot_available")

    def test_tags_family_reads_tags(self) -> None:
        fake = _FakeClient()
        with mock.patch.object(tags, "_client", return_value=fake):
            rc, payload = self._run(
                tags.cmd_tags_list,
                SimpleNamespace(ig_user_id="17841400000000000", fields="id,caption"),
                self._ctx(),
            )
        self.assertEqual(rc, 0)
        self.assertEqual(payload["result"]["path"], "/17841400000000000/tags")
        self.assertEqual(payload["result"]["params"], {"fields": "id,caption"})

    def test_stories_family_reads_stories(self) -> None:
        fake = _FakeClient()
        with mock.patch.object(stories, "_client", return_value=fake):
            rc, payload = self._run(
                stories.cmd_stories_list,
                SimpleNamespace(ig_user_id="17841400000000000", fields="id,permalink"),
                self._ctx(),
            )
        self.assertEqual(rc, 0)
        self.assertEqual(payload["result"]["path"], "/17841400000000000/stories")
        self.assertEqual(payload["result"]["params"], {"fields": "id,permalink"})

    def test_live_media_family_reads_live_media(self) -> None:
        fake = _FakeClient()
        with mock.patch.object(live_media, "_client", return_value=fake):
            rc, payload = self._run(
                live_media.cmd_live_media_list,
                SimpleNamespace(ig_user_id="17841400000000000", fields="id,status"),
                self._ctx(),
            )
        self.assertEqual(rc, 0)
        self.assertEqual(payload["result"]["path"], "/17841400000000000/live_media")
        self.assertEqual(payload["result"]["params"], {"fields": "id,status"})

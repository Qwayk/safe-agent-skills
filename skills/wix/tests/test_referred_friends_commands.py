from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import referred_friends
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = (action, payload)


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestReferredFriendsCommands(unittest.TestCase):
    def _ctx(self, **overrides) -> dict:
        cfg = SimpleNamespace(
            base_url="https://www.wixapis.com",
            timeout_s=30.0,
            access_token="token-abc",
            app_id=None,
            app_secret=None,
            instance_id=None,
            has_official_app_auth=False,
        )
        ctx = {
            "cfg": cfg,
            "env_file": "/tmp/.env",
            "tool": "wix-safe-agent-cli",
            "tool_version": "0.0.0",
            "command_str": "wix-safe-agent-cli referred-friends",
            "apply": False,
            "yes": False,
            "verbose": False,
            "out": Output(mode="json"),
            "audit": _DummyAudit(),
            "plan_in": None,
            "plan_out": None,
            "receipt_out": None,
            "ack_irreversible": False,
            "enforce_reviewed_plan": True,
        }
        ctx.update(overrides)
        return ctx

    def test_parser_recognizes_referred_friends_commands(self) -> None:
        parser = build_parser()
        cases = [
            ["referred-friends", "get", "--referred-friend-id", "friend-123"],
            ["referred-friends", "query", "--query-json", '{"query":{"filter":{"status":{"$eq":"ACTIONS_COMPLETED"}}}}'],
            ["referred-friends", "get-by-contact-id", "--contact-id", "me"],
            ["referred-friends", "create", "--referral-code", "9zb9JvjwrvQF"],
            [
                "referred-friends",
                "update",
                "--referred-friend-json",
                '{"referredFriend":{"id":"friend-123","contactId":"contact-1","referringCustomerId":"customer-1","status":"ACTIONS_COMPLETED","revision":"2"}}',
            ],
            ["referred-friends", "delete", "--referred-friend-id", "friend-123", "--revision", "2"],
        ]
        for argv in cases:
            with self.subTest(argv=argv):
                args = parser.parse_args(argv)
                self.assertTrue(callable(args.func))
                self.assertEqual(args.write_capable, argv[1] in {"create", "update", "delete"})

    @patch("wix_safe_agent_cli.commands.referred_friends.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.referred_friends.HttpClient")
    def test_get_uses_official_path(self, mock_client, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"referredFriend": {"id": "friend-123"}})

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = referred_friends.cmd_referred_friends_get(SimpleNamespace(referred_friend_id="friend-123"), self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertEqual(payload["request"]["method"], "GET")
        self.assertEqual(payload["request"]["path"], "/referral_friends/v1/referred-friends/friend-123")
        self.assertEqual(mock_auth.call_args.kwargs["command_family"], "referred-friends")

    @patch("wix_safe_agent_cli.commands.referred_friends.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.referred_friends.HttpClient")
    def test_query_uses_official_path_and_body(self, mock_client, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"referredFriends": []})

        query_json = '{"query":{"filter":{"status":{"$eq":"ACTIONS_COMPLETED"}},"sort":[{"fieldName":"revision","order":"DESC"}]}}'
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = referred_friends.cmd_referred_friends_query(SimpleNamespace(query_json=query_json), self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertEqual(payload["request"]["method"], "POST")
        self.assertEqual(payload["request"]["path"], "/referral_friends/v1/referred-friends/query")
        self.assertEqual(payload["request"]["body"]["query"]["filter"]["status"]["$eq"], "ACTIONS_COMPLETED")

    @patch("wix_safe_agent_cli.commands.referred_friends.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.referred_friends.HttpClient")
    def test_get_by_contact_id_uses_official_path(self, mock_client, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"referredFriend": {"contactId": "me"}})

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = referred_friends.cmd_referred_friends_get_by_contact_id(SimpleNamespace(contact_id="me"), self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertEqual(payload["request"]["method"], "GET")
        self.assertEqual(payload["request"]["path"], "/referral_friends/v1/referred-friends/contact/me")

    @patch("wix_safe_agent_cli.commands.referred_friends.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.referred_friends.HttpClient")
    def test_create_is_plan_first_and_uses_referral_code_body(self, mock_client, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"referredFriend": {"id": "friend-123"}})

        dry_buf = io.StringIO()
        with redirect_stdout(dry_buf):
            dry_rc = referred_friends.cmd_referred_friends_create(SimpleNamespace(referral_code="9zb9JvjwrvQF"), self._ctx())

        with tempfile.TemporaryDirectory() as tmp:
            plan_path = Path(tmp) / "plan.json"
            plan = {
                "method": "referredFriends.createReferredFriend",
                "baseline": {
                    "env_fingerprint": "https://www.wixapis.com",
                    "selector": {"kind": "referred-friends", "operation": "create"},
                },
                "proposed_changes": [{"operation": "create"}],
            }
            plan_path.write_text(json.dumps(plan), encoding="utf-8")

            apply_buf = io.StringIO()
            with redirect_stdout(apply_buf):
                apply_rc = referred_friends.cmd_referred_friends_create(
                    SimpleNamespace(referral_code="9zb9JvjwrvQF"),
                    self._ctx(apply=True, yes=True, plan_in=str(plan_path)),
                )

        dry = json.loads(dry_buf.getvalue())
        applied = json.loads(apply_buf.getvalue())
        self.assertEqual(dry_rc, 0)
        self.assertTrue(dry["dry_run"])
        self.assertEqual(dry["plan"]["request"]["method"], "POST")
        self.assertEqual(dry["plan"]["request"]["path"], "/referral_friends/v1/referred-friends")
        self.assertEqual(dry["plan"]["request"]["body"], {"referralCode": "9zb9JvjwrvQF"})
        self.assertEqual(apply_rc, 0)
        self.assertFalse(applied["dry_run"])
        self.assertEqual(mock_client.return_value.request.call_args.kwargs["json_body"], {"referralCode": "9zb9JvjwrvQF"})

    @patch("wix_safe_agent_cli.commands.referred_friends.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.referred_friends.HttpClient")
    def test_update_requires_referred_friend_object_with_id_and_revision(self, mock_client, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"referredFriend": {"id": "friend-123", "revision": "3"}})
        update_json = '{"referredFriend":{"id":"friend-123","contactId":"contact-1","referringCustomerId":"customer-1","status":"ACTIONS_COMPLETED","revision":"2"}}'

        dry_buf = io.StringIO()
        with redirect_stdout(dry_buf):
            dry_rc = referred_friends.cmd_referred_friends_update(SimpleNamespace(referred_friend_json=update_json), self._ctx())

        bad_buf = io.StringIO()
        with redirect_stdout(bad_buf):
            bad_rc = referred_friends.cmd_referred_friends_update(
                SimpleNamespace(referred_friend_json='{"referredFriend":{"id":"friend-123","revision":"2"}}'),
                self._ctx(),
            )

        dry = json.loads(dry_buf.getvalue())
        bad = json.loads(bad_buf.getvalue())
        self.assertEqual(dry_rc, 0)
        self.assertTrue(dry["dry_run"])
        self.assertEqual(dry["plan"]["request"]["method"], "PATCH")
        self.assertEqual(dry["plan"]["request"]["path"], "/referral_friends/v1/referred-friends/friend-123")
        self.assertEqual(dry["plan"]["request"]["body"]["referredFriend"]["revision"], "2")
        self.assertEqual(bad_rc, 1)
        self.assertEqual(bad["error_type"], "ValidationError")
        mock_client.return_value.request.assert_not_called()

    @patch("wix_safe_agent_cli.commands.referred_friends.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.referred_friends.HttpClient")
    def test_delete_requires_ack_and_sends_revision_query_param(self, mock_client, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({})

        dry_buf = io.StringIO()
        with redirect_stdout(dry_buf):
            dry_rc = referred_friends.cmd_referred_friends_delete(
                SimpleNamespace(referred_friend_id="friend-123", revision="2"),
                self._ctx(),
            )

        no_ack_buf = io.StringIO()
        with redirect_stdout(no_ack_buf):
            no_ack_rc = referred_friends.cmd_referred_friends_delete(
                SimpleNamespace(referred_friend_id="friend-123", revision="2"),
                self._ctx(apply=True, yes=True, plan_in="/tmp/no-plan.json"),
            )
        mock_client.return_value.request.assert_not_called()

        with tempfile.TemporaryDirectory() as tmp:
            plan_path = Path(tmp) / "plan.json"
            plan = {
                "method": "referredFriends.deleteReferredFriend",
                "baseline": {
                    "env_fingerprint": "https://www.wixapis.com",
                    "selector": {"kind": "referred-friends", "operation": "delete"},
                },
                "proposed_changes": [{"operation": "delete"}],
            }
            plan_path.write_text(json.dumps(plan), encoding="utf-8")

            apply_buf = io.StringIO()
            with redirect_stdout(apply_buf):
                apply_rc = referred_friends.cmd_referred_friends_delete(
                    SimpleNamespace(referred_friend_id="friend-123", revision="2"),
                    self._ctx(apply=True, yes=True, ack_irreversible=True, plan_in=str(plan_path)),
                )

        dry = json.loads(dry_buf.getvalue())
        no_ack = json.loads(no_ack_buf.getvalue())
        applied = json.loads(apply_buf.getvalue())
        self.assertEqual(dry_rc, 0)
        self.assertTrue(dry["dry_run"])
        self.assertIn("apply also requires --ack-irreversible", dry["plan"]["preconditions"])
        self.assertEqual(dry["plan"]["request"]["params"], {"revision": "2"})
        self.assertEqual(no_ack_rc, 0)
        self.assertTrue(no_ack["dry_run"])
        self.assertEqual(apply_rc, 0)
        self.assertFalse(applied["dry_run"])
        self.assertEqual(mock_client.return_value.request.call_args.kwargs["params"], {"revision": "2"})

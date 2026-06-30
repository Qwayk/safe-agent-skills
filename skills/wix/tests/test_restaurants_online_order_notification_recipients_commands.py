from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import restaurants_online_order_notification_recipients
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = (action, payload)


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestRestaurantsOnlineOrderNotificationRecipientsCommands(unittest.TestCase):
    def _ctx(self, **overrides) -> dict:
        cfg = SimpleNamespace(
            base_url="https://www.wixapis.com",
            timeout_s=30.0,
            app_id=None,
            app_secret=None,
            instance_id=None,
            access_token="token-abc",
            has_official_app_auth=False,
        )
        ctx = {
            "cfg": cfg,
            "env_file": "/tmp/.env",
            "verbose": False,
            "out": Output(mode="json"),
            "audit": _DummyAudit(),
            "tool": "wix-safe-agent-cli",
            "tool_version": "0.0.0",
            "command_str": "wix-safe-agent-cli restaurants-online-order-notification-recipients",
            "apply": False,
            "yes": False,
            "plan_in": None,
            "plan_out": None,
            "receipt_out": None,
            "ack_irreversible": False,
            "enforce_reviewed_plan": True,
        }
        ctx.update(overrides)
        return ctx

    @patch("wix_safe_agent_cli.commands.restaurants_online_order_notification_recipients.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.restaurants_online_order_notification_recipients.HttpClient")
    def test_read_commands_use_official_paths(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"recipients": []})

        cases = [
            (restaurants_online_order_notification_recipients.cmd_restaurants_online_order_notification_recipients_get, SimpleNamespace(recipient_id="rec-1"), "GET", "/rest-notification-recipients/v1/recipients/rec-1"),
            (restaurants_online_order_notification_recipients.cmd_restaurants_online_order_notification_recipients_query, SimpleNamespace(query_json='{"query":{}}'), "POST", "/rest-notification-recipients/v1/recipients/query"),
        ]

        for func, args, method, path in cases:
            with self.subTest(path=path):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = func(args, self._ctx())
                payload = json.loads(buf.getvalue())
                self.assertEqual(rc, 0)
                self.assertEqual(payload["request"]["method"], method)
                self.assertEqual(payload["request"]["path"], path)

        self.assertEqual(mock_auth.call_args.kwargs["command_family"], "restaurants-online-order-notification-recipients")

    @patch("wix_safe_agent_cli.commands.restaurants_online_order_notification_recipients.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.restaurants_online_order_notification_recipients.HttpClient")
    def test_write_commands_are_plan_first(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}

        cases = [
            (restaurants_online_order_notification_recipients.cmd_restaurants_online_order_notification_recipients_create, SimpleNamespace(recipient_json='{"recipient":{"phone":"123"}}'), "POST", "/rest-notification-recipients/v1/recipients"),
            (restaurants_online_order_notification_recipients.cmd_restaurants_online_order_notification_recipients_bulk_create, SimpleNamespace(recipients_json='{"recipients":[{"phone":"123"}]}'), "POST", "/rest-notification-recipients/v1/bulk/recipients"),
            (restaurants_online_order_notification_recipients.cmd_restaurants_online_order_notification_recipients_update, SimpleNamespace(recipient_id="rec-1", recipient_json='{"recipient":{"revision":"1"}}'), "PATCH", "/rest-notification-recipients/v1/recipients/rec-1"),
            (restaurants_online_order_notification_recipients.cmd_restaurants_online_order_notification_recipients_bulk_update, SimpleNamespace(recipients_json='{"recipients":[{"id":"rec-1","revision":"1"}]}'), "POST", "/rest-notification-recipients/v1/bulk/recipients/update"),
            (restaurants_online_order_notification_recipients.cmd_restaurants_online_order_notification_recipients_delete, SimpleNamespace(recipient_id="rec-1"), "DELETE", "/rest-notification-recipients/v1/recipients/rec-1"),
            (restaurants_online_order_notification_recipients.cmd_restaurants_online_order_notification_recipients_bulk_delete, SimpleNamespace(recipients_json='{"ids":["rec-1"]}'), "POST", "/rest-notification-recipients/v1/bulk/recipients/delete"),
            (restaurants_online_order_notification_recipients.cmd_restaurants_online_order_notification_recipients_bulk_update_tags, SimpleNamespace(tags_json='{"ids":["rec-1"],"assignTags":["vip"]}'), "POST", "/rest-notification-recipients/v1/bulk/recipients/update-tags"),
            (restaurants_online_order_notification_recipients.cmd_restaurants_online_order_notification_recipients_bulk_update_tags_by_filter, SimpleNamespace(filter_json='{"filter":{"locationId":"loc-1"},"assignTags":["vip"]}'), "POST", "/rest-notification-recipients/v1/bulk/recipients/update-tags-by-filter"),
        ]

        for func, args, method, path in cases:
            with self.subTest(path=path):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = func(args, self._ctx())
                payload = json.loads(buf.getvalue())
                self.assertEqual(rc, 0)
                self.assertTrue(payload["dry_run"])
                self.assertEqual(payload["plan"]["request"]["method"], method)
                self.assertEqual(payload["plan"]["request"]["path"], path)

        mock_client.return_value.request.assert_not_called()

    @patch("wix_safe_agent_cli.commands.restaurants_online_order_notification_recipients.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.restaurants_online_order_notification_recipients.HttpClient")
    def test_irreversible_commands_require_ack(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}

        cases = [
            (restaurants_online_order_notification_recipients.cmd_restaurants_online_order_notification_recipients_delete, SimpleNamespace(recipient_id="rec-1")),
            (restaurants_online_order_notification_recipients.cmd_restaurants_online_order_notification_recipients_bulk_delete, SimpleNamespace(recipients_json='{"ids":["rec-1"]}')),
            (restaurants_online_order_notification_recipients.cmd_restaurants_online_order_notification_recipients_bulk_update_tags_by_filter, SimpleNamespace(filter_json='{"filter":{"locationId":"loc-1"},"assignTags":["vip"]}')),
        ]
        for func, args in cases:
            with self.subTest(func=func.__name__):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = func(args, self._ctx(apply=True, yes=True, plan_in="/tmp/reviewed-plan.json"))
                payload = json.loads(buf.getvalue())
                self.assertEqual(rc, 0)
                self.assertTrue(payload["dry_run"])
                self.assertIn("apply also requires --ack-irreversible", payload["plan"]["preconditions"])

        mock_client.return_value.request.assert_not_called()

    @patch("wix_safe_agent_cli.commands.restaurants_online_order_notification_recipients.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.restaurants_online_order_notification_recipients.HttpClient")
    def test_revision_and_tag_selectors_are_required(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}

        cases = [
            (restaurants_online_order_notification_recipients.cmd_restaurants_online_order_notification_recipients_update, SimpleNamespace(recipient_id="rec-1", recipient_json='{"recipient":{"name":"Kitchen"}}'), "revision"),
            (restaurants_online_order_notification_recipients.cmd_restaurants_online_order_notification_recipients_bulk_update, SimpleNamespace(recipients_json='{"recipients":[{"id":"rec-1"}]}'), "revision"),
            (restaurants_online_order_notification_recipients.cmd_restaurants_online_order_notification_recipients_bulk_update_tags, SimpleNamespace(tags_json='{"assignTags":["vip"]}'), "ids or recipientIds"),
        ]
        for func, args, error_text in cases:
            with self.subTest(func=func.__name__):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = func(args, self._ctx())
                payload = json.loads(buf.getvalue())
                self.assertEqual(rc, 1)
                self.assertIn(error_text, payload["error"])

        mock_client.return_value.request.assert_not_called()

    def test_parser_exposes_all_restaurants_online_order_notification_recipient_commands_and_write_flags(self) -> None:
        parser = build_parser()
        cases = [
            (["restaurants-online-order-notification-recipients", "get", "--recipient-id", "rec-1"], restaurants_online_order_notification_recipients.cmd_restaurants_online_order_notification_recipients_get, False),
            (["restaurants-online-order-notification-recipients", "query"], restaurants_online_order_notification_recipients.cmd_restaurants_online_order_notification_recipients_query, False),
            (["restaurants-online-order-notification-recipients", "create", "--recipient-json", "{}"], restaurants_online_order_notification_recipients.cmd_restaurants_online_order_notification_recipients_create, True),
            (["restaurants-online-order-notification-recipients", "bulk-create", "--recipients-json", "{}"], restaurants_online_order_notification_recipients.cmd_restaurants_online_order_notification_recipients_bulk_create, True),
            (["restaurants-online-order-notification-recipients", "update", "--recipient-id", "rec-1", "--recipient-json", "{}"], restaurants_online_order_notification_recipients.cmd_restaurants_online_order_notification_recipients_update, True),
            (["restaurants-online-order-notification-recipients", "bulk-update", "--recipients-json", "{}"], restaurants_online_order_notification_recipients.cmd_restaurants_online_order_notification_recipients_bulk_update, True),
            (["restaurants-online-order-notification-recipients", "delete", "--recipient-id", "rec-1"], restaurants_online_order_notification_recipients.cmd_restaurants_online_order_notification_recipients_delete, True),
            (["restaurants-online-order-notification-recipients", "bulk-delete", "--recipients-json", "{}"], restaurants_online_order_notification_recipients.cmd_restaurants_online_order_notification_recipients_bulk_delete, True),
            (["restaurants-online-order-notification-recipients", "bulk-update-tags", "--tags-json", "{}"], restaurants_online_order_notification_recipients.cmd_restaurants_online_order_notification_recipients_bulk_update_tags, True),
            (["restaurants-online-order-notification-recipients", "bulk-update-tags-by-filter", "--filter-json", "{}"], restaurants_online_order_notification_recipients.cmd_restaurants_online_order_notification_recipients_bulk_update_tags_by_filter, True),
        ]
        for argv, func, write_capable in cases:
            with self.subTest(argv=argv):
                args = parser.parse_args(argv)
                self.assertIs(args.func, func)
                self.assertEqual(args.write_capable, write_capable)

from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import events_forms
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = (action, payload)


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestEventsFormsCommands(unittest.TestCase):
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
            "command_str": "wix-safe-agent-cli events-forms",
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

    @patch("wix_safe_agent_cli.commands.events_forms.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.events_forms.HttpClient")
    def test_get_form_uses_official_path(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"form": {"controls": []}})

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = events_forms.cmd_events_forms_get_form(SimpleNamespace(event_id="event-1"), self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertEqual(payload["method"], "events-forms.get-form")
        self.assertEqual(payload["request"]["method"], "GET")
        self.assertEqual(payload["request"]["path"], "/events/v1/events/event-1/form")
        self.assertEqual(mock_auth.call_args.kwargs["command_family"], "events-forms")

    @patch("wix_safe_agent_cli.commands.events_forms.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.events_forms.HttpClient")
    def test_write_commands_are_plan_first(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}

        cases = [
            (events_forms.cmd_events_forms_discard_draft, SimpleNamespace(event_id="event-1"), "DELETE", "/events/v1/events/event-1/form"),
            (
                events_forms.cmd_events_forms_add_control,
                SimpleNamespace(event_id="event-1", control_json='{"control":{"type":"TEXT"}}'),
                "POST",
                "/events/v1/events/event-1/form/control",
            ),
            (
                events_forms.cmd_events_forms_update_control,
                SimpleNamespace(event_id="event-1", control_id="phone", control_json='{"control":{"type":"PHONE"}}'),
                "PUT",
                "/events/v1/events/event-1/form/controls/phone",
            ),
            (
                events_forms.cmd_events_forms_delete_control,
                SimpleNamespace(event_id="event-1", control_id="phone"),
                "DELETE",
                "/events/v1/events/event-1/form/controls/phone",
            ),
            (
                events_forms.cmd_events_forms_update_messages,
                SimpleNamespace(event_id="event-1", messages_json='{"messages":{"thankYou":"Thanks"}}'),
                "PATCH",
                "/events/v1/events/event-1/form/messages",
            ),
            (events_forms.cmd_events_forms_publish_draft, SimpleNamespace(event_id="event-1"), "POST", "/events/v1/events/event-1/form/publish"),
        ]

        for func, args, http_method, path in cases:
            with self.subTest(path=path):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = func(args, self._ctx())
                payload = json.loads(buf.getvalue())
                self.assertEqual(rc, 0)
                self.assertTrue(payload["dry_run"])
                self.assertEqual(payload["plan"]["request"]["method"], http_method)
                self.assertEqual(payload["plan"]["request"]["path"], path)

        mock_client.return_value.request.assert_not_called()

    @patch("wix_safe_agent_cli.commands.events_forms.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.events_forms.HttpClient")
    def test_destructive_and_deprecated_actions_require_irreversible_ack(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        cases = [
            (events_forms.cmd_events_forms_discard_draft, SimpleNamespace(event_id="event-1")),
            (events_forms.cmd_events_forms_delete_control, SimpleNamespace(event_id="event-1", control_id="phone")),
            (events_forms.cmd_events_forms_update_messages, SimpleNamespace(event_id="event-1", messages_json='{"messages":{"thankYou":"Thanks"}}')),
            (events_forms.cmd_events_forms_publish_draft, SimpleNamespace(event_id="event-1")),
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

    @patch("wix_safe_agent_cli.commands.events_forms.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.events_forms.HttpClient")
    def test_json_body_must_be_non_empty_object(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = events_forms.cmd_events_forms_add_control(SimpleNamespace(event_id="event-1", control_json="{}"), self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertIn("cannot be empty", payload["error"])
        mock_client.return_value.request.assert_not_called()

    def test_parser_exposes_all_events_forms_commands_and_write_flags(self) -> None:
        parser = build_parser()
        cases = [
            (["events-forms", "get-form", "--event-id", "event-1"], events_forms.cmd_events_forms_get_form, False),
            (["events-forms", "discard-draft", "--event-id", "event-1"], events_forms.cmd_events_forms_discard_draft, True),
            (["events-forms", "add-control", "--event-id", "event-1", "--control-json", "{}"], events_forms.cmd_events_forms_add_control, True),
            (
                ["events-forms", "update-control", "--event-id", "event-1", "--control-id", "phone", "--control-json", "{}"],
                events_forms.cmd_events_forms_update_control,
                True,
            ),
            (["events-forms", "delete-control", "--event-id", "event-1", "--control-id", "phone"], events_forms.cmd_events_forms_delete_control, True),
            (["events-forms", "update-messages", "--event-id", "event-1", "--messages-json", "{}"], events_forms.cmd_events_forms_update_messages, True),
            (["events-forms", "publish-draft", "--event-id", "event-1"], events_forms.cmd_events_forms_publish_draft, True),
        ]
        for argv, func, writable in cases:
            with self.subTest(argv=argv):
                args = parser.parse_args(argv)
                self.assertIs(args.func, func)
                self.assertEqual(args.write_capable, writable)

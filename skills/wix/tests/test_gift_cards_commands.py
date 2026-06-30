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
from wix_safe_agent_cli.commands import gift_cards
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = (action, payload)


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestGiftCardsCommands(unittest.TestCase):
    def _ctx(self, **overrides) -> dict:
        cfg = SimpleNamespace(
            base_url="https://www.wixapis.com",
            timeout_s=30.0,
            access_token="site-app-token",
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
            "command_str": "wix-safe-agent-cli gift-cards",
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

    @staticmethod
    def _gift_card(*, disabled: bool = False) -> dict:
        payload = {
            "id": "gift-1",
            "codeSuffix": "4444",
            "initialValue": {"amount": "50.00"},
            "balance": {"amount": "50.00"},
            "currency": "USD",
            "source": "MANUAL",
        }
        if disabled:
            payload["disabledDate"] = "2026-06-24T00:00:00Z"
        return payload

    def _write_plan(self, plan: dict) -> str:
        handle = tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json")
        json.dump(plan, handle)
        handle.close()
        return handle.name

    def test_parser_recognizes_gift_card_subcommands(self) -> None:
        parser = build_parser()

        get_args = parser.parse_args(["gift-cards", "get", "--gift-card-id", "gift-1"])
        self.assertEqual(get_args.gift_cards_cmd, "get")
        self.assertFalse(get_args.write_capable)

        query_args = parser.parse_args(["gift-cards", "query"])
        self.assertEqual(query_args.gift_cards_cmd, "query")
        self.assertFalse(query_args.write_capable)

        search_args = parser.parse_args(["gift-cards", "search"])
        self.assertEqual(search_args.gift_cards_cmd, "search")
        self.assertFalse(search_args.write_capable)

        count_args = parser.parse_args(["gift-cards", "count"])
        self.assertEqual(count_args.gift_cards_cmd, "count")
        self.assertFalse(count_args.write_capable)

        create_args = parser.parse_args(
            [
                "gift-cards",
                "create",
                "--gift-card-json",
                '{"initialValue":{"amount":"50.00"},"currency":"USD","source":"MANUAL"}',
            ]
        )
        self.assertEqual(create_args.gift_cards_cmd, "create")
        self.assertTrue(create_args.write_capable)

        disable_args = parser.parse_args(["gift-cards", "disable", "--gift-card-id", "gift-1"])
        self.assertEqual(disable_args.gift_cards_cmd, "disable")
        self.assertTrue(disable_args.write_capable)

        send_email_args = parser.parse_args(["gift-cards", "send-email", "--gift-card-id", "gift-1"])
        self.assertEqual(send_email_args.gift_cards_cmd, "send-email")
        self.assertTrue(send_email_args.write_capable)

    @patch("wix_safe_agent_cli.commands.gift_cards.HttpClient")
    def test_get_builds_expected_request(self, mock_client) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"giftCard": self._gift_card()})
        args = SimpleNamespace(gift_card_id="gift-1")

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = gift_cards.cmd_gift_cards_get(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["request"]["path"], "/gift-cards/v1/gift-cards/gift-1")

    @patch("wix_safe_agent_cli.commands.gift_cards.HttpClient")
    def test_query_builds_expected_request(self, mock_client) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"giftCards": []})
        args = SimpleNamespace(query_json='{"paging":{"limit":25}}')

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = gift_cards.cmd_gift_cards_query(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertEqual(payload["request"]["path"], "/gift-cards/v1/gift-cards/query")
        self.assertEqual(payload["request"]["body"], {"paging": {"limit": 25}})

    @patch("wix_safe_agent_cli.commands.gift_cards.HttpClient")
    def test_count_wraps_raw_filter_object(self, mock_client) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"count": 1})
        args = SimpleNamespace(filter_json='{"source":"MANUAL"}')

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = gift_cards.cmd_gift_cards_count(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertEqual(payload["request"]["path"], "/gift-cards/v1/gift-cards/count")
        self.assertEqual(payload["request"]["body"], {"filter": {"source": "MANUAL"}})

    def test_create_dry_run_wraps_raw_gift_card_body(self) -> None:
        args = SimpleNamespace(
            gift_card_json='{"initialValue":{"amount":"50.00"},"currency":"USD","source":"MANUAL"}'
        )

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = gift_cards.cmd_gift_cards_create(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["method"], "gift-cards.create")
        self.assertEqual(
            payload["plan"]["request"]["body"],
            {"giftCard": {"initialValue": {"amount": "50.00"}, "currency": "USD", "source": "MANUAL"}},
        )

    @patch("wix_safe_agent_cli.commands.gift_cards.HttpClient")
    def test_create_apply_requires_reviewed_plan_before_write(self, mock_client) -> None:
        args = SimpleNamespace(
            gift_card_json='{"giftCard":{"initialValue":{"amount":"50.00"},"currency":"USD","source":"MANUAL"}}'
        )

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = gift_cards.cmd_gift_cards_create(args, self._ctx(apply=True, yes=True))
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertEqual(mock_client.return_value.request.call_count, 0)

    @patch("wix_safe_agent_cli.commands.gift_cards.HttpClient")
    def test_disable_apply_requires_reviewed_plan_before_write(self, mock_client) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"giftCard": self._gift_card()})
        args = SimpleNamespace(gift_card_id="gift-1")

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = gift_cards.cmd_gift_cards_disable(args, self._ctx(apply=True, yes=True, ack_irreversible=True))
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertEqual(mock_client.return_value.request.call_count, 1)

    @patch("wix_safe_agent_cli.commands.gift_cards.HttpClient")
    def test_disable_apply_verifies_disabled_date(self, mock_client) -> None:
        mock_client.return_value.request.side_effect = [
            _DummyResponse({"giftCard": self._gift_card()}),
            _DummyResponse({"giftCard": self._gift_card()}),
            _DummyResponse({"giftCard": self._gift_card()}),
            _DummyResponse({"giftCard": self._gift_card(disabled=True)}),
            _DummyResponse({"giftCard": self._gift_card(disabled=True)}),
        ]
        args = SimpleNamespace(gift_card_id="gift-1")

        dry_buf = io.StringIO()
        with redirect_stdout(dry_buf):
            gift_cards.cmd_gift_cards_disable(args, self._ctx())
        plan_path = self._write_plan(json.loads(dry_buf.getvalue())["plan"])
        try:
            apply_ctx = self._ctx(apply=True, yes=True, ack_irreversible=True, plan_in=plan_path)
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = gift_cards.cmd_gift_cards_disable(args, apply_ctx)
            payload = json.loads(buf.getvalue())

            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(
                payload["receipt"]["verification"]["after"]["disabledDate"],
                "2026-06-24T00:00:00Z",
            )
        finally:
            Path(plan_path).unlink()

    def test_send_email_dry_run_builds_recipient_override(self) -> None:
        args = SimpleNamespace(gift_card_id="gift-1", recipient_email="friend@example.com")
        with patch("wix_safe_agent_cli.commands.gift_cards.HttpClient") as mock_client:
            mock_client.return_value.request.return_value = _DummyResponse({"giftCard": self._gift_card()})
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = gift_cards.cmd_gift_cards_send_email(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["request"]["body"], {"recipientEmail": "friend@example.com"})

    @patch("wix_safe_agent_cli.commands.gift_cards.HttpClient")
    def test_send_email_apply_requires_reviewed_plan_before_write(self, mock_client) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"giftCard": self._gift_card()})
        args = SimpleNamespace(gift_card_id="gift-1", recipient_email=None)

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = gift_cards.cmd_gift_cards_send_email(args, self._ctx(apply=True, yes=True))
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertEqual(mock_client.return_value.request.call_count, 1)

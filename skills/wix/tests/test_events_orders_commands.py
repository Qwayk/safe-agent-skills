from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import events_orders
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = (action, payload)


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestEventsOrdersCommands(unittest.TestCase):
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
            "command_str": "wix-safe-agent-cli events-orders",
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

    @patch("wix_safe_agent_cli.commands.events_orders.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.events_orders.HttpClient")
    def test_read_commands_use_official_paths(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"ok": True})

        cases = [
            (events_orders.cmd_events_orders_list, SimpleNamespace(params_json='{"eventId":"event-1"}'), "GET", "/events/v1/orders"),
            (
                events_orders.cmd_events_orders_get,
                SimpleNamespace(event_id="event-1", order_number="1001"),
                "GET",
                "/events/v1/events/event-1/orders/1001",
            ),
            (events_orders.cmd_events_orders_get_summary, SimpleNamespace(params_json='{"eventId":"event-1"}'), "GET", "/events/v1/orders/summary"),
            (events_orders.cmd_events_orders_get_checkout_options, SimpleNamespace(params_json='{"eventId":"event-1"}'), "GET", "/events/v1/checkout/options"),
            (events_orders.cmd_events_orders_list_available_tickets, SimpleNamespace(params_json='{"eventId":"event-1"}'), "GET", "/events/v1/checkout/available-tickets"),
            (
                events_orders.cmd_events_orders_query_available_tickets,
                SimpleNamespace(query_json='{"eventId":"event-1","limit":1000,"offset":0}'),
                "POST",
                "/events/v1/checkout/available-tickets/query",
            ),
            (
                events_orders.cmd_events_orders_get_invoice,
                SimpleNamespace(reservation_id="reservation-1", invoice_json='{"couponCode":"SAVE"}'),
                "POST",
                "/events/v1/checkout/invoices/reservation-1",
            ),
        ]

        for func, args, http_method, path in cases:
            with self.subTest(path=path):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = func(args, self._ctx())
                payload = json.loads(buf.getvalue())
                self.assertEqual(rc, 0)
                self.assertEqual(payload["request"]["method"], http_method)
                self.assertEqual(payload["request"]["path"], path)

        self.assertEqual(mock_auth.call_args.kwargs["command_family"], "events-orders")

    @patch("wix_safe_agent_cli.commands.events_orders.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.events_orders.HttpClient")
    def test_write_commands_are_plan_first(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}

        cases = [
            (
                events_orders.cmd_events_orders_update,
                SimpleNamespace(event_id="event-1", order_number="1001", order_json='{"archived":true}'),
                "/events/v1/events/event-1/orders/1001",
            ),
            (
                events_orders.cmd_events_orders_bulk_update,
                SimpleNamespace(event_id="event-1", orders_json='{"orderNumbers":["1001"],"archived":true}'),
                "/events/v1/events/event-1/orders",
            ),
            (
                events_orders.cmd_events_orders_confirm,
                SimpleNamespace(event_id="event-1", request_json='{"orderNumber":"1001"}'),
                "/events/v1/events/event-1/orders/confirm",
            ),
            (
                events_orders.cmd_events_orders_create_reservation,
                SimpleNamespace(reservation_json='{"eventId":"event-1","ticketQuantities":[{"ticketDefinitionId":"ticket-1","quantity":1}]}'),
                "/events/v1/checkout/reservations",
            ),
            (events_orders.cmd_events_orders_cancel_reservation, SimpleNamespace(reservation_id="reservation-1"), "/events/v1/checkout/reservations/reservation-1"),
            (events_orders.cmd_events_orders_checkout, SimpleNamespace(checkout_json='{"reservationId":"reservation-1"}'), "/events/v1/checkout"),
            (
                events_orders.cmd_events_orders_update_checkout,
                SimpleNamespace(order_number="1001", checkout_json='{"checkoutForm":{"firstName":"Ada"}}'),
                "/events/v1/checkout/1001",
            ),
        ]

        for func, args, path in cases:
            with self.subTest(path=path):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = func(args, self._ctx())
                payload = json.loads(buf.getvalue())
                self.assertEqual(rc, 0)
                self.assertTrue(payload["dry_run"])
                self.assertEqual(payload["plan"]["request"]["path"], path)

        mock_client.return_value.request.assert_not_called()

    @patch("wix_safe_agent_cli.commands.events_orders.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.events_orders.HttpClient")
    def test_payment_and_reservation_actions_require_irreversible_ack(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        cases = [
            (events_orders.cmd_events_orders_confirm, SimpleNamespace(event_id="event-1", request_json='{"orderNumber":"1001"}')),
            (events_orders.cmd_events_orders_create_reservation, SimpleNamespace(reservation_json='{"eventId":"event-1"}')),
            (events_orders.cmd_events_orders_cancel_reservation, SimpleNamespace(reservation_id="reservation-1")),
            (events_orders.cmd_events_orders_checkout, SimpleNamespace(checkout_json='{"reservationId":"reservation-1"}')),
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

    @patch("wix_safe_agent_cli.commands.events_orders.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.events_orders.HttpClient")
    def test_query_available_tickets_paging_limits_are_enforced(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}

        limit_buf = io.StringIO()
        with redirect_stdout(limit_buf):
            rc_limit = events_orders.cmd_events_orders_query_available_tickets(SimpleNamespace(query_json='{"limit":1001}'), self._ctx())
        limit_payload = json.loads(limit_buf.getvalue())

        offset_buf = io.StringIO()
        with redirect_stdout(offset_buf):
            rc_offset = events_orders.cmd_events_orders_query_available_tickets(SimpleNamespace(query_json='{"offset":-1}'), self._ctx())
        offset_payload = json.loads(offset_buf.getvalue())

        self.assertEqual(rc_limit, 1)
        self.assertIn("at most 1000", limit_payload["error"])
        self.assertEqual(rc_offset, 1)
        self.assertIn("0 or greater", offset_payload["error"])
        mock_client.return_value.request.assert_not_called()

    def test_parser_exposes_all_events_orders_commands_and_write_flags(self) -> None:
        parser = build_parser()
        cases = [
            (["events-orders", "list"], events_orders.cmd_events_orders_list, False),
            (["events-orders", "get", "--event-id", "event-1", "--order-number", "1001"], events_orders.cmd_events_orders_get, False),
            (["events-orders", "update", "--event-id", "event-1", "--order-number", "1001", "--order-json", "{}"], events_orders.cmd_events_orders_update, True),
            (["events-orders", "bulk-update", "--event-id", "event-1", "--orders-json", "{}"], events_orders.cmd_events_orders_bulk_update, True),
            (["events-orders", "confirm", "--event-id", "event-1", "--request-json", "{}"], events_orders.cmd_events_orders_confirm, True),
            (["events-orders", "get-summary"], events_orders.cmd_events_orders_get_summary, False),
            (["events-orders", "get-checkout-options"], events_orders.cmd_events_orders_get_checkout_options, False),
            (["events-orders", "list-available-tickets"], events_orders.cmd_events_orders_list_available_tickets, False),
            (["events-orders", "query-available-tickets"], events_orders.cmd_events_orders_query_available_tickets, False),
            (["events-orders", "create-reservation", "--reservation-json", "{}"], events_orders.cmd_events_orders_create_reservation, True),
            (["events-orders", "cancel-reservation", "--reservation-id", "reservation-1"], events_orders.cmd_events_orders_cancel_reservation, True),
            (["events-orders", "checkout", "--checkout-json", "{}"], events_orders.cmd_events_orders_checkout, True),
            (["events-orders", "update-checkout", "--order-number", "1001", "--checkout-json", "{}"], events_orders.cmd_events_orders_update_checkout, True),
            (["events-orders", "get-invoice", "--reservation-id", "reservation-1"], events_orders.cmd_events_orders_get_invoice, False),
        ]
        for argv, func, writable in cases:
            with self.subTest(argv=argv):
                args = parser.parse_args(argv)
                self.assertIs(args.func, func)
                self.assertEqual(args.write_capable, writable)

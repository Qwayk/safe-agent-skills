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
from wix_safe_agent_cli.commands import payment_links
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = (action, payload)


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestPaymentLinksCommands(unittest.TestCase):
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
            "command_str": "wix-safe-agent-cli payment-links",
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

    def test_parser_recognizes_payment_links_commands(self) -> None:
        parser = build_parser()
        cases = [
            ["payment-links", "create", "--payment-link-json", '{"title":"Deposit","type":"ECOM"}'],
            ["payment-links", "get", "--payment-link-id", "pl-1"],
            ["payment-links", "delete", "--payment-link-id", "pl-1"],
            ["payment-links", "query", "--query-json", "{}"],
            ["payment-links", "search", "--search-json", "{}"],
            ["payment-links", "activate", "--payment-link-id", "pl-1"],
            ["payment-links", "deactivate", "--payment-link-id", "pl-1"],
            ["payment-links", "initiate-payment", "--payment-link-id", "pl-1"],
            ["payment-links", "send", "--payment-link-id", "pl-1", "--send-json", '{"recipients":[]}'],
            ["payment-links", "set-note", "--payment-link-id", "pl-1", "--note-json", '{"note":{"text":"VIP"}}'],
            [
                "payment-links",
                "update-extended-fields",
                "--payment-link-id",
                "pl-1",
                "--extended-fields-json",
                '{"extendedFields":{"namespaces":{}}}',
            ],
            ["payment-links", "bulk-update-tags", "--tags-json", '{"paymentLinkIds":["pl-1"]}'],
            ["payment-links", "bulk-update-tags-by-filter", "--tags-json", '{"filter":{},"assignTags":["vip"]}'],
        ]
        for argv in cases:
            with self.subTest(argv=argv):
                args = parser.parse_args(argv)
                self.assertTrue(callable(args.func))

    @patch("wix_safe_agent_cli.commands.payment_links.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.payment_links.HttpClient")
    def test_reads_use_official_paths(self, mock_client, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"paymentLinks": []})

        cases = [
            (
                payment_links.cmd_payment_links_get,
                SimpleNamespace(payment_link_id="pl-1"),
                "GET",
                "/payment-links/v1/payment-links/pl-1",
                None,
            ),
            (
                payment_links.cmd_payment_links_query,
                SimpleNamespace(query_json='{"filter":{"status":"ACTIVE"}}'),
                "POST",
                "/payment-links/v1/payment-links/query",
                {"filter": {"status": "ACTIVE"}},
            ),
            (
                payment_links.cmd_payment_links_search,
                SimpleNamespace(search_json='{"search":{"expression":"deposit"}}'),
                "POST",
                "/payment-links/v1/payment-links/search",
                {"search": {"expression": "deposit"}},
            ),
        ]
        for func, args, http_method, path, body in cases:
            with self.subTest(path=path):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = func(args, self._ctx())
                payload = json.loads(buf.getvalue())
                self.assertEqual(rc, 0)
                self.assertEqual(payload["request"]["method"], http_method)
                self.assertEqual(payload["request"]["path"], path)
                if body is None:
                    self.assertNotIn("body", payload["request"])
                else:
                    self.assertEqual(payload["request"]["body"], body)

        self.assertEqual(mock_auth.call_args.kwargs["command_family"], "payment-links")

    @patch("wix_safe_agent_cli.commands.payment_links.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.payment_links.HttpClient")
    def test_writes_emit_reviewed_plans_on_official_paths(self, mock_client, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        cases = [
            (
                payment_links.cmd_payment_links_create,
                SimpleNamespace(payment_link_json='{"title":"Deposit","type":"ECOM"}'),
                "paymentLinks.createPaymentLink",
                "POST",
                "/payment-links/v1/payment-links",
                True,
            ),
            (
                payment_links.cmd_payment_links_delete,
                SimpleNamespace(payment_link_id="pl-1"),
                "paymentLinks.deletePaymentLink",
                "DELETE",
                "/payment-links/v1/payment-links/pl-1",
                True,
            ),
            (
                payment_links.cmd_payment_links_activate,
                SimpleNamespace(payment_link_id="pl-1"),
                "paymentLinks.activatePaymentLink",
                "POST",
                "/payment-links/v1/payment-links/pl-1/activate",
                True,
            ),
            (
                payment_links.cmd_payment_links_deactivate,
                SimpleNamespace(payment_link_id="pl-1"),
                "paymentLinks.deactivatePaymentLink",
                "POST",
                "/payment-links/v1/payment-links/pl-1/deactivate",
                True,
            ),
            (
                payment_links.cmd_payment_links_initiate_payment,
                SimpleNamespace(payment_link_id="pl-1"),
                "paymentLinks.initiatePayment",
                "POST",
                "/payment-links/v1/payment-links/pl-1/initiate-payment",
                False,
            ),
            (
                payment_links.cmd_payment_links_send,
                SimpleNamespace(payment_link_id="pl-1", send_json='{"recipients":[]}'),
                "paymentLinks.sendPaymentLink",
                "POST",
                "/payment-links/v1/payment-links/pl-1/send",
                True,
            ),
            (
                payment_links.cmd_payment_links_set_note,
                SimpleNamespace(payment_link_id="pl-1", note_json='{"note":{"text":"VIP"}}'),
                "paymentLinks.setNote",
                "POST",
                "/payment-links/v1/payment-links/pl-1/set-note",
                False,
            ),
            (
                payment_links.cmd_payment_links_update_extended_fields,
                SimpleNamespace(payment_link_id="pl-1", extended_fields_json='{"extendedFields":{"namespaces":{}}}'),
                "paymentLinks.updateExtendedFields",
                "POST",
                "/payment-links/v1/payment-links/pl-1/update-extended-fields",
                False,
            ),
            (
                payment_links.cmd_payment_links_bulk_update_tags,
                SimpleNamespace(tags_json='{"paymentLinkIds":["pl-1"],"assignTags":["vip"]}'),
                "paymentLinks.bulkUpdatePaymentLinkTags",
                "POST",
                "/payment-links/v1/payment-links/bulk-update-tags",
                False,
            ),
            (
                payment_links.cmd_payment_links_bulk_update_tags_by_filter,
                SimpleNamespace(tags_json='{"filter":{},"assignTags":["vip"]}'),
                "paymentLinks.bulkUpdatePaymentLinkTagsByFilter",
                "POST",
                "/payment-links/v1/bulk/payment-links/update-tags-by-filter",
                True,
            ),
        ]
        for func, args, method_name, http_method, path, requires_ack in cases:
            with self.subTest(method_name=method_name):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = func(args, self._ctx())
                payload = json.loads(buf.getvalue())
                self.assertEqual(rc, 0)
                self.assertTrue(payload["dry_run"])
                self.assertEqual(payload["plan"]["method"], method_name)
                self.assertEqual(payload["plan"]["request"]["method"], http_method)
                self.assertEqual(payload["plan"]["request"]["path"], path)
                if requires_ack:
                    self.assertIn("apply also requires --ack-irreversible", payload["plan"]["preconditions"])
                else:
                    self.assertNotIn("apply also requires --ack-irreversible", payload["plan"]["preconditions"])

        mock_client.return_value.request.assert_not_called()

    @patch("wix_safe_agent_cli.commands.payment_links.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.payment_links.HttpClient")
    def test_apply_requires_matching_plan_and_calls_provider(self, mock_client, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"paymentLink": {"id": "pl-1", "status": "ACTIVE"}})
        with tempfile.TemporaryDirectory() as tmp:
            plan_path = Path(tmp) / "plan.json"
            selector = {"paymentLinkId": "pl-1"}
            plan = {
                "method": "paymentLinks.setNote",
                "baseline": {"env_fingerprint": "https://www.wixapis.com", "selector": selector},
                "proposed_changes": [{"operation": "set-payment-link-note"}],
            }
            plan_path.write_text(json.dumps(plan), encoding="utf-8")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = payment_links.cmd_payment_links_set_note(
                    SimpleNamespace(payment_link_id="pl-1", note_json='{"note":{"text":"VIP"}}'),
                    self._ctx(apply=True, yes=True, plan_in=str(plan_path)),
                )

        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertFalse(payload["dry_run"])
        self.assertEqual(payload["receipt"]["request"]["method"], "POST")
        self.assertEqual(payload["receipt"]["request"]["path"], "/payment-links/v1/payment-links/pl-1/set-note")
        mock_client.return_value.request.assert_called_once()

    @patch("wix_safe_agent_cli.commands.payment_links.HttpClient")
    def test_create_rejects_empty_payment_link_before_request(self, mock_client) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = payment_links.cmd_payment_links_create(SimpleNamespace(payment_link_json="{}"), self._ctx())
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 1)
        self.assertEqual(payload["error_type"], "ValidationError")
        mock_client.return_value.request.assert_not_called()

    @patch("wix_safe_agent_cli.commands.payment_links.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.payment_links.HttpClient")
    def test_send_apply_refuses_without_ack_irreversible(self, mock_client, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        with tempfile.TemporaryDirectory() as tmp:
            plan_path = Path(tmp) / "plan.json"
            plan = {
                "method": "paymentLinks.sendPaymentLink",
                "baseline": {"env_fingerprint": "https://www.wixapis.com", "selector": {"paymentLinkId": "pl-1"}},
            }
            plan_path.write_text(json.dumps(plan), encoding="utf-8")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = payment_links.cmd_payment_links_send(
                    SimpleNamespace(payment_link_id="pl-1", send_json='{"recipients":[]}'),
                    self._ctx(apply=True, yes=True, plan_in=str(plan_path), ack_irreversible=False),
                )

        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertIn("apply also requires --ack-irreversible", payload["plan"]["preconditions"])
        mock_client.return_value.request.assert_not_called()

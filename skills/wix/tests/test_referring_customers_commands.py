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
from wix_safe_agent_cli.commands import referring_customers
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = (action, payload)


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestReferringCustomersCommands(unittest.TestCase):
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
            "command_str": "wix-safe-agent-cli referring-customers",
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

    def test_parser_recognizes_referring_customers_read_commands(self) -> None:
        parser = build_parser()
        cases = [
            ["referring-customers", "get", "--referring-customer-id", "ref-customer-123"],
            ["referring-customers", "query", "--query-json", '{"query":{"filter":{"contactId":{"$eq":"contact-1"}}}}'],
            ["referring-customers", "get-by-referral-code", "--referral-code", "GxpxwAoMqxH8"],
            ["referring-customers", "generate-for-contact", "--contact-id", "contact-1"],
            ["referring-customers", "delete", "--referring-customer-id", "ref-customer-123", "--revision", "7"],
        ]
        for argv in cases:
            with self.subTest(argv=argv):
                args = parser.parse_args(argv)
                self.assertTrue(callable(args.func))
                self.assertEqual(args.write_capable, argv[1] in {"generate-for-contact", "delete"})

    @patch("wix_safe_agent_cli.commands.referring_customers.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.referring_customers.HttpClient")
    def test_get_uses_official_path(self, mock_client, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"referringCustomer": {"id": "ref-customer-123"}})

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = referring_customers.cmd_referring_customers_get(
                SimpleNamespace(referring_customer_id="ref-customer-123"),
                self._ctx(),
            )
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertEqual(payload["request"]["method"], "GET")
        self.assertEqual(payload["request"]["path"], "/referral-customers/v1/referring-customers/ref-customer-123")
        self.assertEqual(mock_auth.call_args.kwargs["command_family"], "referring-customers")
        mock_client.return_value.request.assert_called_once()

    @patch("wix_safe_agent_cli.commands.referring_customers.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.referring_customers.HttpClient")
    def test_query_uses_official_path_and_body(self, mock_client, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"referringCustomers": []})

        query_json = '{"query":{"filter":{"contactId":{"$eq":"contact-1"}},"sort":[{"fieldName":"createdDate","order":"DESC"}]}}'
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = referring_customers.cmd_referring_customers_query(SimpleNamespace(query_json=query_json), self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertEqual(payload["request"]["method"], "POST")
        self.assertEqual(payload["request"]["path"], "/referral-customers/v1/referring-customers/query")
        self.assertEqual(payload["request"]["body"]["query"]["filter"]["contactId"]["$eq"], "contact-1")
        request_kwargs = mock_client.return_value.request.call_args.kwargs
        self.assertEqual(request_kwargs["json_body"]["query"]["sort"][0]["fieldName"], "createdDate")

    @patch("wix_safe_agent_cli.commands.referring_customers.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.referring_customers.HttpClient")
    def test_get_by_referral_code_uses_official_path(self, mock_client, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"referringCustomer": {"referralCode": "GxpxwAoMqxH8"}})

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = referring_customers.cmd_referring_customers_get_by_referral_code(
                SimpleNamespace(referral_code="GxpxwAoMqxH8"),
                self._ctx(),
            )
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertEqual(payload["request"]["method"], "GET")
        self.assertEqual(payload["request"]["path"], "/referral-customers/v1/referring-customers/code/GxpxwAoMqxH8")

    @patch("wix_safe_agent_cli.commands.referring_customers.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.referring_customers.HttpClient")
    def test_query_requires_query_object_before_http(self, mock_client, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = referring_customers.cmd_referring_customers_query(SimpleNamespace(query_json='{"filter":{}}'), self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertEqual(payload["error_type"], "ValidationError")
        self.assertIn("query", payload["error"])
        mock_client.return_value.request.assert_not_called()

    @patch("wix_safe_agent_cli.commands.referring_customers.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.referring_customers.HttpClient")
    def test_generate_for_contact_is_plan_first_and_apply_uses_matching_plan(self, mock_client, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"referringCustomer": {"contactId": "contact-1"}})

        dry_buf = io.StringIO()
        with redirect_stdout(dry_buf):
            dry_rc = referring_customers.cmd_referring_customers_generate_for_contact(
                SimpleNamespace(contact_id="contact-1"),
                self._ctx(),
            )

        with tempfile.TemporaryDirectory() as tmp:
            plan_path = Path(tmp) / "plan.json"
            plan = {
                "method": "referringCustomers.generateReferringCustomerForContact",
                "baseline": {
                    "env_fingerprint": "https://www.wixapis.com",
                    "selector": {"kind": "referring-customers", "operation": "generate-for-contact"},
                },
                "proposed_changes": [{"operation": "generate-for-contact"}],
            }
            plan_path.write_text(json.dumps(plan), encoding="utf-8")

            apply_buf = io.StringIO()
            with redirect_stdout(apply_buf):
                apply_rc = referring_customers.cmd_referring_customers_generate_for_contact(
                    SimpleNamespace(contact_id="contact-1"),
                    self._ctx(apply=True, yes=True, plan_in=str(plan_path)),
                )

        dry = json.loads(dry_buf.getvalue())
        applied = json.loads(apply_buf.getvalue())
        self.assertEqual(dry_rc, 0)
        self.assertTrue(dry["dry_run"])
        self.assertEqual(dry["plan"]["request"]["method"], "POST")
        self.assertEqual(dry["plan"]["request"]["path"], "/referral-customers/v1/referring-customers")
        self.assertEqual(dry["plan"]["request"]["body"], {"contactId": "contact-1"})
        self.assertEqual(apply_rc, 0)
        self.assertFalse(applied["dry_run"])
        request_kwargs = mock_client.return_value.request.call_args.kwargs
        self.assertEqual(request_kwargs["method"], "POST")
        self.assertEqual(request_kwargs["json_body"], {"contactId": "contact-1"})

    @patch("wix_safe_agent_cli.commands.referring_customers.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.referring_customers.HttpClient")
    def test_delete_requires_ack_and_sends_revision_query_param(self, mock_client, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({})

        dry_buf = io.StringIO()
        with redirect_stdout(dry_buf):
            dry_rc = referring_customers.cmd_referring_customers_delete(
                SimpleNamespace(referring_customer_id="ref-customer-123", revision="7"),
                self._ctx(),
            )

        no_ack_buf = io.StringIO()
        with redirect_stdout(no_ack_buf):
            no_ack_rc = referring_customers.cmd_referring_customers_delete(
                SimpleNamespace(referring_customer_id="ref-customer-123", revision="7"),
                self._ctx(apply=True, yes=True, plan_in="/tmp/no-plan.json"),
            )
        mock_client.return_value.request.assert_not_called()

        with tempfile.TemporaryDirectory() as tmp:
            plan_path = Path(tmp) / "plan.json"
            plan = {
                "method": "referringCustomers.deleteReferringCustomer",
                "baseline": {
                    "env_fingerprint": "https://www.wixapis.com",
                    "selector": {"kind": "referring-customers", "operation": "delete"},
                },
                "proposed_changes": [{"operation": "delete"}],
            }
            plan_path.write_text(json.dumps(plan), encoding="utf-8")

            apply_buf = io.StringIO()
            with redirect_stdout(apply_buf):
                apply_rc = referring_customers.cmd_referring_customers_delete(
                    SimpleNamespace(referring_customer_id="ref-customer-123", revision="7"),
                    self._ctx(apply=True, yes=True, ack_irreversible=True, plan_in=str(plan_path)),
                )

        dry = json.loads(dry_buf.getvalue())
        no_ack = json.loads(no_ack_buf.getvalue())
        applied = json.loads(apply_buf.getvalue())
        self.assertEqual(dry_rc, 0)
        self.assertTrue(dry["dry_run"])
        self.assertIn("apply also requires --ack-irreversible", dry["plan"]["preconditions"])
        self.assertEqual(dry["plan"]["request"]["params"], {"revision": "7"})
        self.assertEqual(no_ack_rc, 0)
        self.assertTrue(no_ack["dry_run"])
        self.assertEqual(no_ack["plan"]["method"], "referringCustomers.deleteReferringCustomer")
        self.assertEqual(apply_rc, 0)
        self.assertFalse(applied["dry_run"])
        request_kwargs = mock_client.return_value.request.call_args.kwargs
        self.assertEqual(request_kwargs["method"], "DELETE")
        self.assertEqual(request_kwargs["params"], {"revision": "7"})

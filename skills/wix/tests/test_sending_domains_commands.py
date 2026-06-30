from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import sending_domains
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = (action, payload)


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestSendingDomainsCommands(unittest.TestCase):
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
            "command_str": "wix-safe-agent-cli sending-domains",
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

    def _write_plan(self, plan: dict) -> str:
        handle = tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json")
        json.dump(plan, handle)
        handle.close()
        return handle.name

    def test_parser_recognizes_sending_domains_subcommands(self) -> None:
        parser = build_parser()

        get_args = parser.parse_args(["sending-domains", "get", "--sending-domain-id", "domain-1"])
        self.assertEqual(get_args.sending_domains_cmd, "get")
        self.assertFalse(get_args.write_capable)

        query_args = parser.parse_args(["sending-domains", "query", "--domain", "example.com"])
        self.assertEqual(query_args.sending_domains_cmd, "query")
        self.assertFalse(query_args.write_capable)

        authenticate_args = parser.parse_args(["sending-domains", "authenticate", "--sending-domain-id", "domain-1"])
        self.assertEqual(authenticate_args.sending_domains_cmd, "authenticate")
        self.assertTrue(authenticate_args.write_capable)

    @patch("wix_safe_agent_cli.commands.sending_domains.HttpClient")
    def test_query_builds_expected_request(self, mock_client) -> None:
        mock_client.return_value.request.return_value = _DummyResponse(
            {"sendingDomains": [{"id": "domain-1", "domain": "example.com", "status": "NOT_AUTHENTICATED"}]}
        )
        args = SimpleNamespace(domain="example.com", sending_domain_id=None, query_json=None)

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = sending_domains.cmd_sending_domains_query(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["request"]["path"], "/sending-domains/v1/sending-domains/query")
        self.assertEqual(payload["request"]["body"]["query"]["filter"]["domain"], "example.com")

    def test_query_requires_filter(self) -> None:
        args = SimpleNamespace(domain=None, sending_domain_id=None, query_json=None)

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = sending_domains.cmd_sending_domains_query(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertEqual(payload["error_type"], "ValidationError")
        self.assertIn("Provide --domain", payload["error"])

    @patch("wix_safe_agent_cli.commands.sending_domains.HttpClient")
    def test_authenticate_dry_run_builds_plan(self, mock_client) -> None:
        mock_client.return_value.request.return_value = _DummyResponse(
            {"sendingDomain": {"id": "domain-1", "domain": "example.com", "status": "NOT_AUTHENTICATED"}}
        )
        args = SimpleNamespace(sending_domain_id="domain-1")

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = sending_domains.cmd_sending_domains_authenticate(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["method"], "sending-domains.authenticate")

    @patch("wix_safe_agent_cli.commands.sending_domains.HttpClient")
    def test_authenticate_apply_requires_reviewed_plan(self, mock_client) -> None:
        mock_client.return_value.request.return_value = _DummyResponse(
            {"sendingDomain": {"id": "domain-1", "domain": "example.com", "status": "NOT_AUTHENTICATED"}}
        )
        args = SimpleNamespace(sending_domain_id="domain-1")

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = sending_domains.cmd_sending_domains_authenticate(args, self._ctx(apply=True, yes=True))
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertIn("--plan-out", payload["reasons"][0])
        self.assertEqual(mock_client.return_value.request.call_count, 1)

    @patch("wix_safe_agent_cli.commands.sending_domains.HttpClient")
    def test_authenticate_refuses_when_status_not_ready(self, mock_client) -> None:
        mock_client.return_value.request.return_value = _DummyResponse(
            {"sendingDomain": {"id": "domain-1", "domain": "example.com", "status": "INITIALIZING"}}
        )
        args = SimpleNamespace(sending_domain_id="domain-1")

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = sending_domains.cmd_sending_domains_authenticate(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertIn("NOT_AUTHENTICATED", payload["reasons"][0])

    def test_authenticate_live_apply_verifies_authenticated_status(self) -> None:
        args = SimpleNamespace(sending_domain_id="domain-1")
        plan = {
            "method": "sending-domains.authenticate",
            "baseline": {
                "env_fingerprint": "https://www.wixapis.com",
                "selector": {
                    "kind": "wix-sending-domain",
                    "operation": "authenticate",
                    "sending_domain_id": "domain-1",
                },
                "before_state": {
                    "sendingDomain": {"id": "domain-1", "domain": "example.com", "status": "NOT_AUTHENTICATED"}
                },
            },
            "proposed_changes": [{"operation": "authenticate", "sendingDomainId": "domain-1"}],
        }
        plan_path = self._write_plan(plan)
        before = {"id": "domain-1", "domain": "example.com", "status": "NOT_AUTHENTICATED"}
        after = {"id": "domain-1", "domain": "example.com", "status": "AUTHENTICATED"}

        with patch.object(sending_domains, "_get_sending_domain", side_effect=[before, before, after]), patch.object(
            sending_domains, "_request_json", return_value={"sendingDomain": after}
        ) as mock_request:
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = sending_domains.cmd_sending_domains_authenticate(
                    args,
                    self._ctx(apply=True, yes=True, plan_in=plan_path),
                )
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertFalse(payload["dry_run"])
        self.assertEqual(payload["receipt"]["verification"]["after"]["status"], "AUTHENTICATED")
        self.assertEqual(mock_request.call_count, 1)

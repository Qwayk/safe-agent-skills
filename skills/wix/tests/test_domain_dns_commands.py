from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import domain_dns
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def __init__(self) -> None:
        self.writes: list[tuple[str, dict]] = []

    def write(self, action: str, payload: dict) -> None:
        self.writes.append((action, payload))


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestDomainDnsCommands(unittest.TestCase):
    def _ctx(self, *, cfg_override: dict | None = None, **overrides) -> dict:
        cfg = SimpleNamespace(
            base_url="https://www.wixapis.com",
            timeout_s=30.0,
            access_token=None,
            api_key="acct-api-key",
            account_id="acct-001",
            app_id=None,
            app_secret=None,
            instance_id=None,
            has_official_app_auth=False,
        )
        if cfg_override:
            for key, value in cfg_override.items():
                setattr(cfg, key, value)

        ctx = {
            "cfg": cfg,
            "env_file": "/tmp/.env",
            "tool": "wix-safe-agent-cli",
            "tool_version": "0.0.0",
            "command_str": "wix-safe-agent-cli domain-dns get-zone",
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

    def test_parser_recognizes_domain_dns_get_zone(self) -> None:
        parser = build_parser()
        parsed = parser.parse_args(["domain-dns", "get-zone", "--domain-name", "store.example.com"])

        self.assertEqual(parsed.domain_dns_cmd, "get-zone")
        self.assertFalse(parsed.write_capable)
        self.assertEqual(parsed.domain_name, "store.example.com")
        self.assertEqual(parsed.func.__name__, "cmd_domain_dns_get_zone")

    def test_parser_recognizes_domain_dns_preview_zone(self) -> None:
        parser = build_parser()
        parsed = parser.parse_args(["domain-dns", "preview-zone", "--domain-name", "example.com"])

        self.assertEqual(parsed.domain_dns_cmd, "preview-zone")
        self.assertFalse(parsed.write_capable)
        self.assertEqual(parsed.domain_name, "example.com")
        self.assertEqual(parsed.func.__name__, "cmd_domain_dns_preview_zone")

    def test_parser_recognizes_domain_dns_create_zone(self) -> None:
        parser = build_parser()
        parsed = parser.parse_args(
            [
                "domain-dns",
                "create-zone",
                "--dns-zone-json",
                '{"domainName":"example.com","records":[{"type":"NS","hostName":"example.com","values":["ns1.example.com"]},{"type":"SOA","hostName":"example.com","values":["ns1.example.com hostmaster.example.com 1 7200 3600 1209600 3600"]}]}',
            ]
        )

        self.assertEqual(parsed.domain_dns_cmd, "create-zone")
        self.assertTrue(parsed.write_capable)
        self.assertEqual(parsed.func.__name__, "cmd_domain_dns_create_zone")

    def test_parser_recognizes_domain_dns_update_zone(self) -> None:
        parser = build_parser()
        parsed = parser.parse_args(
            [
                "domain-dns",
                "update-zone",
                "--domain-name",
                "example.com",
                "--additions-json",
                '[{"type":"TXT","hostName":"example.com","values":["v=spf1 include:_spf.example.com ~all"]}]',
                "--dnssec-enabled",
                "true",
            ]
        )

        self.assertEqual(parsed.domain_dns_cmd, "update-zone")
        self.assertTrue(parsed.write_capable)
        self.assertEqual(parsed.func.__name__, "cmd_domain_dns_update_zone")

    def test_parser_recognizes_domain_dns_delete_zone(self) -> None:
        parser = build_parser()
        parsed = parser.parse_args(
            ["--apply", "--yes", "--ack-irreversible", "domain-dns", "delete-zone", "--domain-name", "example.com"]
        )

        self.assertEqual(parsed.domain_dns_cmd, "delete-zone")
        self.assertTrue(parsed.write_capable)
        self.assertTrue(parsed.apply)
        self.assertTrue(parsed.yes)
        self.assertTrue(parsed.ack_irreversible)
        self.assertEqual(parsed.func.__name__, "cmd_domain_dns_delete_zone")

    @patch("wix_safe_agent_cli.commands.domain_dns.HttpClient")
    def test_domain_dns_get_zone_builds_expected_request_and_headers(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"dnsZone": {"domainName": "store.example.com"}})
        args = SimpleNamespace(domain_name="store.example.com")
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = domain_dns.cmd_domain_dns_get_zone(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["method"], "domain-dns.get-zone")
        self.assertEqual(payload["auth_mode"], "account_api_key")
        self.assertEqual(payload["request"], {"method": "GET", "path": "/domains/v1/dns-zones/store.example.com"})

        call = mock_client.return_value.request.call_args
        headers = call.kwargs["headers"]
        self.assertEqual(headers["Authorization"], "acct-api-key")
        self.assertEqual(headers["wix-account-id"], "acct-001")
        self.assertNotIn("Content-Type", headers)

    @patch("wix_safe_agent_cli.commands.domain_dns.HttpClient")
    def test_domain_dns_preview_zone_builds_expected_request_and_headers(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse(
            {"dnsZone": {"domainName": "store.example.com", "records": [], "id": "store.example.com"}}
        )
        args = SimpleNamespace(domain_name="store.example.com")
        ctx = self._ctx(command_str="wix-safe-agent-cli domain-dns preview-zone")

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = domain_dns.cmd_domain_dns_preview_zone(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["method"], "domain-dns.preview-zone")
        self.assertEqual(
            payload["request"],
            {"method": "GET", "path": "/domains/v1/dns-zones/store.example.com/preview"},
        )

    @patch("wix_safe_agent_cli.commands.domain_dns.HttpClient")
    def test_domain_dns_create_zone_dry_run_builds_plan(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.side_effect = [
            RuntimeError("HTTP 404 for https://www.wixapis.com/domains/v1/dns-zones/example.com"),
        ]
        args = SimpleNamespace(
            dns_zone_json=json.dumps(
                {
                    "domainName": "example.com",
                    "records": [
                        {"type": "NS", "hostName": "example.com", "values": ["ns1.example.com"]},
                        {
                            "type": "SOA",
                            "hostName": "example.com",
                            "values": ["ns1.example.com hostmaster.example.com 1 7200 3600 1209600 3600"],
                        },
                    ],
                }
            )
        )
        ctx = self._ctx(command_str="wix-safe-agent-cli domain-dns create-zone")

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = domain_dns.cmd_domain_dns_create_zone(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["method"], "domain-dns.create-zone")
        self.assertEqual(payload["plan"]["request"]["method"], "POST")
        self.assertEqual(payload["plan"]["request"]["path"], "/domains/v1/dns-zones")
        self.assertIsNone(payload["plan"]["baseline"]["before_state"])

    @patch("wix_safe_agent_cli.commands.domain_dns.HttpClient")
    def test_domain_dns_update_zone_apply_without_plan_in_is_refused_before_http(self, mock_client: unittest.mock.MagicMock) -> None:
        _ = mock_client
        args = SimpleNamespace(
            domain_name="example.com",
            additions_json='[{"type":"TXT","hostName":"example.com","values":["v=spf1 ~all"]}]',
            deletions_json=None,
            dnssec_enabled=None,
        )
        ctx = self._ctx(
            command_str="wix-safe-agent-cli domain-dns update-zone",
            apply=True,
            yes=True,
            enforce_reviewed_plan=True,
        )

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = domain_dns.cmd_domain_dns_update_zone(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertEqual(payload["error_type"], "SafetyError")
        self.assertIn("reviewed saved plan", payload["error"])
        mock_client.return_value.request.assert_not_called()

    @patch("wix_safe_agent_cli.commands.domain_dns.HttpClient")
    def test_domain_dns_update_zone_apply_with_deletions_requires_ack(self, mock_client: unittest.mock.MagicMock) -> None:
        _ = mock_client
        args = SimpleNamespace(
            domain_name="example.com",
            additions_json=None,
            deletions_json='[{"type":"TXT","hostName":"example.com","values":["old-value"]}]',
            dnssec_enabled=None,
        )
        ctx = self._ctx(
            command_str="wix-safe-agent-cli domain-dns update-zone",
            apply=True,
            yes=True,
            enforce_reviewed_plan=True,
            plan_in="/tmp/reviewed-plan.json",
        )

        with patch("wix_safe_agent_cli.commands.domain_dns.read_json_file") as mock_read_plan:
            mock_read_plan.return_value = {
                "method": "domain-dns.update-zone",
                "baseline": {
                    "env_fingerprint": "https://www.wixapis.com",
                    "selector": {
                        "kind": "wix-domain-dns-zone",
                        "operation": "update",
                        "domain_name": "example.com",
                    },
                    "before_state": {"dnsZone": {"domainName": "example.com", "records": []}},
                },
            }
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = domain_dns.cmd_domain_dns_update_zone(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertEqual(payload["error_type"], "SafetyError")
        self.assertIn("--ack-irreversible", payload["error"])
        mock_client.return_value.request.assert_not_called()

    @patch("wix_safe_agent_cli.commands.domain_dns.HttpClient")
    def test_domain_dns_delete_zone_apply_verifies_404_after_delete(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.side_effect = [
            _DummyResponse({"dnsZone": {"domainName": "example.com", "records": []}}),
            _DummyResponse({"dnsZone": {"domainName": "example.com", "records": []}}),
            _DummyResponse({}),
            RuntimeError("HTTP 404 for https://www.wixapis.com/domains/v1/dns-zones/example.com"),
        ]
        args = SimpleNamespace(domain_name="example.com")
        ctx = self._ctx(
            command_str="wix-safe-agent-cli domain-dns delete-zone",
            apply=True,
            yes=True,
            ack_irreversible=True,
            plan_in="/tmp/reviewed-plan.json",
        )

        with patch("wix_safe_agent_cli.commands.domain_dns.read_json_file") as mock_read_plan:
            mock_read_plan.return_value = {
                "method": "domain-dns.delete-zone",
                "baseline": {
                    "env_fingerprint": "https://www.wixapis.com",
                    "selector": {
                        "kind": "wix-domain-dns-zone",
                        "operation": "delete",
                        "domain_name": "example.com",
                    },
                    "before_state": {"dnsZone": {"domainName": "example.com", "records": []}},
                },
                "proposed_changes": [{"operation": "delete-zone", "domainName": "example.com"}],
            }
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = domain_dns.cmd_domain_dns_delete_zone(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertFalse(payload["dry_run"])
        self.assertTrue(payload["verification"]["ok"])
        self.assertTrue(payload["verification"]["removed"])

    @patch("wix_safe_agent_cli.commands.domain_dns.HttpClient")
    def test_domain_dns_get_zone_rejects_domain_without_tld(self, mock_client: unittest.mock.MagicMock) -> None:
        _ = mock_client
        args = SimpleNamespace(domain_name="example")
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = domain_dns.cmd_domain_dns_get_zone(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertEqual(payload["error_type"], "ValidationError")
        self.assertIn("hostname with a TLD", payload["error"])

    @patch("wix_safe_agent_cli.commands.domain_dns.HttpClient")
    def test_domain_dns_create_zone_rejects_unknown_record_type(self, mock_client: unittest.mock.MagicMock) -> None:
        _ = mock_client
        args = SimpleNamespace(
            dns_zone_json=json.dumps(
                {
                    "domainName": "example.com",
                    "records": [
                        {"type": "UNKNOWN", "hostName": "example.com", "values": ["bad"]},
                        {
                            "type": "SOA",
                            "hostName": "example.com",
                            "values": ["ns1.example.com hostmaster.example.com 1 7200 3600 1209600 3600"],
                        },
                    ],
                }
            )
        )
        ctx = self._ctx(command_str="wix-safe-agent-cli domain-dns create-zone")

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = domain_dns.cmd_domain_dns_create_zone(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertEqual(payload["error_type"], "ValidationError")
        self.assertIn("must be one of", payload["error"])

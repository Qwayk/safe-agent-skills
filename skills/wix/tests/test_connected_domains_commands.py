from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import connected_domains
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


class TestConnectedDomainsCommands(unittest.TestCase):
    def _ctx(self, *, cfg_override: dict | None = None, **overrides) -> dict:
        cfg = SimpleNamespace(
            base_url="https://www.wixapis.com",
            timeout_s=30.0,
            access_token="token-legacy",
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
            "command_str": "wix-safe-agent-cli connected-domains list",
            "apply": False,
            "yes": False,
            "verbose": False,
            "out": Output(mode="json"),
            "audit": _DummyAudit(),
            "plan_in": None,
            "plan_out": None,
            "receipt_out": None,
            "ack_irreversible": False,
        }
        ctx.update(overrides)
        return ctx

    def test_parser_recognizes_connected_domains_list(self) -> None:
        parser = build_parser()
        parsed = parser.parse_args(["connected-domains", "list"])

        self.assertEqual(parsed.connected_domains_cmd, "list")
        self.assertFalse(parsed.write_capable)
        self.assertEqual(parsed.func.__name__, "cmd_connected_domains_list")

    def test_parser_recognizes_connected_domains_get(self) -> None:
        parser = build_parser()
        parsed = parser.parse_args(
            ["connected-domains", "get", "--connected-domain-id", "store.example.com"]
        )
        self.assertEqual(parsed.connected_domains_cmd, "get")
        self.assertFalse(parsed.write_capable)
        self.assertEqual(parsed.connected_domain_id, "store.example.com")
        self.assertEqual(parsed.func.__name__, "cmd_connected_domains_get")

    def test_parser_recognizes_connected_domains_get_setup_info(self) -> None:
        parser = build_parser()
        parsed = parser.parse_args(
            ["connected-domains", "get-setup-info", "--connected-domain-id", "store.example.com"]
        )
        self.assertEqual(parsed.connected_domains_cmd, "get-setup-info")
        self.assertFalse(parsed.write_capable)
        self.assertEqual(parsed.connected_domain_id, "store.example.com")
        self.assertEqual(parsed.func.__name__, "cmd_connected_domains_get_setup_info")

    def test_parser_recognizes_connected_domains_create(self) -> None:
        parser = build_parser()
        parsed = parser.parse_args(
            [
                "connected-domains",
                "create",
                "--domain",
                "store.example.com",
                "--site-id",
                "site-123",
                "--connection-type",
                "POINTING",
                "--assignment-type",
                "PRIMARY",
                "--suppress-notifications",
            ]
        )

        self.assertEqual(parsed.connected_domains_cmd, "create")
        self.assertTrue(parsed.write_capable)
        self.assertEqual(parsed.domain, "store.example.com")
        self.assertEqual(parsed.site_id, "site-123")
        self.assertEqual(parsed.connection_type, "POINTING")
        self.assertEqual(parsed.assignment_type, "PRIMARY")
        self.assertTrue(parsed.suppress_notifications)
        self.assertEqual(parsed.func.__name__, "cmd_connected_domains_create")

    def test_parser_recognizes_connected_domains_delete(self) -> None:
        parser = build_parser()
        parsed = parser.parse_args(
            ["--apply", "--yes", "--ack-irreversible", "connected-domains", "delete", "--connected-domain-id", "store.example.com"]
        )

        self.assertEqual(parsed.connected_domains_cmd, "delete")
        self.assertTrue(parsed.write_capable)
        self.assertTrue(parsed.apply)
        self.assertTrue(parsed.yes)
        self.assertTrue(parsed.ack_irreversible)
        self.assertEqual(parsed.connected_domain_id, "store.example.com")
        self.assertEqual(parsed.func.__name__, "cmd_connected_domains_delete")

    @patch("wix_safe_agent_cli.commands.connected_domains.HttpClient")
    def test_connected_domains_list_request_shape_and_headers(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"items": []})
        args = SimpleNamespace(cursor="cursor-1", limit=25)
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = connected_domains.cmd_connected_domains_list(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["method"], "connected_domains.list")
        self.assertEqual(payload["request"]["method"], "GET")
        self.assertEqual(payload["request"]["path"], "/domains/v1/connected-domains")
        self.assertEqual(payload["request"]["params"], {"cursor": "cursor-1", "limit": 25})

        http_call = mock_client.return_value.request.call_args
        self.assertTrue(str(http_call.kwargs["url"]).endswith("/domains/v1/connected-domains"))
        headers = http_call.kwargs["headers"]
        self.assertEqual(headers["Authorization"], "acct-api-key")
        self.assertEqual(headers["wix-account-id"], "acct-001")
        self.assertNotIn("Content-Type", headers)

    @patch("wix_safe_agent_cli.commands.connected_domains.HttpClient")
    def test_connected_domains_create_dry_run_builds_plan_and_preflights_site(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.side_effect = [
            _DummyResponse({"sites": [{"id": "site-123"}], "pagingMetadata": {"count": 1}}),
            RuntimeError("HTTP 404 for https://www.wixapis.com/domains/v1/connected-domains/store.example.com"),
        ]
        args = SimpleNamespace(
            domain="store.example.com",
            site_id="site-123",
            connection_type="NAMESERVERS",
            assignment_type="REDIRECT",
            suppress_notifications=True,
        )
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = connected_domains.cmd_connected_domains_create(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["method"], "connected_domains.create")
        self.assertEqual(payload["plan"]["request"]["method"], "POST")
        self.assertEqual(payload["plan"]["request"]["path"], "/domains/v1/connected-domains")
        self.assertEqual(
            payload["plan"]["request"]["body"],
            {
                "connectedDomain": {
                    "domain": "store.example.com",
                    "connectionType": "NAMESERVERS",
                    "siteInfo": {"assignmentType": "REDIRECT"},
                    "suppressNotifications": True,
                }
            },
        )
        self.assertEqual(payload["plan"]["baseline"]["site_snapshot"], {"id": "site-123"})
        call_args_list = mock_client.return_value.request.call_args_list
        self.assertEqual(len(call_args_list), 2)
        self.assertEqual(call_args_list[0].kwargs["method"], "POST")
        self.assertTrue(str(call_args_list[0].kwargs["url"]).endswith("/site-list/v2/sites/query"))
        self.assertEqual(call_args_list[1].kwargs["method"], "GET")
        self.assertTrue(str(call_args_list[1].kwargs["url"]).endswith("/domains/v1/connected-domains/store.example.com"))

    @patch("wix_safe_agent_cli.commands.connected_domains.HttpClient")
    def test_connected_domains_create_apply_reads_back_created_domain(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.side_effect = [
            _DummyResponse({"sites": [{"id": "site-123"}], "pagingMetadata": {"count": 1}}),
            RuntimeError("HTTP 404 for https://www.wixapis.com/domains/v1/connected-domains/store.example.com"),
            _DummyResponse(
                {
                    "connectedDomain": {
                        "id": "store.example.com",
                        "domain": "store.example.com",
                        "connectionType": "POINTING",
                        "siteInfo": {"id": "site-123", "assignmentType": "PRIMARY"},
                    }
                }
            ),
            _DummyResponse(
                {
                    "connectedDomain": {
                        "id": "store.example.com",
                        "domain": "store.example.com",
                        "connectionType": "POINTING",
                        "siteInfo": {"id": "site-123", "assignmentType": "PRIMARY"},
                    }
                }
            ),
        ]
        args = SimpleNamespace(
            domain="store.example.com",
            site_id="site-123",
            connection_type="POINTING",
            assignment_type="PRIMARY",
            suppress_notifications=False,
        )
        ctx = self._ctx(apply=True, yes=True)

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = connected_domains.cmd_connected_domains_create(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertFalse(payload["dry_run"])
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["method"], "connected_domains.create")
        self.assertTrue(payload["receipt"]["verification"]["ok"])
        self.assertEqual(payload["receipt"]["verification"]["path"], "/domains/v1/connected-domains/store.example.com")
        self.assertEqual(payload["receipt"]["verification"]["response"]["connectedDomain"]["siteInfo"]["id"], "site-123")
        call_args_list = mock_client.return_value.request.call_args_list
        self.assertEqual(len(call_args_list), 4)
        write_call = call_args_list[2]
        self.assertEqual(write_call.kwargs["method"], "POST")
        self.assertTrue(str(write_call.kwargs["url"]).endswith("/domains/v1/connected-domains"))
        headers = write_call.kwargs["headers"]
        self.assertEqual(headers["Authorization"], "acct-api-key")
        self.assertEqual(headers["wix-account-id"], "acct-001")
        self.assertEqual(headers["wix-site-id"], "site-123")
        self.assertEqual(write_call.kwargs["json_body"]["connectedDomain"]["domain"], "store.example.com")
        self.assertEqual(write_call.kwargs["json_body"]["connectedDomain"]["siteInfo"], {"assignmentType": "PRIMARY"})

    @patch("wix_safe_agent_cli.commands.connected_domains.HttpClient")
    def test_connected_domains_create_rejects_missing_site_id(self, mock_client: unittest.mock.MagicMock) -> None:
        _ = mock_client
        args = SimpleNamespace(domain="store.example.com", site_id="   ", connection_type=None, assignment_type=None, suppress_notifications=False)
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = connected_domains.cmd_connected_domains_create(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error_type"], "ValidationError")
        self.assertIn("Missing --site-id", payload["error"])

    @patch("wix_safe_agent_cli.commands.connected_domains.HttpClient")
    def test_connected_domains_delete_requires_ack_irreversible_for_apply(self, mock_client: unittest.mock.MagicMock) -> None:
        _ = mock_client
        args = SimpleNamespace(connected_domain_id="store.example.com")
        ctx = self._ctx(apply=True, yes=True)

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = connected_domains.cmd_connected_domains_delete(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertFalse(payload["dry_run"])
        self.assertIn("--ack-irreversible", payload["reasons"][0])

    @patch("wix_safe_agent_cli.commands.connected_domains.HttpClient")
    def test_connected_domains_delete_apply_verifies_404_after_delete(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.side_effect = [
            _DummyResponse(
                {
                    "connectedDomain": {
                        "id": "store.example.com",
                        "domain": "store.example.com",
                        "siteInfo": {"id": "site-123"},
                    }
                }
            ),
            _DummyResponse({}),
            RuntimeError("HTTP 404 for https://www.wixapis.com/domains/v1/connected-domains/store.example.com"),
        ]
        args = SimpleNamespace(connected_domain_id="store.example.com")
        ctx = self._ctx(apply=True, yes=True, ack_irreversible=True)

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = connected_domains.cmd_connected_domains_delete(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertFalse(payload["dry_run"])
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["receipt"]["verification"]["ok"], True)
        self.assertEqual(payload["receipt"]["verification"]["removed"], True)
        self.assertEqual(payload["receipt"]["verification"]["path"], "/domains/v1/connected-domains/store.example.com")
        call_args_list = mock_client.return_value.request.call_args_list
        self.assertEqual(len(call_args_list), 3)
        self.assertEqual(call_args_list[1].kwargs["method"], "DELETE")
        headers = call_args_list[1].kwargs["headers"]
        self.assertEqual(headers["Authorization"], "acct-api-key")
        self.assertEqual(headers["wix-account-id"], "acct-001")
        self.assertNotIn("wix-site-id", headers)

    @patch("wix_safe_agent_cli.commands.connected_domains.HttpClient")
    def test_connected_domains_get_request_shape_and_headers(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"id": "store.example.com"})
        args = SimpleNamespace(connected_domain_id="store.example.com")
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = connected_domains.cmd_connected_domains_get(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertEqual(payload["method"], "connected_domains.get")
        self.assertEqual(payload["auth_mode"], "account_api_key")
        self.assertEqual(payload["request"]["method"], "GET")
        self.assertEqual(payload["request"]["path"], "/domains/v1/connected-domains/store.example.com")
        http_call = mock_client.return_value.request.call_args
        self.assertTrue(str(http_call.kwargs["url"]).endswith("/domains/v1/connected-domains/store.example.com"))
        headers = http_call.kwargs["headers"]
        self.assertEqual(headers["Authorization"], "acct-api-key")
        self.assertEqual(headers["wix-account-id"], "acct-001")

    @patch("wix_safe_agent_cli.commands.connected_domains.HttpClient")
    def test_connected_domains_get_setup_info_request_shape_and_headers(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"dnsSettings": {"a": "1.2.3.4"}})
        args = SimpleNamespace(connected_domain_id="store.example.com")
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = connected_domains.cmd_connected_domains_get_setup_info(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertEqual(payload["method"], "connected_domains.get_setup_info")
        self.assertEqual(
            payload["request"]["path"],
            "/domains/v1/connected-domain-setup-info/store.example.com",
        )
        http_call = mock_client.return_value.request.call_args
        self.assertTrue(
            str(http_call.kwargs["url"]).endswith("/domains/v1/connected-domain-setup-info/store.example.com")
        )

    def test_connected_domains_list_rejects_limit_over_100(self) -> None:
        args = SimpleNamespace(cursor=None, limit=101)
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = connected_domains.cmd_connected_domains_list(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error_type"], "ValidationError")
        self.assertIn("between 1 and 100", payload["error"])

    def test_connected_domains_list_rejects_empty_cursor(self) -> None:
        args = SimpleNamespace(cursor="   ", limit=None)
        ctx = self._ctx()
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = connected_domains.cmd_connected_domains_list(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertFalse(payload["ok"])
        self.assertIn("cannot be empty", payload["error"])

    def test_connected_domains_get_rejects_missing_tld(self) -> None:
        args = SimpleNamespace(connected_domain_id="example")
        ctx = self._ctx()
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = connected_domains.cmd_connected_domains_get(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertFalse(payload["ok"])
        self.assertIn("must include a TLD", payload["error"])

    def test_connected_domains_get_rejects_leading_or_trailing_dot(self) -> None:
        args = SimpleNamespace(connected_domain_id=".example.com")
        ctx = self._ctx()
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = connected_domains.cmd_connected_domains_get(args, ctx)
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 1)
        self.assertFalse(payload["ok"])
        self.assertIn("must not start or end with a dot", payload["error"])

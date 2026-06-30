from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import cookie_consent_policy
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = (action, payload)


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestCookieConsentPolicyCommands(unittest.TestCase):
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
            "command_str": "wix-safe-agent-cli cookie-consent-policy",
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

    def test_parser_recognizes_cookie_consent_policy_subcommands(self) -> None:
        parser = build_parser()

        read_args = parser.parse_args(
            [
                "cookie-consent-policy",
                "get-cookie-banner-settings",
                "--language-code",
                "en",
            ]
        )
        self.assertEqual(read_args.cookie_consent_policy_cmd, "get-cookie-banner-settings")
        self.assertFalse(read_args.write_capable)

        write_args = parser.parse_args(
            [
                "cookie-consent-policy",
                "update-cookie-banner-settings",
                "--settings-json",
                '{"settings":{"enabled":true}}',
            ]
        )
        self.assertEqual(write_args.cookie_consent_policy_cmd, "update-cookie-banner-settings")
        self.assertTrue(write_args.write_capable)

        delete_args = parser.parse_args(
            [
                "cookie-consent-policy",
                "delete-consent-config",
                "--consent-config-id",
                "config-1",
            ]
        )
        self.assertEqual(delete_args.cookie_consent_policy_cmd, "delete-consent-config")
        self.assertTrue(delete_args.write_capable)

    @patch("wix_safe_agent_cli.commands.cookie_consent_policy.HttpClient")
    def test_get_cookie_banner_settings_builds_expected_request(self, mock_client) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"settings": {"enabled": True}})
        args = SimpleNamespace(language_code="en")

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cookie_consent_policy.cmd_cookie_consent_policy_get_cookie_banner_settings(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["method"], "cookie-consent-policy.get-cookie-banner-settings")
        self.assertEqual(payload["request"]["params"], {"languageCode": "en"})
        call = mock_client.return_value.request.call_args
        self.assertEqual(call.kwargs["method"], "GET")
        self.assertEqual(call.kwargs["url"], "https://www.wixapis.com/cookie-consent/v1/cookie-banner-settings")
        self.assertEqual(call.kwargs["headers"], {"Authorization": "site-app-token"})

    @patch("wix_safe_agent_cli.commands.cookie_consent_policy.HttpClient")
    def test_update_cookie_banner_settings_dry_run_builds_plan(self, mock_client) -> None:
        args = SimpleNamespace(settings_json='{"settings":{"enabled":true}}')

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cookie_consent_policy.cmd_cookie_consent_policy_update_cookie_banner_settings(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["method"], "cookie-consent-policy.update-cookie-banner-settings")
        self.assertEqual(payload["plan"]["request"]["path"], "/cookie-consent/v1/cookie-banner-settings/update")
        self.assertEqual(mock_client.return_value.request.call_count, 0)

    @patch("wix_safe_agent_cli.commands.cookie_consent_policy.HttpClient")
    def test_update_consent_config_requires_revision(self, mock_client) -> None:
        args = SimpleNamespace(consent_config_json='{"consentConfig":{"id":"config-1"}}')

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cookie_consent_policy.cmd_cookie_consent_policy_update_consent_config(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertEqual(payload["error_type"], "ValidationError")
        self.assertIn("revision", payload["error"])
        self.assertEqual(mock_client.return_value.request.call_count, 0)

    def test_delete_consent_config_apply_requires_ack_irreversible(self) -> None:
        args = SimpleNamespace(consent_config_id="config-1")

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cookie_consent_policy.cmd_cookie_consent_policy_delete_consent_config(
                args,
                self._ctx(apply=True, yes=True),
            )
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertIn("apply also requires --ack-irreversible", payload["plan"]["preconditions"])

    @patch("wix_safe_agent_cli.commands.cookie_consent_policy.HttpClient")
    def test_delete_consent_config_apply_uses_reviewed_plan(self, mock_client) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({})
        args = SimpleNamespace(consent_config_id="config-1")
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            cookie_consent_policy.cmd_cookie_consent_policy_delete_consent_config(args, ctx)
        plan = json.loads(buf.getvalue())["plan"]
        plan_path = self._write_plan(plan)

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cookie_consent_policy.cmd_cookie_consent_policy_delete_consent_config(
                args,
                self._ctx(apply=True, yes=True, ack_irreversible=True, plan_in=plan_path),
            )
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertFalse(payload["dry_run"])
        self.assertEqual(payload["receipt"]["method"], "cookie-consent-policy.delete-consent-config")
        call = mock_client.return_value.request.call_args
        self.assertEqual(call.kwargs["method"], "DELETE")
        self.assertEqual(call.kwargs["url"], "https://www.wixapis.com/consent/consent-config/v1/consent-configs/config-1")

    @patch("wix_safe_agent_cli.commands.cookie_consent_policy.HttpClient")
    def test_bulk_update_tags_by_filter_requires_ack_irreversible(self, mock_client) -> None:
        args = SimpleNamespace(tags_json='{"filter":{},"assignTags":["analytics"]}')

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cookie_consent_policy.cmd_cookie_consent_policy_bulk_update_consent_config_tags_by_filter(
                args,
                self._ctx(apply=True, yes=True),
            )
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertIn("apply also requires --ack-irreversible", payload["plan"]["preconditions"])
        self.assertEqual(mock_client.return_value.request.call_count, 0)

    @patch("wix_safe_agent_cli.commands.cookie_consent_policy.HttpClient")
    def test_list_apps_and_storage_builds_expected_request(self, mock_client) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"apps": []})
        args = SimpleNamespace(query_json="{}")

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cookie_consent_policy.cmd_cookie_consent_policy_list_apps_and_storage(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["request"]["path"], "/consent/consent-config/v1/site-apps-and-storage")
        call = mock_client.return_value.request.call_args
        self.assertEqual(call.kwargs["method"], "POST")
        self.assertEqual(call.kwargs["json_body"], {})

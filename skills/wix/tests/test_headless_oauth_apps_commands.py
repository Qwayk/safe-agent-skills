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
from wix_safe_agent_cli.commands import headless_oauth_apps
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = (action, payload)


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestHeadlessOAuthAppsCommands(unittest.TestCase):
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
            "command_str": "wix-safe-agent-cli headless-oauth-apps",
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

    def test_parser_recognizes_headless_oauth_apps_commands(self) -> None:
        parser = build_parser()
        cases = [
            ["headless-oauth-apps", "create", "--o-auth-app-json", '{"name":"Client App"}'],
            ["headless-oauth-apps", "get", "--o-auth-app-id", "app-1"],
            ["headless-oauth-apps", "update", "--o-auth-app-json", '{"id":"app-1","name":"Client App","mask":{"paths":["name"]}}'],
            ["headless-oauth-apps", "query", "--query-json", '{"query":{"paging":{"limit":10}}}'],
        ]
        for argv in cases:
            with self.subTest(argv=argv):
                args = parser.parse_args(argv)
                self.assertTrue(callable(args.func))

    @patch("wix_safe_agent_cli.commands.headless_oauth_apps.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.headless_oauth_apps.HttpClient")
    def test_get_uses_official_path(self, mock_client, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"oAuthApp": {"id": "app-1"}})

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = headless_oauth_apps.cmd_headless_oauth_apps_get(SimpleNamespace(o_auth_app_id="app-1"), self._ctx())

        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertEqual(payload["request"]["method"], "GET")
        self.assertEqual(payload["request"]["path"], "/oauth-app/v1/oauth-apps/app-1")
        self.assertEqual(mock_auth.call_args.kwargs["command_family"], "headless-oauth-apps")

    @patch("wix_safe_agent_cli.commands.headless_oauth_apps.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.headless_oauth_apps.HttpClient")
    def test_query_uses_official_path_as_read_helper(self, mock_client, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"oAuthApps": []})

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = headless_oauth_apps.cmd_headless_oauth_apps_query(SimpleNamespace(query_json='{"query":{}}'), self._ctx())

        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertEqual(payload["request"]["method"], "POST")
        self.assertEqual(payload["request"]["path"], "/oauth-app/v1/oauth-apps/query")
        self.assertEqual(payload["request"]["body"], {"query": {}})

    @patch("wix_safe_agent_cli.commands.headless_oauth_apps.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.headless_oauth_apps.HttpClient")
    def test_create_emits_reviewed_plan_on_official_path(self, mock_client, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = headless_oauth_apps.cmd_headless_oauth_apps_create(
                SimpleNamespace(o_auth_app_json='{"name":"Client App","allowedRedirectUris":["https://example.com/callback"]}'),
                self._ctx(),
            )

        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["method"], "headlessOauthApps.createOAuthApp")
        self.assertEqual(payload["plan"]["request"]["method"], "POST")
        self.assertEqual(payload["plan"]["request"]["path"], "/oauth-app/v1/oauth-apps")
        self.assertIn("external-client-auth-access", payload["plan"]["risk_reasons"])
        mock_client.return_value.request.assert_not_called()

    @patch("wix_safe_agent_cli.commands.headless_oauth_apps.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.headless_oauth_apps.HttpClient")
    def test_update_emits_reviewed_plan_and_requires_mask(self, mock_client, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = headless_oauth_apps.cmd_headless_oauth_apps_update(
                SimpleNamespace(o_auth_app_json='{"oAuthApp":{"id":"app-1","name":"Client App"},"mask":{"paths":["name"]}}'),
                self._ctx(),
            )

        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["request"]["method"], "PATCH")
        self.assertEqual(payload["plan"]["request"]["path"], "/oauth-app/v1/oauth-apps/app-1")
        self.assertEqual(payload["plan"]["selector"]["oAuthAppId"], "app-1")
        mock_client.return_value.request.assert_not_called()

    @patch("wix_safe_agent_cli.commands.headless_oauth_apps.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.headless_oauth_apps.HttpClient")
    def test_update_apply_requires_matching_plan_and_calls_provider(self, mock_client, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"oAuthApp": {"id": "app-1"}})

        with tempfile.TemporaryDirectory() as tmp:
            plan_path = Path(tmp) / "plan.json"
            plan = {
                "method": "headlessOauthApps.updateOAuthApp",
                "baseline": {
                    "env_fingerprint": "https://www.wixapis.com",
                    "selector": {"oAuthAppId": "app-1", "mask": {"paths": ["name"]}},
                },
                "proposed_changes": [{"operation": "update-headless-oauth-app"}],
            }
            plan_path.write_text(json.dumps(plan), encoding="utf-8")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = headless_oauth_apps.cmd_headless_oauth_apps_update(
                    SimpleNamespace(o_auth_app_json='{"oAuthApp":{"id":"app-1","name":"Client App"},"mask":{"paths":["name"]}}'),
                    self._ctx(apply=True, yes=True, plan_in=str(plan_path)),
                )

        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertFalse(payload["dry_run"])
        self.assertEqual(payload["receipt"]["request"]["path"], "/oauth-app/v1/oauth-apps/app-1")
        mock_client.return_value.request.assert_called_once()

    @patch("wix_safe_agent_cli.commands.headless_oauth_apps.HttpClient")
    def test_update_rejects_missing_mask_before_request(self, mock_client) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = headless_oauth_apps.cmd_headless_oauth_apps_update(
                SimpleNamespace(o_auth_app_json='{"id":"app-1","name":"Client App"}'),
                self._ctx(),
            )

        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 1)
        self.assertEqual(payload["error_type"], "ValidationError")
        mock_client.return_value.request.assert_not_called()

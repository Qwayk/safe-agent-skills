from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.commands import data_sharing
from wix_safe_agent_cli.cli import build_parser
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


class TestDataSharingCommands(unittest.TestCase):
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
            "command_str": "wix-safe-agent-cli data-sharing",
            "apply": False,
            "yes": False,
            "plan_in": None,
            "plan_out": None,
            "receipt_out": None,
            "ack_irreversible": False,
        }
        ctx.update(overrides)
        return ctx

    @patch("wix_safe_agent_cli.commands.data_sharing.HttpClient")
    def test_list_policies_builds_filter_request(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"dataSharingPolicies": []})
        args = SimpleNamespace(data_collection_ids_json='["Products","Posts"]')
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = data_sharing.cmd_data_sharing_list_policies(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["method"], "data-sharing.list-policies")
        self.assertEqual(payload["request"]["method"], "GET")
        self.assertEqual(payload["request"]["path"], "/data/v1/data-collection-sharing/policies")
        self.assertEqual(payload["request"]["params"]["dataCollectionIds"], ["Products", "Posts"])

    @patch("wix_safe_agent_cli.commands.data_sharing.HttpClient")
    def test_get_policy_builds_expected_request(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"dataSharingPolicy": {"id": "p1"}})
        args = SimpleNamespace(policy_id="p1")
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = data_sharing.cmd_data_sharing_get_policy(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertEqual(payload["request"]["method"], "GET")
        self.assertEqual(payload["request"]["path"], "/data/v1/data-collection-sharing/policies/p1")

    @patch("wix_safe_agent_cli.commands.data_sharing.HttpClient")
    def test_create_policy_dry_run_wraps_policy_and_emits_plan(self, mock_client: unittest.mock.MagicMock) -> None:
        args = SimpleNamespace(policy_json='{"dataCollectionId":"Products","dataItemsFilter":{"status":"ACTIVE"}}')
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = data_sharing.cmd_data_sharing_create_policy(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["method"], "data-sharing.create-policy")
        self.assertEqual(payload["plan"]["request"]["method"], "POST")
        self.assertEqual(payload["plan"]["request"]["path"], "/data/v1/data-collection-sharing/policies")
        self.assertEqual(payload["plan"]["request"]["body"]["dataSharingPolicy"]["dataCollectionId"], "Products")
        mock_client.assert_not_called()

    @patch("wix_safe_agent_cli.commands.data_sharing.HttpClient")
    def test_update_policy_dry_run_forces_path_policy_id_into_body(self, mock_client: unittest.mock.MagicMock) -> None:
        args = SimpleNamespace(policy_id="p1", policy_json='{"dataSharingPolicy":{"dataItemsFilter":{"type":"A"}}}')
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = data_sharing.cmd_data_sharing_update_policy(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["request"]["path"], "/data/v1/data-collection-sharing/policies/p1")
        self.assertEqual(payload["plan"]["request"]["body"]["dataSharingPolicy"]["id"], "p1")

    @patch("wix_safe_agent_cli.commands.data_sharing.HttpClient")
    def test_delete_policy_missing_irreversible_ack_stays_dry_run(self, mock_client: unittest.mock.MagicMock) -> None:
        args = SimpleNamespace(policy_id="p1")
        ctx = self._ctx(apply=True, yes=True, plan_in="/tmp/plan.json", ack_irreversible=False)

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = data_sharing.cmd_data_sharing_delete_policy(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["method"], "data-sharing.delete-policy")
        self.assertIn("target-sites-lose-access", payload["plan"]["risk_reasons"])
        mock_client.assert_not_called()

    @patch("wix_safe_agent_cli.commands.data_sharing.HttpClient")
    def test_disconnect_dry_run_uses_official_endpoint_and_irreversible_risk(self, mock_client: unittest.mock.MagicMock) -> None:
        args = SimpleNamespace(connection_json='{"namespace":"sharedProducts","dataSharingPolicyId":"p1"}')
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = data_sharing.cmd_data_sharing_disconnect(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(
            payload["plan"]["request"]["path"],
            "/data/v1/data-collection-sharing/disconnect-from-shared-collection",
        )
        self.assertIn("cms-data-sharing-disconnect", payload["plan"]["risk_reasons"])

    def test_parser_exposes_data_sharing_commands(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "data-sharing",
                "connect",
                "--connection-json",
                '{"namespace":"sharedProducts","dataSharingPolicyId":"p1"}',
            ]
        )

        self.assertIs(args.func, data_sharing.cmd_data_sharing_connect)
        self.assertTrue(args.write_capable)

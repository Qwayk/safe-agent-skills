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
from wix_safe_agent_cli.commands import suppliers_hub_marketplace_provider_submissions
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = action, payload


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestSuppliersHubMarketplaceProviderSubmissionsCommands(unittest.TestCase):
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
            "command_str": "wix-safe-agent-cli suppliers-hub-marketplace-provider-submissions",
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

    @patch("wix_safe_agent_cli.commands.suppliers_hub_marketplace_provider_submissions.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.suppliers_hub_marketplace_provider_submissions.HttpClient")
    def test_submit_generated_mockups_dry_run_is_plan_first(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "Bearer token-abc"}, "mode": "access_token"}
        args = SimpleNamespace(
            mockups_json='{"mockups":[{"providerProductId":"001","imageType":"CUSTOM","status":"COMPLETED","mockupUrl":"https://static.wixstatic.com/media/mockup.jpg"}]}'
        )

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = suppliers_hub_marketplace_provider_submissions.cmd_suppliers_hub_marketplace_provider_submissions_submit_generated_mockups(
                args,
                self._ctx(),
            )
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["method"], "suppliers-hub-marketplace-provider-submissions.submit-generated-mockups")
        self.assertEqual(payload["plan"]["request"]["method"], "POST")
        self.assertEqual(payload["plan"]["request"]["path"], "/suppliershub/v2/submit-generated-mockups")
        self.assertEqual(payload["plan"]["proposed_changes"][0]["provider_product_id"], "001")
        mock_client.return_value.request.assert_not_called()

    def test_submit_generated_mockups_validates_mockup_payload(self) -> None:
        args = SimpleNamespace(mockups_json='{"mockups":[{"providerProductId":"001","imageType":"CUSTOM","status":"COMPLETED"}]}')

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = suppliers_hub_marketplace_provider_submissions.cmd_suppliers_hub_marketplace_provider_submissions_submit_generated_mockups(
                args,
                self._ctx(),
            )
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertIn("mockupUrl", payload["error"])

    @patch("wix_safe_agent_cli.commands.suppliers_hub_marketplace_provider_submissions.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.suppliers_hub_marketplace_provider_submissions.HttpClient")
    def test_reviewed_apply_posts_and_writes_receipt(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "Bearer token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"results": [], "bulkActionMetadata": {"totalSuccesses": 1}})
        body = {
            "mockups": [
                {
                    "providerProductId": "001",
                    "imageType": "CUSTOM",
                    "status": "COMPLETED",
                    "mockupUrl": "https://static.wixstatic.com/media/mockup.jpg",
                }
            ]
        }
        plan = {
            "method": "suppliers-hub-marketplace-provider-submissions.submit-generated-mockups",
            "baseline": {
                "env_fingerprint": "https://www.wixapis.com",
                "selector": {
                    "kind": "suppliers-hub-marketplace-provider-submissions",
                    "operation": "submit-generated-mockups",
                    "mockups": [{"providerProductId": "001", "imageType": "CUSTOM", "status": "COMPLETED"}],
                },
            },
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            plan_path = Path(tmpdir) / "plan.json"
            receipt_path = Path(tmpdir) / "receipt.json"
            plan_path.write_text(json.dumps(plan), encoding="utf-8")
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = suppliers_hub_marketplace_provider_submissions.cmd_suppliers_hub_marketplace_provider_submissions_submit_generated_mockups(
                    SimpleNamespace(mockups_json=json.dumps(body)),
                    self._ctx(apply=True, yes=True, plan_in=str(plan_path), receipt_out=str(receipt_path)),
                )
            self.assertTrue(receipt_path.exists())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertFalse(payload["dry_run"])
        self.assertEqual(payload["request"]["path"], "/suppliershub/v2/submit-generated-mockups")
        self.assertEqual(payload["receipt"]["verification"]["type"], "provider-response")
        self.assertEqual(mock_client.return_value.request.call_count, 1)

    def test_parser_includes_suppliers_hub_marketplace_provider_submissions_command(self) -> None:
        parser = build_parser()
        parsed = parser.parse_args(
            [
                "suppliers-hub-marketplace-provider-submissions",
                "submit-generated-mockups",
                "--mockups-json",
                '{"mockups":[{"providerProductId":"001","imageType":"CUSTOM","status":"FAILED"}]}',
            ]
        )
        self.assertTrue(parsed.write_capable)
        self.assertIs(
            parsed.func,
            suppliers_hub_marketplace_provider_submissions.cmd_suppliers_hub_marketplace_provider_submissions_submit_generated_mockups,
        )

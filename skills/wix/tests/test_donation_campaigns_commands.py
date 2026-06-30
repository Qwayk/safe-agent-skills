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
from wix_safe_agent_cli.commands import donation_campaigns
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = (action, payload)


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestDonationCampaignsCommands(unittest.TestCase):
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
            "command_str": "wix-safe-agent-cli donation-campaigns",
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

    @staticmethod
    def _campaign(*, revision: str = "1", tags: list[str] | None = None) -> dict:
        return {
            "id": "campaign-1",
            "revision": revision,
            "name": "Summer Fund",
            "customAmountEnabled": True,
            "frequencies": ["ONE_TIME"],
            "tags": tags or ["summer"],
        }

    def _write_plan(self, plan: dict) -> str:
        handle = tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json")
        json.dump(plan, handle)
        handle.close()
        return handle.name

    def test_parser_recognizes_donation_campaign_subcommands(self) -> None:
        parser = build_parser()

        get_args = parser.parse_args(["donation-campaigns", "get", "--donation-campaign-id", "campaign-1"])
        self.assertEqual(get_args.donation_campaigns_cmd, "get")
        self.assertFalse(get_args.write_capable)

        metrics_args = parser.parse_args(
            ["donation-campaigns", "get-metrics", "--donation-campaign-id", "campaign-1"]
        )
        self.assertEqual(metrics_args.donation_campaigns_cmd, "get-metrics")
        self.assertFalse(metrics_args.write_capable)

        query_args = parser.parse_args(["donation-campaigns", "query"])
        self.assertEqual(query_args.donation_campaigns_cmd, "query")
        self.assertFalse(query_args.write_capable)

        create_args = parser.parse_args(
            [
                "donation-campaigns",
                "create",
                "--donation-campaign-json",
                '{"name":"Summer Fund","customAmountEnabled":true,"frequencies":["ONE_TIME"]}',
            ]
        )
        self.assertEqual(create_args.donation_campaigns_cmd, "create")
        self.assertTrue(create_args.write_capable)

        update_args = parser.parse_args(
            [
                "donation-campaigns",
                "update",
                "--donation-campaign-id",
                "campaign-1",
                "--donation-campaign-json",
                '{"revision":"1","customAmountEnabled":true,"frequencies":["ONE_TIME"]}',
            ]
        )
        self.assertEqual(update_args.donation_campaigns_cmd, "update")
        self.assertTrue(update_args.write_capable)

        bulk_update_args = parser.parse_args(
            [
                "donation-campaigns",
                "bulk-update",
                "--donation-campaigns-json",
                '[{"id":"campaign-1","revision":"1","customAmountEnabled":true,"frequencies":["ONE_TIME"]}]',
            ]
        )
        self.assertEqual(bulk_update_args.donation_campaigns_cmd, "bulk-update")
        self.assertTrue(bulk_update_args.write_capable)

        tags_args = parser.parse_args(
            [
                "donation-campaigns",
                "bulk-update-tags",
                "--update-tags-json",
                '{"ids":["campaign-1"],"assignTags":["vip"]}',
            ]
        )
        self.assertEqual(tags_args.donation_campaigns_cmd, "bulk-update-tags")
        self.assertTrue(tags_args.write_capable)

        tags_filter_args = parser.parse_args(
            [
                "donation-campaigns",
                "bulk-update-tags-by-filter",
                "--update-tags-json",
                '{"filter":{"archived":{"$eq":false}},"assignTags":["vip"]}',
            ]
        )
        self.assertEqual(tags_filter_args.donation_campaigns_cmd, "bulk-update-tags-by-filter")
        self.assertTrue(tags_filter_args.write_capable)

    @patch("wix_safe_agent_cli.commands.donation_campaigns.HttpClient")
    def test_get_builds_expected_request(self, mock_client) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"donationCampaign": self._campaign()})
        args = SimpleNamespace(donation_campaign_id="campaign-1")

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = donation_campaigns.cmd_donation_campaigns_get(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["request"]["path"], "/donation-campaigns/v2/donation-campaigns/campaign-1")

    @patch("wix_safe_agent_cli.commands.donation_campaigns.HttpClient")
    def test_get_metrics_builds_expected_request(self, mock_client) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"metrics": {"donationCount": 3}})
        args = SimpleNamespace(donation_campaign_id="campaign-1")

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = donation_campaigns.cmd_donation_campaigns_get_metrics(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["request"]["path"], "/donation-campaigns/v2/donation-campaigns/campaign-1/metrics")

    @patch("wix_safe_agent_cli.commands.donation_campaigns.HttpClient")
    def test_query_builds_expected_request(self, mock_client) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"donationCampaigns": []})
        args = SimpleNamespace(query_json='{"paging":{"limit":25}}')

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = donation_campaigns.cmd_donation_campaigns_query(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertEqual(payload["request"]["path"], "/donation-campaigns/v2/donation-campaigns/query")
        self.assertEqual(payload["request"]["body"], {"paging": {"limit": 25}})

    def test_create_dry_run_builds_plan(self) -> None:
        args = SimpleNamespace(
            donation_campaign_json='{"name":"Summer Fund","customAmountEnabled":true,"frequencies":["ONE_TIME"]}'
        )

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = donation_campaigns.cmd_donation_campaigns_create(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["method"], "donation-campaigns.create")

    @patch("wix_safe_agent_cli.commands.donation_campaigns.HttpClient")
    def test_create_apply_requires_reviewed_plan_before_write(self, mock_client) -> None:
        args = SimpleNamespace(
            donation_campaign_json='{"name":"Summer Fund","customAmountEnabled":true,"frequencies":["ONE_TIME"]}'
        )

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = donation_campaigns.cmd_donation_campaigns_create(args, self._ctx(apply=True, yes=True))
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertEqual(mock_client.return_value.request.call_count, 0)

    def test_update_dry_run_injects_id_into_body(self) -> None:
        args = SimpleNamespace(
            donation_campaign_id="campaign-1",
            donation_campaign_json='{"revision":"1","customAmountEnabled":true,"frequencies":["ONE_TIME"]}',
        )

        with patch("wix_safe_agent_cli.commands.donation_campaigns.HttpClient") as mock_client:
            mock_client.return_value.request.return_value = _DummyResponse({"donationCampaign": self._campaign()})
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = donation_campaigns.cmd_donation_campaigns_update(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["request"]["body"]["id"], "campaign-1")

    @patch("wix_safe_agent_cli.commands.donation_campaigns.HttpClient")
    def test_bulk_update_apply_requires_reviewed_plan_before_write(self, mock_client) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"donationCampaign": self._campaign()})
        args = SimpleNamespace(
            donation_campaigns_json='[{"id":"campaign-1","revision":"1","customAmountEnabled":true,"frequencies":["ONE_TIME"]}]'
        )

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = donation_campaigns.cmd_donation_campaigns_bulk_update(args, self._ctx(apply=True, yes=True))
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertEqual(mock_client.return_value.request.call_count, 1)

    @patch("wix_safe_agent_cli.commands.donation_campaigns.HttpClient")
    def test_bulk_update_tags_apply_requires_reviewed_plan_before_write(self, mock_client) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"donationCampaign": self._campaign()})
        args = SimpleNamespace(update_tags_json='{"ids":["campaign-1"],"assignTags":["vip"]}')

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = donation_campaigns.cmd_donation_campaigns_bulk_update_tags(args, self._ctx(apply=True, yes=True))
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertEqual(mock_client.return_value.request.call_count, 1)

    def test_bulk_update_tags_by_filter_rejects_empty_filter(self) -> None:
        args = SimpleNamespace(update_tags_json='{"filter":{},"assignTags":["vip"]}')

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = donation_campaigns.cmd_donation_campaigns_bulk_update_tags_by_filter(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertIn("non-empty filter object", payload["error"])

    @patch("wix_safe_agent_cli.commands.donation_campaigns.HttpClient")
    def test_bulk_update_tags_by_filter_apply_returns_job_id_receipt(self, mock_client) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"jobId": "job-1"})
        args = SimpleNamespace(update_tags_json='{"filter":{"archived":{"$eq":false}},"assignTags":["vip"]}')

        dry_buf = io.StringIO()
        with redirect_stdout(dry_buf):
            donation_campaigns.cmd_donation_campaigns_bulk_update_tags_by_filter(args, self._ctx())
        plan_path = self._write_plan(json.loads(dry_buf.getvalue())["plan"])
        try:
            apply_ctx = self._ctx(apply=True, yes=True, plan_in=plan_path)
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = donation_campaigns.cmd_donation_campaigns_bulk_update_tags_by_filter(args, apply_ctx)
            payload = json.loads(buf.getvalue())

            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["receipt"]["verification"]["job_id"], "job-1")
        finally:
            Path(plan_path).unlink()

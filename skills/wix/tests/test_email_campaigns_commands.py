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
from wix_safe_agent_cli.commands import email_campaigns
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = (action, payload)


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestEmailCampaignCommands(unittest.TestCase):
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
            "command_str": "wix-safe-agent-cli email-campaigns",
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
    def _current_campaign(*, distribution_status: str = "SCHEDULED") -> dict:
        return {
            "campaignId": "camp-1",
            "distributionStatus": distribution_status,
            "name": "Spring launch",
        }

    def test_parser_recognizes_email_campaign_subcommands(self) -> None:
        parser = build_parser()

        list_args = parser.parse_args(["email-campaigns", "list"])
        self.assertEqual(list_args.email_campaigns_cmd, "list")
        self.assertFalse(list_args.write_capable)

        get_args = parser.parse_args(["email-campaigns", "get", "--campaign-id", "camp-1"])
        self.assertEqual(get_args.email_campaigns_cmd, "get")
        self.assertFalse(get_args.write_capable)

        get_audience_args = parser.parse_args(["email-campaigns", "get-audience", "--campaign-id", "camp-1"])
        self.assertEqual(get_audience_args.email_campaigns_cmd, "get-audience")
        self.assertFalse(get_audience_args.write_capable)

        stats_args = parser.parse_args(
            ["email-campaigns", "list-statistics", "--campaign-ids-json", '["camp-1"]']
        )
        self.assertEqual(stats_args.email_campaigns_cmd, "list-statistics")
        self.assertFalse(stats_args.write_capable)

        recipients_args = parser.parse_args(
            ["email-campaigns", "list-recipients", "--campaign-id", "camp-1", "--activity", "OPENED"]
        )
        self.assertEqual(recipients_args.email_campaigns_cmd, "list-recipients")
        self.assertFalse(recipients_args.write_capable)

        pause_args = parser.parse_args(["email-campaigns", "pause-scheduling", "--campaign-id", "camp-1"])
        self.assertEqual(pause_args.email_campaigns_cmd, "pause-scheduling")
        self.assertTrue(pause_args.write_capable)

        reschedule_args = parser.parse_args(
            ["email-campaigns", "reschedule", "--campaign-id", "camp-1", "--send-at", "2026-07-01T12:00:00Z"]
        )
        self.assertEqual(reschedule_args.email_campaigns_cmd, "reschedule")
        self.assertTrue(reschedule_args.write_capable)

        send_test_args = parser.parse_args(
            [
                "email-campaigns",
                "send-test",
                "--campaign-id",
                "camp-1",
                "--send-test-json",
                '{"toEmailAddress":"owner@example.com"}',
            ]
        )
        self.assertEqual(send_test_args.email_campaigns_cmd, "send-test")
        self.assertTrue(send_test_args.write_capable)

        publish_args = parser.parse_args(
            [
                "email-campaigns",
                "publish",
                "--campaign-id",
                "camp-1",
                "--publish-json",
                '{"emailDistributionOptions":{"emailSubject":"Launch"}}',
            ]
        )
        self.assertEqual(publish_args.email_campaigns_cmd, "publish")
        self.assertTrue(publish_args.write_capable)

        reuse_args = parser.parse_args(["email-campaigns", "reuse", "--campaign-id", "camp-1"])
        self.assertEqual(reuse_args.email_campaigns_cmd, "reuse")
        self.assertTrue(reuse_args.write_capable)

        delete_args = parser.parse_args(["email-campaigns", "delete", "--campaign-id", "camp-1"])
        self.assertEqual(delete_args.email_campaigns_cmd, "delete")
        self.assertTrue(delete_args.write_capable)

        identify_args = parser.parse_args(
            ["email-campaigns", "identify-sender-address", "--email-address", "owner@example.com"]
        )
        self.assertEqual(identify_args.email_campaigns_cmd, "identify-sender-address")
        self.assertFalse(identify_args.write_capable)

        pause_args = parser.parse_args(["email-campaigns", "pause-scheduling", "--campaign-id", "camp-1"])
        self.assertEqual(pause_args.email_campaigns_cmd, "pause-scheduling")
        self.assertTrue(pause_args.write_capable)

        reschedule_args = parser.parse_args(
            ["email-campaigns", "reschedule", "--campaign-id", "camp-1", "--send-at", "2026-06-24T10:00:00Z"]
        )
        self.assertEqual(reschedule_args.email_campaigns_cmd, "reschedule")
        self.assertTrue(reschedule_args.write_capable)

        send_test_args = parser.parse_args(
            [
                "email-campaigns",
                "send-test",
                "--campaign-id",
                "camp-1",
                "--send-test-json",
                '{"toEmailAddress":"owner@example.com"}',
            ]
        )
        self.assertEqual(send_test_args.email_campaigns_cmd, "send-test")
        self.assertTrue(send_test_args.write_capable)

        validate_link_args = parser.parse_args(
            ["campaign-validation", "validate-link", "--url", "https://example.com"]
        )
        self.assertEqual(validate_link_args.campaign_validation_cmd, "validate-link")
        self.assertFalse(validate_link_args.write_capable)

        validate_html_args = parser.parse_args(
            ["campaign-validation", "validate-html-links", "--html", "<a href='https://example.com'>x</a>"]
        )
        self.assertEqual(validate_html_args.campaign_validation_cmd, "validate-html-links")
        self.assertFalse(validate_html_args.write_capable)

    @patch("wix_safe_agent_cli.commands.email_campaigns.HttpClient")
    def test_list_builds_expected_request(self, mock_client) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"campaigns": []})
        args = SimpleNamespace(
            include_statistics=True,
            statuses_json='["ACTIVE"]',
            visibility_statuses_json='["DRAFT"]',
            limit=25,
            offset=10,
        )

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = email_campaigns.cmd_email_campaigns_list(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["request"]["path"], "/email-marketing/v1/campaigns")
        self.assertEqual(payload["request"]["params"]["optionIncludeStatistics"], "true")
        self.assertEqual(payload["request"]["params"]["statuses"], ["ACTIVE"])
        self.assertEqual(payload["request"]["params"]["visibilityStatuses"], ["DRAFT"])
        self.assertEqual(payload["request"]["params"]["paging.limit"], 25)
        self.assertEqual(payload["request"]["params"]["paging.offset"], 10)

    @patch("wix_safe_agent_cli.commands.email_campaigns.HttpClient")
    def test_get_builds_expected_request(self, mock_client) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"campaign": {"campaignId": "camp-1"}})
        args = SimpleNamespace(campaign_id="camp-1", include_statistics=True)

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = email_campaigns.cmd_email_campaigns_get(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["request"]["path"], "/email-marketing/v1/campaigns/camp-1")
        self.assertEqual(payload["request"]["params"]["optionIncludeStatistics"], "true")

    @patch("wix_safe_agent_cli.commands.email_campaigns.HttpClient")
    def test_get_audience_builds_expected_request(self, mock_client) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"audience": []})
        args = SimpleNamespace(campaign_id="camp-1")

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = email_campaigns.cmd_email_campaigns_get_audience(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["method"], "email-campaigns.get-audience")
        self.assertEqual(payload["request"]["path"], "/email-marketing/v1/campaigns/camp-1/audience")
        self.assertIsNone(payload["request"]["body"])

    @patch("wix_safe_agent_cli.commands.email_campaigns.HttpClient")
    def test_list_statistics_builds_expected_request(self, mock_client) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"statistics": []})
        args = SimpleNamespace(campaign_ids_json='["camp-1","camp-2"]')

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = email_campaigns.cmd_email_campaigns_list_statistics(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["request"]["path"], "/email-marketing/v1/campaigns/statistics")
        self.assertEqual(payload["request"]["params"]["campaignIds"], ["camp-1", "camp-2"])

    def test_list_statistics_rejects_more_than_100_ids(self) -> None:
        too_many = json.dumps([f"camp-{index}" for index in range(101)])
        args = SimpleNamespace(campaign_ids_json=too_many)

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = email_campaigns.cmd_email_campaigns_list_statistics(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertFalse(payload["ok"])
        self.assertIn("at most 100", payload["error"])

    @patch("wix_safe_agent_cli.commands.email_campaigns.HttpClient")
    def test_list_recipients_builds_expected_request(self, mock_client) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"recipients": []})
        args = SimpleNamespace(campaign_id="camp-1", activity="OPENED", limit=40, cursor="next-1")

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = email_campaigns.cmd_email_campaigns_list_recipients(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(
            payload["request"]["path"],
            "/email-marketing/v1/campaigns/camp-1/statistics/recipients",
        )
        self.assertEqual(payload["request"]["params"]["activity"], "OPENED")
        self.assertEqual(payload["request"]["params"]["paging.limit"], 40)
        self.assertEqual(payload["request"]["params"]["paging.cursor"], "next-1")

    def test_pause_scheduling_apply_requires_reviewed_plan(self) -> None:
        args = SimpleNamespace(campaign_id="camp-1")

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = email_campaigns.cmd_email_campaigns_pause_scheduling(args, self._ctx(apply=True, yes=True))
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertEqual(payload["method"], "email-campaigns.pause-scheduling")

    def test_pause_scheduling_dry_run_builds_plan(self) -> None:
        args = SimpleNamespace(campaign_id="camp-1")
        current_campaign = self._current_campaign()

        with patch.object(email_campaigns, "_get_campaign", return_value=current_campaign):
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = email_campaigns.cmd_email_campaigns_pause_scheduling(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["method"], "email-campaigns.pause-scheduling")
        self.assertEqual(payload["plan"]["request"]["path"], "/email-marketing/v1/campaigns/camp-1/pause-scheduling")

    def test_reschedule_rejects_invalid_send_at(self) -> None:
        args = SimpleNamespace(campaign_id="camp-1", send_at="tomorrow maybe")

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = email_campaigns.cmd_email_campaigns_reschedule(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertFalse(payload["ok"])
        self.assertIn("RFC 3339", payload["error"])

    def test_reschedule_apply_requires_reviewed_plan(self) -> None:
        args = SimpleNamespace(campaign_id="camp-1", send_at="2026-07-01T12:00:00Z")

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = email_campaigns.cmd_email_campaigns_reschedule(args, self._ctx(apply=True, yes=True))
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertEqual(payload["method"], "email-campaigns.reschedule")

    def test_send_test_rejects_invalid_email(self) -> None:
        args = SimpleNamespace(campaign_id="camp-1", send_test_json='{"toEmailAddress":"not-an-email"}')

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = email_campaigns.cmd_email_campaigns_send_test(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertFalse(payload["ok"])
        self.assertIn("valid email address", payload["error"])

    def test_send_test_apply_requires_reviewed_plan(self) -> None:
        args = SimpleNamespace(campaign_id="camp-1", send_test_json='{"toEmailAddress":"owner@example.com"}')

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = email_campaigns.cmd_email_campaigns_send_test(args, self._ctx(apply=True, yes=True))
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertEqual(payload["method"], "email-campaigns.send-test")

    def test_publish_apply_without_plan_in_refuses_before_http(self) -> None:
        args = SimpleNamespace(
            campaign_id="camp-1",
            publish_json='{"emailDistributionOptions":{"emailSubject":"Launch"}}',
        )

        buf = io.StringIO()
        with patch("wix_safe_agent_cli.commands.email_campaigns.HttpClient") as mock_client:
            with redirect_stdout(buf):
                rc = email_campaigns.cmd_email_campaigns_publish(args, self._ctx(apply=True, yes=True))
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertEqual(payload["method"], "email-campaigns.publish")
        mock_client.assert_not_called()

    def test_reuse_apply_without_plan_in_refuses_before_http(self) -> None:
        args = SimpleNamespace(campaign_id="camp-1")

        buf = io.StringIO()
        with patch("wix_safe_agent_cli.commands.email_campaigns.HttpClient") as mock_client:
            with redirect_stdout(buf):
                rc = email_campaigns.cmd_email_campaigns_reuse(args, self._ctx(apply=True, yes=True))
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertEqual(payload["method"], "email-campaigns.reuse")
        mock_client.assert_not_called()

    def test_delete_apply_without_plan_in_refuses_before_http(self) -> None:
        args = SimpleNamespace(campaign_id="camp-1")

        buf = io.StringIO()
        with patch("wix_safe_agent_cli.commands.email_campaigns.HttpClient") as mock_client:
            with redirect_stdout(buf):
                rc = email_campaigns.cmd_email_campaigns_delete(args, self._ctx(apply=True, yes=True))
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertEqual(payload["method"], "email-campaigns.delete")
        mock_client.assert_not_called()

    @patch("wix_safe_agent_cli.commands.email_campaigns.HttpClient")
    def test_identify_sender_address_builds_expected_request(self, mock_client) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"emailAddress": "owner@example.com"})
        args = SimpleNamespace(email_address="owner@example.com")

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = email_campaigns.cmd_email_campaigns_identify_sender_address(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["request"]["path"], "/email-marketing/v1/identify-sender-address")
        self.assertEqual(payload["request"]["body"]["emailAddress"], "owner@example.com")

    @patch("wix_safe_agent_cli.commands.email_campaigns.HttpClient")
    def test_pause_scheduling_builds_reviewed_plan_and_verifies_apply(self, mock_client) -> None:
        mock_client.return_value.request.side_effect = [
            _DummyResponse({}),
        ]
        args = SimpleNamespace(campaign_id="camp-1")
        scheduled = self._current_campaign(distribution_status="SCHEDULED")
        paused = self._current_campaign(distribution_status="PAUSED")

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as plan_handle:
            plan_path = plan_handle.name
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as receipt_handle:
            receipt_path = receipt_handle.name

        try:
            dry_ctx = self._ctx(plan_out=plan_path)
            dry_buf = io.StringIO()
            with patch.object(email_campaigns, "_get_campaign", return_value=scheduled):
                with redirect_stdout(dry_buf):
                    dry_rc = email_campaigns.cmd_email_campaigns_pause_scheduling(args, dry_ctx)
            dry_payload = json.loads(dry_buf.getvalue())

            self.assertEqual(dry_rc, 0)
            self.assertTrue(dry_payload["dry_run"])
            self.assertEqual(dry_payload["plan_out"], plan_path)

            plan = json.loads(Path(plan_path).read_text(encoding="utf-8"))
            self.assertEqual(plan["method"], "email-campaigns.pause-scheduling")
            self.assertEqual(plan["request"]["path"], "/email-marketing/v1/campaigns/camp-1/pause-scheduling")
            self.assertEqual(plan["proposed_changes"], [{"operation": "pause-scheduling", "campaignId": "camp-1"}])

            apply_ctx = self._ctx(
                apply=True,
                yes=True,
                plan_in=plan_path,
                receipt_out=receipt_path,
                command_str="wix-safe-agent-cli email-campaigns pause-scheduling --campaign-id camp-1",
            )
            apply_buf = io.StringIO()
            with patch.object(email_campaigns, "_get_campaign", side_effect=[scheduled, paused]):
                with redirect_stdout(apply_buf):
                    apply_rc = email_campaigns.cmd_email_campaigns_pause_scheduling(args, apply_ctx)
            apply_payload = json.loads(apply_buf.getvalue())

            self.assertEqual(apply_rc, 0)
            self.assertFalse(apply_payload["dry_run"])
            self.assertTrue(apply_payload["ok"])
            self.assertEqual(apply_payload["receipt_out"], receipt_path)

            receipt = json.loads(Path(receipt_path).read_text(encoding="utf-8"))
            self.assertEqual(receipt["method"], "email-campaigns.pause-scheduling")
            self.assertTrue(receipt["verification"]["ok"])
            self.assertEqual(receipt["verification"]["checks"][0]["actual"], "PAUSED")
        finally:
            Path(plan_path).unlink()
            Path(receipt_path).unlink()

    def test_reschedule_builds_reviewed_plan_with_send_at(self) -> None:
        args = SimpleNamespace(campaign_id="camp-1", send_at="2026-06-24T10:00:00Z")

        buf = io.StringIO()
        with patch.object(email_campaigns, "_get_campaign", return_value=self._current_campaign()):
            with redirect_stdout(buf):
                rc = email_campaigns.cmd_email_campaigns_reschedule(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["method"], "email-campaigns.reschedule")
        self.assertEqual(payload["plan"]["request"]["body"], {"sendAt": "2026-06-24T10:00:00Z"})
        self.assertEqual(payload["plan"]["proposed_changes"], [{"operation": "reschedule", "campaignId": "camp-1", "sendAt": "2026-06-24T10:00:00Z"}])
        self.assertEqual(payload["plan"]["verification_plan"]["type"], "provider-response")

    def test_send_test_builds_reviewed_plan_and_notes_rate_limit(self) -> None:
        args = SimpleNamespace(
            campaign_id="camp-1",
            send_test_json='{"toEmailAddress":"owner@example.com","emailSubject":"Preview"}',
        )

        buf = io.StringIO()
        with patch.object(email_campaigns, "_get_campaign", return_value=self._current_campaign()):
            with redirect_stdout(buf):
                rc = email_campaigns.cmd_email_campaigns_send_test(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["method"], "email-campaigns.send-test")
        self.assertEqual(payload["plan"]["request"]["body"]["toEmailAddress"], "owner@example.com")
        self.assertEqual(payload["plan"]["request"]["body"]["emailSubject"], "Preview")
        self.assertEqual(payload["plan"]["proposed_changes"], [{"operation": "send-test", "campaignId": "camp-1", "toEmailAddress": "owner@example.com"}])
        self.assertIn("rate-limited", payload["plan"]["verification_plan"]["notes"])

    def test_publish_builds_reviewed_plan_with_email_distribution_options(self) -> None:
        args = SimpleNamespace(
            campaign_id="camp-1",
            publish_json='{"emailDistributionOptions":{"emailSubject":"Launch","sendAt":"2099-01-01T12:00:00Z"}}',
        )

        buf = io.StringIO()
        with patch.object(email_campaigns, "_get_campaign", return_value=self._current_campaign()):
            with redirect_stdout(buf):
                rc = email_campaigns.cmd_email_campaigns_publish(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["method"], "email-campaigns.publish")
        self.assertEqual(
            payload["plan"]["request"]["path"],
            "/email-marketing/v1/campaigns/camp-1/publish",
        )
        self.assertEqual(
            payload["plan"]["request"]["body"],
            {
                "emailDistributionOptions": {
                    "emailSubject": "Launch",
                    "sendAt": "2099-01-01T12:00:00Z",
                }
            },
        )

    def test_reuse_builds_reviewed_plan_and_creates_copy(self) -> None:
        args = SimpleNamespace(campaign_id="camp-1")

        buf = io.StringIO()
        with patch.object(email_campaigns, "_get_campaign", return_value=self._current_campaign()):
            with redirect_stdout(buf):
                rc = email_campaigns.cmd_email_campaigns_reuse(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["method"], "email-campaigns.reuse")
        self.assertEqual(
            payload["plan"]["request"]["path"],
            "/email-marketing/v1/campaigns/camp-1/reuse",
        )
        self.assertEqual(payload["plan"]["proposed_changes"], [{"operation": "reuse", "campaignId": "camp-1", "createsNewCampaignCopy": True}])

    def test_delete_builds_reviewed_plan_and_requires_ack(self) -> None:
        args = SimpleNamespace(campaign_id="camp-1")

        buf = io.StringIO()
        with patch.object(email_campaigns, "_get_campaign", return_value=self._current_campaign()):
            with redirect_stdout(buf):
                rc = email_campaigns.cmd_email_campaigns_delete(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["method"], "email-campaigns.delete")
        self.assertIn("--ack-irreversible", " ".join(payload["plan"]["preconditions"]))
        self.assertEqual(payload["plan"]["request"]["path"], "/email-marketing/v1/campaigns/camp-1")

    @patch("wix_safe_agent_cli.commands.email_campaigns.HttpClient")
    def test_validate_link_builds_expected_request(self, mock_client) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"valid": True})
        args = SimpleNamespace(url="https://example.com")

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = email_campaigns.cmd_campaign_validation_validate_link(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["request"]["path"], "/email-marketing/v1/campaign-validation/validate-link")
        self.assertEqual(payload["request"]["body"]["url"], "https://example.com")

    @patch("wix_safe_agent_cli.commands.email_campaigns.HttpClient")
    def test_validate_html_links_accepts_file_input(self, mock_client) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"validatedLinks": []})
        handle = tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".html")
        handle.write("<a href='https://example.com'>Example</a>")
        handle.close()
        args = SimpleNamespace(html=f"@{handle.name}")

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = email_campaigns.cmd_campaign_validation_validate_html_links(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(
            payload["request"]["path"],
            "/email-marketing/v1/campaign-validation/validate-html-links",
        )
        self.assertIn("https://example.com", payload["request"]["body"]["html"])

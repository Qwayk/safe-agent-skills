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
from wix_safe_agent_cli.commands import marketing_consent
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = (action, payload)


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestMarketingConsentCommands(unittest.TestCase):
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
            "command_str": "wix-safe-agent-cli marketing-consent",
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

    def _current_consent(self, *, state: str = "CONFIRMED") -> dict:
        return {
            "marketingConsentId": "mc-1",
            "state": state,
            "details": {"type": "EMAIL", "email": "owner@example.com"},
            "communicationEligibility": {"granted": state != "REVOKED"},
        }

    def test_parser_recognizes_marketing_consent_subcommands_and_write_flags(self) -> None:
        parser = build_parser()

        get_args = parser.parse_args(["marketing-consent", "get", "--marketing-consent-id", "mc-1"])
        self.assertEqual(get_args.marketing_consent_cmd, "get")
        self.assertFalse(get_args.write_capable)

        query_args = parser.parse_args(["marketing-consent", "query", "--query-json", '{"query":{}}'])
        self.assertEqual(query_args.marketing_consent_cmd, "query")
        self.assertFalse(query_args.write_capable)

        get_by_args = parser.parse_args(
            [
                "marketing-consent",
                "get-by-identifier",
                "--type",
                "EMAIL",
                "--email",
                "owner@example.com",
                "--link-language",
                "en",
            ]
        )
        self.assertEqual(get_by_args.marketing_consent_cmd, "get-by-identifier")
        self.assertFalse(get_by_args.write_capable)

        create_args = parser.parse_args(
            [
                "marketing-consent",
                "create",
                "--marketing-consent-json",
                '{"details":{"type":"EMAIL","email":"owner@example.com"},"lastConfirmationActivity":{"source":"ui"}}',
            ]
        )
        self.assertEqual(create_args.marketing_consent_cmd, "create")
        self.assertTrue(create_args.write_capable)

        upsert_args = parser.parse_args(
            [
                "marketing-consent",
                "upsert",
                "--marketing-consent-json",
                '{"details":{"type":"EMAIL","email":"owner@example.com"},"state":"CONFIRMED","lastConfirmationActivity":{"source":"ui"}}',
            ]
        )
        self.assertEqual(upsert_args.marketing_consent_cmd, "upsert")
        self.assertTrue(upsert_args.write_capable)

        update_args = parser.parse_args(
            [
                "marketing-consent",
                "update",
                "--marketing-consent-json",
                '{"id":"mc-1","details":{"type":"EMAIL","email":"owner@example.com"},"state":"CONFIRMED","lastConfirmationActivity":{"source":"ui"}}',
                "--mask-json",
                '{"paths":["state"]}',
            ]
        )
        self.assertEqual(update_args.marketing_consent_cmd, "update")
        self.assertTrue(update_args.write_capable)

        delete_args = parser.parse_args(
            ["marketing-consent", "delete", "--marketing-consent-id", "mc-1"]
        )
        self.assertEqual(delete_args.marketing_consent_cmd, "delete")
        self.assertTrue(delete_args.write_capable)

        bulk_upsert_args = parser.parse_args(
            [
                "marketing-consent",
                "bulk-upsert",
                "--marketing-consents-json",
                '{"info":[{"details":{"type":"EMAIL","email":"owner@example.com"},"state":"CONFIRMED","lastConfirmationActivity":{"source":"ui"}}]}',
            ]
        )
        self.assertEqual(bulk_upsert_args.marketing_consent_cmd, "bulk-upsert")
        self.assertTrue(bulk_upsert_args.write_capable)

        remove_args = parser.parse_args(
            [
                "marketing-consent",
                "remove",
                "--type",
                "EMAIL",
                "--email",
                "owner@example.com",
                "--last-revoke-activity-json",
                '{"source":"ui"}',
            ]
        )
        self.assertEqual(remove_args.marketing_consent_cmd, "remove")
        self.assertTrue(remove_args.write_capable)

    @patch("wix_safe_agent_cli.commands.marketing_consent.HttpClient")
    def test_get_builds_expected_request(self, mock_client) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"marketingConsent": self._current_consent()})
        args = SimpleNamespace(marketing_consent_id="mc-1")

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = marketing_consent.cmd_marketing_consent_get(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["method"], "marketing-consent.get")
        self.assertEqual(payload["request"]["method"], "GET")
        self.assertEqual(payload["request"]["path"], "/marketing-consent/v1/marketing-consent/mc-1")

    @patch("wix_safe_agent_cli.commands.marketing_consent.HttpClient")
    def test_get_by_identifier_builds_expected_request(self, mock_client) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"marketingConsent": self._current_consent()})
        args = SimpleNamespace(type="EMAIL", email="owner@example.com", phone=None, link_language="en")

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = marketing_consent.cmd_marketing_consent_get_by_identifier(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["method"], "marketing-consent.get-by-identifier")
        self.assertEqual(payload["request"]["method"], "GET")
        self.assertEqual(payload["request"]["path"], "/marketing-consent/v1/marketing-consent/get-by")
        self.assertEqual(payload["request"]["params"]["type"], "EMAIL")
        self.assertEqual(payload["request"]["params"]["email"], "owner@example.com")
        self.assertEqual(payload["request"]["params"]["linkLanguage"], "en")

    @patch("wix_safe_agent_cli.commands.marketing_consent.HttpClient")
    def test_query_normalizes_inner_payload_and_limits(self, mock_client) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"marketingConsent": []})
        args = SimpleNamespace(query_json='{"filter":{"state":{"$eq":"CONFIRMED"}},"cursor_paging":{"limit":10}}')

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = marketing_consent.cmd_marketing_consent_query(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["request"]["body"], {"query": {"filter": {"state": {"$eq": "CONFIRMED"}}, "cursorPaging": {"limit": 10}}})

    def test_query_refuses_cursor_paging_limit_above_100(self) -> None:
        args = SimpleNamespace(query_json='{"query":{"cursorPaging":{"limit":101}}}')

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = marketing_consent.cmd_marketing_consent_query(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertFalse(payload["ok"])
        self.assertIn("between 0 and 100", payload["error"])

    def test_create_refuses_non_confirmed_state(self) -> None:
        args = SimpleNamespace(
            marketing_consent_json='{"details":{"type":"EMAIL","email":"owner@example.com"},"state":"PENDING","lastConfirmationActivity":{"source":"ui"}}'
        )

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = marketing_consent.cmd_marketing_consent_create(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertFalse(payload["ok"])
        self.assertIn("Create Marketing Consent only supports a CONFIRMED state", payload["error"])

    @patch("wix_safe_agent_cli.commands.marketing_consent.HttpClient")
    def test_create_dry_run_builds_plan(self, mock_client) -> None:
        mock_client.return_value.request.side_effect = RuntimeError("HTTP 404 Not Found")
        args = SimpleNamespace(
            marketing_consent_json='{"details":{"type":"EMAIL","email":"owner@example.com"},"lastConfirmationActivity":{"source":"ui"}}'
        )

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = marketing_consent.cmd_marketing_consent_create(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["method"], "marketing-consent.create")
        self.assertEqual(payload["plan"]["request"]["path"], "/marketing-consent/v1/marketing-consent")
        self.assertEqual(payload["plan"]["request"]["body"]["marketingConsent"]["state"], "CONFIRMED")

    @patch("wix_safe_agent_cli.commands.marketing_consent.HttpClient")
    def test_create_refuses_existing_consent_and_tells_caller_to_use_upsert(self, mock_client) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"marketingConsent": self._current_consent()})
        args = SimpleNamespace(
            marketing_consent_json='{"details":{"type":"EMAIL","email":"owner@example.com"},"lastConfirmationActivity":{"source":"ui"}}'
        )

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = marketing_consent.cmd_marketing_consent_create(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertIn("use upsert instead", payload["reasons"][0])
        self.assertEqual(mock_client.return_value.request.call_count, 1)

    @patch("wix_safe_agent_cli.commands.marketing_consent.HttpClient")
    def test_create_apply_verifies_by_reread(self, mock_client) -> None:
        args = SimpleNamespace(
            marketing_consent_json='{"details":{"type":"EMAIL","email":"owner@example.com"},"lastConfirmationActivity":{"source":"ui"}}'
        )
        dry_ctx = self._ctx()

        mock_client.return_value.request.side_effect = [RuntimeError("HTTP 404 Not Found")]
        dry_buf = io.StringIO()
        with redirect_stdout(dry_buf):
            marketing_consent.cmd_marketing_consent_create(args, dry_ctx)
        plan_path = self._write_plan(json.loads(dry_buf.getvalue())["plan"])

        try:
            mock_client.return_value.request.side_effect = [
                RuntimeError("HTTP 404 Not Found"),
                _DummyResponse({"marketingConsent": self._current_consent(state="CONFIRMED")}),
                _DummyResponse({"marketingConsent": self._current_consent(state="CONFIRMED")}),
            ]
            apply_ctx = self._ctx(
                apply=True,
                yes=True,
                plan_in=plan_path,
                command_str=(
                    "wix-safe-agent-cli marketing-consent create --marketing-consent-json "
                    '\'{"details":{"type":"EMAIL","email":"owner@example.com"},"lastConfirmationActivity":{"source":"ui"}}\''
                ),
            )
            apply_buf = io.StringIO()
            with redirect_stdout(apply_buf):
                rc = marketing_consent.cmd_marketing_consent_create(args, apply_ctx)
            payload = json.loads(apply_buf.getvalue())

            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertFalse(payload["dry_run"])
            self.assertEqual(payload["receipt"]["verification"]["after"]["state"], "CONFIRMED")
            self.assertEqual(mock_client.return_value.request.call_count, 4)
        finally:
            try:
                Path(plan_path).unlink()
            except FileNotFoundError:
                pass

    @patch("wix_safe_agent_cli.commands.marketing_consent.HttpClient")
    def test_update_refuses_existing_email_unknown_state_without_required_activity(self, mock_client) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"marketingConsent": self._current_consent()})
        args = SimpleNamespace(
            marketing_consent_json='{"id":"mc-1","details":{"type":"EMAIL","email":"owner@example.com"},"state":"UNKNOWN_STATE"}',
            mask_json='{"paths":["state"]}',
        )

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = marketing_consent.cmd_marketing_consent_update(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertFalse(payload["ok"])
        self.assertIn("lastConfirmationActivity", payload["error"])

    @patch("wix_safe_agent_cli.commands.marketing_consent.HttpClient")
    def test_update_dry_run_builds_plan(self, mock_client) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"marketingConsent": self._current_consent()})
        args = SimpleNamespace(
            marketing_consent_json='{"id":"mc-1","details":{"type":"EMAIL","email":"owner@example.com"},"state":"CONFIRMED","lastConfirmationActivity":{"source":"ui"}}',
            mask_json='{"paths":["state"]}',
        )

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = marketing_consent.cmd_marketing_consent_update(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["method"], "marketing-consent.update")
        self.assertEqual(payload["plan"]["request"]["path"], "/marketing-consent/v1/marketing-consent/mc-1")
        self.assertEqual(payload["plan"]["request"]["method"], "PATCH")
        self.assertEqual(payload["plan"]["request"]["body"]["marketingConsent"]["id"], "mc-1")
        self.assertEqual(payload["plan"]["request"]["body"]["mask"], {"paths": ["state"]})

    @patch("wix_safe_agent_cli.commands.marketing_consent.HttpClient")
    def test_update_apply_requires_reviewed_plan_before_http(self, mock_client) -> None:
        args = SimpleNamespace(
            marketing_consent_json='{"id":"mc-1","details":{"type":"EMAIL","email":"owner@example.com"},"state":"CONFIRMED","lastConfirmationActivity":{"source":"ui"}}',
            mask_json='{"paths":["state"]}',
        )
        ctx = self._ctx(apply=True, yes=True)

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = marketing_consent.cmd_marketing_consent_update(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertIn("--plan-in", payload["reasons"][0])
        self.assertEqual(mock_client.return_value.request.call_count, 0)

    @patch("wix_safe_agent_cli.commands.marketing_consent.HttpClient")
    def test_delete_apply_requires_reviewed_plan_before_http(self, mock_client) -> None:
        args = SimpleNamespace(marketing_consent_id="mc-1")
        ctx = self._ctx(apply=True, yes=True, ack_irreversible=True)

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = marketing_consent.cmd_marketing_consent_delete(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertIn("--plan-in", payload["reasons"][0])
        self.assertEqual(mock_client.return_value.request.call_count, 0)

    @patch("wix_safe_agent_cli.commands.marketing_consent.HttpClient")
    def test_delete_dry_run_builds_plan(self, mock_client) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"marketingConsent": self._current_consent()})
        args = SimpleNamespace(marketing_consent_id="mc-1")

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = marketing_consent.cmd_marketing_consent_delete(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["method"], "marketing-consent.delete")
        self.assertEqual(payload["plan"]["request"]["path"], "/marketing-consent/v1/marketing-consent/mc-1")
        self.assertEqual(payload["plan"]["request"]["method"], "DELETE")

    @patch("wix_safe_agent_cli.commands.marketing_consent.HttpClient")
    def test_delete_apply_verifies_by_reread_404_when_available(self, mock_client) -> None:
        args = SimpleNamespace(marketing_consent_id="mc-1")
        dry_ctx = self._ctx()

        mock_client.return_value.request.side_effect = [_DummyResponse({"marketingConsent": self._current_consent()})]
        dry_buf = io.StringIO()
        with redirect_stdout(dry_buf):
            marketing_consent.cmd_marketing_consent_delete(args, dry_ctx)
        plan_path = self._write_plan(json.loads(dry_buf.getvalue())["plan"])

        try:
            mock_client.return_value.request.side_effect = [
                _DummyResponse({"marketingConsent": self._current_consent()}),
                _DummyResponse({"deleted": True}),
                RuntimeError("HTTP 404 Not Found"),
            ]
            apply_ctx = self._ctx(
                apply=True,
                yes=True,
                ack_irreversible=True,
                plan_in=plan_path,
                command_str="wix-safe-agent-cli marketing-consent delete --marketing-consent-id mc-1",
            )
            apply_buf = io.StringIO()
            with redirect_stdout(apply_buf):
                rc = marketing_consent.cmd_marketing_consent_delete(args, apply_ctx)
            payload = json.loads(apply_buf.getvalue())

            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertFalse(payload["dry_run"])
            self.assertEqual(payload["receipt"]["verification"]["expected_http_status"], 404)
            self.assertEqual(payload["receipt"]["verification"]["actual_http_status"], 404)
        finally:
            try:
                Path(plan_path).unlink()
            except FileNotFoundError:
                pass

    def test_bulk_upsert_validates_max_500(self) -> None:
        items = [
            {
                "details": {"type": "EMAIL", "email": f"owner{i}@example.com"},
                "state": "CONFIRMED",
                "lastConfirmationActivity": {"source": "ui"},
            }
            for i in range(501)
        ]
        args = SimpleNamespace(marketing_consents_json=json.dumps({"info": items}))

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = marketing_consent.cmd_marketing_consent_bulk_upsert(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertFalse(payload["ok"])
        self.assertIn("at most 500", payload["error"])

    @patch("wix_safe_agent_cli.commands.marketing_consent.HttpClient")
    def test_bulk_upsert_dry_run_builds_plan(self, mock_client) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"results": [], "metadata": {"totals": {"succeeded": 1}}})
        args = SimpleNamespace(
            marketing_consents_json='{"info":[{"details":{"type":"EMAIL","email":"owner@example.com"},"state":"CONFIRMED","lastConfirmationActivity":{"source":"ui"}}]}'
        )

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = marketing_consent.cmd_marketing_consent_bulk_upsert(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["method"], "marketing-consent.bulk-upsert")
        self.assertEqual(payload["plan"]["request"]["path"], "/marketing-consent/v1/bulk/marketing-consent/upsert")
        self.assertEqual(payload["plan"]["request"]["method"], "POST")
        self.assertEqual(len(payload["plan"]["request"]["body"]["info"]), 1)

    @patch("wix_safe_agent_cli.commands.marketing_consent.HttpClient")
    def test_bulk_upsert_apply_requires_reviewed_plan_before_http(self, mock_client) -> None:
        args = SimpleNamespace(
            marketing_consents_json='{"info":[{"details":{"type":"EMAIL","email":"owner@example.com"},"state":"CONFIRMED","lastConfirmationActivity":{"source":"ui"}}]}'
        )
        ctx = self._ctx(apply=True, yes=True)

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = marketing_consent.cmd_marketing_consent_bulk_upsert(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertIn("--plan-in", payload["reasons"][0])
        self.assertEqual(mock_client.return_value.request.call_count, 0)

    @patch("wix_safe_agent_cli.commands.marketing_consent.HttpClient")
    def test_upsert_apply_accepts_unknown_state_for_existing_email(self, mock_client) -> None:
        args = SimpleNamespace(
            marketing_consent_json='{"details":{"type":"EMAIL","email":"owner@example.com"},"state":"UNKNOWN_STATE"}'
        )
        dry_ctx = self._ctx()

        mock_client.return_value.request.side_effect = [_DummyResponse({"marketingConsent": self._current_consent()})]
        dry_buf = io.StringIO()
        with redirect_stdout(dry_buf):
            marketing_consent.cmd_marketing_consent_upsert(args, dry_ctx)
        plan_path = self._write_plan(json.loads(dry_buf.getvalue())["plan"])

        try:
            mock_client.return_value.request.side_effect = [
                _DummyResponse({"marketingConsent": self._current_consent()}),
                _DummyResponse({"marketingConsent": self._current_consent(state="CONFIRMED")}),
                _DummyResponse({"marketingConsent": self._current_consent(state="CONFIRMED")}),
            ]
            apply_ctx = self._ctx(
                apply=True,
                yes=True,
                plan_in=plan_path,
                command_str=(
                    "wix-safe-agent-cli marketing-consent upsert --marketing-consent-json "
                    '\'{"details":{"type":"EMAIL","email":"owner@example.com"},"state":"UNKNOWN_STATE"}\''
                ),
            )
            apply_buf = io.StringIO()
            with redirect_stdout(apply_buf):
                rc = marketing_consent.cmd_marketing_consent_upsert(args, apply_ctx)
            payload = json.loads(apply_buf.getvalue())

            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertFalse(payload["dry_run"])
            self.assertEqual(payload["receipt"]["verification"]["after"]["state"], "CONFIRMED")
            self.assertEqual(mock_client.return_value.request.call_count, 4)
        finally:
            try:
                Path(plan_path).unlink()
            except FileNotFoundError:
                pass

    @patch("wix_safe_agent_cli.commands.marketing_consent.HttpClient")
    def test_remove_apply_verifies_revoked_and_eligibility_false(self, mock_client) -> None:
        args = SimpleNamespace(
            type="EMAIL",
            email="owner@example.com",
            phone=None,
            last_revoke_activity_json='{"source":"ui"}',
        )
        dry_ctx = self._ctx()

        mock_client.return_value.request.side_effect = [_DummyResponse({"marketingConsent": self._current_consent()})]
        dry_buf = io.StringIO()
        with redirect_stdout(dry_buf):
            marketing_consent.cmd_marketing_consent_remove(args, dry_ctx)
        plan_path = self._write_plan(json.loads(dry_buf.getvalue())["plan"])

        try:
            mock_client.return_value.request.side_effect = [
                _DummyResponse({"marketingConsent": self._current_consent()}),
                _DummyResponse({"marketingConsent": self._current_consent(state="REVOKED")}),
                _DummyResponse({"marketingConsent": self._current_consent(state="REVOKED")}),
            ]
            apply_ctx = self._ctx(
                apply=True,
                yes=True,
                plan_in=plan_path,
                command_str=(
                    "wix-safe-agent-cli marketing-consent remove --type EMAIL --email owner@example.com "
                    '--last-revoke-activity-json \'{"source":"ui"}\''
                ),
            )
            apply_buf = io.StringIO()
            with redirect_stdout(apply_buf):
                rc = marketing_consent.cmd_marketing_consent_remove(args, apply_ctx)
            payload = json.loads(apply_buf.getvalue())

            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertFalse(payload["dry_run"])
            self.assertEqual(payload["receipt"]["verification"]["after"]["state"], "REVOKED")
            self.assertEqual(mock_client.return_value.request.call_count, 4)
        finally:
            try:
                Path(plan_path).unlink()
            except FileNotFoundError:
                pass

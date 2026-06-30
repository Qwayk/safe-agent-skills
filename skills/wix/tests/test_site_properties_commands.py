from __future__ import annotations

import io
import json
import tempfile
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import site_properties
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


class TestSitePropertiesCommands(TestCase):
    def _ctx(self, *, cfg_override: dict | None = None, **overrides) -> dict:
        cfg = SimpleNamespace(
            base_url="https://www.wixapis.com",
            timeout_s=30.0,
            access_token="site-app-token",
            api_key=None,
            account_id=None,
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
            "out": Output(mode="json"),
            "audit": _DummyAudit(),
            "tool": "wix-safe-agent-cli",
            "tool_version": "0.0.0",
            "command_str": "wix-safe-agent-cli site-properties",
            "apply": False,
            "yes": False,
            "verbose": False,
            "plan_in": None,
            "plan_out": None,
            "receipt_out": None,
            "ack_irreversible": False,
        }
        ctx.update(overrides)
        return ctx

    def test_parser_recognizes_site_properties_get(self) -> None:
        parser = build_parser()
        parsed = parser.parse_args(["site-properties", "get", "--field-path", "businessContact.email", "--field-path", "consentPolicy.marketing"])

        self.assertEqual(parsed.site_properties_cmd, "get")
        self.assertFalse(parsed.write_capable)
        self.assertEqual(parsed.field_path, ["businessContact.email", "consentPolicy.marketing"])
        self.assertEqual(parsed.func.__name__, "cmd_site_properties_get")

    def test_parser_recognizes_site_properties_update_business_contact(self) -> None:
        parser = build_parser()
        parsed = parser.parse_args(["site-properties", "update-business-contact", "--contact-json", '{"email":"new@example.com"}'])

        self.assertEqual(parsed.site_properties_cmd, "update-business-contact")
        self.assertTrue(parsed.write_capable)
        self.assertEqual(parsed.contact_json, '{"email":"new@example.com"}')
        self.assertEqual(parsed.func.__name__, "cmd_site_properties_update_business_contact")

    def test_parser_recognizes_site_properties_update_business_profile(self) -> None:
        parser = build_parser()
        parsed = parser.parse_args(["site-properties", "update-business-profile", "--profile-json", '{"industry":"Retail"}'])

        self.assertEqual(parsed.site_properties_cmd, "update-business-profile")
        self.assertTrue(parsed.write_capable)
        self.assertEqual(parsed.profile_json, '{"industry":"Retail"}')
        self.assertEqual(parsed.func.__name__, "cmd_site_properties_update_business_profile")

    def test_parser_recognizes_site_properties_update_business_schedule(self) -> None:
        parser = build_parser()
        parsed = parser.parse_args(["site-properties", "update-business-schedule", "--schedule-json", '{"mon":"8-4"}'])

        self.assertEqual(parsed.site_properties_cmd, "update-business-schedule")
        self.assertTrue(parsed.write_capable)
        self.assertEqual(parsed.schedule_json, '{"mon":"8-4"}')
        self.assertEqual(parsed.func.__name__, "cmd_site_properties_update_business_schedule")

    def test_parser_recognizes_site_properties_update_consent_policy(self) -> None:
        parser = build_parser()
        parsed = parser.parse_args(["site-properties", "update-consent-policy", "--consent-json", '{"marketing":true}'])

        self.assertEqual(parsed.site_properties_cmd, "update-consent-policy")
        self.assertTrue(parsed.write_capable)
        self.assertEqual(parsed.consent_json, '{"marketing":true}')
        self.assertEqual(parsed.func.__name__, "cmd_site_properties_update_consent_policy")

    @patch("wix_safe_agent_cli.commands.site_properties.HttpClient")
    def test_site_properties_get_builds_expected_request_with_field_paths(self, mock_client) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"businessContact": {"email": "old@example.com"}})

        args = SimpleNamespace(field_path=["businessContact.email", "businessContact.phone"])
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = site_properties.cmd_site_properties_get(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertEqual(payload["request"]["method"], "GET")
        self.assertEqual(payload["request"]["path"], "/site-properties/v4/properties")
        self.assertEqual(payload["request"]["params"], {"fields.paths": ["businessContact.email", "businessContact.phone"]})
        call = mock_client.return_value.request.call_args
        self.assertEqual(call.kwargs["method"], "GET")
        self.assertEqual(call.kwargs["params"], {"fields.paths": ["businessContact.email", "businessContact.phone"]})
        self.assertEqual(call.kwargs["headers"], {"Authorization": "site-app-token"})

    @patch("wix_safe_agent_cli.commands.site_properties.HttpClient")
    def test_site_properties_update_business_contact_dry_run_plan(self, mock_client) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"businessContact": {"email": "old@example.com", "phone": "111"}})

        args = SimpleNamespace(contact_json='{"email":"new@example.com","phone":"222"}')

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = site_properties.cmd_site_properties_update_business_contact(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["request"]["path"], "/site-properties/v4/properties/business-contact")
        self.assertEqual(payload["plan"]["request"]["body"], {"businessContact": {"email": "new@example.com", "phone": "222"}})
        self.assertEqual(mock_client.return_value.request.call_count, 1)

    @patch("wix_safe_agent_cli.commands.site_properties.HttpClient")
    def test_site_properties_update_business_profile_dry_run_plan(self, mock_client) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"businessProfile": {"industry": "Fitness"}})

        args = SimpleNamespace(profile_json='{"industry":"Retail","founded":"2020"}')

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = site_properties.cmd_site_properties_update_business_profile(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["request"]["path"], "/site-properties/v4/properties/business-profile")
        self.assertEqual(payload["plan"]["request"].get("body"), {"businessProfile": {"industry": "Retail", "founded": "2020"}})
        self.assertEqual(mock_client.return_value.request.call_count, 1)

    @patch("wix_safe_agent_cli.commands.site_properties.HttpClient")
    def test_site_properties_update_business_schedule_dry_run_plan(self, mock_client) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"businessSchedule": {"mon": "9-5"}})

        args = SimpleNamespace(schedule_json='{"mon":"8-4"}')

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = site_properties.cmd_site_properties_update_business_schedule(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["request"]["path"], "/site-properties/v4/properties/business-schedule")
        self.assertIn("overwrites", " ".join(payload["plan"].get("risk_reasons", [])))
        self.assertEqual(payload["plan"]["request"]["body"], {"businessSchedule": {"mon": "8-4"}})
        self.assertEqual(mock_client.return_value.request.call_count, 1)

    @patch("wix_safe_agent_cli.commands.site_properties.HttpClient")
    def test_site_properties_update_consent_policy_dry_run_plan(self, mock_client) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"consentPolicy": {"marketing": False}})

        args = SimpleNamespace(consent_json='{"marketing":true}')

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = site_properties.cmd_site_properties_update_consent_policy(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["request"]["path"], "/site-properties/v4/properties/policy")
        self.assertEqual(payload["plan"]["request"]["body"], {"consentPolicy": {"marketing": True}})
        self.assertEqual(mock_client.return_value.request.call_count, 1)

    @patch("wix_safe_agent_cli.commands.site_properties.HttpClient")
    def test_site_properties_update_business_contact_apply_writes_and_verifies(self, mock_client) -> None:
        mock_client.return_value.request.side_effect = [
            _DummyResponse({"businessContact": {"email": "old@example.com", "phone": "111"}}),
            _DummyResponse({}),
            _DummyResponse({"businessContact": {"email": "new@example.com", "phone": "222"}}),
        ]

        args = SimpleNamespace(contact_json='{"email":"new@example.com","phone":"222"}')
        ctx = self._ctx(apply=True, yes=True)

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = site_properties.cmd_site_properties_update_business_contact(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertFalse(payload["dry_run"])
        self.assertTrue(payload["ok"])
        calls = mock_client.return_value.request.call_args_list
        self.assertEqual(calls[1].kwargs["method"], "POST")
        self.assertTrue(calls[1].kwargs["url"].endswith("/site-properties/v4/properties/business-contact"))
        self.assertEqual(calls[1].kwargs["headers"], {"Authorization": "site-app-token", "Content-Type": "application/json"})
        self.assertEqual(calls[1].kwargs["json_body"], {"businessContact": {"email": "new@example.com", "phone": "222"}})
        self.assertTrue(payload["receipt"]["verification"]["ok"])
        self.assertEqual(payload["receipt"]["verification"]["checks"], [
            {"field": "email", "expected": "new@example.com", "actual": "new@example.com"},
            {"field": "phone", "expected": "222", "actual": "222"},
        ])

    @patch("wix_safe_agent_cli.commands.site_properties.HttpClient")
    def test_site_properties_runtime_gate_refuses_apply_without_reviewed_plan(self, mock_client) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"businessContact": {"email": "old@example.com"}})

        args = SimpleNamespace(contact_json='{"email":"new@example.com"}')
        ctx = self._ctx(apply=True, yes=True, enforce_reviewed_plan=True)

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = site_properties.cmd_site_properties_update_business_contact(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertIn("--plan-out", payload["reasons"][0])

    @patch("wix_safe_agent_cli.commands.site_properties.HttpClient")
    def test_site_properties_update_business_profile_apply_writes_and_verifies(self, mock_client) -> None:
        mock_client.return_value.request.side_effect = [
            _DummyResponse({"businessProfile": {"industry": "Fitness", "founded": "2015"}}),
            _DummyResponse({}),
            _DummyResponse({"businessProfile": {"industry": "Retail", "founded": "2020"}}),
        ]

        args = SimpleNamespace(profile_json='{"industry":"Retail","founded":"2020"}')
        ctx = self._ctx(apply=True, yes=True)

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = site_properties.cmd_site_properties_update_business_profile(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertFalse(payload["dry_run"])
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["receipt"]["request"]["path"], "/site-properties/v4/properties/business-profile")
        self.assertTrue(payload["receipt"]["verification"]["ok"])
        self.assertEqual(len(payload["receipt"]["verification"]["checks"]), 2)

    @patch("wix_safe_agent_cli.commands.site_properties.HttpClient")
    def test_site_properties_update_business_schedule_apply_writes_and_verifies(self, mock_client) -> None:
        mock_client.return_value.request.side_effect = [
            _DummyResponse({"businessSchedule": {"mon": "9-5", "fri": "11-4"}}),
            _DummyResponse({}),
            _DummyResponse({"businessSchedule": {"mon": "8-4", "fri": "closed"}}),
        ]

        args = SimpleNamespace(schedule_json='{"mon":"8-4","fri":"closed"}')
        ctx = self._ctx(apply=True, yes=True)

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = site_properties.cmd_site_properties_update_business_schedule(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertFalse(payload["dry_run"])
        self.assertEqual(payload["method"], "site-properties.update-business-schedule")
        self.assertTrue(payload["receipt"]["verification"]["ok"])
        self.assertEqual(payload["receipt"]["request"]["path"], "/site-properties/v4/properties/business-schedule")

    @patch("wix_safe_agent_cli.commands.site_properties.HttpClient")
    def test_site_properties_update_consent_policy_apply_writes_and_verifies(self, mock_client) -> None:
        mock_client.return_value.request.side_effect = [
            _DummyResponse({"consentPolicy": {"marketing": False, "analytics": True}}),
            _DummyResponse({}),
            _DummyResponse({"consentPolicy": {"marketing": True, "analytics": False}}),
        ]

        args = SimpleNamespace(consent_json='{"marketing":true,"analytics":false}')
        ctx = self._ctx(apply=True, yes=True)

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = site_properties.cmd_site_properties_update_consent_policy(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertFalse(payload["dry_run"])
        self.assertEqual(payload["method"], "site-properties.update-consent-policy")
        self.assertTrue(payload["receipt"]["verification"]["ok"])
        self.assertEqual(payload["receipt"]["verification"]["checks"], [
            {"field": "marketing", "expected": True, "actual": True},
            {"field": "analytics", "expected": False, "actual": False},
        ])

    @patch("wix_safe_agent_cli.commands.site_properties.HttpClient")
    def test_site_properties_update_business_contact_refuses_stale_plan(self, mock_client) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"businessContact": {"email": "old@example.com"}})

        args = SimpleNamespace(contact_json='{"email":"new@example.com"}')
        dry_ctx = self._ctx()
        dry_buf = io.StringIO()
        with redirect_stdout(dry_buf):
            dry_rc = site_properties.cmd_site_properties_update_business_contact(args, dry_ctx)
        self.assertEqual(dry_rc, 0)
        dry_payload = json.loads(dry_buf.getvalue())
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as handle:
            json.dump(dry_payload["plan"], handle)
            plan_path = handle.name

        try:
            mock_client.return_value.request.reset_mock()
            mock_client.return_value.request.side_effect = [
                _DummyResponse({"businessContact": {"email": "changed@example.com"}}),
            ]
            apply_ctx = self._ctx(apply=True, yes=True, plan_in=plan_path)
            apply_buf = io.StringIO()
            with redirect_stdout(apply_buf):
                apply_rc = site_properties.cmd_site_properties_update_business_contact(args, apply_ctx)
            apply_payload = json.loads(apply_buf.getvalue())

            self.assertEqual(apply_rc, 0)
            self.assertTrue(apply_payload["refused"])
            self.assertIn("changed since plan was created", apply_payload["reasons"][0])
            self.assertEqual(mock_client.return_value.request.call_count, 1)
        finally:
            Path(plan_path).unlink()

from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import intake_form_submissions, intake_forms
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = action, payload


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self.body = json.dumps(payload).encode("utf-8")
        self.headers = {"content-type": "application/json"}
        self.status = 200
        self.url = "https://www.wixapis.com/test"

    def json(self):
        return json.loads(self.body.decode("utf-8"))

    def text(self) -> str:
        return self.body.decode("utf-8")


class TestIntakeFormsCommands(unittest.TestCase):
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
            "tool": "wix-safe-agent-cli",
            "tool_version": "0.0.0",
            "command_str": "wix-safe-agent-cli intake-forms",
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

    def test_parser_exposes_intake_forms_commands(self) -> None:
        parser = build_parser()
        cases = [
            (["intake-forms", "query"], "query", False),
            (["intake-forms", "create-customer-submission-link", "--intake-form-id", "form-1"], "create-customer-submission-link", False),
            (["intake-forms", "archive", "--intake-form-id", "form-1"], "archive", True),
            (["intake-forms", "unarchive", "--intake-form-id", "form-1"], "unarchive", True),
            (
                ["intake-forms", "update-expiration-period", "--intake-form-id", "form-1", "--expiration-period-in-months", "6"],
                "update-expiration-period",
                True,
            ),
            (["intake-forms", "delete", "--intake-form-id", "form-1"], "delete", True),
        ]
        for argv, command, write_capable in cases:
            with self.subTest(command=command):
                args = parser.parse_args(argv)
                self.assertEqual(args.intake_forms_cmd, command)
                self.assertEqual(args.write_capable, write_capable)

    def test_parser_exposes_intake_form_submissions_commands(self) -> None:
        parser = build_parser()
        cases = [
            (["intake-form-submissions", "query"], "query", False),
            (["intake-form-submissions", "search"], "search", False),
            (["intake-form-submissions", "count-by-intake-form-ids", "--request-json", '{"intakeFormIds":["form-1"]}'], "count-by-intake-form-ids", False),
            (["intake-form-submissions", "list-data-by-contacts", "--request-json", '{"contactIds":["contact-1"]}'], "list-data-by-contacts", False),
            (["intake-form-submissions", "cancel", "--submission-id", "sub-1"], "cancel", True),
            (["intake-form-submissions", "extend", "--submission-id", "sub-1"], "extend", True),
            (["intake-form-submissions", "exempt", "--intake-form-id", "form-1", "--exemption-json", '{"contactId":"contact-1"}'], "exempt", True),
            (["intake-form-submissions", "delete", "--submission-id", "sub-1"], "delete", True),
        ]
        for argv, command, write_capable in cases:
            with self.subTest(command=command):
                args = parser.parse_args(argv)
                self.assertEqual(args.intake_form_submissions_cmd, command)
                self.assertEqual(args.write_capable, write_capable)

    @patch("wix_safe_agent_cli.commands.intake_forms.HttpClient")
    def test_intake_forms_read_helpers_use_official_paths(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"ok": True})
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = intake_forms.cmd_intake_forms_create_customer_submission_link(
                SimpleNamespace(intake_form_id="form-1", contact_id="contact-1"),
                self._ctx(),
            )
        self.assertEqual(rc, 0)
        self.assertEqual(mock_client.return_value.request.call_args.kwargs["method"], "GET")
        self.assertTrue(mock_client.return_value.request.call_args.kwargs["url"].endswith("/_api/intake-forms/v1/intake-forms/form-1/link"))
        self.assertEqual(mock_client.return_value.request.call_args.kwargs["params"], {"contactId": "contact-1"})

    @patch("wix_safe_agent_cli.commands.intake_forms.HttpClient")
    def test_intake_form_writes_are_plan_first_and_delete_requires_ack(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"ok": True})
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = intake_forms.cmd_intake_forms_delete(SimpleNamespace(intake_form_id="form-1"), self._ctx())
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["request"]["method"], "DELETE")
        self.assertEqual(payload["plan"]["selector"], {"intakeFormId": "form-1"})
        self.assertFalse(mock_client.return_value.request.called)

        ctx = self._ctx(apply=True, yes=True, plan_in="/tmp/plan.json", ack_irreversible=False)
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = intake_forms.cmd_intake_forms_delete(SimpleNamespace(intake_form_id="form-1"), ctx)
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertFalse(mock_client.return_value.request.called)

    @patch("wix_safe_agent_cli.commands.intake_form_submissions.HttpClient")
    def test_intake_submission_writes_are_plan_first_and_cancel_requires_ack(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"ok": True})
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = intake_form_submissions.cmd_intake_form_submissions_cancel(
                SimpleNamespace(submission_id="sub-1"),
                self._ctx(),
            )
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["request"]["path"], "/_api/intake-forms/v1/submissions/sub-1/cancel")
        self.assertFalse(mock_client.return_value.request.called)

        ctx = self._ctx(apply=True, yes=True, plan_in="/tmp/plan.json", ack_irreversible=False)
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = intake_form_submissions.cmd_intake_form_submissions_cancel(SimpleNamespace(submission_id="sub-1"), ctx)
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertFalse(mock_client.return_value.request.called)

    @patch("wix_safe_agent_cli.commands.intake_forms.HttpClient")
    def test_update_expiration_period_validates_range(self, mock_client: unittest.mock.MagicMock) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = intake_forms.cmd_intake_forms_update_expiration_period(
                SimpleNamespace(intake_form_id="form-1", expiration_period_in_months=61),
                self._ctx(),
            )
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 1)
        self.assertEqual(payload["error_type"], "ValidationError")
        self.assertFalse(mock_client.return_value.request.called)

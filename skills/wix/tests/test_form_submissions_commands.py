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
from wix_safe_agent_cli.commands import form_submissions
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


class TestFormSubmissionsParser(unittest.TestCase):
    def test_parser_recognizes_form_submissions_commands(self) -> None:
        parser = build_parser()

        get_submission = parser.parse_args(["form-submissions", "get-submission", "--submission-id", "sub-1"])
        self.assertEqual(get_submission.form_submissions_cmd, "get-submission")
        self.assertFalse(get_submission.write_capable)
        self.assertIs(get_submission.func, form_submissions.cmd_form_submissions_get_submission)

        query_submissions = parser.parse_args(
            [
                "form-submissions",
                "query-submissions-by-namespace",
                "--query-json",
                '{"query":{"namespace":"site-1"}}',
            ]
        )
        self.assertEqual(query_submissions.form_submissions_cmd, "query-submissions-by-namespace")
        self.assertFalse(query_submissions.write_capable)
        self.assertIs(query_submissions.func, form_submissions.cmd_form_submissions_query_submissions_by_namespace)

        count_submissions = parser.parse_args(
            [
                "form-submissions",
                "count-submissions",
                "--form-ids-json",
                '["f1", "f2"]',
                "--namespace",
                "site-1",
            ]
        )
        self.assertEqual(count_submissions.form_submissions_cmd, "count-submissions")
        self.assertFalse(count_submissions.write_capable)
        self.assertIs(count_submissions.func, form_submissions.cmd_form_submissions_count_submissions)

        get_media_upload_url = parser.parse_args(
            [
                "form-submissions",
                "get-media-upload-url",
                "--form-id",
                "f1",
                "--filename",
                "resume.pdf",
                "--mime-type",
                "application/pdf",
            ]
        )
        self.assertEqual(get_media_upload_url.form_submissions_cmd, "get-media-upload-url")
        self.assertFalse(get_media_upload_url.write_capable)
        self.assertIs(get_media_upload_url.func, form_submissions.cmd_form_submissions_get_media_upload_url)

        create_submission = parser.parse_args(
            [
                "form-submissions",
                "create-submission",
                "--submission-json",
                '{"formId":"f1","fields":{"name":"Alice"}}',
            ]
        )
        self.assertEqual(create_submission.form_submissions_cmd, "create-submission")
        self.assertTrue(create_submission.write_capable)
        self.assertIs(create_submission.func, form_submissions.cmd_form_submissions_create_submission)

        update_submission = parser.parse_args(
            [
                "form-submissions",
                "update-submission",
                "--submission-json",
                '{"id":"sub-1","formId":"f1","revision":"rev-2","fields":{"name":"Alice"}}',
            ]
        )
        self.assertEqual(update_submission.form_submissions_cmd, "update-submission")
        self.assertTrue(update_submission.write_capable)
        self.assertIs(update_submission.func, form_submissions.cmd_form_submissions_update_submission)

        delete_submission = parser.parse_args(
            [
                "form-submissions",
                "delete-submission",
                "--submission-id",
                "sub-1",
                "--permanent",
                "true",
                "--preserve-files",
                "false",
            ]
        )
        self.assertEqual(delete_submission.form_submissions_cmd, "delete-submission")
        self.assertTrue(delete_submission.write_capable)
        self.assertIs(delete_submission.func, form_submissions.cmd_form_submissions_delete_submission)

        confirm_submission = parser.parse_args(
            [
                "form-submissions",
                "confirm-submission",
                "--submission-id",
                "sub-1",
            ]
        )
        self.assertEqual(confirm_submission.form_submissions_cmd, "confirm-submission")
        self.assertTrue(confirm_submission.write_capable)
        self.assertIs(confirm_submission.func, form_submissions.cmd_form_submissions_confirm_submission)

        bulk_mark = parser.parse_args(
            [
                "form-submissions",
                "bulk-mark-submissions-as-seen",
                "--form-id",
                "f1",
                "--ids-json",
                '["sub-1"]',
            ]
        )
        self.assertEqual(bulk_mark.form_submissions_cmd, "bulk-mark-submissions-as-seen")
        self.assertTrue(bulk_mark.write_capable)
        self.assertIs(
            bulk_mark.func,
            form_submissions.cmd_form_submissions_bulk_mark_submissions_as_seen,
        )


class TestFormSubmissionsCommands(unittest.TestCase):
    def _ctx(self, *, cfg_override: dict | None = None, verbose: bool = False, **overrides) -> dict:
        cfg = SimpleNamespace(
            base_url="https://www.wixapis.com",
            timeout_s=30.0,
            app_id=None,
            app_secret=None,
            instance_id=None,
            access_token="token-abc",
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
            "command_str": "wix-safe-agent-cli form-submissions",
            "apply": False,
            "yes": False,
            "verbose": verbose,
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

    @patch("wix_safe_agent_cli.commands.form_submissions.HttpClient")
    def test_form_submissions_create_apply_refuses_without_plan_in(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.side_effect = [
            _DummyResponse({"site": {"installedWixApps": ["wix_forms"]}}),
            _DummyResponse({"id": "sub-1", "formId": "f1", "revision": "rev-1"}),
        ]
        args = SimpleNamespace(submission_json='{"formId":"f1","fields":{"name":"Alice"}}')
        ctx = self._ctx(apply=True, yes=True)

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = form_submissions.cmd_form_submissions_create_submission(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertEqual(payload["method"], "form-submissions.create-submission")
        methods = [call.kwargs["method"] for call in mock_client.return_value.request.call_args_list]
        self.assertNotIn("POST", methods)

    @patch("wix_safe_agent_cli.commands.form_submissions.HttpClient")
    def test_form_submissions_create_dry_run_plans_expected_body(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"site": {"installedWixApps": ["wix_forms"]}})
        args = SimpleNamespace(submission_json='{"formId":"f1","fields":{"name":"Alice"}}')
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = form_submissions.cmd_form_submissions_create_submission(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["method"], "form-submissions.create-submission")
        self.assertEqual(payload["plan"]["request"]["method"], "POST")
        self.assertEqual(payload["plan"]["request"]["path"], "/form-submission-service/v4/submissions")
        self.assertEqual(payload["plan"]["request"]["body"]["submission"], {"formId": "f1", "fields": {"name": "Alice"}})

    @patch("wix_safe_agent_cli.commands.form_submissions.HttpClient")
    def test_form_submissions_precheck_refuses_when_wix_forms_not_installed(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"site": {"installedWixApps": ["other"]}})
        args = SimpleNamespace(submission_id="sub-1")
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = form_submissions.cmd_form_submissions_get_submission(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error_type"], "ValidationError")
        self.assertIn("wix_forms", payload["error"])
        self.assertEqual(mock_client.return_value.request.call_count, 1)

    @patch("wix_safe_agent_cli.commands.form_submissions.HttpClient")
    def test_form_submissions_get_submission_builds_expected_request(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.side_effect = [
            _DummyResponse({"site": {"installedWixApps": ["wix_forms"]}}),
            _DummyResponse({"id": "sub-1"}),
        ]
        args = SimpleNamespace(submission_id="sub-1")
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = form_submissions.cmd_form_submissions_get_submission(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["request"]["method"], "GET")
        self.assertEqual(payload["request"]["path"], "/form-submission-service/v4/submissions/sub-1")

        self.assertEqual(mock_client.return_value.request.call_count, 2)
        instance_call = mock_client.return_value.request.call_args_list[0]
        submission_call = mock_client.return_value.request.call_args_list[1]
        self.assertEqual(instance_call.kwargs["url"], "https://www.wixapis.com/apps/v1/instance")
        self.assertEqual(submission_call.kwargs["url"], "https://www.wixapis.com/form-submission-service/v4/submissions/sub-1")

    @patch("wix_safe_agent_cli.commands.form_submissions.HttpClient")
    def test_form_submissions_query_submissions_by_namespace_builds_expected_body(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.side_effect = [
            _DummyResponse({"site": {"installedWixApps": ["wix_forms"]}}),
            _DummyResponse({"results": []}),
        ]
        args = SimpleNamespace(
            query_json='{"query":{"filter":{"namespace":"wix.form_app.form","status":"PENDING"}}}',
            only_your_own="true",
        )
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = form_submissions.cmd_form_submissions_query_submissions_by_namespace(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["request"]["method"], "POST")
        self.assertEqual(payload["request"]["path"], "/form-submission-service/v4/submissions/namespace/query")
        self.assertEqual(payload["request"]["body"]["query"]["filter"]["namespace"], "wix.form_app.form")
        self.assertEqual(payload["request"]["body"]["query"]["filter"]["status"], "PENDING")
        self.assertTrue(payload["request"]["body"]["onlyYourOwn"])

    @patch("wix_safe_agent_cli.commands.form_submissions.HttpClient")
    def test_form_submissions_count_submissions_validates_required_counts_and_shapes(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.side_effect = [
            _DummyResponse({"site": {"installedWixApps": ["wix_forms"]}}),
            _DummyResponse({"count": 3}),
        ]
        args = SimpleNamespace(
            form_ids_json='["f1","f2","f3"]',
            namespace="wix.form_app.form",
            statuses_json='["PENDING","CONFIRMED"]',
        )
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = form_submissions.cmd_form_submissions_count_submissions(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["request"]["method"], "POST")
        self.assertEqual(payload["request"]["path"], "/form-submission-service/v4/submissions/count")
        self.assertEqual(payload["request"]["body"]["formIds"], ["f1", "f2", "f3"])
        self.assertEqual(payload["request"]["body"]["namespace"], "wix.form_app.form")
        self.assertEqual(payload["request"]["body"]["statuses"], ["PENDING", "CONFIRMED"])

        count_request_body = mock_client.return_value.request.call_args_list[1].kwargs["json_body"]
        self.assertEqual(count_request_body["formIds"], ["f1", "f2", "f3"])
        self.assertEqual(len(count_request_body["formIds"]), 3)

        bad_args = SimpleNamespace(
            form_ids_json="[]",
            namespace="wix.form_app.form",
            statuses_json='["PENDING","CONFIRMED"]',
        )
        with redirect_stdout(io.StringIO()):
            bad_rc = form_submissions.cmd_form_submissions_count_submissions(bad_args, ctx)
        self.assertEqual(bad_rc, 1)

    @patch("wix_safe_agent_cli.commands.form_submissions.HttpClient")
    def test_form_submissions_get_media_upload_url_builds_expected_body(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.side_effect = [
            _DummyResponse({"site": {"installedWixApps": ["wix_forms"]}}),
            _DummyResponse({"url": "https://upload.example.com/file"}),
        ]
        args = SimpleNamespace(form_id="f1", filename="resume.pdf", mime_type="application/pdf")
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = form_submissions.cmd_form_submissions_get_media_upload_url(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["request"]["method"], "POST")
        self.assertEqual(payload["request"]["path"], "/form-submission-service/v4/submissions/media-upload-url")
        self.assertEqual(payload["request"]["body"]["formId"], "f1")
        self.assertEqual(payload["request"]["body"]["filename"], "resume.pdf")
        self.assertEqual(payload["request"]["body"]["mimeType"], "application/pdf")

    @patch("wix_safe_agent_cli.commands.form_submissions.HttpClient")
    def test_form_submissions_update_apply_refuses_without_plan_in(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.side_effect = [
            _DummyResponse({"site": {"installedWixApps": ["wix_forms"]}}),
            _DummyResponse({"id": "sub-1", "formId": "f1", "revision": "rev-1"}),
        ]
        args = SimpleNamespace(submission_json='{"id":"sub-1","formId":"f1","revision":"rev-2","fields":{"name":"Alice"}}')
        ctx = self._ctx(apply=True, yes=True)

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = form_submissions.cmd_form_submissions_update_submission(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        methods = [call.kwargs["method"] for call in mock_client.return_value.request.call_args_list]
        self.assertNotIn("PATCH", methods)

    @patch("wix_safe_agent_cli.commands.form_submissions.HttpClient")
    def test_form_submissions_update_dry_run_plans_expected_path_and_revision(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.side_effect = [
            _DummyResponse({"site": {"installedWixApps": ["wix_forms"]}}),
            _DummyResponse({"id": "sub-1", "formId": "f1", "revision": "rev-2"}),
        ]
        args = SimpleNamespace(submission_json='{"id":"sub-1","formId":"f1","revision":"rev-2","fields":{"name":"Alice"}}')
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = form_submissions.cmd_form_submissions_update_submission(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["request"]["method"], "PATCH")
        self.assertEqual(payload["plan"]["request"]["path"], "/form-submission-service/v4/submissions/sub-1")
        self.assertEqual(payload["plan"]["request"]["body"]["submission"]["revision"], "rev-2")

    @patch("wix_safe_agent_cli.commands.form_submissions.HttpClient")
    def test_form_submissions_update_refuses_stale_revision(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.side_effect = [
            _DummyResponse({"site": {"installedWixApps": ["wix_forms"]}}),
            _DummyResponse({"id": "sub-1", "formId": "f1", "revision": "rev-2"}),
        ]
        args = SimpleNamespace(submission_json='{"id":"sub-1","formId":"f1","revision":"rev-1","fields":{"name":"Alice"}}')
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = form_submissions.cmd_form_submissions_update_submission(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertIn("stale", payload["reasons"][0])

    @patch("wix_safe_agent_cli.commands.form_submissions.HttpClient")
    def test_form_submissions_delete_apply_refuses_without_plan_in(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.side_effect = [
            _DummyResponse({"site": {"installedWixApps": ["wix_forms"]}}),
            _DummyResponse({"id": "sub-1", "formId": "f1", "revision": "rev-1"}),
        ]
        args = SimpleNamespace(submission_id="sub-1", permanent="true", preserve_files="false")
        ctx = self._ctx(apply=True, yes=True, ack_irreversible=True)

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = form_submissions.cmd_form_submissions_delete_submission(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        methods = [call.kwargs["method"] for call in mock_client.return_value.request.call_args_list]
        self.assertNotIn("DELETE", methods)

    @patch("wix_safe_agent_cli.commands.form_submissions.HttpClient")
    def test_form_submissions_delete_apply_refuses_without_ack_irreversible(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.side_effect = [
            _DummyResponse({"site": {"installedWixApps": ["wix_forms"]}}),
            _DummyResponse({"id": "sub-1", "formId": "f1", "revision": "rev-1"}),
        ]
        plan = {
            "method": "form-submissions.delete-submission",
            "baseline": {
                "env_fingerprint": "https://www.wixapis.com",
                "selector": {
                    "kind": "wix-form-submission",
                    "operation": "delete",
                    "submission_id": "sub-1",
                },
                "before_state": {"submission": {"id": "sub-1", "formId": "f1", "revision": "rev-1"}},
            },
            "selector": {
                "kind": "wix-form-submission",
                "operation": "delete",
                "submission_id": "sub-1",
            },
            "request": {
                "method": "DELETE",
                "path": "/form-submission-service/v4/submissions/sub-1",
                "params": {},
            },
            "proposed_changes": [{"operation": "delete-submission", "submission_id": "sub-1"}],
        }
        plan_path = self._write_plan(plan)
        try:
            args = SimpleNamespace(submission_id="sub-1", permanent="true", preserve_files="false")
            ctx = self._ctx(apply=True, yes=True, plan_in=plan_path, ack_irreversible=False)

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = form_submissions.cmd_form_submissions_delete_submission(args, ctx)
            payload = json.loads(buf.getvalue())

            self.assertEqual(rc, 0)
            self.assertTrue(payload["refused"])
            self.assertIn("--ack-irreversible", payload["reasons"][0])
        finally:
            Path(plan_path).unlink()

    @patch("wix_safe_agent_cli.commands.form_submissions.HttpClient")
    def test_form_submissions_confirm_apply_refuses_without_plan_in(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.side_effect = [
            _DummyResponse({"site": {"installedWixApps": ["wix_forms"]}}),
            _DummyResponse({"id": "sub-1", "formId": "f1", "status": "PENDING"}),
        ]
        args = SimpleNamespace(submission_id="sub-1")
        ctx = self._ctx(apply=True, yes=True)

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = form_submissions.cmd_form_submissions_confirm_submission(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        methods = [call.kwargs["method"] for call in mock_client.return_value.request.call_args_list]
        self.assertNotIn("POST", methods)

    @patch("wix_safe_agent_cli.commands.form_submissions.HttpClient")
    def test_form_submissions_confirm_refuses_when_status_is_not_pending(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.side_effect = [
            _DummyResponse({"site": {"installedWixApps": ["wix_forms"]}}),
            _DummyResponse({"id": "sub-1", "formId": "f1", "status": "CONFIRMED"}),
        ]
        args = SimpleNamespace(submission_id="sub-1")
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = form_submissions.cmd_form_submissions_confirm_submission(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertIn("PENDING", payload["reasons"][0])

    @patch("wix_safe_agent_cli.commands.form_submissions.HttpClient")
    def test_form_submissions_bulk_mark_submissions_as_seen_apply_refuses_without_plan_in(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.side_effect = [
            _DummyResponse({"site": {"installedWixApps": ["wix_forms"]}}),
            _DummyResponse({"id": "sub-1", "formId": "f1"}),
        ]
        args = SimpleNamespace(form_id="f1", ids_json='["sub-1"]', all_unseen=False)
        ctx = self._ctx(apply=True, yes=True)

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = form_submissions.cmd_form_submissions_bulk_mark_submissions_as_seen(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        methods = [call.kwargs["method"] for call in mock_client.return_value.request.call_args_list]
        self.assertNotIn("POST", methods)

    @patch("wix_safe_agent_cli.commands.form_submissions.HttpClient")
    def test_form_submissions_bulk_mark_submissions_as_seen_refuses_without_ids_and_all_unseen(self, mock_client: unittest.mock.MagicMock) -> None:
        args = SimpleNamespace(form_id="f1", ids_json='[]', all_unseen=False)
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = form_submissions.cmd_form_submissions_bulk_mark_submissions_as_seen(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertEqual(mock_client.return_value.request.call_count, 0)

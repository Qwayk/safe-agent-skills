from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import faq_category_v2, faq_question_entry_v2
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = (action, payload)


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestFaqAppCommands(unittest.TestCase):
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
            "command_str": "wix-safe-agent-cli faq",
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

    def test_parser_recognizes_faq_subcommands_when_registered(self) -> None:
        parser = build_parser()
        cases = [
            ["faq-category-v2", "list"],
            ["faq-category-v2", "get", "--category-id", "cat-1"],
            ["faq-category-v2", "query", "--query-json", "{}"],
            ["faq-category-v2", "create", "--category-json", '{"title":"Shipping"}'],
            ["faq-category-v2", "update", "--category-json", '{"id":"cat-1","revision":"2"}'],
            ["faq-category-v2", "delete", "--category-id", "cat-1"],
            ["faq-category-v2", "update-extended-fields", "--category-id", "cat-1", "--extended-fields-json", "{}"],
            ["faq-question-entry-v2", "list"],
            ["faq-question-entry-v2", "get", "--question-entry-id", "qe-1"],
            ["faq-question-entry-v2", "query", "--query-json", "{}"],
            ["faq-question-entry-v2", "create", "--question-entry-json", '{"question":"Q","categoryId":"cat-1"}'],
            ["faq-question-entry-v2", "update", "--question-entry-json", '{"id":"qe-1","revision":"3"}'],
            ["faq-question-entry-v2", "delete", "--question-entry-id", "qe-1"],
            ["faq-question-entry-v2", "bulk-delete", "--question-entries-json", '{"questionEntryIds":["qe-1"]}'],
            ["faq-question-entry-v2", "bulk-update", "--question-entries-json", '{"questionEntries":[{"id":"qe-1","revision":"3"}]}'],
            ["faq-question-entry-v2", "set-labels", "--question-entry-id", "qe-1", "--labels-json", '{"labels":[]}'],
            ["faq-question-entry-v2", "update-extended-fields", "--question-entry-id", "qe-1", "--extended-fields-json", "{}"],
        ]
        for argv in cases:
            with self.subTest(argv=argv):
                args = parser.parse_args(argv)
                self.assertTrue(callable(args.func))

    @patch("wix_safe_agent_cli.commands.faq_category_v2.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.faq_category_v2.HttpClient")
    def test_category_reads_use_official_paths(self, mock_client, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"category": {"id": "cat-1"}})
        cases = [
            (faq_category_v2.cmd_faq_category_v2_list, SimpleNamespace(), "GET", "/faq/v2/categories"),
            (faq_category_v2.cmd_faq_category_v2_get, SimpleNamespace(category_id="cat-1"), "GET", "/faq/v2/categories/cat-1"),
            (faq_category_v2.cmd_faq_category_v2_query, SimpleNamespace(query_json='{"filter":{}}'), "POST", "/faq/v2/categories/query"),
        ]
        for func, args, method, path in cases:
            with self.subTest(path=path):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = func(args, self._ctx())
                payload = json.loads(buf.getvalue())
                self.assertEqual(rc, 0)
                self.assertEqual(payload["request"]["method"], method)
                self.assertEqual(payload["request"]["path"], path)
        self.assertEqual(mock_auth.call_args.kwargs["command_family"], "faq-category-v2")

    @patch("wix_safe_agent_cli.commands.faq_category_v2.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.faq_category_v2.HttpClient")
    def test_category_writes_build_plans_and_delete_requires_ack(self, mock_client, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        cases = [
            (faq_category_v2.cmd_faq_category_v2_create, SimpleNamespace(category_json='{"title":"Shipping"}'), "POST", "/faq/v2/categories", False),
            (
                faq_category_v2.cmd_faq_category_v2_update,
                SimpleNamespace(category_json='{"id":"cat-1","revision":"2","title":"Returns"}'),
                "PATCH",
                "/faq/v2/categories/cat-1",
                False,
            ),
            (faq_category_v2.cmd_faq_category_v2_delete, SimpleNamespace(category_id="cat-1"), "DELETE", "/faq/v2/categories/cat-1", True),
            (
                faq_category_v2.cmd_faq_category_v2_update_extended_fields,
                SimpleNamespace(category_id="cat-1", extended_fields_json='{"extendedFields":{}}'),
                "POST",
                "/faq/v2/categories/cat-1/update-extended-fields",
                False,
            ),
        ]
        for func, args, method, path, requires_ack in cases:
            with self.subTest(path=path):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = func(args, self._ctx())
                payload = json.loads(buf.getvalue())
                self.assertEqual(rc, 0)
                self.assertTrue(payload["dry_run"])
                self.assertEqual(payload["plan"]["request"]["method"], method)
                self.assertEqual(payload["plan"]["request"]["path"], path)
                self.assertEqual("apply also requires --ack-irreversible" in payload["plan"]["preconditions"], requires_ack)
        mock_client.return_value.request.assert_not_called()

    @patch("wix_safe_agent_cli.commands.faq_category_v2.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.faq_category_v2.HttpClient")
    def test_question_entry_paths_and_safety(self, mock_client, mock_auth) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"questionEntry": {"id": "qe-1"}})
        read_cases = [
            (faq_question_entry_v2.cmd_faq_question_entry_v2_list, SimpleNamespace(), "GET", "/faq/v2/question-entries"),
            (
                faq_question_entry_v2.cmd_faq_question_entry_v2_get,
                SimpleNamespace(question_entry_id="qe-1"),
                "GET",
                "/faq/v2/question-entries/qe-1",
            ),
            (
                faq_question_entry_v2.cmd_faq_question_entry_v2_query,
                SimpleNamespace(query_json="{}"),
                "POST",
                "/faq/v2/question-entries/query",
            ),
        ]
        for func, args, method, path in read_cases:
            with self.subTest(path=path):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = func(args, self._ctx())
                payload = json.loads(buf.getvalue())
                self.assertEqual(rc, 0)
                self.assertEqual(payload["request"]["method"], method)
                self.assertEqual(payload["request"]["path"], path)
        self.assertEqual(mock_auth.call_args.kwargs["command_family"], "faq-question-entry-v2")

        write_cases = [
            (
                faq_question_entry_v2.cmd_faq_question_entry_v2_create,
                SimpleNamespace(question_entry_json='{"question":"Q","categoryId":"cat-1"}'),
                "POST",
                "/faq/v2/question-entries",
                False,
            ),
            (
                faq_question_entry_v2.cmd_faq_question_entry_v2_update,
                SimpleNamespace(question_entry_json='{"id":"qe-1","revision":"3","question":"Q"}'),
                "PATCH",
                "/faq/v2/question-entries/qe-1",
                False,
            ),
            (
                faq_question_entry_v2.cmd_faq_question_entry_v2_delete,
                SimpleNamespace(question_entry_id="qe-1"),
                "DELETE",
                "/faq/v2/question-entries/qe-1",
                True,
            ),
            (
                faq_question_entry_v2.cmd_faq_question_entry_v2_bulk_delete,
                SimpleNamespace(question_entries_json='{"questionEntryIds":["qe-1"]}'),
                "POST",
                "/faq/question-entry/v2/bulk/question-entries/delete",
                True,
            ),
            (
                faq_question_entry_v2.cmd_faq_question_entry_v2_bulk_update,
                SimpleNamespace(question_entries_json='{"questionEntries":[{"id":"qe-1","revision":"3"}]}'),
                "POST",
                "/faq/question-entry/v2/bulk/question-entries/update",
                False,
            ),
            (
                faq_question_entry_v2.cmd_faq_question_entry_v2_set_labels,
                SimpleNamespace(question_entry_id="qe-1", labels_json='{"labels":[]}'),
                "PATCH",
                "/faq/v2/question-entries/qe-1/labels",
                False,
            ),
            (
                faq_question_entry_v2.cmd_faq_question_entry_v2_update_extended_fields,
                SimpleNamespace(question_entry_id="qe-1", extended_fields_json='{"extendedFields":{}}'),
                "POST",
                "/faq/v2/question-entries/qe-1/update-extended-fields",
                False,
            ),
        ]
        for func, args, method, path, requires_ack in write_cases:
            with self.subTest(path=path):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = func(args, self._ctx())
                payload = json.loads(buf.getvalue())
                self.assertEqual(rc, 0)
                self.assertTrue(payload["dry_run"])
                self.assertEqual(payload["plan"]["request"]["method"], method)
                self.assertEqual(payload["plan"]["request"]["path"], path)
                self.assertEqual("apply also requires --ack-irreversible" in payload["plan"]["preconditions"], requires_ack)

    def test_updates_require_revision(self) -> None:
        cases = [
            (faq_category_v2.cmd_faq_category_v2_update, SimpleNamespace(category_json='{"id":"cat-1"}')),
            (faq_question_entry_v2.cmd_faq_question_entry_v2_update, SimpleNamespace(question_entry_json='{"id":"qe-1"}')),
        ]
        for func, args in cases:
            with self.subTest(func=func.__name__):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = func(args, self._ctx())
                payload = json.loads(buf.getvalue())
                self.assertEqual(rc, 1)
                self.assertEqual(payload["error_type"], "ValidationError")

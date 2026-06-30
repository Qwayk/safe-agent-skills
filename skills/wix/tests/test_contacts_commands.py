from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import contacts
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


class TestContactsCommands(unittest.TestCase):
    def _ctx(self, *, cfg_override: dict | None = None, verbose: bool = False) -> dict:
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
        return {
            "cfg": cfg,
            "env_file": "/tmp/.env",
            "verbose": verbose,
            "out": Output(mode="json"),
            "audit": _DummyAudit(),
            "tool": "wix-safe-agent-cli",
            "tool_version": "0.0.0",
            "command_str": "wix-safe-agent-cli contacts",
            "apply": False,
            "yes": False,
            "plan_in": None,
            "plan_out": None,
            "receipt_out": None,
            "ack_irreversible": False,
            "enforce_reviewed_plan": True,
        }

    @patch("wix_safe_agent_cli.commands.contacts.HttpClient")
    def test_contacts_list_builds_expected_request(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse(
            {"contacts": [{"id": "c1"}], "pagingMetadata": {"count": 1}}
        )
        args = SimpleNamespace(
            limit=5,
            offset=1,
            sort_json='{"fieldName":"createdDate","order":"DESC"}',
            fields_json='["primaryInfo.email"]',
            fieldsets_json='["FULL"]',
        )
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = contacts.cmd_contacts_list(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["request"]["method"], "GET")
        self.assertEqual(payload["request"]["path"], "/contacts/v4/contacts")
        self.assertEqual(payload["request"]["params"]["paging.limit"], 5)
        self.assertEqual(payload["request"]["params"]["paging.offset"], 1)
        self.assertEqual(payload["request"]["params"]["sort.fieldName"], "createdDate")
        self.assertEqual(payload["request"]["params"]["sort.order"], "DESC")

    @patch("wix_safe_agent_cli.commands.contacts.HttpClient")
    def test_contacts_get_builds_expected_request(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"id": "c1", "revision": "1"})
        args = SimpleNamespace(contact_id="c1", fields_json='["primaryInfo"]', fieldsets_json=None)
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = contacts.cmd_contacts_get(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["request"]["path"], "/contacts/v4/contacts/c1")
        self.assertEqual(payload["request"]["params"]["fields"], ["primaryInfo"])

    @patch("wix_safe_agent_cli.commands.contacts.HttpClient")
    def test_contacts_query_builds_expected_request(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse(
            {"contacts": [{"id": "c1"}], "pagingMetadata": {"count": 1}}
        )
        args = SimpleNamespace(
            query_json=None,
            filter_json='{"info.name.last":"Smith"}',
            sort_json='{"fieldName":"createdDate","order":"ASC"}',
            search="Smith",
            fields_json='["primaryInfo.email"]',
            limit=4,
            offset=2,
        )
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = contacts.cmd_contacts_query(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["request"]["method"], "POST")
        self.assertEqual(payload["request"]["path"], "/contacts/v4/contacts/query")
        body = payload["request"]["body"]
        self.assertEqual(body["query"]["search"], "Smith")
        self.assertEqual(body["query"]["filter"]["info.name.last"], "Smith")
        self.assertEqual(body["query"]["paging"]["limit"], 4)

    @patch("wix_safe_agent_cli.commands.contacts.HttpClient")
    def test_contacts_v4_extra_reads_use_official_paths(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"ok": True})
        cases = [
            (
                contacts.cmd_contacts_list_facets,
                SimpleNamespace(),
                "GET",
                "/contacts/v4/contacts/facets",
                None,
            ),
            (
                contacts.cmd_contacts_query_facets,
                SimpleNamespace(query_json='{"filter":{"info.emails.subscriptionStatus.email":{"$eq":"SUBSCRIBED"}}}'),
                "POST",
                "/contacts/v4/contacts/facets/query",
                {"query": {"filter": {"info.emails.subscriptionStatus.email": {"$eq": "SUBSCRIBED"}}}},
            ),
            (
                contacts.cmd_contacts_get_bulk_job,
                SimpleNamespace(job_id="job-1"),
                "GET",
                "/contacts/v4/bulk/jobs/job-1",
                None,
            ),
            (
                contacts.cmd_contacts_preview_merge,
                SimpleNamespace(target_contact_id="target-1", merge_json='{"sourceContactIds":["source-1"]}'),
                "POST",
                "/contacts/v4/contacts/target-1/preview-merge",
                {"sourceContactIds": ["source-1"]},
            ),
        ]
        for func, args, method, path, body in cases:
            with self.subTest(path=path):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = func(args, self._ctx())
                payload = json.loads(buf.getvalue())
                self.assertEqual(rc, 0)
                self.assertEqual(payload["request"]["method"], method)
                self.assertEqual(payload["request"]["path"], path)
                if body is not None:
                    self.assertEqual(payload["request"]["body"], body)

    @patch("wix_safe_agent_cli.commands.contacts.HttpClient")
    def test_contacts_v4_writes_are_plan_first_with_expected_ack(self, mock_client: unittest.mock.MagicMock) -> None:
        cases = [
            (
                contacts.cmd_contacts_create,
                SimpleNamespace(contact_json='{"info":{"name":{"first":"Ada"}}}'),
                "POST",
                "/contacts/v4/contacts",
                False,
            ),
            (
                contacts.cmd_contacts_update,
                SimpleNamespace(contact_id="contact-1", contact_json='{"contact":{"revision":"1","info":{"name":{"first":"Ada"}}}}'),
                "PATCH",
                "/contacts/v4/contacts/contact-1",
                False,
            ),
            (
                contacts.cmd_contacts_delete,
                SimpleNamespace(contact_id="contact-1"),
                "DELETE",
                "/contacts/v4/contacts/contact-1",
                True,
            ),
            (
                contacts.cmd_contacts_merge,
                SimpleNamespace(target_contact_id="target-1", merge_json='{"sourceContactIds":["source-1"]}'),
                "POST",
                "/contacts/v4/contacts/target-1/merge",
                True,
            ),
            (
                contacts.cmd_contacts_label,
                SimpleNamespace(contact_id="contact-1", labels_json='{"labelKeys":["custom.vip"]}'),
                "POST",
                "/contacts/v4/contacts/contact-1/labels",
                False,
            ),
            (
                contacts.cmd_contacts_unlabel,
                SimpleNamespace(contact_id="contact-1", labels_json='{"labelKeys":["custom.vip"]}'),
                "DELETE",
                "/contacts/v4/contacts/contact-1/labels",
                False,
            ),
            (
                contacts.cmd_contacts_bulk_delete,
                SimpleNamespace(bulk_json='{"filter":{"id":{"$in":["contact-1"]}}}'),
                "POST",
                "/contacts/v4/bulk/contacts/delete",
                True,
            ),
            (
                contacts.cmd_contacts_bulk_update,
                SimpleNamespace(bulk_json='{"filter":{"id":{"$in":["contact-1"]}},"fieldMask":{"paths":["info.name.first"]}}'),
                "POST",
                "/contacts/v4/bulk/contacts/update",
                True,
            ),
            (
                contacts.cmd_contacts_bulk_label_unlabel,
                SimpleNamespace(bulk_json='{"filter":{"id":{"$in":["contact-1"]}},"labelKeysToAdd":["custom.vip"]}'),
                "POST",
                "/contacts/v4/bulk/contacts/add-remove-labels",
                True,
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
                preconditions = payload["plan"]["preconditions"]
                self.assertEqual("apply also requires --ack-irreversible" in preconditions, requires_ack)

        mock_client.return_value.request.assert_not_called()

    def test_contacts_update_requires_revision(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = contacts.cmd_contacts_update(
                SimpleNamespace(contact_id="contact-1", contact_json='{"contact":{"info":{"name":{"first":"Ada"}}}}'),
                self._ctx(),
            )
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 1)
        self.assertEqual(payload["error_type"], "ValidationError")
        self.assertIn("contact.revision", payload["error"])

    def test_parser_exposes_contacts_v4_expansion(self) -> None:
        parser = build_parser()
        cases = [
            (["contacts", "list-facets"], contacts.cmd_contacts_list_facets, False),
            (["contacts", "query-facets", "--query-json", "{}"], contacts.cmd_contacts_query_facets, False),
            (["contacts", "get-bulk-job", "--job-id", "job-1"], contacts.cmd_contacts_get_bulk_job, False),
            (
                ["contacts", "preview-merge", "--target-contact-id", "target-1", "--merge-json", "{}"],
                contacts.cmd_contacts_preview_merge,
                False,
            ),
            (["contacts", "create", "--contact-json", "{}"], contacts.cmd_contacts_create, True),
            (
                ["contacts", "update", "--contact-id", "contact-1", "--contact-json", "{}"],
                contacts.cmd_contacts_update,
                True,
            ),
            (["contacts", "delete", "--contact-id", "contact-1"], contacts.cmd_contacts_delete, True),
            (
                ["contacts", "merge", "--target-contact-id", "target-1", "--merge-json", "{}"],
                contacts.cmd_contacts_merge,
                True,
            ),
            (["contacts", "label", "--contact-id", "contact-1", "--labels-json", "{}"], contacts.cmd_contacts_label, True),
            (["contacts", "unlabel", "--contact-id", "contact-1", "--labels-json", "{}"], contacts.cmd_contacts_unlabel, True),
            (["contacts", "bulk-delete", "--bulk-json", "{}"], contacts.cmd_contacts_bulk_delete, True),
            (["contacts", "bulk-update", "--bulk-json", "{}"], contacts.cmd_contacts_bulk_update, True),
            (["contacts", "bulk-label-unlabel", "--bulk-json", "{}"], contacts.cmd_contacts_bulk_label_unlabel, True),
        ]
        for argv, func, write_capable in cases:
            with self.subTest(argv=argv):
                args = parser.parse_args(argv)
                self.assertIs(args.func, func)
                self.assertEqual(args.write_capable, write_capable)

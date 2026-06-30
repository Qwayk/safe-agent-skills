from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.commands import members
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


class TestMembersCommands(unittest.TestCase):
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
            "apply": False,
            "yes": False,
            "ack_irreversible": False,
            "enforce_reviewed_plan": True,
        }

    @patch("wix_safe_agent_cli.commands.members.HttpClient")
    def test_members_list_builds_expected_request(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse(
            {"members": [{"id": "m1"}], "pagingMetadata": {"count": 1}}
        )
        args = SimpleNamespace(
            limit=10,
            offset=2,
            sort_json='{"fieldName":"createdDate","order":"ASC"}',
            fieldsets_json='["FULL", "PRIVATE"]',
        )
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = members.cmd_members_list(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["request"]["method"], "GET")
        self.assertEqual(payload["request"]["path"], "/members/v1/members")
        self.assertEqual(payload["request"]["params"]["paging.limit"], 10)
        self.assertEqual(payload["request"]["params"]["paging.offset"], 2)
        self.assertEqual(payload["request"]["params"]["sort.fieldName"], "createdDate")
        self.assertEqual(payload["request"]["params"]["sort.order"], "ASC")
        self.assertEqual(payload["request"]["params"]["fieldsets"], ["FULL", "PRIVATE"])

    @patch("wix_safe_agent_cli.commands.members.HttpClient")
    def test_members_get_builds_expected_request(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"id": "m1", "status": "approved"})
        args = SimpleNamespace(member_id="m1", fieldsets_json='["FULL"]')
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = members.cmd_members_get(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["request"]["method"], "GET")
        self.assertEqual(payload["request"]["path"], "/members/v1/members/m1")
        self.assertEqual(payload["request"]["params"], {"fieldsets": ["FULL"]})

    @patch("wix_safe_agent_cli.commands.members.HttpClient")
    def test_members_query_builds_expected_request(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse(
            {"members": [{"id": "m1"}], "pagingMetadata": {"count": 1}}
        )
        args = SimpleNamespace(
            query_json='{"filter":{"contactId":{"$eq":"c1"}}}',
            fieldsets_json='["FULL"]',
        )
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = members.cmd_members_query(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["request"]["method"], "POST")
        self.assertEqual(payload["request"]["path"], "/members/v1/members/query")
        body = payload["request"]["body"]
        self.assertEqual(body["query"]["fieldsets"], ["FULL"])
        self.assertEqual(body["query"]["filter"]["contactId"]["$eq"], "c1")

    def test_members_create_dry_run_builds_reviewed_plan(self) -> None:
        args = SimpleNamespace(member_json='{"member":{"loginEmail":"a@example.com"}}')
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = members.cmd_members_create(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["method"], "members.create")
        self.assertEqual(payload["plan"]["request"]["method"], "POST")
        self.assertEqual(payload["plan"]["request"]["path"], "/members/v1/members")
        self.assertEqual(payload["plan"]["request"]["body"]["member"]["loginEmail"], "a@example.com")

    @patch("wix_safe_agent_cli.commands.members.HttpClient")
    def test_members_get_my_builds_expected_request(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"member": {"id": "m1"}})
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = members.cmd_members_get_my(SimpleNamespace(), ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["request"], {"method": "GET", "path": "/members/v1/members/my"})

    def test_members_delete_requires_irreversible_ack_for_apply(self) -> None:
        args = SimpleNamespace(member_id="m1")
        ctx = self._ctx()
        ctx.update({"apply": True, "yes": True, "plan_in": "/tmp/plan.json", "ack_irreversible": False})

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = members.cmd_members_delete(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["request"]["method"], "DELETE")
        self.assertEqual(payload["plan"]["request"]["path"], "/members/v1/members/m1")

    def test_members_disconnect_plan_marks_irreversible(self) -> None:
        args = SimpleNamespace(member_id="m1")
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = members.cmd_members_disconnect(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["risk_level"], "high")
        self.assertIn("official-docs-say-disconnect-is-irreversible", payload["plan"]["risk_reasons"])
        self.assertEqual(payload["plan"]["request"]["path"], "/members/v1/members/m1/disconnect")

    def test_members_bulk_delete_by_filter_uses_official_path(self) -> None:
        args = SimpleNamespace(filter_json='{"filter":{"status":"PENDING"}}')
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = members.cmd_members_bulk_delete_by_filter(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["method"], "members.bulk-delete-by-filter")
        self.assertEqual(payload["plan"]["request"]["path"], "/members/v1/members/bulk/delete-by-filter")
        self.assertEqual(payload["plan"]["request"]["body"]["filter"]["status"], "PENDING")

    def test_members_clear_emails_uses_official_delete_endpoint(self) -> None:
        args = SimpleNamespace(member_id="m1")
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = members.cmd_members_delete_emails(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["request"]["method"], "DELETE")
        self.assertEqual(payload["plan"]["request"]["path"], "/members/v1/members/m1/emails")

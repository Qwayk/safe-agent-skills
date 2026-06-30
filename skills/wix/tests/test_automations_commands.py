from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import automation_storage_items, automations_v2
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = action, payload


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestAutomationsCommands(unittest.TestCase):
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
            "command_str": "wix-safe-agent-cli automations",
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

    def test_parser_exposes_storage_and_automations_commands(self) -> None:
        parser = build_parser()
        cases = [
            (["automation-storage-items", "create", "--storage-item-json", '{"storageItem":{"key":"k","displayName":"K","type":"STRING","stringValue":{"value":"v"}}}'], "automation_storage_items_cmd", "create", True),
            (["automation-storage-items", "get", "--key", "k"], "automation_storage_items_cmd", "get", False),
            (["automation-storage-items", "query", "--query-json", "{}"], "automation_storage_items_cmd", "query", False),
            (["automation-storage-items", "bulk-update-tags", "--tags-json", '{"storageItemIds":["id1"],"assignTags":{"publicTags":{"tagIds":["t1"]}}}'], "automation_storage_items_cmd", "bulk-update-tags", True),
            (["automation-storage-items", "bulk-update-tags-by-filter", "--tags-json", '{"filter":{},"assignTags":{"publicTags":{"tagIds":["t1"]}}}'], "automation_storage_items_cmd", "bulk-update-tags-by-filter", True),
            (["automation-storage-items", "update-counter-by", "--key", "k", "--value", "1"], "automation_storage_items_cmd", "update-counter-by", True),
            (["automation-storage-items", "update-value", "--key", "k", "--value-json", '{"stringValue":"v"}'], "automation_storage_items_cmd", "update-value", True),
            (["automations-v2", "create", "--automation-json", '{"automation":{"name":"A","origin":"APPLICATION"}}'], "automations_v2_cmd", "create", True),
            (["automations-v2", "get", "--automation-id", "a1"], "automations_v2_cmd", "get", False),
            (["automations-v2", "update", "--automation-json", '{"automation":{"id":"a1","revision":"1"}}'], "automations_v2_cmd", "update", True),
            (["automations-v2", "delete", "--automation-id", "a1"], "automations_v2_cmd", "delete", True),
            (["automations-v2", "query", "--query-json", "{}"], "automations_v2_cmd", "query", False),
            (["automations-v2", "validate", "--automation-json", '{"automation":{"name":"A"}}'], "automations_v2_cmd", "validate", False),
        ]
        for argv, dest, command, write_capable in cases:
            with self.subTest(command=command):
                args = parser.parse_args(argv)
                self.assertEqual(getattr(args, dest), command)
                self.assertEqual(args.write_capable, write_capable)

    @patch("wix_safe_agent_cli.commands.community_groups.HttpClient")
    def test_reads_use_official_paths(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse({"ok": True})
        cases = [
            (automation_storage_items.cmd_automation_storage_items_get, SimpleNamespace(key="k", consistent_read="true"), "GET", "/storage-service/v1/storage-items/k", {"consistentRead": True}),
            (automation_storage_items.cmd_automation_storage_items_query, SimpleNamespace(query_json="{}"), "POST", "/storage-service/v1/storage-items/query", None),
            (automations_v2.cmd_automations_v2_get, SimpleNamespace(automation_id="a1"), "GET", "/automations-service/v2/automations/a1", None),
            (automations_v2.cmd_automations_v2_query, SimpleNamespace(query_json="{}"), "POST", "/automations-service/v2/automations/query", None),
            (automations_v2.cmd_automations_v2_validate, SimpleNamespace(automation_json='{"automation":{"name":"A"}}'), "POST", "/automations-service/v2/automations/validate", None),
        ]
        for func, args, http_method, path, params in cases:
            with self.subTest(path=path):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = func(args, self._ctx())
                payload = json.loads(buf.getvalue())
                self.assertEqual(rc, 0)
                self.assertEqual(payload["request"]["method"], http_method)
                self.assertEqual(payload["request"]["path"], path)
                if params is not None:
                    self.assertEqual(payload["request"]["params"], params)

    @patch("wix_safe_agent_cli.commands.community_groups.HttpClient")
    def test_writes_plan_first_and_ack_when_needed(self, mock_client: unittest.mock.MagicMock) -> None:
        cases = [
            (automation_storage_items.cmd_automation_storage_items_create, SimpleNamespace(storage_item_json='{"storageItem":{"key":"k","displayName":"K","type":"STRING","stringValue":{"value":"v"}}}'), "POST", "/storage-service/v1/storage-items", False),
            (automation_storage_items.cmd_automation_storage_items_bulk_update_tags, SimpleNamespace(tags_json='{"storageItemIds":["id1"],"assignTags":{"publicTags":{"tagIds":["t1"]}}}'), "POST", "/storage-service/v1/bulk/storage-items/update-tags", False),
            (automation_storage_items.cmd_automation_storage_items_bulk_update_tags_by_filter, SimpleNamespace(tags_json='{"filter":{},"assignTags":{"publicTags":{"tagIds":["t1"]}}}'), "POST", "/storage-service/v1/bulk/storage-items/update-tags-by-filter", True),
            (automation_storage_items.cmd_automation_storage_items_update_counter_by, SimpleNamespace(key="k", value="1"), "PATCH", "/storage-service/v1/storage-items/k/update-counter-by", False),
            (automation_storage_items.cmd_automation_storage_items_update_value, SimpleNamespace(key="k", value_json='{"stringValue":"v"}'), "PATCH", "/storage-service/v1/storage-items/k/update-value", False),
            (automations_v2.cmd_automations_v2_create, SimpleNamespace(automation_json='{"automation":{"name":"A","origin":"APPLICATION"}}'), "POST", "/automations-service/v2/automations", True),
            (automations_v2.cmd_automations_v2_update, SimpleNamespace(automation_json='{"automation":{"id":"a1","revision":"1"}}'), "PATCH", "/automations-service/v2/automations/a1", True),
            (automations_v2.cmd_automations_v2_delete, SimpleNamespace(automation_id="a1"), "DELETE", "/automations-service/v2/automations/a1", True),
        ]
        for func, args, http_method, path, needs_ack in cases:
            with self.subTest(path=path):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = func(args, self._ctx())
                payload = json.loads(buf.getvalue())
                self.assertEqual(rc, 0)
                self.assertTrue(payload["dry_run"])
                self.assertEqual(payload["plan"]["request"]["method"], http_method)
                self.assertEqual(payload["plan"]["request"]["path"], path)
                if needs_ack:
                    self.assertIn("apply also requires --ack-irreversible", payload["plan"]["preconditions"])
                self.assertFalse(mock_client.return_value.request.called)

    @patch("wix_safe_agent_cli.commands.community_groups.HttpClient")
    def test_validates_required_shapes(self, mock_client: unittest.mock.MagicMock) -> None:
        cases = [
            (automation_storage_items.cmd_automation_storage_items_create, SimpleNamespace(storage_item_json='{"storageItem":{"key":"k"}}')),
            (automation_storage_items.cmd_automation_storage_items_bulk_update_tags, SimpleNamespace(tags_json='{"storageItemIds":[]}')),
            (automation_storage_items.cmd_automation_storage_items_update_value, SimpleNamespace(key="k", value_json='{"stringValue":"v","numberValue":"1"}')),
            (automations_v2.cmd_automations_v2_update, SimpleNamespace(automation_json='{"automation":{"id":"a1"}}')),
        ]
        for func, args in cases:
            with self.subTest(func=func.__name__):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = func(args, self._ctx())
                payload = json.loads(buf.getvalue())
                self.assertEqual(rc, 1)
                self.assertEqual(payload["error_type"], "ValidationError")
                self.assertFalse(mock_client.return_value.request.called)

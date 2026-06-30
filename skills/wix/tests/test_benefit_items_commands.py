from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from wix_safe_agent_cli.cli import build_parser
from wix_safe_agent_cli.commands import benefit_items
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = (action, payload)


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestBenefitItemsCommands(unittest.TestCase):
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
            "command_str": "wix-safe-agent-cli benefit-items",
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
    def _instance_payload() -> dict:
        return {"site": {"installedWixApps": ["pricingPlans"]}}

    @staticmethod
    def _item(*, revision: str = "1") -> dict:
        return {
            "id": "item-1",
            "revision": revision,
            "externalId": "reward-1",
            "itemSetId": "benefit-set-1",
            "providerAppId": "app-123",
        }

    def _http_side_effect(self, responses: list[dict]) -> list[dict]:
        queue = list(responses)

        def _side_effect(*args, **kwargs):
            _ = (args, kwargs)
            return _DummyResponse(queue.pop(0))

        return _side_effect

    def test_parser_recognizes_benefit_item_subcommands(self) -> None:
        parser = build_parser()

        get_args = parser.parse_args(["benefit-items", "get", "--item-id", "item-1"])
        self.assertEqual(get_args.benefit_items_cmd, "get")
        self.assertFalse(get_args.write_capable)

        list_args = parser.parse_args(["benefit-items", "list"])
        self.assertEqual(list_args.benefit_items_cmd, "list")
        self.assertFalse(list_args.write_capable)

        query_args = parser.parse_args(["benefit-items", "query"])
        self.assertEqual(query_args.benefit_items_cmd, "query")
        self.assertFalse(query_args.write_capable)

        count_args = parser.parse_args(["benefit-items", "count"])
        self.assertEqual(count_args.benefit_items_cmd, "count")
        self.assertFalse(count_args.write_capable)

        create_args = parser.parse_args(
            [
                "benefit-items",
                "create",
                "--item-json",
                '{"externalId":"reward-1","itemSetId":"benefit-set-1","providerAppId":"app-123"}',
            ]
        )
        self.assertEqual(create_args.benefit_items_cmd, "create")
        self.assertTrue(create_args.write_capable)

        update_args = parser.parse_args(
            [
                "benefit-items",
                "update",
                "--item-id",
                "item-1",
                "--item-json",
                '{"revision":"1","externalId":"reward-1"}',
            ]
        )
        self.assertEqual(update_args.benefit_items_cmd, "update")
        self.assertTrue(update_args.write_capable)

        bulk_update_args = parser.parse_args(
            [
                "benefit-items",
                "bulk-update",
                "--items-json",
                '[{"id":"item-1","revision":"1","externalId":"reward-1"}]',
            ]
        )
        self.assertEqual(bulk_update_args.benefit_items_cmd, "bulk-update")
        self.assertTrue(bulk_update_args.write_capable)

        bulk_delete_args = parser.parse_args(
            [
                "benefit-items",
                "bulk-delete",
                "--item-ids-json",
                '["item-1","item-2"]',
            ]
        )
        self.assertEqual(bulk_delete_args.benefit_items_cmd, "bulk-delete")
        self.assertTrue(bulk_delete_args.write_capable)

        bulk_delete_filter_args = parser.parse_args(
            [
                "benefit-items",
                "bulk-delete-by-filter",
                "--filter-json",
                '{"providerAppId":{"$eq":"app-123"}}',
            ]
        )
        self.assertEqual(bulk_delete_filter_args.benefit_items_cmd, "bulk-delete-by-filter")
        self.assertTrue(bulk_delete_filter_args.write_capable)

    @patch("wix_safe_agent_cli.commands.benefit_items.HttpClient")
    def test_get_builds_expected_request(self, mock_client) -> None:
        mock_client.return_value.request.side_effect = self._http_side_effect(
            [self._instance_payload(), {"item": self._item()}]
        )
        args = SimpleNamespace(item_id="item-1")

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = benefit_items.cmd_benefit_items_get(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["request"]["path"], "/benefit-programs/v1/items/item-1")

    @patch("wix_safe_agent_cli.commands.benefit_items.HttpClient")
    def test_list_builds_expected_request(self, mock_client) -> None:
        mock_client.return_value.request.side_effect = self._http_side_effect(
            [self._instance_payload(), {"items": [self._item()]}]
        )
        args = SimpleNamespace()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = benefit_items.cmd_benefit_items_list(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["request"]["path"], "/benefit-programs/v1/items")

    @patch("wix_safe_agent_cli.commands.benefit_items.HttpClient")
    def test_query_builds_expected_request(self, mock_client) -> None:
        mock_client.return_value.request.side_effect = self._http_side_effect(
            [self._instance_payload(), {"items": []}]
        )
        args = SimpleNamespace(query_json='{"paging":{"limit":25}}')

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = benefit_items.cmd_benefit_items_query(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertEqual(payload["request"]["path"], "/benefit-programs/v1/items/query")
        self.assertEqual(payload["request"]["body"], {"paging": {"limit": 25}})

    @patch("wix_safe_agent_cli.commands.benefit_items.HttpClient")
    def test_count_builds_expected_request(self, mock_client) -> None:
        mock_client.return_value.request.side_effect = self._http_side_effect(
            [self._instance_payload(), {"count": 1}]
        )
        args = SimpleNamespace(filter_json='{"providerAppId":{"$eq":"app-123"}}')

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = benefit_items.cmd_benefit_items_count(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertEqual(payload["request"]["path"], "/benefit-programs/v1/items/count")
        self.assertEqual(payload["request"]["body"], {"filter": {"providerAppId": {"$eq": "app-123"}}})

    def test_create_dry_run_builds_plan(self) -> None:
        args = SimpleNamespace(item_json='{"externalId":"reward-1","itemSetId":"benefit-set-1"}')

        with patch("wix_safe_agent_cli.commands.benefit_items.HttpClient") as mock_client:
            mock_client.return_value.request.side_effect = self._http_side_effect([self._instance_payload()])
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = benefit_items.cmd_benefit_items_create(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["method"], "benefit-items.create")

    @patch("wix_safe_agent_cli.commands.benefit_items.HttpClient")
    def test_create_apply_requires_reviewed_plan_before_write(self, mock_client) -> None:
        args = SimpleNamespace(item_json='{"externalId":"reward-1","itemSetId":"benefit-set-1"}')

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = benefit_items.cmd_benefit_items_create(args, self._ctx(apply=True, yes=True))
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertEqual(mock_client.return_value.request.call_count, 0)

    def test_update_dry_run_injects_id_into_body(self) -> None:
        args = SimpleNamespace(item_id="item-1", item_json='{"revision":"1","externalId":"reward-1"}')

        with patch("wix_safe_agent_cli.commands.benefit_items.HttpClient") as mock_client:
            mock_client.return_value.request.side_effect = self._http_side_effect(
                [self._instance_payload(), {"item": self._item()}]
            )
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = benefit_items.cmd_benefit_items_update(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["request"]["body"]["id"], "item-1")

    def test_update_refuses_missing_revision(self) -> None:
        args = SimpleNamespace(item_id="item-1", item_json='{"externalId":"reward-1"}')

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = benefit_items.cmd_benefit_items_update(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertIn("revision", payload["error"])

    @patch("wix_safe_agent_cli.commands.benefit_items.HttpClient")
    def test_delete_apply_requires_reviewed_plan_before_write(self, mock_client) -> None:
        args = SimpleNamespace(item_id="item-1")

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = benefit_items.cmd_benefit_items_delete(args, self._ctx(apply=True, yes=True, ack_irreversible=True))
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertEqual(mock_client.return_value.request.call_count, 0)

    @patch("wix_safe_agent_cli.commands.benefit_items.HttpClient")
    def test_delete_apply_requires_ack(self, mock_client) -> None:
        args = SimpleNamespace(item_id="item-1")

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = benefit_items.cmd_benefit_items_delete(args, self._ctx(apply=True, yes=True, plan_in="/tmp/x"))
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertIn("--ack-irreversible", payload["reasons"][0])
        self.assertEqual(mock_client.return_value.request.call_count, 0)

    @patch("wix_safe_agent_cli.commands.benefit_items.HttpClient")
    def test_bulk_update_apply_requires_reviewed_plan_before_write(self, mock_client) -> None:
        args = SimpleNamespace(items_json='[{"id":"item-1","revision":"1","externalId":"reward-1"}]')

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = benefit_items.cmd_benefit_items_bulk_update(args, self._ctx(apply=True, yes=True))
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertEqual(mock_client.return_value.request.call_count, 0)

    @patch("wix_safe_agent_cli.commands.benefit_items.HttpClient")
    def test_bulk_delete_apply_requires_reviewed_plan_before_write(self, mock_client) -> None:
        args = SimpleNamespace(item_ids_json='["item-1","item-2"]')

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = benefit_items.cmd_benefit_items_bulk_delete(
                args,
                self._ctx(apply=True, yes=True, ack_irreversible=True),
            )
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertEqual(mock_client.return_value.request.call_count, 0)

    def test_bulk_delete_by_filter_rejects_empty_filter(self) -> None:
        args = SimpleNamespace(filter_json='{"filter":{}}')

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = benefit_items.cmd_benefit_items_bulk_delete_by_filter(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertIn("non-empty filter object", payload["error"])

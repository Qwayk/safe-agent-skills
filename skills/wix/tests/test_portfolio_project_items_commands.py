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
from wix_safe_agent_cli.commands import portfolio_project_items
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = action, payload


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestPortfolioProjectItemsCommands(unittest.TestCase):
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
            "verbose": False,
            "out": Output(mode="json"),
            "audit": _DummyAudit(),
            "tool": "wix-safe-agent-cli",
            "tool_version": "0.0.0",
            "command_str": "wix-safe-agent-cli portfolio-project-items",
            "apply": False,
            "yes": False,
            "plan_in": None,
            "plan_out": None,
            "receipt_out": None,
            "ack_irreversible": False,
            "enforce_reviewed_plan": True,
        }
        ctx.update(overrides)
        return ctx

    @patch("wix_safe_agent_cli.commands.portfolio_project_items.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.portfolio_project_items.HttpClient")
    def test_read_commands_use_official_paths(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "Bearer token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"items": []})

        cases = [
            (portfolio_project_items.cmd_portfolio_project_items_list, SimpleNamespace(project_id="proj-1", params_json='{"limit":10}'), "GET", "/portfolio/v1/projectItems/proj-1/items", {"limit": 10}),
            (portfolio_project_items.cmd_portfolio_project_items_get, SimpleNamespace(item_id="item-1", params_json="{}"), "GET", "/portfolio/v1/items/item-1", {}),
        ]
        for func, args, method, path, params in cases:
            with self.subTest(path=path):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = func(args, self._ctx())
                payload = json.loads(buf.getvalue())
                self.assertEqual(rc, 0)
                self.assertEqual(payload["request"]["method"], method)
                self.assertEqual(payload["request"]["path"], path)
                self.assertEqual(payload["request"]["params"], params)

        self.assertEqual(mock_auth.call_args.kwargs["command_family"], "portfolio-project-items")

    @patch("wix_safe_agent_cli.commands.portfolio_project_items.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.portfolio_project_items.HttpClient")
    def test_create_dry_run_is_plan_first(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "Bearer token-abc"}, "mode": "access_token"}
        args = SimpleNamespace(item_json='{"item":{"projectId":"proj-1","title":"Hero"}}')

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = portfolio_project_items.cmd_portfolio_project_items_create(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["method"], "portfolio-project-items.create")
        self.assertEqual(payload["plan"]["request"]["method"], "POST")
        self.assertEqual(payload["plan"]["request"]["path"], "/portfolio/v1/items")
        mock_client.return_value.request.assert_not_called()

    @patch("wix_safe_agent_cli.commands.portfolio_project_items.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.portfolio_project_items.HttpClient")
    def test_update_dry_run_reads_before_state_and_fills_item_id(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "Bearer token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"item": {"id": "item-1", "title": "Old"}})
        args = SimpleNamespace(item_id="item-1", item_json='{"item":{"title":"New"}}')

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = portfolio_project_items.cmd_portfolio_project_items_update(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        plan = payload["plan"]
        self.assertEqual(plan["request"]["method"], "PATCH")
        self.assertEqual(plan["request"]["path"], "/portfolio/v1/items/item-1")
        self.assertEqual(plan["request"]["body"]["item"]["id"], "item-1")
        self.assertIn("before_state", plan["baseline"])
        self.assertEqual(mock_client.return_value.request.call_count, 1)

    @patch("wix_safe_agent_cli.commands.portfolio_project_items.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.portfolio_project_items.HttpClient")
    def test_update_refuses_mismatched_item_id(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "Bearer token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"item": {"id": "item-1"}})
        args = SimpleNamespace(item_id="item-1", item_json='{"item":{"id":"item-2","title":"New"}}')

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = portfolio_project_items.cmd_portfolio_project_items_update(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertIn("item.id", payload["reasons"][0])
        self.assertEqual(mock_client.return_value.request.call_count, 1)

    @patch("wix_safe_agent_cli.commands.portfolio_project_items.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.portfolio_project_items.HttpClient")
    def test_delete_requires_ack_for_apply(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "Bearer token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"item": {"id": "item-1"}})

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = portfolio_project_items.cmd_portfolio_project_items_delete(
                SimpleNamespace(item_id="item-1"),
                self._ctx(apply=True, yes=True, plan_in="/tmp/reviewed-plan.json"),
            )
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertIn("apply also requires --ack-irreversible", payload["plan"]["preconditions"])
        self.assertEqual(mock_client.return_value.request.call_count, 1)

    @patch("wix_safe_agent_cli.commands.portfolio_project_items.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.portfolio_project_items.HttpClient")
    def test_bulk_update_dry_run_reads_before_states_and_fills_ids(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "Bearer token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.side_effect = [
            _DummyResponse({"item": {"id": "item-1"}}),
            _DummyResponse({"item": {"id": "item-2"}}),
        ]
        args = SimpleNamespace(items_json='{"items":[{"item":{"id":"item-1","title":"One"}},{"id":"item-2","title":"Two"}]}')

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = portfolio_project_items.cmd_portfolio_project_items_bulk_update(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        plan = payload["plan"]
        self.assertEqual(plan["request"]["method"], "PATCH")
        self.assertEqual(plan["request"]["path"], "/portfolio/project-items/api/v1/bulk/portfolio/items/update")
        self.assertEqual(plan["request"]["body"]["items"][0]["item"]["id"], "item-1")
        self.assertEqual(plan["request"]["body"]["items"][1]["id"], "item-2")
        self.assertEqual(plan["selector"]["item_ids"], ["item-1", "item-2"])
        self.assertEqual(mock_client.return_value.request.call_count, 2)

    @patch("wix_safe_agent_cli.commands.portfolio_project_items.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.portfolio_project_items.HttpClient")
    def test_bulk_delete_requires_ack_and_reads_before_states(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "Bearer token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.side_effect = [
            _DummyResponse({"item": {"id": "item-1"}}),
            _DummyResponse({"item": {"id": "item-2"}}),
        ]
        args = SimpleNamespace(item_ids_json='{"itemIds":["item-1","item-2"]}')

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = portfolio_project_items.cmd_portfolio_project_items_bulk_delete(
                args,
                self._ctx(apply=True, yes=True, plan_in="/tmp/reviewed-plan.json"),
            )
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["request"]["method"], "DELETE")
        self.assertEqual(payload["plan"]["request"]["path"], "/portfolio/project-items/api/v1/bulk/portfolio/items/delete")
        self.assertEqual(payload["plan"]["selector"]["item_ids"], ["item-1", "item-2"])
        self.assertEqual(mock_client.return_value.request.call_count, 2)

    @patch("wix_safe_agent_cli.commands.portfolio_project_items.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.portfolio_project_items.HttpClient")
    def test_reviewed_update_apply_sends_patch_and_readback(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "Bearer token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.side_effect = [
            _DummyResponse({"item": {"id": "item-1", "title": "Old"}}),
            _DummyResponse({"item": {"id": "item-1", "title": "New"}}),
            _DummyResponse({"item": {"id": "item-1", "title": "New"}}),
        ]
        plan = {
            "method": "portfolio-project-items.update",
            "baseline": {"env_fingerprint": "https://www.wixapis.com", "selector": {"kind": "portfolio-project-items", "item_id": "item-1"}},
            "proposed_changes": [{"operation": "update-project-item", "item_id": "item-1"}],
        }
        with tempfile.TemporaryDirectory() as tmp:
            plan_path = Path(tmp) / "plan.json"
            plan_path.write_text(json.dumps(plan), encoding="utf-8")
            args = SimpleNamespace(item_id="item-1", item_json='{"item":{"title":"New"}}')
            ctx = self._ctx(apply=True, yes=True, plan_in=str(plan_path))

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = portfolio_project_items.cmd_portfolio_project_items_update(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertFalse(payload["dry_run"])
        self.assertEqual(payload["request"]["method"], "PATCH")
        self.assertEqual(payload["request"]["body"]["item"]["id"], "item-1")
        self.assertEqual(payload["receipt"]["verification"]["type"], "read-after-write")
        self.assertEqual(mock_client.return_value.request.call_count, 3)

    @patch("wix_safe_agent_cli.commands.portfolio_project_items.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.portfolio_project_items.HttpClient")
    def test_duplicate_dry_run_uses_official_path(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "Bearer token-abc"}, "mode": "access_token"}
        args = SimpleNamespace(duplicate_json='{"originProjectId":"proj-1","targetProjectId":"proj-2"}')

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = portfolio_project_items.cmd_portfolio_project_items_duplicate(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["request"]["method"], "POST")
        self.assertEqual(payload["plan"]["request"]["path"], "/portfolio/project-items/api/v1/items/duplicate")
        mock_client.return_value.request.assert_not_called()

    def test_parser_exposes_portfolio_project_items_commands(self) -> None:
        parser = build_parser()
        cases = [
            (["portfolio-project-items", "list", "--project-id", "proj-1"], portfolio_project_items.cmd_portfolio_project_items_list, False),
            (["portfolio-project-items", "get", "--item-id", "item-1"], portfolio_project_items.cmd_portfolio_project_items_get, False),
            (["portfolio-project-items", "create", "--item-json", "{}"], portfolio_project_items.cmd_portfolio_project_items_create, True),
            (["portfolio-project-items", "update", "--item-id", "item-1", "--item-json", "{}"], portfolio_project_items.cmd_portfolio_project_items_update, True),
            (["portfolio-project-items", "delete", "--item-id", "item-1"], portfolio_project_items.cmd_portfolio_project_items_delete, True),
            (["portfolio-project-items", "bulk-create", "--items-json", "{}"], portfolio_project_items.cmd_portfolio_project_items_bulk_create, True),
            (["portfolio-project-items", "bulk-update", "--items-json", "{}"], portfolio_project_items.cmd_portfolio_project_items_bulk_update, True),
            (["portfolio-project-items", "bulk-delete", "--item-ids-json", "{}"], portfolio_project_items.cmd_portfolio_project_items_bulk_delete, True),
            (["portfolio-project-items", "duplicate", "--duplicate-json", "{}"], portfolio_project_items.cmd_portfolio_project_items_duplicate, True),
        ]
        for argv, func, write_capable in cases:
            with self.subTest(argv=argv):
                args = parser.parse_args(argv)
                self.assertIs(args.func, func)
                self.assertEqual(args.write_capable, write_capable)

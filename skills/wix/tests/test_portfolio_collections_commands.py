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
from wix_safe_agent_cli.commands import portfolio_collections
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = action, payload


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestPortfolioCollectionsCommands(unittest.TestCase):
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
            "command_str": "wix-safe-agent-cli portfolio-collections",
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

    @patch("wix_safe_agent_cli.commands.portfolio_collections.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.portfolio_collections.HttpClient")
    def test_read_commands_use_official_paths(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "Bearer token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"collections": []})

        cases = [
            (portfolio_collections.cmd_portfolio_collections_list, SimpleNamespace(params_json='{"includePageUrl":true}'), "GET", "/portfolio/v1/collections", {"includePageUrl": True}, None),
            (portfolio_collections.cmd_portfolio_collections_get, SimpleNamespace(collection_id="col-1", params_json="{}"), "GET", "/portfolio/v1/collections/col-1", {}, None),
            (portfolio_collections.cmd_portfolio_collections_query, SimpleNamespace(query_json='{"query":{"paging":{"limit":10}}}'), "POST", "/portfolio/v1/collections/query", None, {"query": {"paging": {"limit": 10}}}),
        ]
        for func, args, method, path, params, body in cases:
            with self.subTest(path=path):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = func(args, self._ctx())
                payload = json.loads(buf.getvalue())
                self.assertEqual(rc, 0)
                self.assertEqual(payload["request"]["method"], method)
                self.assertEqual(payload["request"]["path"], path)
                if params is not None:
                    self.assertEqual(payload["request"]["params"], params)
                if body is not None:
                    self.assertEqual(payload["request"]["body"], body)

        self.assertEqual(mock_auth.call_args.kwargs["command_family"], "portfolio-collections")

    @patch("wix_safe_agent_cli.commands.portfolio_collections.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.portfolio_collections.HttpClient")
    def test_create_dry_run_is_plan_first(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "Bearer token-abc"}, "mode": "access_token"}
        args = SimpleNamespace(collection_json='{"collection":{"title":"Work"}}')

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = portfolio_collections.cmd_portfolio_collections_create(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["method"], "portfolio-collections.create")
        self.assertEqual(payload["plan"]["request"]["method"], "POST")
        self.assertEqual(payload["plan"]["request"]["path"], "/portfolio/v1/collections")
        mock_client.return_value.request.assert_not_called()

    @patch("wix_safe_agent_cli.commands.portfolio_collections.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.portfolio_collections.HttpClient")
    def test_update_dry_run_reads_current_revision_and_fills_body(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "Bearer token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"collection": {"id": "col-1", "revision": "7", "title": "Old"}})
        args = SimpleNamespace(collection_id="col-1", collection_json='{"collection":{"title":"New"}}')

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = portfolio_collections.cmd_portfolio_collections_update(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        plan = payload["plan"]
        self.assertEqual(plan["request"]["method"], "PATCH")
        self.assertEqual(plan["request"]["path"], "/portfolio/v1/collections/col-1")
        self.assertEqual(plan["request"]["body"]["collection"]["id"], "col-1")
        self.assertEqual(plan["request"]["body"]["collection"]["revision"], "7")
        self.assertIn("before_state", plan["baseline"])
        self.assertEqual(mock_client.return_value.request.call_count, 1)

    @patch("wix_safe_agent_cli.commands.portfolio_collections.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.portfolio_collections.HttpClient")
    def test_update_refuses_mismatched_revision(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "Bearer token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"collection": {"id": "col-1", "revision": "7"}})
        args = SimpleNamespace(collection_id="col-1", collection_json='{"collection":{"id":"col-1","revision":"6","title":"New"}}')

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = portfolio_collections.cmd_portfolio_collections_update(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertIn("revision", payload["reasons"][0])
        self.assertEqual(mock_client.return_value.request.call_count, 1)

    @patch("wix_safe_agent_cli.commands.portfolio_collections.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.portfolio_collections.HttpClient")
    def test_delete_requires_ack_for_apply(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "Bearer token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"collection": {"id": "col-1", "revision": "7"}})

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = portfolio_collections.cmd_portfolio_collections_delete(
                SimpleNamespace(collection_id="col-1"),
                self._ctx(apply=True, yes=True, plan_in="/tmp/reviewed-plan.json"),
            )
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertIn("apply also requires --ack-irreversible", payload["plan"]["preconditions"])
        self.assertEqual(mock_client.return_value.request.call_count, 1)

    @patch("wix_safe_agent_cli.commands.portfolio_collections.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.portfolio_collections.HttpClient")
    def test_reviewed_update_apply_sends_patch_and_readback(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "Bearer token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.side_effect = [
            _DummyResponse({"collection": {"id": "col-1", "revision": "7", "title": "Old"}}),
            _DummyResponse({"collection": {"id": "col-1", "revision": "8", "title": "New"}}),
            _DummyResponse({"collection": {"id": "col-1", "revision": "8", "title": "New"}}),
        ]
        plan = {
            "method": "portfolio-collections.update",
            "baseline": {"env_fingerprint": "https://www.wixapis.com", "selector": {"kind": "portfolio-collections", "collection_id": "col-1"}},
            "proposed_changes": [{"operation": "update-collection", "collection_id": "col-1"}],
        }
        with tempfile.TemporaryDirectory() as tmp:
            plan_path = Path(tmp) / "plan.json"
            plan_path.write_text(json.dumps(plan), encoding="utf-8")
            args = SimpleNamespace(collection_id="col-1", collection_json='{"collection":{"title":"New"}}')
            ctx = self._ctx(apply=True, yes=True, plan_in=str(plan_path))

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = portfolio_collections.cmd_portfolio_collections_update(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertFalse(payload["dry_run"])
        self.assertEqual(payload["request"]["method"], "PATCH")
        self.assertEqual(payload["request"]["body"]["collection"]["revision"], "7")
        self.assertEqual(payload["receipt"]["verification"]["type"], "read-after-write")
        self.assertEqual(mock_client.return_value.request.call_count, 3)

    def test_parser_exposes_portfolio_collections_commands(self) -> None:
        parser = build_parser()
        cases = [
            (["portfolio-collections", "list"], portfolio_collections.cmd_portfolio_collections_list, False),
            (["portfolio-collections", "get", "--collection-id", "col-1"], portfolio_collections.cmd_portfolio_collections_get, False),
            (["portfolio-collections", "query"], portfolio_collections.cmd_portfolio_collections_query, False),
            (["portfolio-collections", "create", "--collection-json", "{}"], portfolio_collections.cmd_portfolio_collections_create, True),
            (["portfolio-collections", "update", "--collection-id", "col-1", "--collection-json", "{}"], portfolio_collections.cmd_portfolio_collections_update, True),
            (["portfolio-collections", "delete", "--collection-id", "col-1"], portfolio_collections.cmd_portfolio_collections_delete, True),
        ]
        for argv, func, write_capable in cases:
            with self.subTest(argv=argv):
                args = parser.parse_args(argv)
                self.assertIs(args.func, func)
                self.assertEqual(args.write_capable, write_capable)

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
from wix_safe_agent_cli.commands import portfolio_projects
from wix_safe_agent_cli.output import Output


class _DummyAudit:
    def write(self, action: str, payload: dict) -> None:
        _ = action, payload


class _DummyResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class TestPortfolioProjectsCommands(unittest.TestCase):
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
            "command_str": "wix-safe-agent-cli portfolio-projects",
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

    @patch("wix_safe_agent_cli.commands.portfolio_projects.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.portfolio_projects.HttpClient")
    def test_read_commands_use_official_paths(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "Bearer token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"projects": []})

        cases = [
            (portfolio_projects.cmd_portfolio_projects_list, SimpleNamespace(params_json='{"includePageUrl":true}'), "GET", "/portfolio/v1/projects", {"includePageUrl": True}, None),
            (portfolio_projects.cmd_portfolio_projects_get, SimpleNamespace(project_id="proj-1", params_json="{}"), "GET", "/portfolio/v1/projects/proj-1", {}, None),
            (portfolio_projects.cmd_portfolio_projects_query, SimpleNamespace(query_json='{"query":{"paging":{"limit":10}}}'), "POST", "/portfolio/v1/projects/query", None, {"query": {"paging": {"limit": 10}}}),
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

        self.assertEqual(mock_auth.call_args.kwargs["command_family"], "portfolio-projects")

    @patch("wix_safe_agent_cli.commands.portfolio_projects.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.portfolio_projects.HttpClient")
    def test_create_dry_run_is_plan_first(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "Bearer token-abc"}, "mode": "access_token"}
        args = SimpleNamespace(project_json='{"project":{"title":"Launch"}}')

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = portfolio_projects.cmd_portfolio_projects_create(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["plan"]["method"], "portfolio-projects.create")
        self.assertEqual(payload["plan"]["request"]["method"], "POST")
        self.assertEqual(payload["plan"]["request"]["path"], "/portfolio/v1/projects")
        mock_client.return_value.request.assert_not_called()

    @patch("wix_safe_agent_cli.commands.portfolio_projects.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.portfolio_projects.HttpClient")
    def test_update_dry_run_reads_current_revision_and_fills_body(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "Bearer token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"project": {"id": "proj-1", "revision": "7", "title": "Old"}})
        args = SimpleNamespace(project_id="proj-1", project_json='{"project":{"title":"New"}}')

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = portfolio_projects.cmd_portfolio_projects_update(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        plan = payload["plan"]
        self.assertEqual(plan["request"]["method"], "PATCH")
        self.assertEqual(plan["request"]["path"], "/portfolio/v1/projects/proj-1")
        self.assertEqual(plan["request"]["body"]["project"]["id"], "proj-1")
        self.assertEqual(plan["request"]["body"]["project"]["revision"], "7")
        self.assertIn("before_state", plan["baseline"])
        self.assertEqual(mock_client.return_value.request.call_count, 1)

    @patch("wix_safe_agent_cli.commands.portfolio_projects.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.portfolio_projects.HttpClient")
    def test_update_refuses_mismatched_revision(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "Bearer token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"project": {"id": "proj-1", "revision": "7"}})
        args = SimpleNamespace(project_id="proj-1", project_json='{"project":{"id":"proj-1","revision":"6","title":"New"}}')

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = portfolio_projects.cmd_portfolio_projects_update(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["refused"])
        self.assertIn("revision", payload["reasons"][0])
        self.assertEqual(mock_client.return_value.request.call_count, 1)

    @patch("wix_safe_agent_cli.commands.portfolio_projects.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.portfolio_projects.HttpClient")
    def test_delete_requires_ack_for_apply(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "Bearer token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.return_value = _DummyResponse({"project": {"id": "proj-1", "revision": "7"}})

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = portfolio_projects.cmd_portfolio_projects_delete(
                SimpleNamespace(project_id="proj-1"),
                self._ctx(apply=True, yes=True, plan_in="/tmp/reviewed-plan.json"),
            )
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertIn("apply also requires --ack-irreversible", payload["plan"]["preconditions"])
        self.assertEqual(mock_client.return_value.request.call_count, 1)

    @patch("wix_safe_agent_cli.commands.portfolio_projects.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.portfolio_projects.HttpClient")
    def test_bulk_update_dry_run_reads_current_revisions_and_fills_body(
        self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock
    ) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "Bearer token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.side_effect = [
            _DummyResponse({"project": {"id": "proj-1", "revision": "7"}}),
            _DummyResponse({"project": {"id": "proj-2", "revision": "3"}}),
        ]
        args = SimpleNamespace(projects_json='{"projects":[{"project":{"id":"proj-1","title":"One"}},{"id":"proj-2","title":"Two"}]}')

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = portfolio_projects.cmd_portfolio_projects_bulk_update(args, self._ctx())
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        plan = payload["plan"]
        self.assertEqual(plan["request"]["method"], "PATCH")
        self.assertEqual(plan["request"]["path"], "/portfolio/projects/projects/api/v1/bulk/portfolio/projects/update")
        self.assertEqual(plan["request"]["body"]["projects"][0]["project"]["revision"], "7")
        self.assertEqual(plan["request"]["body"]["projects"][1]["revision"], "3")
        self.assertEqual(plan["selector"]["project_ids"], ["proj-1", "proj-2"])
        self.assertEqual(mock_client.return_value.request.call_count, 2)

    @patch("wix_safe_agent_cli.commands.portfolio_projects.resolve_auth_mode")
    @patch("wix_safe_agent_cli.commands.portfolio_projects.HttpClient")
    def test_reviewed_update_apply_sends_patch_and_readback(self, mock_client: unittest.mock.MagicMock, mock_auth: unittest.mock.MagicMock) -> None:
        mock_auth.return_value = {"headers": {"Authorization": "Bearer token-abc"}, "mode": "access_token"}
        mock_client.return_value.request.side_effect = [
            _DummyResponse({"project": {"id": "proj-1", "revision": "7", "title": "Old"}}),
            _DummyResponse({"project": {"id": "proj-1", "revision": "8", "title": "New"}}),
            _DummyResponse({"project": {"id": "proj-1", "revision": "8", "title": "New"}}),
        ]
        plan = {
            "method": "portfolio-projects.update",
            "baseline": {"env_fingerprint": "https://www.wixapis.com", "selector": {"kind": "portfolio-projects", "project_id": "proj-1"}},
            "proposed_changes": [{"operation": "update-project", "project_id": "proj-1"}],
        }
        with tempfile.TemporaryDirectory() as tmp:
            plan_path = Path(tmp) / "plan.json"
            plan_path.write_text(json.dumps(plan), encoding="utf-8")
            args = SimpleNamespace(project_id="proj-1", project_json='{"project":{"title":"New"}}')
            ctx = self._ctx(apply=True, yes=True, plan_in=str(plan_path))

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = portfolio_projects.cmd_portfolio_projects_update(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertFalse(payload["dry_run"])
        self.assertEqual(payload["request"]["method"], "PATCH")
        self.assertEqual(payload["request"]["body"]["project"]["revision"], "7")
        self.assertEqual(payload["receipt"]["verification"]["type"], "read-after-write")
        self.assertEqual(mock_client.return_value.request.call_count, 3)

    def test_parser_exposes_portfolio_projects_commands(self) -> None:
        parser = build_parser()
        cases = [
            (["portfolio-projects", "list"], portfolio_projects.cmd_portfolio_projects_list, False),
            (["portfolio-projects", "get", "--project-id", "proj-1"], portfolio_projects.cmd_portfolio_projects_get, False),
            (["portfolio-projects", "query"], portfolio_projects.cmd_portfolio_projects_query, False),
            (["portfolio-projects", "create", "--project-json", "{}"], portfolio_projects.cmd_portfolio_projects_create, True),
            (["portfolio-projects", "update", "--project-id", "proj-1", "--project-json", "{}"], portfolio_projects.cmd_portfolio_projects_update, True),
            (["portfolio-projects", "delete", "--project-id", "proj-1"], portfolio_projects.cmd_portfolio_projects_delete, True),
            (["portfolio-projects", "bulk-update", "--projects-json", "{}"], portfolio_projects.cmd_portfolio_projects_bulk_update, True),
        ]
        for argv, func, write_capable in cases:
            with self.subTest(argv=argv):
                args = parser.parse_args(argv)
                self.assertIs(args.func, func)
                self.assertEqual(args.write_capable, write_capable)

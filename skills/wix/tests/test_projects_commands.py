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
from wix_safe_agent_cli.commands import projects
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


class TestProjectsCommands(unittest.TestCase):
    def _ctx(self, *, cfg_override: dict | None = None, **overrides) -> dict:
        cfg = SimpleNamespace(
            base_url="https://www.wixapis.com",
            timeout_s=30.0,
            access_token=None,
            api_key="acct-api-key",
            account_id="acct-001",
            app_id=None,
            app_secret=None,
            instance_id=None,
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
            "command_str": "wix-safe-agent-cli projects create-project",
            "apply": False,
            "yes": False,
            "verbose": False,
            "out": Output(mode="json"),
            "audit": _DummyAudit(),
            "plan_in": None,
            "plan_out": None,
            "receipt_out": None,
            "ack_irreversible": False,
        }
        ctx.update(overrides)
        return ctx

    def test_parser_recognizes_projects_create_project(self) -> None:
        parser = build_parser()

        parsed = parser.parse_args(["projects", "create-project", "--type", "WIX", "--name", "My Project"])
        self.assertEqual(parsed.projects_cmd, "create-project")
        self.assertTrue(parsed.write_capable)
        self.assertEqual(parsed.func.__name__, "cmd_projects_create_project")

    def _args(self, **kwargs) -> SimpleNamespace:
        data = {
            "type": "WIX",
            "name": "New Site Project",
            "template_id": None,
            "folder_id": None,
            "apps_json": None,
        }
        data.update(kwargs)
        return SimpleNamespace(**data)

    def test_projects_create_project_dry_run_builds_plan(self) -> None:
        args = self._args(
            template_id="tmpl-123",
            folder_id="folder-1",
            apps_json='[{"appDefId":"app-1"},{"appDefId":"app-2"}]',
        )
        ctx = self._ctx()
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = projects.cmd_projects_create_project(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["method"], "projects.create-project")
        self.assertEqual(payload["plan"]["method"], "projects.create-project")
        self.assertEqual(payload["plan"]["request"]["method"], "POST")
        self.assertEqual(payload["plan"]["request"]["path"], "/funnel/projects/v1/create")
        self.assertEqual(payload["plan"]["request"]["body"]["name"], "New Site Project")
        self.assertEqual(payload["plan"]["request"]["body"]["templateId"], "tmpl-123")
        self.assertEqual(payload["plan"]["request"]["body"]["folderId"], "folder-1")
        self.assertEqual(payload["plan"]["request"]["body"]["apps"], [{"appDefId": "app-1"}, {"appDefId": "app-2"}])

    def test_projects_create_project_requires_name(self) -> None:
        args = self._args(name="   ")
        ctx = self._ctx()
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = projects.cmd_projects_create_project(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error_type"], "ValidationError")
        self.assertIn("--name", payload["error"])

    def test_projects_create_project_type_validation_accepts_wix(self) -> None:
        args = self._args(type="WIX")
        ctx = self._ctx()
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = projects.cmd_projects_create_project(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["method"], "projects.create-project")

    def test_projects_create_project_type_validation_rejects_other_types(self) -> None:
        for blocked_type in ["HEADLESS", "BRANDED_APP", "UNKNOWN", "VIBE"]:
            args = self._args(type=blocked_type)
            ctx = self._ctx()
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = projects.cmd_projects_create_project(args, ctx)
            payload = json.loads(buf.getvalue())

            self.assertEqual(rc, 1)
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["error_type"], "ValidationError")
            self.assertIn("Only --type WIX is supported", payload["error"])

    def test_projects_create_project_apps_json_must_be_array(self) -> None:
        args = self._args(apps_json='{"appDefId":"app-1"}')
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = projects.cmd_projects_create_project(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error_type"], "ValidationError")
        self.assertIn("--apps-json must be a JSON array", payload["error"])

    def test_projects_create_project_apps_json_requires_app_def_id(self) -> None:
        args = self._args(apps_json='[{}]')
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = projects.cmd_projects_create_project(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error_type"], "ValidationError")
        self.assertIn("appDefId is required", payload["error"])

    def test_projects_create_project_apps_json_rejects_duplicate_app_def_ids(self) -> None:
        args = self._args(apps_json='[{"appDefId":"app-1"},{"appDefId":"app-1"}]')
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = projects.cmd_projects_create_project(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error_type"], "ValidationError")
        self.assertIn("duplicate appDefId", payload["error"])

    def test_projects_create_project_apps_json_rejects_too_many_items(self) -> None:
        apps = [{"appDefId": f"app-{i}"} for i in range(101)]
        args = self._args(apps_json=json.dumps(apps))
        ctx = self._ctx()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = projects.cmd_projects_create_project(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 1)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error_type"], "ValidationError")
        self.assertIn("at most 100", payload["error"])

    def test_projects_create_project_apply_requires_apply_and_yes(self) -> None:
        args = self._args()
        ctx = self._ctx(apply=True, yes=False)

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = projects.cmd_projects_create_project(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertTrue(payload["dry_run"])
        self.assertNotIn("receipt", payload)

    def test_projects_create_project_plan_in_mismatch_is_refused(self) -> None:
        args = self._args()
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as handle:
            json.dump(
                {
                    "method": "projects.create-project",
                    "env_fingerprint": "https://other-env.example",
                    "command": "wix-safe-agent-cli projects create-project",
                    "baseline": {
                        "env_fingerprint": "https://other-env.example",
                        "selector": {"kind": "wix-project", "operation": "create-project", "type": "WIX", "name": "New Site Project"},
                    },
                    "selector": {"kind": "wix-project", "operation": "create-project", "type": "WIX", "name": "New Site Project"},
                    "request": {"method": "POST"},
                },
                handle,
            )
            plan_path = handle.name

        try:
            ctx = self._ctx(apply=True, yes=True, plan_in=plan_path)

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = projects.cmd_projects_create_project(args, ctx)
            payload = json.loads(buf.getvalue())

            self.assertEqual(rc, 0)
            self.assertTrue(payload["refused"])
            self.assertEqual(payload["refusal_type"], "SafetyError")
            self.assertIn("plan env_fingerprint does not match current environment", payload["reasons"][0])
        finally:
            Path(plan_path).unlink()

    @patch("wix_safe_agent_cli.commands.projects.HttpClient")
    def test_projects_create_project_apply_request_headers_and_body(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse(
            {
                "project": {
                    "id": "project-1",
                    "templateId": "tmpl-1",
                    "metaSiteId": "meta-1",
                    "siteId": "site-1",
                    "apps": [{"appDefId": "app-1"}, {"appDefId": "app-2"}],
                },
            }
        )

        args = self._args(
            template_id="tmpl-1",
            folder_id="folder-1",
            apps_json='[{"appDefId":"app-1"},{"appDefId":"app-2"}]',
        )
        ctx = self._ctx(apply=True, yes=True)

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = projects.cmd_projects_create_project(args, ctx)
        payload = json.loads(buf.getvalue())

        self.assertEqual(rc, 0)
        self.assertFalse(payload["dry_run"])
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["method"], "projects.create-project")

        call = mock_client.return_value.request.call_args
        headers = call.kwargs["headers"]
        self.assertEqual(headers["Authorization"], "acct-api-key")
        self.assertEqual(headers["wix-account-id"], "acct-001")
        self.assertEqual(headers["Content-Type"], "application/json")
        self.assertEqual(call.kwargs["method"], "POST")
        self.assertTrue(str(call.kwargs["url"]).endswith("/funnel/projects/v1/create"))
        self.assertEqual(call.kwargs["json_body"]["name"], "New Site Project")
        self.assertEqual(call.kwargs["json_body"]["templateId"], "tmpl-1")
        self.assertEqual(call.kwargs["json_body"]["folderId"], "folder-1")
        self.assertEqual(call.kwargs["json_body"]["apps"], [{"appDefId": "app-1"}, {"appDefId": "app-2"}])

    @patch("wix_safe_agent_cli.commands.projects.HttpClient")
    def test_projects_create_project_response_verification(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse(
            {
                "project": {
                    "id": "project-1",
                    "templateId": "tmpl-1",
                    "metaSiteId": "meta-1",
                    "siteId": "site-1",
                    "apps": [{"appDefId": "app-1"}, {"appDefId": "app-2"}, {"appDefId": "app-3"}],
                },
            }
        )

        args = self._args(
            template_id="tmpl-1",
            apps_json='[{"appDefId":"app-2"},{"appDefId":"app-1"}]',
        )
        ctx = self._ctx(apply=True, yes=True)

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = projects.cmd_projects_create_project(args, ctx)
        payload = json.loads(buf.getvalue())
        verification = payload["receipt"]["verification"]

        self.assertEqual(rc, 0)
        self.assertTrue(verification["ok"])
        self.assertIn("No post-write readback exists yet because no projects read command is shipped.", verification["notes"])

        ctx_fail = self._ctx(apply=True, yes=True)
        args_fail = self._args()
        with patch("wix_safe_agent_cli.commands.projects.HttpClient") as fail_client:
            fail_client.return_value.request.return_value = _DummyResponse({"project": {"metaSiteId": "", "siteId": "site-1"}})
            buf_fail = io.StringIO()
            with redirect_stdout(buf_fail):
                fail_rc = projects.cmd_projects_create_project(args_fail, ctx_fail)
            payload_fail = json.loads(buf_fail.getvalue())
            verification_fail = payload_fail["receipt"]["verification"]

        self.assertEqual(fail_rc, 1)
        self.assertFalse(verification_fail["ok"])
        self.assertIn("metaSiteId", verification_fail["notes"])

    def test_projects_create_project_plan_out_writes_file(self) -> None:
        args = self._args()

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as handle:
            plan_path = handle.name

        try:
            ctx = self._ctx(plan_out=plan_path)
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = projects.cmd_projects_create_project(args, ctx)
            payload = json.loads(buf.getvalue())

            self.assertEqual(rc, 0)
            self.assertTrue(payload["dry_run"])
            self.assertEqual(payload["plan_out"], plan_path)
            stored_plan = json.loads(Path(plan_path).read_text(encoding="utf-8"))
            self.assertEqual(stored_plan["method"], "projects.create-project")
        finally:
            Path(plan_path).unlink()

    @patch("wix_safe_agent_cli.commands.projects.HttpClient")
    def test_projects_create_project_receipt_out_writes_file(self, mock_client: unittest.mock.MagicMock) -> None:
        mock_client.return_value.request.return_value = _DummyResponse(
            {
                "project": {
                    "id": "project-1",
                    "metaSiteId": "meta-1",
                    "siteId": "site-1",
                }
            }
        )

        args = self._args()
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as handle:
            receipt_path = handle.name

        try:
            ctx = self._ctx(apply=True, yes=True, receipt_out=receipt_path)
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = projects.cmd_projects_create_project(args, ctx)
            payload = json.loads(buf.getvalue())

            self.assertEqual(rc, 0)
            self.assertEqual(payload["receipt_out"], receipt_path)
            stored_receipt = json.loads(Path(receipt_path).read_text(encoding="utf-8"))
            self.assertEqual(stored_receipt["method"], "projects.create-project")
        finally:
            Path(receipt_path).unlink()

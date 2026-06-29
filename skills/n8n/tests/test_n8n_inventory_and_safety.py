from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from n8n_safe_agent_cli.cli import main
from n8n_safe_agent_cli.commands.api import _redact_response
from n8n_safe_agent_cli.inventory import load_inventory


class TestN8nInventoryAndSafety(unittest.TestCase):
    def _env(self, root: Path) -> Path:
        env_path = root / ".env"
        env_path.write_text(
            "N8N_BASE_URL=https://example.app.n8n.cloud/api/v1\n"
            "N8N_API_KEY=test-secret-api-key\n"
            "N8N_TIMEOUT_S=30\n",
            encoding="utf-8",
        )
        return env_path

    def test_inventory_covers_official_families(self) -> None:
        inventory = load_inventory()
        self.assertEqual(inventory["operation_count"], 80)
        for family in [
            "workflow",
            "execution",
            "credential",
            "tags",
            "variables",
            "user",
            "projects",
            "folders",
            "data-table",
            "source-control",
            "community-package",
            "n8n-package",
            "audit",
            "discover",
            "insights",
        ]:
            self.assertIn(family, inventory["families"])

    def test_api_list_needs_no_env_and_has_one_json_object(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = main(["--output", "json", "api", "list"])
        self.assertEqual(rc, 0)
        payload = json.loads(buf.getvalue())
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["operation_count"], 80)

    def test_write_dry_run_creates_plan_without_applying(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = self._env(root)
            plan_path = root / "plan.json"
            body = json.dumps({"name": "Safe test workflow", "nodes": [], "connections": {}})
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--plan-out",
                        str(plan_path),
                        "api",
                        "workflow",
                        "create-workflow",
                        "--body-json",
                        body,
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])
            self.assertTrue(plan_path.exists())
            self.assertEqual(payload["plan"]["operation"]["method"], "POST")
            self.assertIn("n8n-write", payload["plan"]["risk_reasons"])

    def test_apply_refuses_without_reviewed_plan(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = self._env(Path(d))
            body = json.dumps({"name": "Safe test workflow", "nodes": [], "connections": {}})
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--yes",
                        "api",
                        "workflow",
                        "create-workflow",
                        "--body-json",
                        body,
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            self.assertIn("--plan-in", payload["reasons"][0])

    def test_auth_check_redacts_api_key_and_calls_safe_read(self) -> None:
        class FakeResponse:
            status = 200
            url = "https://example.app.n8n.cloud/api/v1/workflows?limit=1"

            def json(self):
                return {"data": [{"id": "wf1", "name": "One"}]}

            def text(self):
                return "{}"

        with tempfile.TemporaryDirectory() as d:
            env_path = self._env(Path(d))
            with patch("n8n_safe_agent_cli.http.HttpClient.request", return_value=FakeResponse()) as req:
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = main(["--env-file", str(env_path), "auth", "check"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertNotIn("test-secret-api-key", buf.getvalue())
            req.assert_called_once()
            self.assertEqual(req.call_args.args[0], "GET")

    def test_credential_response_scrubs_data_without_hiding_normal_lists(self) -> None:
        credential_op = {"family_slug": "credential"}
        workflow_op = {"family_slug": "workflow"}
        body = {"data": [{"id": "x", "data": {"password": "secret"}, "name": "Visible"}]}

        self.assertEqual(_redact_response(credential_op, body)["data"], "[REDACTED]")
        visible = _redact_response(workflow_op, body)
        self.assertIsInstance(visible["data"], list)
        self.assertEqual(visible["data"][0]["name"], "Visible")
        self.assertEqual(visible["data"][0]["data"]["password"], "[REDACTED]")

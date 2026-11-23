from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from azure_safe_agent_cli.cli import main


class TestRunArtifacts(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.settings = self.root / "settings.env"
        self.input_path = self.root / "input.json"
        self.input_path.write_text(json.dumps({
            "subscriptionId": "test-subscription", "resourceGroupName": "test-group",
            "body": {"location": "eastus"},
        }))
        self.command = [
            "resources-management", "resourcegroups_createorupdate_2025-04-01_148562",
            "--input-json", str(self.input_path),
        ]

    def run_cli(self, *args):
        output = io.StringIO()
        with redirect_stdout(output):
            code = main(["--env-file", str(self.settings), *args])
        self.assertEqual(0, code, output.getvalue())
        return json.loads(output.getvalue())

    def test_azure_preview_creates_a_run_that_can_be_listed_and_read(self):
        run_id = "2026-01-19T120000Z_deadbe"
        preview = self.run_cli("--run-id", run_id, *self.command)
        self.assertTrue(preview["dry_run"])
        self.assertFalse(preview["approval_ready"])
        self.assertEqual(run_id, preview["run_id"])
        artifacts = Path(preview["artifacts_dir"])
        self.assertTrue((artifacts / "plan.json").is_file())
        self.assertTrue((artifacts / "summary.md").is_file())
        self.assertTrue((artifacts / "audit.jsonl").is_file())
        self.assertIn(run_id, Path(preview["runs_index"]).read_text())
        self.assertEqual(1, self.run_cli("runs", "list")["count"])
        shown = self.run_cli("runs", "show", "--run-id", run_id)
        self.assertEqual(run_id, shown["run"]["run_id"])
        self.assertIsNotNone(shown["summary_md"])

    def test_refused_write_keeps_run_history(self):
        run_id = "2026-01-19T121000Z_refuse1"
        refused = self.run_cli("--run-id", run_id, "--apply", *self.command)
        self.assertTrue(refused["refused"])
        self.assertIn("--plan-in", refused["reasons"][0])
        self.assertTrue((Path(refused["artifacts_dir"]) / "summary.md").is_file())
        self.assertIn(run_id, Path(refused["runs_index"]).read_text())

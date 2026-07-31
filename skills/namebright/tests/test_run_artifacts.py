from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from namebright_safe_cli.runs import (
    append_index_row,
    build_deterministic_summary,
    find_run,
    init_run_context,
    list_runs,
    write_summary_md,
)


class TestRunArtifacts(unittest.TestCase):
    def test_init_run_context_creates_private_paths(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_file = Path(d) / "workspace.env"
            env_file.write_text("NAMEBRIGHT_API_TOKEN=example\n", encoding="utf-8")

            context = init_run_context(
                env_file=str(env_file),
                enabled=True,
                run_id="run-1",
                artifacts_dir=None,
                no_artifacts=False,
            )

            self.assertTrue(context.enabled)
            self.assertEqual(context.run_id, "run-1")
            self.assertIsNotNone(context.artifacts_dir)
            self.assertIsNotNone(context.runs_index_path)
            assert context.artifacts_dir is not None
            assert context.runs_index_path is not None
            self.assertTrue(context.artifacts_dir.exists())
            self.assertTrue(context.runs_index_path.exists() is False)
            self.assertEqual(context.artifacts_dir.stat().st_mode & 0o777, 0o700)

    def test_append_index_row_and_list_and_find(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            index = Path(d) / "index.jsonl"
            append_index_row(
                index,
                {
                    "run_id": "run-1",
                    "tool": "namebright-safe-cli",
                    "token": "top-secret",
                    "authorization": "Bearer abc",
                },
            )
            append_index_row(
                index,
                {
                    "run_id": "run-2",
                    "tool": "namebright-safe-agent-cli",
                    "token": "other-secret",
                },
            )

            self.assertEqual(index.stat().st_mode & 0o777, 0o600)
            self.assertEqual(index.parent.stat().st_mode & 0o777, 0o700)

            rows = [
                line.strip()
                for line in index.read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
            self.assertEqual(len(rows), 2)
            self.assertIn('"run_id": "run-1"', rows[0])
            self.assertNotIn("top-secret", rows[0])

            listed = list_runs(index)
            self.assertEqual(listed[0]["run_id"], "run-2")
            found = find_run(index, run_id="run-1")
            self.assertEqual(found["run_id"], "run-1")
            self.assertIsNone(find_run(index, run_id="run-missing"))

    def test_build_and_write_summary_are_redacted(self) -> None:
        lines = build_deterministic_summary(
            tool="namebright-safe-cli",
            version="0.1.0",
            run_id="run-3",
            env_fingerprint="dev",
            command="namebright-safe-cli apply",
            output_obj={
                "ok": True,
                "token": "nested-token",
                "clientSecret": "nested-secret",
            },
            plan_path="plan.json",
            receipt_path="receipt.json",
            audit_log_path="run-audit.jsonl",
            audit_log_global_path="global-audit.jsonl",
            runs_index_path="index.jsonl",
        )

        with tempfile.TemporaryDirectory() as d:
            summary_path = Path(d) / "summary.md"
            write_summary_md(path=summary_path, lines=lines)

            text = summary_path.read_text(encoding="utf-8")
            self.assertEqual(summary_path.stat().st_mode & 0o777, 0o600)
            self.assertNotIn("nested-token", text)
            self.assertNotIn("nested-secret", text)

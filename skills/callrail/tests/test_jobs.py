from __future__ import annotations

import argparse
import unittest
from pathlib import Path

from callrail_safe_agent_cli.cli import build_parser


def _subparser_choices(parser: argparse.ArgumentParser) -> dict[str, argparse.ArgumentParser]:
    for action in parser._actions:  # noqa: SLF001
        if isinstance(action, argparse._SubParsersAction):  # noqa: SLF001
            return action.choices
    raise AssertionError("Top-level subparsers not found in CLI parser")


class TestLegacyJobsSurfaceRemoved(unittest.TestCase):
    def test_jobs_and_demo_are_not_shipped_parser_commands(self) -> None:
        parser = build_parser()
        top = _subparser_choices(parser)
        self.assertNotIn("jobs", top)
        self.assertNotIn("demo", top)

    def test_jobs_docs_and_examples_are_honest_non_shipped_notes(self) -> None:
        root = Path(__file__).resolve().parents[1]
        jobs_doc = (root / "docs" / "jobs_and_batches.md").read_text(encoding="utf-8").lower()
        jobs_csv = (root / "examples" / "jobs.csv").read_text(encoding="utf-8").lower()
        jobs_write_csv = (root / "examples" / "jobs_with_write.csv").read_text(encoding="utf-8").lower()
        self.assertIn("does not ship a generic batch runner", jobs_doc)
        self.assertIn("does not ship a generic jobs runner", jobs_csv)
        self.assertIn("does not ship a generic jobs runner", jobs_write_csv)

    def test_scaffold_provenance_files_are_not_current_customer_docs(self) -> None:
        root = Path(__file__).resolve().parents[1]
        token_sample = (root / "examples" / "token.sample.json").read_text(encoding="utf-8").lower()
        self.assertFalse((root / "TEMPLATE_README.md").exists())
        self.assertFalse((root / "TEMPLATE_GUIDE.md").exists())
        self.assertIn("does not ship token-json storage commands", token_sample)

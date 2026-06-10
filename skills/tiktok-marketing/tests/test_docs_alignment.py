from __future__ import annotations

import re
import unittest
from pathlib import Path

from tiktok_marketing_safe_agent_cli.api_dispatch import load_operations_from_pinned_snapshot
from tiktok_marketing_safe_agent_cli.cli import build_parser


DOCS_DIR = Path(__file__).resolve().parent / ".." / "docs"


def _read_doc(name: str) -> str:
    return (DOCS_DIR / name).read_text(encoding="utf-8")


def _markdown_sections(text: str) -> list[str]:
    return [line.removeprefix("## ").strip() for line in re.findall(r"^##\s+.+$", text, flags=re.M)]


class TestDocsAlignment(unittest.TestCase):
    def test_runtime_operation_count_is_240(self) -> None:
        self.assertEqual(len(load_operations_from_pinned_snapshot()), 240)

    def test_api_coverage_documents_240_operations(self) -> None:
        coverage_text = _read_doc("api_coverage.md")

        match = re.search(r"Total operations in pinned manifest:\s*`(\d+)`", coverage_text)
        self.assertIsNotNone(match)
        self.assertEqual(int(match.group(1)), 240)

        marker = "## Endpoint coverage"
        endpoint_section = coverage_text.split(marker, 1)
        self.assertEqual(len(endpoint_section), 2)

        rows = 0
        in_table = False
        for line in endpoint_section[1].splitlines():
            if line.startswith("| Family | Operation command |"):
                in_table = True
                continue
            if not in_table:
                continue
            stripped = line.strip()
            if not stripped:
                break
            if stripped.startswith("|-") or "---" in stripped:
                continue
            if stripped.startswith("|"):
                rows += 1
        self.assertEqual(rows, 240)

    def test_command_reference_lists_real_command_groups_only(self) -> None:
        parser = build_parser()
        commands_action = next(action for action in parser._actions if action.dest == "cmd")
        command_groups = sorted(commands_action.choices.keys())
        self.assertListEqual(command_groups, ["api", "auth", "onboarding", "runs"])

        reference_text = _read_doc("command_reference.md")
        sections = {section.strip().lower() for section in _markdown_sections(reference_text)}
        self.assertIn("global flags", sections)
        self.assertIn("onboarding", sections)
        self.assertIn("auth", sections)
        self.assertIn("api operations", sections)
        self.assertIn("runs (local history)", sections)

        self.assertNotIn("demo", sections)
        self.assertNotIn("jobs", sections)

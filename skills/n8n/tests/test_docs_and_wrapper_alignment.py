from __future__ import annotations

import unittest
from pathlib import Path

from n8n_safe_agent_cli.inventory import load_inventory


class TestDocsAndWrapperAlignment(unittest.TestCase):
    def test_docs_and_skill_wrapper_match_inventory(self) -> None:
        root = Path(__file__).resolve().parents[1]
        inventory = load_inventory()
        operation_count = str(inventory["operation_count"])

        coverage = (root / "docs/api_coverage.md").read_text(encoding="utf-8")
        commands = (root / "docs/command_reference.md").read_text(encoding="utf-8")
        readme = (root / "README.md").read_text(encoding="utf-8")
        public_skill = root / "SKILL.md"
        source_skill = root / "skills/n8n/SKILL.md"
        skill = (public_skill if public_skill.exists() else source_skill).read_text(encoding="utf-8")

        self.assertIn(f"Official documented operations covered: **{operation_count}**", coverage)
        self.assertIn(f"covers {operation_count} public REST API operations", readme)
        self.assertIn("n8n-safe-agent-cli api workflow create-workflow", commands)
        self.assertIn("n8n-safe-agent-cli api list", skill)
        self.assertNotIn("raw request", skill.lower())

    def test_no_template_public_copy_left(self) -> None:
        root = Path(__file__).resolve().parents[1]
        bad: list[str] = []
        for path in [root / "README.md", root / "docs", root / "skills"]:
            files = [path] if path.is_file() else list(path.rglob("*.md"))
            for file in files:
                text = file.read_text(encoding="utf-8")
                markers = ("Example" + " Skill", "example" + "-skill", "<" + "tool>", "READ" + "_COMMAND")
                for marker in markers:
                    if marker in text:
                        bad.append(f"{file.relative_to(root)} contains {marker}")
        self.assertFalse(bad, "\n".join(bad))

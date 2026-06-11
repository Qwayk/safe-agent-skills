from __future__ import annotations

import argparse
import unittest
from pathlib import Path

from awin_advertiser_safe_agent_cli.cli import build_parser


class TestDocsStandard(unittest.TestCase):
    def setUp(self) -> None:
        self.root = Path(__file__).resolve().parents[1]
        self.docs = self.root / "docs"

    def test_required_repo_standard_docs_exist(self) -> None:
        required = [
            self.docs / "use_cases.md",
            self.docs / "safety_model.md",
            self.docs / "quickstart.md",
        ]
        for path in required:
            with self.subTest(path=path.name):
                self.assertTrue(path.exists(), f"Missing required docs file: {path.name}")

    def test_readme_is_non_technical_first(self) -> None:
        text = (self.root / "README.md").read_text(encoding="utf-8")
        self.assertIn("## For non-technical users: Start here (no coding)", text)
        self.assertIn("## For technical users: Start here (CLI)", text)
        self.assertIn("docs/use_cases.md", text)
        self.assertIn("docs/safety_model.md", text)

    def test_docs_readme_lists_required_order(self) -> None:
        text = (self.docs / "README.md").read_text(encoding="utf-8")
        use_cases_idx = text.index("use_cases.md")
        onboarding_idx = text.index("onboarding.md")
        safety_idx = text.index("safety_model.md")
        quickstart_idx = text.index("quickstart.md")
        command_idx = text.index("command_reference.md")
        self.assertLess(use_cases_idx, onboarding_idx)
        self.assertLess(onboarding_idx, safety_idx)
        self.assertLess(safety_idx, quickstart_idx)
        self.assertLess(quickstart_idx, command_idx)

    def test_onboarding_and_technical_labels_exist(self) -> None:
        onboarding = (self.docs / "onboarding.md").read_text(encoding="utf-8")
        quickstart = (self.docs / "quickstart.md").read_text(encoding="utf-8")
        command_reference = (self.docs / "command_reference.md").read_text(encoding="utf-8")
        proof = (self.docs / "proof.md").read_text(encoding="utf-8")

        self.assertIn("What to ask your AI agent (examples)", onboarding)
        self.assertIn("Technical reference", quickstart)
        self.assertIn("Technical reference", command_reference)
        self.assertIn("You don’t need to run these commands yourself", proof)

    def test_api_coverage_lists_all_provider_backed_commands(self) -> None:
        parser = build_parser()
        endpoint_coverage = self._endpoint_coverage_section()
        support_only = {"onboarding", "runs list", "runs show"}
        live_commands = sorted(
            command
            for command in self._leaf_commands(parser)
            if command not in support_only
        )
        missing = [command for command in live_commands if f"`{command}`" not in endpoint_coverage]
        self.assertEqual(
            [],
            missing,
            "docs/api_coverage.md is missing shipped provider-backed command(s): "
            + ", ".join(missing),
        )

    def _endpoint_coverage_section(self) -> str:
        text = (self.docs / "api_coverage.md").read_text(encoding="utf-8")
        return text.split("## Endpoint coverage", 1)[1].split("## Implementation notes and live limits", 1)[0]

    def _leaf_commands(self, parser: argparse.ArgumentParser, prefix: tuple[str, ...] = ()) -> list[str]:
        commands: list[str] = []
        for action in parser._actions:
            if not isinstance(action, argparse._SubParsersAction):
                continue
            for name, subparser in action.choices.items():
                command = prefix + (name,)
                nested = self._leaf_commands(subparser, command)
                if nested:
                    commands.extend(nested)
                    continue
                if subparser._defaults.get("func") is not None:
                    commands.append(" ".join(command))
        return commands

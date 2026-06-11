from __future__ import annotations

import argparse
import json
import re
import unittest
from pathlib import Path

from google_business_profile_safe_agent_cli.cli import TOOL_NAME, build_parser


_IMPLEMENTED_PATTERN = re.compile(r"- `([^`]+)` -> `([^`]+)` \(`implemented`\)")


class TestOfficialInventory(unittest.TestCase):
    def _root(self) -> Path:
        return Path(__file__).resolve().parents[1]

    def _load_inventory(self) -> dict:
        inventory_path = self._root() / "docs" / "official_inventory.json"
        return json.loads(inventory_path.read_text(encoding="utf-8"))

    def _implemented_from_coverage(self) -> set[tuple[str, str]]:
        coverage_path = self._root() / "docs" / "api_coverage.md"
        coverage_text = coverage_path.read_text(encoding="utf-8")
        return set(_IMPLEMENTED_PATTERN.findall(coverage_text))

    def _implemented_from_inventory(self) -> set[tuple[str, str]]:
        data = self._load_inventory()
        implemented: set[tuple[str, str]] = set()
        for family in data["families"]:
            for op in family["operations"]:
                if "implemented" in op.get("flags", []):
                    implemented.add((op["method_id"], op["planned_command"]))
        return implemented

    def _collect_leaf_commands(self) -> set[str]:
        parser = build_parser()
        commands: set[str] = set()

        def walk(current: argparse.ArgumentParser, parts: list[str]) -> None:
            if current.get_default("func") is not None and parts:
                commands.add(f"{TOOL_NAME} {' '.join(parts)}")
            for action in current._actions:
                if isinstance(action, argparse._SubParsersAction):
                    for name, child in action.choices.items():
                        walk(child, [*parts, name])

        walk(parser, [])
        return commands

    def test_inventory_has_expected_families_and_unique_commands(self) -> None:
        data = self._load_inventory()

        self.assertEqual(data["tool_name"], TOOL_NAME)
        self.assertIn("families", data)

        families = data["families"]
        slugs = {family["slug"] for family in families}
        self.assertEqual(
            slugs,
            {
                "account-management",
                "business-info",
                "lodging",
                "notifications",
                "performance",
                "place-actions",
                "qanda",
                "verifications",
                "business-calls",
                "media-upload-v1",
                "legacy-v49",
            },
        )

        commands: list[str] = []
        for family in families:
            self.assertIn("operations", family)
            self.assertTrue(family["operations"], f"Family {family['slug']} should not be empty")
            for op in family["operations"]:
                self.assertIn("method_id", op)
                self.assertIn("planned_command", op)
                commands.append(op["planned_command"])

        self.assertEqual(len(commands), len(set(commands)), "Planned commands must be unique")

    def test_implemented_inventory_matches_api_coverage_and_cli(self) -> None:
        coverage_implemented = self._implemented_from_coverage()
        inventory_implemented = self._implemented_from_inventory()

        self.assertEqual(
            inventory_implemented,
            coverage_implemented,
            "docs/official_inventory.json implemented flags must match docs/api_coverage.md implemented rows",
        )

        leaf_commands = self._collect_leaf_commands()
        missing_commands = sorted(command for _, command in coverage_implemented if command not in leaf_commands)
        self.assertEqual(
            missing_commands,
            [],
            f"Implemented coverage commands missing from CLI parser: {missing_commands}",
        )

    def test_discontinued_and_discovery_only_flags_are_present(self) -> None:
        data = self._load_inventory()
        families = {family["slug"]: family for family in data["families"]}

        qanda_flags = set(families["qanda"]["default_flags"])
        self.assertIn("provider-discontinued", qanda_flags)

        verification_ops = families["verifications"]["operations"]
        verification_tokens = next(op for op in verification_ops if op["method_id"] == "verificationTokens.generate")
        self.assertIn("discovery-only", verification_tokens["flags"])

        legacy_ops = families["legacy-v49"]["operations"]
        legacy_qanda = next(op for op in legacy_ops if op["method_id"] == "accounts.locations.questions.list")
        self.assertIn("provider-discontinued", legacy_qanda["flags"])

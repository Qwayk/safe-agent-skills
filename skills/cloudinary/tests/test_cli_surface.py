from __future__ import annotations

import argparse
import unittest
from pathlib import Path

from cloudinary_safe_agent_cli.cli import build_parser
from cloudinary_safe_agent_cli.inventory import load_operation_specs, load_specs_by_area


def _subparser_choices(parser: argparse.ArgumentParser) -> dict[str, argparse.ArgumentParser]:
    for action in parser._actions:
        if isinstance(action, argparse._SubParsersAction):
            return action.choices
    return {}


class TestCliSurface(unittest.TestCase):
    def test_top_level_commands_are_explicit(self) -> None:
        parser = build_parser()
        self.assertEqual(
            set(_subparser_choices(parser).keys()),
            {"runs", "onboarding", "auth", "operations"},
        )

    def test_every_inventory_operation_is_wired_into_parser(self) -> None:
        parser = build_parser()
        top = _subparser_choices(parser)
        operations_parser = top["operations"]
        operations_top = _subparser_choices(operations_parser)
        grouped = load_specs_by_area()

        self.assertIn("list", operations_top)
        self.assertIn("show", operations_top)
        self.assertEqual(set(grouped.keys()), {k for k in operations_top.keys() if k not in {"list", "show"}})

        for area, specs in grouped.items():
            area_parser = operations_top[area]
            area_top = _subparser_choices(area_parser)
            for spec in specs:
                self.assertIn(spec.op_key, area_top, f"Missing parser for {spec.command}")

    def test_api_coverage_file_lists_every_shipped_command(self) -> None:
        root = Path(__file__).resolve().parents[1]
        coverage_text = (root / "docs" / "api_coverage.md").read_text(encoding="utf-8")
        specs = load_operation_specs()

        self.assertIn(f"Official REST operations shipped: `{len(specs)}`", coverage_text)
        for spec in specs:
            self.assertIn(spec.command, coverage_text, spec.command)

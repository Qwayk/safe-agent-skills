from __future__ import annotations

import unittest
import argparse
from pathlib import Path

from bluesky_safe_agent_cli.api_dispatch import load_operations_from_pinned_snapshot
from bluesky_safe_agent_cli.cli import build_parser


def _get_subparser(parser: argparse.ArgumentParser, name: str) -> argparse.ArgumentParser:
    for action in parser._actions:  # noqa: SLF001
        if isinstance(action, argparse._SubParsersAction):  # noqa: SLF001
            target = action.choices.get(name)
            if target is not None:
                return target
    raise AssertionError(f"Missing subparser: {name}")


def _get_subcommand_names(parser: argparse.ArgumentParser) -> set[str]:
    for action in parser._actions:  # noqa: SLF001
        if isinstance(action, argparse._SubParsersAction):  # noqa: SLF001
            return set(action.choices.keys())
    return set()


def _extract_api_coverage_commands(text: str) -> list[str]:
    rows: list[str] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line.startswith("|"):
            continue
        if line.startswith("| operation_command "):
            continue
        if line.startswith("|---"):
            continue
        cols = [part.strip() for part in line.strip("|").split("|")]
        if not cols:
            continue
        command = cols[0].strip("`").strip()
        if command:
            rows.append(command)
    return rows


class TestApiSurface(unittest.TestCase):
    def test_every_pinned_operation_is_registered_as_api_subcommand(self) -> None:
        ops = load_operations_from_pinned_snapshot()
        expected = sorted((op.operation_command for op in ops))
        parser = build_parser()
        api_parser = _get_subparser(parser, "api")
        names = sorted(name for name in _get_subcommand_names(api_parser) if name != "ops")

        reserved = {"ops"}
        for op in expected:
            self.assertNotIn(op, reserved, f"Reserved command collision: {op}")
            self.assertIn(op, names, f"Missing api subcommand for operation: {op}")
        self.assertEqual(len(names), len(set(names)))
        self.assertEqual(names, expected)

    def test_pinned_inventory_has_unique_operation_commands(self) -> None:
        ops = load_operations_from_pinned_snapshot()
        commands = [op.operation_command for op in ops]
        self.assertEqual(len(commands), len(set(commands)))
        self.assertEqual(len(commands), 304)

    def test_docs_api_coverage_tracks_every_pinned_inventory_command(self) -> None:
        root = Path(__file__).resolve().parents[1]
        parser = build_parser()
        api_parser = _get_subparser(parser, "api")
        names = sorted([name for name in _get_subcommand_names(api_parser) if name != "ops"])
        coverage = _extract_api_coverage_commands((root / "docs" / "api_coverage.md").read_text(encoding="utf-8"))

        ops = load_operations_from_pinned_snapshot()
        expected = sorted(op.operation_command for op in ops)

        self.assertEqual(expected, coverage)
        self.assertEqual(names, expected)

    def test_parser_accepts_explicit_inventory_subcommands(self) -> None:
        parser = build_parser()
        parsed = parser.parse_args(["api", "app-bsky-feed-get-timeline"])
        self.assertEqual(parsed.cmd, "api")
        self.assertEqual(parsed.op, "app-bsky-feed-get-timeline")

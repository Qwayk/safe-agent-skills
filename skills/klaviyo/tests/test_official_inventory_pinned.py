from __future__ import annotations

import argparse
import json
import unittest
from pathlib import Path

from klaviyo_safe_agent_cli.cli import build_parser
from klaviyo_safe_agent_cli.official_inventory import load_official_operations_file


def _tool_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _latest_official_ops_file() -> Path:
    docs = _tool_root() / "docs"
    candidates = sorted(docs.glob("official_operations_v1_*.json"))
    if not candidates:
        raise AssertionError("Missing docs/official_operations_v1_*.json")
    return candidates[-1]


def _get_subparser(choices, name: str) -> argparse.ArgumentParser:
    for action in choices._actions:  # noqa: SLF001
        if isinstance(action, argparse._SubParsersAction):  # noqa: SLF001
            if name in action.choices:
                return action.choices[name]
    raise AssertionError(f"Missing subparser: {name}")


def _subparser_names(action: argparse._SubParsersAction) -> set[str]:
    return set(action.choices.keys())


class TestOfficialInventoryPinned(unittest.TestCase):
    def test_pinned_snapshot_metadata_and_count(self) -> None:
        ops_path = _latest_official_ops_file()
        payload = json.loads(ops_path.read_text(encoding="utf-8"))
        self.assertEqual(payload.get("operation_source_count"), 308)
        self.assertEqual(payload.get("beta_source_count"), 87)
        reason = payload.get("excluded_beta_reason")
        self.assertIsNotNone(reason)
        self.assertIn("beta", str(reason).lower())

    def test_pinned_operations_are_unique(self) -> None:
        ops = load_official_operations_file(_latest_official_ops_file())
        self.assertTrue(ops)

        seen_cmd: set[str] = set()
        seen_method_path: set[tuple[str, str]] = set()
        for op in ops:
            key = (op.method, op.path)
            self.assertNotIn(key, seen_method_path, f"Duplicate method+path: {key}")
            self.assertNotIn(op.operation_command, seen_cmd, f"Duplicate operation command: {op.operation_command}")
            seen_method_path.add(key)
            seen_cmd.add(op.operation_command)

    def test_every_pinned_operation_is_a_cli_subcommand(self) -> None:
        ops = load_official_operations_file(_latest_official_ops_file())
        parser = build_parser()
        api_parser = _get_subparser(parser, "api")
        for action in api_parser._actions:  # noqa: SLF001
            if isinstance(action, argparse._SubParsersAction):  # noqa: SLF001
                names = _subparser_names(action)
                break
        else:
            raise AssertionError("Missing api subparser action")

        reserved = {"ops", "show"}
        for op in ops:
            self.assertNotIn(op.operation_command, reserved)
            self.assertIn(op.operation_command, names, f"Missing api subcommand for operation: {op.operation_command}")

    def test_api_coverage_has_one_row_per_stable_operation(self) -> None:
        coverage = (_tool_root() / "docs" / "api_coverage.md").read_text(encoding="utf-8")
        rows: list[str] = []
        for raw in coverage.splitlines():
            line = raw.strip()
            if not line.startswith("|"):
                continue
            if line.startswith("| Operation command") or line.startswith("|---"):
                continue
            cols = [c.strip() for c in line.strip("|").split("|")]
            if cols and cols[0]:
                rows.append(cols[0].strip("`"))

        expected = [op.operation_command for op in load_official_operations_file(_latest_official_ops_file())]
        self.assertEqual(rows, expected)

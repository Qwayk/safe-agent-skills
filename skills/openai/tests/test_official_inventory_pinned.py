from __future__ import annotations

import argparse
import hashlib
import unittest
from pathlib import Path

from openai_api_tool.cli import build_parser
from openai_api_tool.official_inventory import load_official_operations_file


def _tool_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _latest_official_ops_file() -> Path:
    docs = _tool_root() / "docs"
    candidates = sorted(docs.glob("official_operations_v1_*.txt"))
    if not candidates:
        raise AssertionError("Missing docs/official_operations_v1_*.txt")
    return candidates[-1]


def _get_subparser_choices(p: argparse.ArgumentParser, name: str) -> argparse.ArgumentParser:
    for a in p._actions:  # noqa: SLF001
        if isinstance(a, argparse._SubParsersAction):  # noqa: SLF001
            if name in a.choices:
                return a.choices[name]
    raise AssertionError(f"Missing subparser: {name}")


def _get_subcommand_names(p: argparse.ArgumentParser) -> set[str]:
    for a in p._actions:  # noqa: SLF001
        if isinstance(a, argparse._SubParsersAction):  # noqa: SLF001
            return set(a.choices.keys())
    return set()


class TestOfficialInventoryPinned(unittest.TestCase):
    def test_pinned_operations_are_unique(self) -> None:
        ops_path = _latest_official_ops_file()
        ops = load_official_operations_file(ops_path)
        self.assertTrue(ops, "Expected at least one operation in pinned inventory")

        seen_method_path: set[tuple[str, str]] = set()
        for op in ops:
            key = (op.method, op.path)
            self.assertNotIn(key, seen_method_path, f"Duplicate method+path: {key}")
            seen_method_path.add(key)

        seen_cmd: set[str] = set()
        for op in ops:
            self.assertNotIn(op.operation_command, seen_cmd, f"Duplicate operation_command: {op.operation_command}")
            seen_cmd.add(op.operation_command)

    def test_every_pinned_operation_is_a_cli_subcommand(self) -> None:
        ops_path = _latest_official_ops_file()
        ops = load_official_operations_file(ops_path)
        parser = build_parser()

        cmd = _get_subparser_choices(parser, "api")
        # `api` has its own subcommands; operation commands are registered here.
        names = _get_subcommand_names(cmd)

        reserved = {"ops"}
        for op in ops:
            self.assertNotIn(op.operation_command, reserved)
            self.assertIn(op.operation_command, names, f"Missing api subcommand for operation: {op.operation_command}")

    def test_api_coverage_has_one_row_per_operation(self) -> None:
        root = _tool_root()
        coverage = root / "docs" / "api_coverage.md"
        self.assertTrue(coverage.exists(), "Missing docs/api_coverage.md")
        md = coverage.read_text(encoding="utf-8")

        got: list[str] = []
        for raw in md.splitlines():
            line = raw.strip()
            if not line.startswith("|"):
                continue
            if line.startswith("| operation_command "):
                continue
            if line.startswith("|---"):
                continue
            cols = [c.strip() for c in line.strip("|").split("|")]
            if not cols:
                continue
            op_cmd = cols[0].strip().strip("`")
            if op_cmd:
                got.append(op_cmd)

        ops = load_official_operations_file(_latest_official_ops_file())
        expected = [o.operation_command for o in ops]
        self.assertEqual(got, expected)

    def test_official_ops_header_references_snapshot_sha(self) -> None:
        ops_path = _latest_official_ops_file()
        lines = ops_path.read_text(encoding="utf-8").splitlines()
        header = next((line for line in lines if line.startswith("# OpenAPI snapshot:")), None)
        self.assertIsNotNone(header, "Missing OpenAPI snapshot header")
        _, rest = header.split(":", 1)
        snapshot_part, sha_part = rest.strip().rsplit(" sha256=", 1)
        snapshot_file = snapshot_part.strip()
        expected_sha = sha_part.strip()

        snapshot_path = _tool_root() / "docs" / snapshot_file
        self.assertTrue(snapshot_path.exists(), f"Snapshot file not found: {snapshot_file}")
        actual_sha = hashlib.sha256(snapshot_path.read_bytes()).hexdigest()
        self.assertEqual(actual_sha, expected_sha, "Snapshot checksum mismatch")

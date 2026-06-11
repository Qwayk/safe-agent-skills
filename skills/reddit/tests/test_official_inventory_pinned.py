from __future__ import annotations

import argparse
import hashlib
import unittest
from pathlib import Path

from qwayk_reddit_safe_agent_cli.cli import build_parser
from qwayk_reddit_safe_agent_cli.official_inventory import load_official_operations_file


def _tool_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _latest_official_ops_file() -> Path:
    docs = _tool_root() / "docs"
    candidates = sorted(docs.glob("official_operations_v1_*.txt"))
    if not candidates:
        raise AssertionError("Missing docs/official_operations_v1_*.txt")
    return candidates[-1]


def _get_subparser_choices(parser: argparse.ArgumentParser, name: str) -> argparse.ArgumentParser:
    for action in parser._actions:  # noqa: SLF001
        if isinstance(action, argparse._SubParsersAction):  # noqa: SLF001
            if name in action.choices:
                return action.choices[name]
    raise AssertionError(f"Missing subparser: {name}")


def _get_subcommand_names(parser: argparse.ArgumentParser) -> set[str]:
    for action in parser._actions:  # noqa: SLF001
        if isinstance(action, argparse._SubParsersAction):  # noqa: SLF001
            return set(action.choices.keys())
    return set()


class TestOfficialInventoryPinned(unittest.TestCase):
    def test_pinned_operations_are_unique(self) -> None:
        ops = load_official_operations_file(_latest_official_ops_file())
        self.assertTrue(ops, "Expected at least one Reddit operation in pinned inventory")

        seen_method_path: set[tuple[str, str]] = set()
        seen_cmd: set[str] = set()
        for op in ops:
            method_path = (op.method, op.path)
            self.assertNotIn(method_path, seen_method_path, f"Duplicate method+path: {method_path}")
            self.assertNotIn(op.operation_command, seen_cmd, f"Duplicate operation_command: {op.operation_command}")
            seen_method_path.add(method_path)
            seen_cmd.add(op.operation_command)

    def test_api_coverage_has_one_row_per_operation(self) -> None:
        coverage = (_tool_root() / "docs" / "api_coverage.md").read_text(encoding="utf-8")
        got: list[str] = []
        for raw in coverage.splitlines():
            line = raw.strip()
            if not line.startswith("|"):
                continue
            if line.startswith("| operation_command "):
                continue
            if line.startswith("|---"):
                continue
            columns = [part.strip() for part in line.strip("|").split("|")]
            if not columns:
                continue
            op_cmd = columns[0].strip().strip("`")
            if op_cmd:
                got.append(op_cmd)

        expected = [op.operation_command for op in load_official_operations_file(_latest_official_ops_file())]
        self.assertEqual(got, expected)

    def test_every_pinned_operation_is_a_cli_subcommand(self) -> None:
        parser = build_parser()
        api_parser = _get_subparser_choices(parser, "api")
        names = _get_subcommand_names(api_parser)
        reserved = {"ops"}
        for op in load_official_operations_file(_latest_official_ops_file()):
            self.assertNotIn(op.operation_command, reserved)
            self.assertIn(op.operation_command, names, f"Missing api subcommand for operation: {op.operation_command}")

    def test_colon_style_paths_include_required_path_metadata(self) -> None:
        for op in load_official_operations_file(_latest_official_ops_file()):
            if "/:" not in op.path:
                continue
            required = op.required_path_params
            self.assertTrue(required, f"Missing required_path for colon-style path: {op.operation_command} {op.path}")

    def test_snapshot_sha_matches_header(self) -> None:
        ops_path = _latest_official_ops_file()
        lines = ops_path.read_text(encoding="utf-8").splitlines()
        header = next((line for line in lines if line.startswith("# Reddit docs snapshot:")), None)
        self.assertIsNotNone(header, "Missing Reddit docs snapshot header")
        assert header is not None
        _, rest = header.split(":", 1)
        snapshot_part, sha_part = rest.strip().rsplit(" sha256=", 1)
        snapshot_name = snapshot_part.strip()
        expected_sha = sha_part.strip()

        snapshot_path = _tool_root() / "docs" / snapshot_name
        self.assertTrue(snapshot_path.exists(), f"Snapshot file not found: {snapshot_name}")
        actual_sha = hashlib.sha256(snapshot_path.read_bytes()).hexdigest()
        self.assertEqual(actual_sha, expected_sha)

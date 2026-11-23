from __future__ import annotations

import re
import shlex
import unittest
from pathlib import Path

from figma_safe_agent_cli.cli import build_parser
from figma_safe_agent_cli.operation_specs import OPERATION_SPECS


def _build_rows():
    root = Path(__file__).resolve().parents[1]
    path = root / "docs" / "api_coverage.md"
    text = path.read_text(encoding="utf-8")
    rows = []
    for line in text.splitlines():
        if not line.startswith("| "):
            continue
        if line.startswith("| In-scope area") or line.startswith("|---"):
            continue
        cols = [col.strip() for col in line.strip().strip("|").split("|")]
        if len(cols) != 7:
            continue
        area, endpoint, _capability, command_col = cols[:4]
        m = re.match(r"^(GET|POST|PUT|PATCH|DELETE)\s+(.+)$", endpoint.strip("`"))
        if not m:
            raise AssertionError(f"Invalid endpoint format in api_coverage: {endpoint}")
        method, path = m.groups()
        command_clean = command_col.strip().strip("`")
        match = re.search(r"figma-safe-agent-cli\s+operations\s+([^\s]+)\s+([^\s]+)", command_clean)
        if not match:
            raise AssertionError(f"Missing command mapping in api_coverage row: {endpoint}")
        area_arg, op_key = match.groups()
        if area_arg in {"list", "show"}:
            raise AssertionError(f"Invalid helper command in api_coverage row: {area_arg}: {endpoint}")
        rows.append((area, method, path, op_key))
    return rows


class TestDocsAndCoverageGuard(unittest.TestCase):
    def test_api_coverage_matches_operation_inventory(self) -> None:
        spec_rows = {(s.area, s.method, s.path_template, s.op_key) for s in OPERATION_SPECS}
        coverage_rows = set(_build_rows())

        missing_from_coverage = sorted(spec_rows - coverage_rows)
        extra_in_coverage = sorted(coverage_rows - spec_rows)

        if missing_from_coverage:
            joined = ", ".join(
                f"{area}:{method}:{path}:{op}" for area, method, path, op in missing_from_coverage
            )
            self.fail(f"Missing in docs/api_coverage.md: {joined}")
        if extra_in_coverage:
            joined = ", ".join(
                f"{area}:{method}:{path}:{op}" for area, method, path, op in extra_in_coverage
            )
            self.fail(f"Extra in docs/api_coverage.md: {joined}")

    def test_quickstart_and_command_examples_parse(self) -> None:
        root = Path(__file__).resolve().parents[1]
        parser = build_parser()
        checked = []
        for rel in ("docs/quickstart.md", "docs/command_reference.md"):
            for line in (root / rel).read_text(encoding="utf-8").splitlines():
                command = line.strip().strip("`")
                if not command.startswith("figma-safe-agent-cli "):
                    continue
                with self.subTest(command=command):
                    parser.parse_args(shlex.split(command)[1:])
                checked.append(command)
        self.assertTrue(checked)

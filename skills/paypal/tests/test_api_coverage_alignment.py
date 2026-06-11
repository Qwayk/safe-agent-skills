from __future__ import annotations

import re
import unittest
from collections import Counter
from pathlib import Path

from paypal_safe_agent_cli.commands import paypal

_DOC_PATH = Path(__file__).resolve().parents[1] / "docs" / "api_coverage.md"
_COVERAGE_SECTION = "## Endpoint coverage"
_ROW_RE = re.compile(r"^\|\s*[^|]+\|\s*[^|]+\|\s*`([^`]+)`\s*\|")


def _extract_doc_commands(doc_path: Path) -> list[tuple[str, str]]:
    values: list[tuple[str, str]] = []
    in_coverage = False
    for line in doc_path.read_text(encoding="utf-8").splitlines():
        if line.startswith(_COVERAGE_SECTION):
            in_coverage = True
            continue
        if not in_coverage:
            continue
        if line.startswith("## ") and _COVERAGE_SECTION not in line:
            break
        m = _ROW_RE.match(line.strip())
        if not m:
            continue
        command = m.group(1).strip()
        if not command.startswith("qwayk-paypal-safe-agent-cli "):
            continue
        parts = command.split()
        if len(parts) != 3:
            raise AssertionError(f"Invalid command entry in docs table: {command}")
        _, family, action = parts
        values.append((family, action))
    return values


def _extract_doc_gates(doc_path: Path) -> dict[tuple[str, str], str]:
    values: dict[tuple[str, str], str] = {}
    in_coverage = False
    for raw_line in doc_path.read_text(encoding="utf-8").splitlines():
        if raw_line.startswith(_COVERAGE_SECTION):
            in_coverage = True
            continue
        if not in_coverage:
            continue
        if raw_line.startswith("## ") and _COVERAGE_SECTION not in raw_line:
            break
        line = raw_line.strip()
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.split("|")[1:-1]]
        if len(cells) < 4:
            continue
        command = cells[2].strip().strip("`")
        if not command.startswith("qwayk-paypal-safe-agent-cli "):
            continue
        parts = command.split()
        if len(parts) != 3:
            raise AssertionError(f"Invalid command entry in docs table: {command}")
        _, family, action = parts
        values[(family, action)] = cells[3]
    return values


class TestApiCoverageAlignment(unittest.TestCase):
    def test_api_coverage_table_matches_runtime_commands(self) -> None:
        shipped = {(family, action) for family, actions in paypal.actions().items() for action in actions}
        doc_rows = _extract_doc_commands(_DOC_PATH)
        doc_set = set(doc_rows)

        duplicates = [item for item, count in Counter(doc_rows).items() if count > 1]
        self.assertFalse(
            duplicates,
            "Duplicate CLI rows in docs/api_coverage.md endpoint coverage table: "
            + ", ".join(f"{family} {action}" for family, action in sorted(duplicates)),
        )

        if shipped != doc_set:
            missing = sorted(shipped - doc_set)
            extra = sorted(doc_set - shipped)
            details: list[str] = []
            if missing:
                details.append("missing from docs: " + ", ".join(f"{family} {action}" for family, action in missing))
            if extra:
                details.append("extra in docs: " + ", ".join(f"{family} {action}" for family, action in extra))
            self.fail(
                "docs/api_coverage.md endpoint coverage table does not match shipped command ledger; "
                + "; ".join(details)
            )

    def test_api_coverage_safety_gates_match_runtime_requirements(self) -> None:
        doc_gates = _extract_doc_gates(_DOC_PATH)
        for family, family_actions in paypal.actions().items():
            for action, spec in family_actions.items():
                with self.subTest(family=family, action=action):
                    self.assertIn((family, action), doc_gates)
                    gates = doc_gates[(family, action)]
                    self.assertEqual("--yes" in gates, spec.require_yes)
                    self.assertEqual("--ack-irreversible" in gates, spec.require_ack)

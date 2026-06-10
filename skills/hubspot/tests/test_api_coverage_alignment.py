from __future__ import annotations

import re
import unittest
from collections import Counter
from pathlib import Path

from hubspot_safe_agent_cli.commands import hubspot


_DOC_PATH = Path(__file__).resolve().parents[1] / "docs" / "api_coverage.md"
_COVERAGE_SECTION = "## Endpoint coverage"
_ROW_RE = re.compile(r"^\|\s*[^|]+\|\s*[^|]+\|\s*`([^`]+)`\s*\|")


def _extract_doc_commands(doc_path: Path) -> list[tuple[str, str]]:
    lines = doc_path.read_text(encoding="utf-8").splitlines()
    in_section = False
    values: list[tuple[str, str]] = []
    for line in lines:
        if line.startswith(_COVERAGE_SECTION):
            in_section = True
            continue
        if not in_section:
            continue
        if line.startswith("## ") and _COVERAGE_SECTION not in line:
            break
        m = _ROW_RE.match(line.strip())
        if not m:
            continue
        command = m.group(1).strip()
        if not command.startswith("hubspot "):
            continue
        parts = command.split()
        if len(parts) != 3:
            raise AssertionError(f"Invalid CLI command in docs table: {command}")
        _, family, action = parts
        values.append((family, action))
    return values


class TestApiCoverageAlignment(unittest.TestCase):
    def test_api_coverage_table_matches_runtime_commands(self) -> None:
        shipped = {(family, action) for family, actions in hubspot.actions().items() for action in actions}
        doc_rows = _extract_doc_commands(_DOC_PATH)
        doc_set = set(doc_rows)

        duplicates = [item for item, count in Counter(doc_rows).items() if count > 1]
        self.assertFalse(
            duplicates,
            "Duplicate CLI rows in docs/api_coverage.md endpoint table: " + ", ".join(f"{k[0]} {k[1]}" for k in sorted(duplicates)),
        )

        if shipped != doc_set:
            missing = sorted(shipped - doc_set)
            extra = sorted(doc_set - shipped)
            details = []
            if missing:
                details.append("missing from docs: " + ", ".join(f"{family} {action}" for family, action in missing))
            if extra:
                details.append("extra in docs: " + ", ".join(f"{family} {action}" for family, action in extra))
            self.fail("docs/api_coverage.md command ledger no longer matches shipped CLI actions: " + "; ".join(details))

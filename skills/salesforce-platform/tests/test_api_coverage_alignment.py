from __future__ import annotations

import re
import unittest
from pathlib import Path

from tests import bootstrap  # noqa: F401

from salesforce_platform_safe_agent_cli.commands import salesforce

_DOC_PATH = Path(__file__).resolve().parents[1] / "docs" / "api_coverage.md"
_SECTION = "## Runtime action inventory"
_LINE_RE = re.compile(r"^- `([^`]+)`: (.+)$")


def _extract_inventory(doc_path: Path) -> dict[str, set[str]]:
    inventory: dict[str, set[str]] = {}
    in_section = False
    for raw_line in doc_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if line == _SECTION:
            in_section = True
            continue
        if not in_section:
            continue
        if line.startswith("## "):
            break
        match = _LINE_RE.match(line)
        if not match:
            continue
        family = match.group(1)
        actions = {part.strip().strip("`") for part in match.group(2).split(",") if part.strip()}
        inventory[family] = actions
    return inventory


class TestApiCoverageAlignment(unittest.TestCase):
    def test_runtime_inventory_matches_docs(self) -> None:
        runtime = {family: set(actions.keys()) for family, actions in salesforce.actions().items()}
        documented = _extract_inventory(_DOC_PATH)
        self.assertEqual(runtime, documented)

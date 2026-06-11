from __future__ import annotations

import json
from pathlib import Path
import unittest


def _catalog_commands(root: Path) -> set[str]:
    catalog_path = root / "src" / ".openapi" / "pipedrive_endpoint_catalog.json"
    raw = json.loads(catalog_path.read_text(encoding="utf-8"))
    commands = set()
    for entry in raw:
        operation = str(entry.get("operation") or "").strip()
        if not operation.startswith("GET "):
            continue
        tokens = [str(t).strip() for t in (entry.get("command_tokens") or []) if str(t).strip()]
        if len(tokens) != 2:
            continue
        commands.add(" ".join(tokens))
    return commands


def _docs_commands(root: Path) -> set[str]:
    docs_path = root / "docs" / "api_coverage.md"
    lines = docs_path.read_text(encoding="utf-8").splitlines()
    prefix = "qwayk-pipedrive-safe-agent-cli "
    commands = set()
    for line in lines:
        if not line.startswith("| GET |"):
            continue
        cols = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cols) < 5:
            continue
        planned = cols[4]
        if not planned.startswith(prefix):
            continue
        command = planned[len(prefix):].strip()
        if command and not command.startswith("excluded"):
            commands.add(command)
    return commands


class TestCoverageAlignment(unittest.TestCase):
    def test_shipped_get_commands_match_docs_catalog(self) -> None:
        root = Path(__file__).resolve().parents[1]
        self.assertEqual(_catalog_commands(root), _docs_commands(root))

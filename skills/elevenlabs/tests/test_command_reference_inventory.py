from __future__ import annotations

from pathlib import Path
import unittest

from elevenlabs_api_tool.operations import OPERATIONS


class TestCommandReferenceInventory(unittest.TestCase):
    def test_every_operation_command_is_listed_in_command_reference(self) -> None:
        text = Path("docs/command_reference.md").read_text(encoding="utf-8")
        missing: list[str] = []
        for op in OPERATIONS:
            if op.cli_command not in text:
                missing.append(op.cli_command)
        self.assertFalse(
            missing,
            msg="docs/command_reference.md must list every explicit CLI command. Missing: " + ", ".join(missing),
        )

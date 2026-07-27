from __future__ import annotations

import unittest

from asana_safe_agent_cli.cli import build_parser
from asana_safe_agent_cli.inventory import command_names


class TestNoGenericBridge(unittest.TestCase):
    def test_only_fixed_inventory_commands_are_accepted_by_api_parser(self) -> None:
        parser = build_parser()
        namespace = parser.parse_args(["api", "get-workspaces"])
        self.assertEqual(namespace.operation, "get-workspaces")
        self.assertNotIn("create-batch-request", command_names())

    def test_generic_bridge_words_are_not_top_level_commands(self) -> None:
        parser = build_parser()
        top_level = next(action for action in parser._actions if action.dest == "cmd")
        names = set(top_level.choices)
        self.assertFalse(names & {"raw", "request", "batch", "jobs", "sdk", "call"})


if __name__ == "__main__":
    unittest.main()

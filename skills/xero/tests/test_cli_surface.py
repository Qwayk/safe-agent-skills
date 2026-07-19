from __future__ import annotations

import argparse
import unittest

from xero_safe_agent_cli.cli import build_parser
from xero_safe_agent_cli.registry import load_registry


class TestCliSurface(unittest.TestCase):
    def test_every_callable_catalog_row_is_a_fixed_argparse_command(self) -> None:
        registry = load_registry()
        parser = build_parser(registry)
        subparsers = next(
            action for action in parser._actions if isinstance(action, argparse._SubParsersAction)
        )
        fixed = {name for name in subparsers.choices if "." in name}
        self.assertEqual(fixed, set(registry.commands))
        self.assertEqual(len(fixed), 474)
        self.assertNotIn("raw-request", subparsers.choices)
        self.assertNotIn("request", subparsers.choices)
        self.assertNotIn("call", subparsers.choices)

    def test_fixed_command_parses_only_the_catalog_input_shape(self) -> None:
        parser = build_parser(load_registry())
        args = parser.parse_args(
            [
                "--output",
                "json",
                "--protected-output",
                "/tmp/xero-result.json",
                "accounting.get-invoices",
                "--input",
                "request.json",
            ]
        )
        self.assertEqual(args.command, "accounting.get-invoices")
        self.assertEqual(args.input, "request.json")


if __name__ == "__main__":
    unittest.main()

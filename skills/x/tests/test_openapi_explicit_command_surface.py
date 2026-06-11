from __future__ import annotations

import argparse
import unittest

from x_api_tool.api_dispatch import load_operations_from_pinned_snapshot
from x_api_tool.cli import build_parser


def _subparser_choices(parser: argparse.ArgumentParser, *, dest: str) -> dict[str, argparse.ArgumentParser]:
    for action in parser._actions:
        if isinstance(action, argparse._SubParsersAction) and action.dest == dest:
            return dict(action.choices)
    raise AssertionError(f"Missing subparser action dest={dest!r}")


class TestOpenApiExplicitCommandSurface(unittest.TestCase):
    def test_api_subcommands_cover_every_pinned_operation(self) -> None:
        ops = load_operations_from_pinned_snapshot()
        parser = build_parser()

        root_choices = _subparser_choices(parser, dest="cmd")
        self.assertIn("api", root_choices)

        api_parser = root_choices["api"]
        api_choices = _subparser_choices(api_parser, dest="api_cmd")

        self.assertIn("ops", api_choices)
        self.assertNotIn("call", api_choices)

        expected_ids = {o.operation_id for o in ops}
        for op_id in expected_ids:
            self.assertIn(op_id, api_choices, f"Missing explicit api subcommand for operationId: {op_id}")

        # Each operation parser should have the shared flags.
        shared_flags = {"--auth", "--path-json", "--query-json", "--body-json", "--path", "--query", "--file"}
        for op_id in expected_ids:
            op_parser = api_choices[op_id]
            flags = set(op_parser._option_string_actions.keys())
            for f in shared_flags:
                self.assertIn(f, flags, f"Missing shared flag {f} for operationId: {op_id}")


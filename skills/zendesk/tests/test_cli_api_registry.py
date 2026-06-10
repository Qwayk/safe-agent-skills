from __future__ import annotations

import argparse
import unittest

from zendesk_api_tool.cli import build_parser
from zendesk_api_tool.openapi_ops import load_operation_specs
from zendesk_api_tool.openapi_snapshot import load_pinned_openapi_snapshot


def _subparser_choices(parser: argparse.ArgumentParser) -> dict[str, argparse.ArgumentParser]:
    for action in parser._actions:  # noqa: SLF001
        if isinstance(action, argparse._SubParsersAction):
            return dict(action.choices)
    return {}


class TestCliApiRegistry(unittest.TestCase):
    def test_cli_registers_all_pinned_api_operations(self) -> None:
        parser = build_parser()
        top = _subparser_choices(parser)
        self.assertIn("api", top)

        api_parser = top["api"]
        api_sub = _subparser_choices(api_parser)

        snapshot = load_pinned_openapi_snapshot()
        specs = load_operation_specs(snapshot)
        expected = sorted([s.command_name for s in specs])

        actual = sorted([k for k in api_sub.keys() if k.strip()])
        self.assertEqual(len(actual), len(expected))
        self.assertEqual(actual, expected)


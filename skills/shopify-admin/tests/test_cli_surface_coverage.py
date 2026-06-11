import argparse
import unittest

from shopify_admin_api_tool.cli import build_parser
from shopify_admin_api_tool.official import camel_to_kebab, load_official_operations_list


def _subparser_choices(parser: argparse.ArgumentParser, *, dest: str) -> dict[str, argparse.ArgumentParser]:
    for action in parser._actions:  # noqa: SLF001 - argparse has no public API for this
        if isinstance(action, argparse._SubParsersAction) and action.dest == dest:
            return dict(action.choices)
    raise AssertionError(f"Missing subparsers action dest={dest!r}")


class TestCliSurfaceCoverage(unittest.TestCase):
    def test_cli_covers_every_official_operation(self) -> None:
        parser = build_parser()
        top_choices = _subparser_choices(parser, dest="cmd")
        self.assertIn("query", top_choices)
        self.assertIn("mutation", top_choices)

        query_choices = _subparser_choices(top_choices["query"], dest="query_cmd")
        mutation_choices = _subparser_choices(top_choices["mutation"], dest="mutation_cmd")

        ops = load_official_operations_list()
        expected_query = set()
        expected_mutation = set()
        for line in ops:
            kind, name = line.split(":", 1)
            kind = kind.strip()
            name = name.strip()
            if kind == "query":
                expected_query.add(camel_to_kebab(name))
            elif kind == "mutation":
                expected_mutation.add(camel_to_kebab(name))

        self.assertEqual(expected_query, set(query_choices.keys()))
        self.assertEqual(expected_mutation, set(mutation_choices.keys()))

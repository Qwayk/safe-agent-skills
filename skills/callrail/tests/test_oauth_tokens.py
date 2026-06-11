from __future__ import annotations

import argparse
import unittest
from pathlib import Path

from callrail_safe_agent_cli.cli import build_parser


def _subparser_choices(parser: argparse.ArgumentParser) -> dict[str, argparse.ArgumentParser]:
    for action in parser._actions:  # noqa: SLF001
        if isinstance(action, argparse._SubParsersAction):  # noqa: SLF001
            return action.choices
    raise AssertionError("Top-level subparsers not found in CLI parser")


class TestLegacyOAuthSurfaceRemoved(unittest.TestCase):
    def test_auth_surface_is_api_key_only(self) -> None:
        parser = build_parser()
        auth_parser = _subparser_choices(parser)["auth"]
        self.assertEqual(set(_subparser_choices(auth_parser).keys()), {"check"})

    def test_token_sample_is_explicitly_non_shipped(self) -> None:
        root = Path(__file__).resolve().parents[1]
        token_sample = (root / "examples" / "token.sample.json").read_text(encoding="utf-8").lower()
        authentication = (root / "docs" / "authentication.md").read_text(encoding="utf-8").lower()
        self.assertIn("does not ship token-json storage commands", token_sample)
        self.assertIn("does not ship any alternate auth mode", authentication)

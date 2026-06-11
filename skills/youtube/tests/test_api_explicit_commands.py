from __future__ import annotations

import argparse
import io
import json
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from youtube_api_tool.cli import build_parser, main


def _first_subparser_choices(p: argparse.ArgumentParser) -> dict[str, argparse.ArgumentParser]:
    for a in getattr(p, "_actions", []):
        if isinstance(a, argparse._SubParsersAction):
            return a.choices  # type: ignore[return-value]
    raise AssertionError("Parser missing subparsers")


class TestApiExplicitCommands(unittest.TestCase):
    def test_api_has_explicit_command_for_every_official_method(self) -> None:
        root = Path(__file__).resolve().parents[1]
        methods_txt = root / "docs" / "official_methods.txt"
        methods = [ln.strip() for ln in methods_txt.read_text(encoding="utf-8").splitlines() if ln.strip()]
        self.assertGreater(len(methods), 0)

        parser = build_parser()
        top = _first_subparser_choices(parser)
        self.assertIn("api", top)

        api_parser = top["api"]
        api_choices = _first_subparser_choices(api_parser)
        self.assertNotIn("call", api_choices)

        missing = [m for m in methods if m not in api_choices]
        self.assertEqual(missing, [], f"Missing api subcommands for methods: {missing}")

    def test_api_call_dispatcher_is_absent(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = main(["--output", "json", "api", "call"])
        self.assertEqual(rc, 1)
        payload = json.loads(buf.getvalue())
        self.assertFalse(payload.get("ok"))
        self.assertEqual(payload.get("error_type"), "ValidationError")


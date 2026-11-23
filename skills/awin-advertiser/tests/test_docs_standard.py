from __future__ import annotations

import argparse
import io
import json
import shlex
import tempfile
from contextlib import redirect_stdout
from unittest.mock import patch
import unittest
from pathlib import Path

from awin_advertiser_safe_agent_cli.cli import build_parser, main
from awin_advertiser_safe_agent_cli.http import HttpResponse


class TestDocsStandard(unittest.TestCase):
    def setUp(self) -> None:
        self.root = Path(__file__).resolve().parents[1]
        self.docs = self.root / "docs"

    def test_required_repo_standard_docs_exist(self) -> None:
        required = [
            self.docs / "use_cases.md",
            self.docs / "safety_model.md",
            self.docs / "quickstart.md",
        ]
        for path in required:
            with self.subTest(path=path.name):
                self.assertTrue(path.exists(), f"Missing required docs file: {path.name}")

    def test_quickstart_commands_use_the_same_advertiser(self) -> None:
        lines = (self.docs / "quickstart.md").read_text().splitlines()
        commands = {
            kind: shlex.split(next(line for line in lines if line.startswith(".venv/bin/awin-advertiser-safe-cli ") and kind in line))
            for kind in ("--version", "onboarding", "auth check", "reports publisher")
        }

        def run(kind: str) -> dict:
            args = commands[kind][1:]
            if "--env-file" in args:
                args[args.index("--env-file") + 1] = str(settings)
            with redirect_stdout(out := io.StringIO()):
                self.assertEqual(main(args), 0)
            return json.loads(out.getvalue())

        with tempfile.TemporaryDirectory() as directory:
            settings = Path(directory) / ".env"
            self.assertEqual(run("--version")["tool"], "awin-advertiser-safe-cli")
            self.assertTrue(run("onboarding")["onboarding"]["env_created"])
            settings.write_text("AWIN_API_TOKEN=fixture-token\nAWIN_ADVERTISER_ID=123456\n")
            with patch("awin_advertiser_safe_agent_cli.http.HttpClient.request", return_value=HttpResponse(200, {}, b"[]", "")) as call:
                self.assertEqual(run("auth check")["auth_check"]["advertiser_id"], "123456")
                run("reports publisher")
            self.assertEqual([args.args[1] for args in call.call_args_list], [
                "https://api.awin.com/advertisers/123456/publishers",
                "https://api.awin.com/advertisers/123456/reports/publisher",
            ])

    def test_api_coverage_lists_all_provider_backed_commands(self) -> None:
        parser = build_parser()
        endpoint_coverage = self._endpoint_coverage_section()
        support_only = {"onboarding", "runs list", "runs show"}
        live_commands = sorted(
            command
            for command in self._leaf_commands(parser)
            if command not in support_only
        )
        missing = [command for command in live_commands if f"`{command}`" not in endpoint_coverage]
        self.assertEqual(
            [],
            missing,
            "docs/api_coverage.md is missing shipped provider-backed command(s): "
            + ", ".join(missing),
        )

    def _endpoint_coverage_section(self) -> str:
        text = (self.docs / "api_coverage.md").read_text(encoding="utf-8")
        return text.split("## Endpoint coverage", 1)[1].split("## Implementation notes and live limits", 1)[0]

    def _leaf_commands(self, parser: argparse.ArgumentParser, prefix: tuple[str, ...] = ()) -> list[str]:
        commands: list[str] = []
        for action in parser._actions:
            if not isinstance(action, argparse._SubParsersAction):
                continue
            for name, subparser in action.choices.items():
                command = prefix + (name,)
                nested = self._leaf_commands(subparser, command)
                if nested:
                    commands.extend(nested)
                    continue
                if subparser._defaults.get("func") is not None:
                    commands.append(" ".join(command))
        return commands

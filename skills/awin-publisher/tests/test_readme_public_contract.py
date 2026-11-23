from __future__ import annotations

import io
import json
import shlex
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

import requests

from awin_publisher_safe_agent_cli.cli import main


ROOT = Path(__file__).resolve().parents[1]


class TestPublishedQuickstart(unittest.TestCase):
    def setUp(self) -> None:
        self.quickstart = (ROOT / "docs/quickstart.md").read_text(encoding="utf-8")

    def test_quickstart_checks_the_installed_cli_version(self) -> None:
        command, = (
            shlex.split(line) for line in self.quickstart.splitlines()
            if line.startswith("awin-publisher-safe-cli --version")
        )
        executable, *args = command
        with redirect_stdout(stdout := io.StringIO()):
            self.assertEqual(main(args), 0)
        self.assertEqual(json.loads(stdout.getvalue())["tool"], executable)

    def test_quickstart_lists_only_publisher_accounts_using_the_selected_file(self) -> None:
        command, = (
            shlex.split(line) for line in self.quickstart.splitlines()
            if line.startswith("awin-publisher-safe-cli ") and line.endswith(" accounts list")
        )
        _, *args = command
        accounts = [
            {"id": 100, "name": "Example publisher", "type": "publisher"},
            {"id": 200, "name": "Example advertiser", "type": "advertiser"},
        ]
        response = requests.Response()
        response.status_code = 200
        response.url = "https://api.awin.com/accounts"
        response._content = json.dumps(accounts).encode("utf-8")
        response._content_consumed = True

        with tempfile.TemporaryDirectory() as directory:
            env_file = Path(directory) / args[args.index("--env-file") + 1]
            env_file.write_text("AWIN_API_TOKEN=fixture-quickstart-token\n", encoding="utf-8")
            args[args.index("--env-file") + 1] = str(env_file)
            with patch("requests.Session.request", return_value=response) as send, redirect_stdout(stdout := io.StringIO()):
                self.assertEqual(main(args), 0)
        result = json.loads(stdout.getvalue())
        self.assertEqual([account["id"] for account in result["accounts"]], [100])
        send.assert_called_once()
        self.assertEqual(send.call_args.kwargs["method"], "GET")
        self.assertEqual(send.call_args.kwargs["url"], "https://api.awin.com/accounts")

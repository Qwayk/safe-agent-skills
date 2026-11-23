from __future__ import annotations

import io
import json
import os
import re
import shlex
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from urllib.parse import unquote, urlsplit
from unittest.mock import patch

from azure_safe_agent_cli.cli import main


ROOT = Path(__file__).resolve().parents[1]


class TestPublishedGuides(unittest.TestCase):
    def test_public_guide_links_open_shipped_files(self) -> None:
        pages = [ROOT / "README.md", ROOT / "SKILL.md", *sorted((ROOT / "docs").glob("*.md"))]
        for page in pages:
            for link in re.findall(r"\]\(([^)\s]+)\)", page.read_text(encoding="utf-8")):
                parts = urlsplit(link)
                if parts.scheme or parts.netloc or not parts.path:
                    continue
                with self.subTest(page=page.name, link=link):
                    destination = (page.parent / unquote(parts.path)).resolve()
                    self.assertTrue(destination.is_relative_to(ROOT))
                    self.assertTrue(destination.is_file())

    def test_documented_first_read_lists_the_chosen_subscription(self) -> None:
        quickstart = (ROOT / "docs/quickstart.md").read_text(encoding="utf-8")
        json_blocks = re.findall(r"```json\n(.*?)\n```", quickstart, re.DOTALL)
        bash_blocks = re.findall(r"```bash\n(.*?)\n```", quickstart, re.DOTALL)
        input_json, = json_blocks
        command, = (shlex.split(line) for block in bash_blocks for line in block.splitlines() if "--input-json" in line)
        executable, *args = command
        self.assertEqual(executable, "qwayk-azure-safe-agent-cli")
        with tempfile.TemporaryDirectory() as directory:
            scratch = Path(directory)
            settings = scratch / "settings.env"
            settings.write_text("AZURE_API_TOKEN=fixture-guide-token\n", encoding="utf-8")
            input_file_index = args.index("--input-json") + 1
            input_file = scratch / args[input_file_index]
            input_file.write_text(input_json.replace("SUBSCRIPTION_ID", "guide-subscription"), encoding="utf-8")
            args[input_file_index] = str(input_file)
            response = SimpleNamespace(status=200, json=lambda: {"value": [{"name": "guide-group"}]})
            output = io.StringIO()
            with (
                patch.dict(os.environ, {}, clear=True),
                patch("azure_safe_agent_cli.generated_runtime.HttpClient.request", return_value=response) as request,
                redirect_stdout(output),
            ):
                code = main(["--output", "json", "--no-artifacts", "--env-file", str(settings), *args])
            result = json.loads(output.getvalue())
            self.assertEqual(code, 0, result)
            self.assertEqual(result["response"]["value"], [{"name": "guide-group"}])
            request.assert_called_once()
            method, url = request.call_args.args
            self.assertEqual(method, "GET")
            self.assertEqual(urlsplit(url).path, "/subscriptions/guide-subscription/resourcegroups")

    def test_published_json_examples_parse(self) -> None:
        examples = [
            ROOT / "examples/token.sample.json",
            ROOT / "docs/examples/plan.example.json",
            ROOT / "docs/examples/receipt.example.json",
            ROOT / "docs/examples/outputs/auth_check.json",
            ROOT / "docs/examples/outputs/version.json",
        ]
        for example in examples:
            with self.subTest(example=example.name):
                self.assertIsInstance(json.loads(example.read_text(encoding="utf-8")), dict)

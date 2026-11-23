from __future__ import annotations

import io
import json
import shlex
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from sovrn_safe_agent_cli.cli import main
from sovrn_safe_agent_cli.http import HttpResponse


class TestDocsUsage(unittest.TestCase):
    def test_public_docs_do_not_leak_private_workspace_paths(self) -> None:
        root = Path(__file__).resolve().parents[1]
        files = [
            root / "docs" / "proof.md",
            root / "docs" / "examples" / "outputs" / "version.json",
            root / "docs" / "examples" / "outputs" / "auth_check.json",
            root / "docs" / "examples" / "outputs" / "commerce_campaigns_invalid_secret.json",
        ]
        forbidden = [
            "/home/" + "ubuntu/",
            "api" + "-tools-for-ai-agents",
            "pro" + "jects/" + "qwayk-skills-control-room/",
            "api" + "-tools/" + "qwayk-sovrn-safe-agent-cli/",
        ]
        for path in files:
            text = path.read_text(encoding="utf-8")
            for needle in forbidden:
                with self.subTest(path=path.name, needle=needle):
                    self.assertNotIn(needle, text)

    def test_quickstart_runs_with_only_the_required_key(self) -> None:
        root = Path(__file__).resolve().parents[1]
        lines = (root / "docs" / "quickstart.md").read_text().splitlines()
        sample_commands = [
            (["commerce", "links", "check"], "SOVRN_COMMERCE_SITE_API_KEY=fixture-site-key\n",
             "https://api.viglink.com/api/link/"),
            (["commerce", "reports", "pages", "get"], "SOVRN_COMMERCE_SECRET_KEY=fixture-secret-key\n",
             "https://viglink.io/v1/reports/pages"),
            (["advertising", "reports", "account", "get"],
             "SOVRN_ADVERTISING_API_KEY=fixture-advertising-key\nSOVRN_ADVERTISING_PUBLISHER_ID=111\n",
             "https://api.sovrn.com/reporting/advertising/publishers/111/account"),
        ]
        for command, values, endpoint in sample_commands:
            with self.subTest(command=command), tempfile.TemporaryDirectory() as directory:
                env = Path(directory) / "reader.env"
                env.write_text(values)
                prefix = ".venv/bin/sovrn-safe-cli --env-file .env " + " ".join(command)
                args = shlex.split(next(line for line in lines if line.startswith(prefix)))[1:]
                args[args.index("--env-file") + 1] = str(env)
                reply = HttpResponse(200, {"content-type": "application/json"}, b"[]", endpoint)
                with patch("sovrn_safe_agent_cli.http.HttpClient.request", return_value=reply) as sent:
                    with redirect_stdout(out := io.StringIO()):
                        self.assertEqual(main(args), 0)
                self.assertTrue(json.loads(out.getvalue())["ok"])
                self.assertEqual(sent.call_args.args[1], endpoint)

from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from elevenlabs_api_tool.cli import main


class TestAdditionalReadCommands(unittest.TestCase):
    def _env_file(self, directory: Path) -> Path:
        env_path = directory / ".env"
        env_path.write_text(
            "\n".join(
                [
                    "ELEVENLABS_API_BASE_URL=http://example.invalid",
                    "ELEVENLABS_TIMEOUT_S=30",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        return env_path

    def _run(self, env_path: Path, args: list[str]) -> dict[str, object]:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = main(["--env-file", str(env_path), "--output", "json"] + args)
        self.assertEqual(rc, 0)
        return json.loads(buf.getvalue())

    def test_models_list_dry_run_is_supported(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            payload = self._run(self._env_file(Path(d)), ["models", "list"])
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])
            self.assertEqual(payload["plan"]["endpoint"], "GET /v1/models")

    def test_usage_get_dry_run_is_supported(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            payload = self._run(self._env_file(Path(d)), ["usage", "get"])
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])
            self.assertEqual(payload["plan"]["endpoint"], "GET /v1/usage/character-stats")

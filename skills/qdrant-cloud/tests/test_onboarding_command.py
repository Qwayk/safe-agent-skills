from __future__ import annotations

import io
import json
import shlex
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from qdrant_cloud_api_tool.cli import main


class TestOnboardingCommand(unittest.TestCase):
    def onboarding(self, settings: Path, *flags: str) -> dict:
        output = io.StringIO()
        with redirect_stdout(output):
            rc = main(["--output", "json", "--env-file", str(settings), "onboarding", *flags])
        self.assertEqual(0, rc)
        return json.loads(output.getvalue())["onboarding"]

    def test_onboarding_creates_private_settings_at_the_selected_path(self) -> None:
        with tempfile.TemporaryDirectory() as td, patch.dict("os.environ", {}, clear=True):
            path = Path(td) / "chosen folder" / "qdrant.env"
            result = self.onboarding(path)
            self.assertTrue(result["env_created"])
            self.assertIn("QDRANT_CLOUD_API_KEY=", path.read_text())
            self.assertEqual(0o600, path.stat().st_mode & 0o777)
            self.assertEqual(["QDRANT_CLOUD_API_KEY"], result["missing"])
            self.assertEqual(
                ["--output", "json", "--env-file", str(path), "auth", "check"],
                shlex.split(result["next_command"])[1:],
            )
            self.assertIn(shlex.quote(str(path)), result["steps"][-1])

            path.write_text("QDRANT_CLOUD_API_KEY='test|fixture'\n")
            self.assertFalse(self.onboarding(path)["env_created"])
            self.assertIn("test|fixture", path.read_text())
            self.assertEqual([], self.onboarding(path)["missing"])

    def test_onboarding_uses_a_shell_key_without_writing_a_file(self) -> None:
        with tempfile.TemporaryDirectory() as td, patch.dict(
            "os.environ", {"QDRANT_CLOUD_API_KEY": "test-shell-key"}, clear=True,
        ):
            path = Path(td) / "qdrant.env"
            result = self.onboarding(path, "--no-write-env")
            self.assertFalse(path.exists())
            self.assertEqual([], result["missing"])
            self.assertNotIn("test-shell-key", json.dumps(result))

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from shlex import split

from ._helpers import run_cli


class TestOnboardingCommand(unittest.TestCase):
    def test_onboarding_creates_env_from_example(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            env_path = root / ".env"
            example_path = root / ".env.example"
            example_path.write_text(
                "\n".join(
                    [
                        "CLOUDINARY_CLOUD_NAME=demo",
                        "CLOUDINARY_API_KEY=paste_here",
                        "CLOUDINARY_API_SECRET=paste_here",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            rc, payload = run_cli(["--output", "json", "--env-file", str(env_path), "onboarding"])
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["onboarding"]["env_created"])
            self.assertTrue(env_path.exists())

    def test_onboarding_keeps_the_selected_file_and_starts_with_a_media_read(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            env_path = Path(tmp) / "chosen settings" / "cloud.env"
            args = ["--env-file", str(env_path), "onboarding"]
            run_cli([*args, "--no-write-env"])
            self.assertFalse(env_path.exists())
            rc, result = run_cli(args)
            self.assertEqual(rc, 0)
            self.assertIn("CLOUDINARY_CLOUD_NAME=", env_path.read_text())
            self.assertEqual(env_path.stat().st_mode & 0o777, 0o600)
            next_command = split(result["onboarding"]["next_command"])
            self.assertEqual(next_command[1:5], ["--env-file", str(env_path), "operations", "admin"])

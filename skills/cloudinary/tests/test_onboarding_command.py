from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

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

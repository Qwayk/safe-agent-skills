from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from qwayk_woocommerce_safe_agent_cli.cli import main


class TestOnboardingCommand(unittest.TestCase):
    def test_onboarding_creates_env_from_example(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / ".env.example").write_text(
                "WOOCOMMERCE_STORE_URL=https://shop.example.com\n"
                "WOOCOMMERCE_CONSUMER_KEY=\n"
                "WOOCOMMERCE_CONSUMER_SECRET=\n",
                encoding="utf-8",
            )
            env_path = root / ".env"

            buffer = io.StringIO()
            with redirect_stdout(buffer):
                rc = main(["--env-file", str(env_path), "--output", "json", "onboarding"])
            self.assertEqual(rc, 0)
            payload = json.loads(buffer.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["onboarding"]["env_created"])
            self.assertTrue(env_path.exists())
            self.assertIn("WOOCOMMERCE_CONSUMER_KEY", payload["onboarding"]["missing"])

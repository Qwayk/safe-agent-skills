from __future__ import annotations

import io
import json
import os
import stat
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from cloudflare_api_tool.cli import main


class TestConfigLocalCommands(unittest.TestCase):
    def test_config_init_seeds_env_from_example(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / ".env.example").write_text(
                "\n".join(
                    [
                        "CLOUDFLARE_API_BASE_URL=https://api.cloudflare.com/client/v4/",
                        "CLOUDFLARE_API_TOKEN=",
                        "CLOUDFLARE_TIMEOUT_S=30",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            env_path = root / ".env"
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--env-file", str(env_path), "config", "init"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(env_path.exists())
            if os.name == "posix":
                mode = stat.S_IMODE(os.stat(str(env_path)).st_mode)
                self.assertEqual(mode & 0o077, 0)

    def test_config_check_missing_token_is_error(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(
                "\n".join(
                    [
                        "CLOUDFLARE_API_BASE_URL=https://api.cloudflare.com/client/v4/",
                        "CLOUDFLARE_API_TOKEN=",
                        "CLOUDFLARE_TIMEOUT_S=30",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--env-file", str(env_path), "config", "check"])
            self.assertEqual(rc, 1)
            payload = json.loads(buf.getvalue())
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["command"], "config.check")
            self.assertFalse(payload["token_present"])


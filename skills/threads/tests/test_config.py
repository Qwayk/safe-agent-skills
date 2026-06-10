from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from threads_api_tool.config import load_config


class TestConfig(unittest.TestCase):
    def test_token_falls_back_to_state_file_when_env_token_missing(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_file = root / ".env"
            state_dir = root / ".state"
            state_dir.mkdir(exist_ok=True)
            state_token = state_dir / "token.json"
            state_token.write_text(json.dumps({"access_token": "state-token"}), encoding="utf-8")

            env_file.write_text(
                "\n".join(
                    [
                        "THREADS_API_BASE_URL=https://graph.threads.net",
                        "THREADS_API_VERSION=v1.0",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            cfg = load_config(str(env_file))
            self.assertEqual(cfg.token, "state-token")

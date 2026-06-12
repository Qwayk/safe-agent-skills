from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from jobber_safe_agent_cli.config import load_config


class TestConfig(unittest.TestCase):
    def test_default_values_without_env(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env = Path(d) / ".env"
            env.write_text("JOBBER_TIMEOUT_S=7\n", encoding="utf-8")

            cfg = load_config(str(env))

            self.assertEqual(cfg.base_url, "https://api.getjobber.com")
            self.assertEqual(cfg.graphql_url, "https://api.getjobber.com/api/graphql")
            self.assertEqual(cfg.graphql_version, "2025-04-16")
            self.assertEqual(cfg.timeout_s, 7.0)
            self.assertIsNone(cfg.client_id)
            self.assertIsNone(cfg.client_secret)
            self.assertIsNone(cfg.redirect_uri)
            self.assertIsNone(cfg.token)

    def test_client_fields_and_token_precedence(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env = Path(d) / ".env"
            env.write_text(
                "\n".join(
                    [
                        "JOBBER_CLIENT_ID=client-id",
                        "JOBBER_CLIENT_SECRET=client-secret",
                        "JOBBER_REDIRECT_URI=https://app.example.com/oauth/cb",
                        "JOBBER_GRAPHQL_VERSION=2026-01-01",
                        "JOBBER_API_TOKEN=env-token",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            token_file = Path(d) / ".state" / "token.json"
            token_file.parent.mkdir(parents=True, exist_ok=True)
            token_file.write_text(json.dumps({"access_token": "stored-token"}), encoding="utf-8")

            cfg = load_config(str(env))
            self.assertEqual(cfg.client_id, "client-id")
            self.assertEqual(cfg.client_secret, "client-secret")
            self.assertEqual(cfg.redirect_uri, "https://app.example.com/oauth/cb")
            self.assertEqual(cfg.graphql_version, "2026-01-01")
            self.assertEqual(cfg.token, "stored-token")


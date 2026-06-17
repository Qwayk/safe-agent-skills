from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from fortnox_api_tool.config import load_config


class TestConfig(unittest.TestCase):
    def test_load_config_reads_auth_fields(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_path = Path(d) / ".env"
            env_path.write_text(
                "\n".join(
                    [
                        "FORTNOX_API_BASE_URL=https://api.fortnox.se/3",
                        "FORTNOX_WS_URL=wss://ws.fortnox.se/topics-v1",
                        "FORTNOX_CLIENT_ID=client-id",
                        "FORTNOX_CLIENT_SECRET=client-secret",
                        "FORTNOX_REDIRECT_URI=https://example.com/callback",
                        "FORTNOX_OAUTH_SCOPES=companyinformation customer",
                        "FORTNOX_SERVICE_TENANT_ID=12345",
                        "FORTNOX_TOKEN_FILE=.tokens/fortnox.json",
                        "FORTNOX_TIMEOUT_S=15",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            cfg = load_config(str(env_path))
            self.assertEqual(cfg.client_id, "client-id")
            self.assertEqual(cfg.client_secret, "client-secret")
            self.assertEqual(cfg.redirect_uri, "https://example.com/callback")
            self.assertEqual(cfg.oauth_scopes, ("companyinformation", "customer"))
            self.assertEqual(cfg.service_tenant_id, "12345")
            self.assertEqual(cfg.token_file, ".tokens/fortnox.json")
            self.assertEqual(cfg.timeout_s, 15.0)

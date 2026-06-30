from __future__ import annotations

import os
import tempfile
import unittest

from wix_safe_agent_cli.authz import resolve_authorization_headers
from wix_safe_agent_cli.config import load_config
from wix_safe_agent_cli.errors import ValidationError


class TestAuthzHelpers(unittest.TestCase):
    def test_sites_auth_requires_api_key(self) -> None:
        cfg = type(
            "cfg",
            (),
            {
                "base_url": "https://www.wixapis.com",
                "api_key": None,
                "account_id": "acct-1",
                "app_id": None,
                "app_secret": None,
                "instance_id": None,
                "access_token": "legacy-token",
                "has_official_app_auth": False,
            },
        )()

        with self.assertRaisesRegex(ValidationError, "Missing required account API key"):
            resolve_authorization_headers(cfg=cfg, env_file=".env", verbose=False, command_family="sites")

    def test_sites_auth_requires_account_id(self) -> None:
        cfg = type(
            "cfg",
            (),
            {
                "base_url": "https://www.wixapis.com",
                "api_key": "api-key",
                "account_id": None,
                "app_id": None,
                "app_secret": None,
                "instance_id": None,
                "access_token": "legacy-token",
                "has_official_app_auth": False,
            },
        )()

        with self.assertRaisesRegex(ValidationError, "Missing required account ID"):
            resolve_authorization_headers(cfg=cfg, env_file=".env", verbose=False, command_family="sites")

    def test_sites_auth_uses_api_key_and_account_id(self) -> None:
        cfg = type(
            "cfg",
            (),
            {
                "base_url": "https://www.wixapis.com",
                "api_key": "api-key",
                "account_id": "acct-1",
                "app_id": None,
                "app_secret": None,
                "instance_id": None,
                "access_token": "legacy-token",
                "has_official_app_auth": False,
            },
        )()

        auth = resolve_authorization_headers(cfg=cfg, env_file=".env", verbose=False, command_family="sites")
        self.assertEqual(auth.headers["Authorization"], "api-key")
        self.assertEqual(auth.headers["wix-account-id"], "acct-1")

    def test_accounts_auth_uses_api_key_and_account_id(self) -> None:
        cfg = type(
            "cfg",
            (),
            {
                "base_url": "https://www.wixapis.com",
                "api_key": "api-key",
                "account_id": "acct-1",
                "app_id": None,
                "app_secret": None,
                "instance_id": None,
                "access_token": "legacy-token",
                "has_official_app_auth": False,
            },
        )()

        auth = resolve_authorization_headers(cfg=cfg, env_file=".env", verbose=False, command_family="accounts")
        self.assertEqual(auth.headers["Authorization"], "api-key")
        self.assertEqual(auth.headers["wix-account-id"], "acct-1")


class TestConfigLoadsSiteAuth(unittest.TestCase):
    def test_load_config_reads_api_key_and_account_id(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = os.path.join(td, ".env")
            with open(env_path, "w", encoding="utf-8") as f:
                f.write("WIX_API_BASE_URL=https://www.wixapis.com\n")
                f.write("WIX_API_KEY=api-key\n")
                f.write("WIX_ACCOUNT_ID=account-id\n")

            cfg = load_config(env_path)
            self.assertEqual(cfg.api_key, "api-key")
            self.assertEqual(cfg.account_id, "account-id")
            self.assertTrue(cfg.has_account_api_auth)

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

TOOL_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOL_ROOT / "src"))


class TestAuthAndRouting(unittest.TestCase):
    def test_region_and_edge_must_be_set_together(self) -> None:
        from twilio_safe_agent_cli.config import load_config
        from twilio_safe_agent_cli.errors import ValidationError

        with tempfile.TemporaryDirectory() as tmp:
            env_file = Path(tmp) / ".env"
            env_file.write_text(
                "TWILIO_ACCOUNT_SID=AC" + "a" * 32 + "\n"
                "TWILIO_API_KEY_SID=SK" + "b" * 32 + "\n"
                "TWILIO_API_KEY_SECRET=private-secret\n"
                "TWILIO_REGION=au1\n",
                encoding="utf-8",
            )
            with self.assertRaises(ValidationError):
                load_config(env_file)

    def test_basic_auth_prefers_api_key_and_never_places_it_in_result(self) -> None:
        from twilio_safe_agent_cli.auth import build_auth
        from twilio_safe_agent_cli.config import Config
        from twilio_safe_agent_cli.registry import load_registry

        cfg = Config(
            account_sid="AC" + "a" * 32,
            api_key_sid="SK" + "b" * 32,
            api_key_secret="private-secret",
            auth_token=None,
            oauth_access_token=None,
            region=None,
            edge=None,
            timeout_s=30.0,
        )
        operation = load_registry().get("api-v2010.fetch-account")
        auth = build_auth(operation, cfg, {})
        self.assertEqual(auth.basic, (cfg.api_key_sid, cfg.api_key_secret))
        self.assertNotIn("Authorization", auth.headers)
        self.assertNotIn("private-secret", repr(auth.public_summary))

    def test_auth_token_fallback_is_warned(self) -> None:
        from twilio_safe_agent_cli.auth import build_auth
        from twilio_safe_agent_cli.config import Config
        from twilio_safe_agent_cli.registry import load_registry

        cfg = Config(
            account_sid="AC" + "a" * 32,
            api_key_sid=None,
            api_key_secret=None,
            auth_token="fallback-token",
            oauth_access_token=None,
            region=None,
            edge=None,
            timeout_s=30.0,
        )
        operation = load_registry().get("api-v2010.fetch-account")
        auth = build_auth(operation, cfg, {})
        self.assertEqual(auth.basic, (cfg.account_sid, cfg.auth_token))
        self.assertIn("fallback", " ".join(auth.warnings).lower())

    def test_oauth_and_declared_manual_authorization(self) -> None:
        from twilio_safe_agent_cli.auth import build_auth
        from twilio_safe_agent_cli.config import Config
        from twilio_safe_agent_cli.registry import load_registry

        cfg = Config(
            account_sid="AC" + "a" * 32,
            api_key_sid="SK" + "b" * 32,
            api_key_secret="private-secret",
            auth_token=None,
            oauth_access_token="oauth-private",
            region=None,
            edge=None,
            timeout_s=30.0,
        )
        oauth_operation = next(
            row
            for row in load_registry().commands.values()
            if any("oAuth2ClientCredentials" in item for item in row["security"]["requirements"])
        )
        oauth = build_auth(oauth_operation, cfg, {})
        self.assertEqual(oauth.headers["Authorization"], "Bearer oauth-private")

        flex_operation = next(
            row
            for row in load_registry().commands.values()
            if any(p.get("in") == "header" and p.get("name") == "Authorization" for p in row["parameters"])
        )
        manual = build_auth(flex_operation, cfg, {"Authorization": "Bearer flex-private"})
        self.assertEqual(manual.headers["Authorization"], "Bearer flex-private")
        self.assertIsNone(manual.basic)

    def test_region_edge_routing_inserts_both_labels(self) -> None:
        from twilio_safe_agent_cli.auth import route_server
        from twilio_safe_agent_cli.config import Config

        cfg = Config(
            account_sid="AC" + "a" * 32,
            api_key_sid="SK" + "b" * 32,
            api_key_secret="private-secret",
            auth_token=None,
            oauth_access_token=None,
            region="au1",
            edge="sydney",
            timeout_s=30.0,
        )
        self.assertEqual(
            route_server("https://api.twilio.com", cfg),
            "https://api.sydney.au1.twilio.com",
        )

    def test_no_security_operation_does_not_require_unrelated_account_credentials(self) -> None:
        from twilio_safe_agent_cli.config import load_config

        with tempfile.TemporaryDirectory() as tmp:
            cfg = load_config(
                Path(tmp) / "missing.env",
                require_account=False,
                require_credentials=False,
            )
        self.assertEqual(cfg.account_sid, "UNSCOPED")
        self.assertIsNone(cfg.api_key_secret)


if __name__ == "__main__":
    unittest.main()

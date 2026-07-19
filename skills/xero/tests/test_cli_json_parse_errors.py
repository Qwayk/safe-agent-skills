from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from xero_safe_agent_cli.auth import TokenStore
from xero_safe_agent_cli.cli import main


class TestCliJsonParseErrors(unittest.TestCase):
    def test_missing_command_is_json_error(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = main(["--output", "json"])
        self.assertEqual(rc, 2)
        payload = json.loads(buf.getvalue())
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error_type"], "ValidationError")

    def test_missing_required_subcommand_is_json_error(self) -> None:
        # `auth` requires a subcommand.
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = main(["--output", "json", "auth"])
        self.assertEqual(rc, 2)
        payload = json.loads(buf.getvalue())
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error_type"], "ValidationError")

    def test_malformed_selected_tenant_is_one_json_validation_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            env_file = root / "xero.env"
            env_file.write_text("XERO_STATE_DIR=.state\n", encoding="utf-8")
            state_root = root / ".state"
            TokenStore(state_root / "oauth" / "token.json").write(
                {"access_token": "private-token", "scope": "accounting.settings.read"}
            )
            state_root.mkdir(exist_ok=True)
            (state_root / "tenant.json").write_text("{}", encoding="utf-8")
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env_file),
                        "accounting.get-organisations",
                    ]
                )
            self.assertEqual(rc, 2)
            payload = json.loads(stdout.getvalue())
            self.assertEqual(payload["error_type"], "ValidationError")
            self.assertNotIn("private-token", stdout.getvalue())

    def test_client_credential_profiles_reject_crossed_or_unknown_scopes_without_a_call(self) -> None:
        cases = (
            ("app-store", "accounting.invoices"),
            ("custom", "app.connections"),
            ("custom", "not.a.real.scope"),
        )
        with tempfile.TemporaryDirectory() as tmp:
            env_file = Path(tmp) / "xero.env"
            env_file.write_text(
                "XERO_CUSTOM_CLIENT_ID=custom-id\n"
                "XERO_CUSTOM_CLIENT_SECRET=custom-secret\n"
                "XERO_APP_STORE_CLIENT_ID=app-id\n"
                "XERO_APP_STORE_CLIENT_SECRET=app-secret\n",
                encoding="utf-8",
            )
            for profile, scope in cases:
                with self.subTest(profile=profile, scope=scope), patch(
                    "xero_safe_agent_cli.cli.client_credentials_token"
                ) as provider_call:
                    stdout = io.StringIO()
                    with redirect_stdout(stdout):
                        rc = main(
                            [
                                "--output",
                                "json",
                                "--env-file",
                                str(env_file),
                                "auth",
                                "client-credentials",
                                "--profile",
                                profile,
                                "--scope",
                                scope,
                            ]
                        )
                    self.assertEqual(rc, 2)
                    self.assertIn("not allowed", json.loads(stdout.getvalue())["error"])
                    provider_call.assert_not_called()

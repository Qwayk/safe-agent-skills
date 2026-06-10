from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from google_business_profile_safe_agent_cli.cli import main


class _Creds:
    def to_json(self) -> str:  # noqa: D401
        return json.dumps(
            {
                "token": "SECRET_ACCESS_TOKEN",
                "refresh_token": "SECRET_REFRESH_TOKEN",
                "token_uri": "https://oauth2.googleapis.com/token",
                "client_id": "CLIENT_ID",
                "client_secret": "CLIENT_SECRET",
                "scopes": ["https://www.googleapis.com/auth/business.manage"],
            }
        )


class _Flow:
    def run_console(self):  # noqa: ANN001
        return _Creds()


class _FlowCapturingScopes:
    def __init__(self) -> None:
        self.scopes: list[str] = []

    def run_console(self):  # noqa: ANN001
        return _Creds()


class TestAuthLogin(unittest.TestCase):
    def test_auth_login_stores_token_and_never_prints_secrets(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_file = Path(d) / ".env"
            client_secrets = Path(d) / "client_secrets.json"
            client_secrets.write_text("{}\n", encoding="utf-8")
            token_src = Path(d) / "token.json"
            token_src.write_text(json.dumps({"token": "start"}), encoding="utf-8")

            buf = io.StringIO()
            with patch("google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file", return_value=_Flow()):
                with redirect_stdout(buf):
                    rc = main(
                        [
                            "--output",
                            "json",
                            "--env-file",
                            str(env_file),
                            "auth",
                            "login",
                            "--console",
                            "--client-secrets-file",
                            str(client_secrets),
                        ]
                    )

            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertNotIn("SECRET_ACCESS_TOKEN", buf.getvalue())
            self.assertNotIn("SECRET_REFRESH_TOKEN", buf.getvalue())

            token_path = Path(d) / ".state" / "oauth_credentials.json"
            self.assertTrue(token_path.exists())
            data = json.loads(token_path.read_text(encoding="utf-8"))
            self.assertEqual(data["token"], "SECRET_ACCESS_TOKEN")

    def test_auth_login_parses_comma_separated_scopes(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env_file = Path(d) / ".env"
            client_secrets = Path(d) / "client_secrets.json"
            client_secrets.write_text("{}\n", encoding="utf-8")
            captured = _FlowCapturingScopes()

            def from_client_secrets_file(path: str, scopes: list[str] | None = None):  # noqa: ANN001
                if scopes is not None:
                    captured.scopes = list(scopes)
                return captured

            with patch(
                "google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file",
                side_effect=from_client_secrets_file,
            ):
                with redirect_stdout(io.StringIO()):
                    main(
                        [
                            "--output",
                            "json",
                            "--env-file",
                            str(env_file),
                            "auth",
                            "login",
                            "--scopes",
                            "scope/a,scope/b",
                            "--console",
                            "--client-secrets-file",
                            str(client_secrets),
                        ]
                    )

            self.assertEqual(captured.scopes, ["scope/a", "scope/b"])

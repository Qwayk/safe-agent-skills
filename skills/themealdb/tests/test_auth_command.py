from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from qwayk_themealdb_safe_agent_cli.cli import main


class _FakeResponse:
    def __init__(self, *, status_code: int, url: str, text: str):
        self.status_code = status_code
        self.url = url
        self.text = text
        self.headers: dict[str, str] = {}
        self.content = text.encode("utf-8")


class TestAuthCommand(unittest.TestCase):
    def test_auth_check_redacts_custom_api_key_on_error(self) -> None:
        secret_key = "super-secret-themealdb-key"
        with tempfile.TemporaryDirectory() as temp_dir:
            env_path = Path(temp_dir) / ".env"
            env_path.write_text(
                "\n".join(
                    [
                        "THEMEALDB_BASE_URL=https://www.themealdb.com/api/json/v1",
                        f"THEMEALDB_API_KEY={secret_key}",
                        "THEMEALDB_TIMEOUT_S=30",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            fake_response = _FakeResponse(
                status_code=401,
                url=f"https://www.themealdb.com/api/json/v1/{secret_key}/categories.php",
                text=f"bad key {secret_key}",
            )
            buffer = io.StringIO()
            with patch(
                "qwayk_themealdb_safe_agent_cli.http.requests.Session.request",
                return_value=fake_response,
            ):
                with redirect_stdout(buffer):
                    rc = main(["--output", "json", "--env-file", str(env_path), "auth", "check"])
        self.assertEqual(rc, 1)
        text = buffer.getvalue()
        self.assertNotIn(secret_key, text)
        payload = json.loads(text)
        self.assertIn("***REDACTED***", payload["error"])

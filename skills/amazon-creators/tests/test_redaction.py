from __future__ import annotations

import io
import json
import re
import tempfile
import time
import unittest
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path
from unittest.mock import patch

import requests

from amazon_creators_api_tool.cli import main

TOKEN_LIKE_PATTERN = re.compile(r"^[A-Za-z0-9_-]{20,}$")

class TestSecretRedaction(unittest.TestCase):
    def test_verbose_search_hides_cfg_secret(self) -> None:
        secret = "SUPER_SECRET_TOKEN_VALUE"
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            env_file = tmp_path / ".env"
            env_file.write_text(
                "\n".join(
                    [
                        "AMAZON_CREATORS_API_BASE_URL=https://creatorsapi.amazon/catalog/v1",
                        "AMAZON_CREATORS_CREDENTIAL_ID=test-id",
                        f"AMAZON_CREATORS_CREDENTIAL_SECRET={secret}",
                        "AMAZON_CREATORS_CREDENTIAL_VERSION=2.1",
                        "AMAZON_CREATORS_LOCALE=us",
                        "AMAZON_CREATORS_PARTNER_TAG=pt",
                        "AMAZON_CREATORS_TIMEOUT_S=30",
                    ]
                )
                + "\n"
            )
            state_dir = tmp_path / ".state"
            state_dir.mkdir(exist_ok=True)
            token_path = state_dir / "token.json"
            token_path.write_text(
                json.dumps(
                    {
                        "accessToken": "dummy-token",
                        "expires_in": 3600,
                        "fetched_at": time.time(),
                    }
                )
                + "\n"
            )

            args = [
                "--env-file",
                str(env_file),
                "--verbose",
                "--apply",
                "search",
                "--keywords",
                "test",
            ]
            with patch("amazon_creators_api_tool.http.requests.Session.request") as mock_request:
                mock_request.side_effect = requests.RequestException(f"HTTP failure {secret}")
                stdout = io.StringIO()
                stderr = io.StringIO()
                with redirect_stdout(stdout), redirect_stderr(stderr):
                    rc = main(args)

        self.assertNotIn(secret, stdout.getvalue())
        self.assertNotIn(secret, stderr.getvalue())
        self.assertEqual(rc, 1)

    def test_token_sample_placeholders_are_safe(self) -> None:
        sample_path = Path(__file__).resolve().parents[1] / "examples/token.sample.json"
        sample = json.loads(sample_path.read_text())
        for field in ("access_token", "refresh_token"):
            value = sample[field]
            self.assertFalse(
                TOKEN_LIKE_PATTERN.match(value),
                f"{field} looks like a real token; replace it with a placeholder",
            )

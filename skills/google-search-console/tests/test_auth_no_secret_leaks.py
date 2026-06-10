from __future__ import annotations

import unittest
from pathlib import Path

from gsc_api_tool import cli as gsc_cli


class TestAuthNoSecretLeaks(unittest.TestCase):
    def test_error_redaction_scrubs_secret_like_env_values(self) -> None:
        # This is a unit test for the CLI redaction layer: if an exception message ever includes a secret-like
        # value from the env file, it should be scrubbed before JSON output.
        env_path = Path(__file__).resolve().parent / "_tmp_no_commit.env"
        try:
            env_path.write_text(
                "\n".join(
                    [
                        "GSC_FAKE_TOKEN=SUPERSECRET_TOKEN_VALUE_12345",
                        "GSC_FAKE_SECRET=SUPERSECRET_VALUE_67890",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            msg = "Boom: SUPERSECRET_TOKEN_VALUE_12345 and SUPERSECRET_VALUE_67890"
            redacted = gsc_cli._redact_secret_like_values(text=msg, env_file=str(env_path))
            self.assertNotIn("SUPERSECRET_TOKEN_VALUE_12345", redacted)
            self.assertNotIn("SUPERSECRET_VALUE_67890", redacted)
            self.assertIn("***REDACTED***", redacted)
        finally:
            try:
                env_path.unlink()
            except Exception:
                pass


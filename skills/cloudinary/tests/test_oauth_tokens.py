from __future__ import annotations

import requests
import tempfile
import unittest
from pathlib import Path

from ._helpers import run_cli, write_env


class TestAuthSafety(unittest.TestCase):
    def test_auth_errors_do_not_leak_secrets(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            secret = "super-secret-cloudinary-value"
            env_path = write_env(Path(tmp), product_context=True, product_auth=True, product_secret=secret)

            def _boom(*args, **kwargs):  # noqa: ANN001, ANN003
                raise requests.RequestException(f"request failed with {secret}")

            rc, payload = run_cli(
                ["--output", "json", "--env-file", str(env_path), "auth", "check"],
                request_side_effect=_boom,
            )
            self.assertEqual(rc, 0)
            text = str(payload)
            self.assertNotIn(secret, text)
            self.assertIn("[REDACTED]", text)

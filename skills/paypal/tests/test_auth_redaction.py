from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from paypal_safe_agent_cli.cli import main


class TestAuthRedaction(unittest.TestCase):
    def test_auth_check_failure_does_not_leak_client_secret(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env = Path(d) / ".env"
            secret = "VERY_SECRET_PAYPAL_CLIENT_SECRET"
            env.write_text(
                "\n".join(
                    [
                        "PAYPAL_ENVIRONMENT=sandbox",
                        "PAYPAL_CLIENT_ID=test-client",
                        f"PAYPAL_CLIENT_SECRET={secret}",
                        "PAYPAL_TIMEOUT_S=30",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            with patch("paypal_safe_agent_cli.paypal_auth.resolve_access_token") as mock_resolve:
                mock_resolve.side_effect = RuntimeError("PayPal auth check failed")
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = main(["--env-file", str(env), "auth", "check"])

            self.assertEqual(rc, 1)
            payload = json.loads(buf.getvalue())
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["error_type"], "ToolError")
            self.assertNotIn(secret, buf.getvalue())

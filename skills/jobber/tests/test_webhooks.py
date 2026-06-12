from __future__ import annotations

import base64
import hashlib
import hmac
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from jobber_safe_agent_cli.cli import main


class TestWebhookVerification(unittest.TestCase):
    def _signature(self, *, body: str, secret: str) -> str:
        mac = hmac.new(secret.encode("utf-8"), body.encode("utf-8"), hashlib.sha256).digest()
        return base64.b64encode(mac).decode("utf-8")

    def test_verify_signature_with_env_secret(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env = Path(d) / ".env"
            env.write_text("JOBBER_CLIENT_SECRET=secret\n", encoding="utf-8")
            body = '{"event":"ok","id":"1"}'
            signature = self._signature(body=body, secret="secret")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env),
                        "--output",
                        "json",
                        "webhooks",
                        "verify-signature",
                        "--body",
                        body,
                        "--header",
                        f"X-Jobber-Hmac-SHA256={signature}",
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["matches"])

    def test_verify_signature_from_body_file(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env = Path(d) / ".env"
            env.write_text("JOBBER_CLIENT_SECRET=secret\n", encoding="utf-8")
            body_file = Path(d) / "webhook.json"
            body_file.write_text("{}", encoding="utf-8")
            signature = self._signature(body="{}", secret="secret")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env),
                        "--output",
                        "json",
                        "webhooks",
                        "verify-signature",
                        "--body-file",
                        str(body_file),
                        "--header",
                        signature,
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["matches"])


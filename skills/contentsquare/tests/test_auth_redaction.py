from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

from contentsquare_safe_agent_cli.cli import main


class AuthRedactionTests(unittest.TestCase):
    def test_secret_value_not_printed_on_auth_failure(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env = Path(td) / ".env"
            env.write_text(
                "CONTENTSQUARE_CLIENT_ID=client\nCONTENTSQUARE_CLIENT_SECRET=SUPER_SECRET_VALUE\n",
                encoding="utf-8",
            )
            with mock.patch(
                "contentsquare_safe_agent_cli.contentsquare_client.HttpClient.request",
                side_effect=RuntimeError("HTTP 401 for POST https://api.contentsquare.com/v1/oauth/token"),
            ):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = main(["--env-file", str(env), "auth", "check"])
            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 1)
            self.assertNotIn("SUPER_SECRET_VALUE", json.dumps(payload))


if __name__ == "__main__":
    unittest.main()

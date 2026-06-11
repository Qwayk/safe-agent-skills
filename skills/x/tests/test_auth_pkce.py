from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from x_api_tool.cli import main


class TestAuthPkce(unittest.TestCase):
    def test_pkce_start_plans_without_writing_verifier(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env = Path(d) / ".env"
            env.write_text(
                "\n".join(
                    [
                        "X_API_BASE_URL=https://api.x.com/2",
                        "X_API_TIMEOUT_S=30",
                        "X_API_OAUTH2_CLIENT_ID=client123",
                        "X_API_OAUTH2_REDIRECT_URI=https://example.com/callback",
                        "X_API_OAUTH2_SCOPES=users.read tweet.read",
                        "",
                    ]
                ),
                encoding="utf-8",
            )

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--output", "json", "--env-file", str(env), "auth", "pkce", "start"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])
            self.assertIn("plan", payload)
            self.assertEqual(payload["plan"]["before_state"]["status"], "no_snapshot_available")
            self.assertNotIn("code_verifier", json.dumps(payload))

            st_path = Path(d) / ".state" / "pkce.json"
            self.assertFalse(st_path.exists())

    def test_token_set_apply_refuses_without_storing_token(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env = Path(d) / ".env"
            env.write_text("X_API_BASE_URL=https://api.x.com/2\nX_API_TIMEOUT_S=30\n", encoding="utf-8")
            src = Path(d) / "token.json"
            src.write_text('{"access_token":"SECRET"}\n', encoding="utf-8")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--output", "json", "--env-file", str(env), "--apply", "auth", "token", "set", "--file", str(src)])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            self.assertFalse((Path(d) / ".state" / "token.json").exists())

    def test_token_set_apply_with_ack_no_snapshot_stores_token(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env = Path(d) / ".env"
            env.write_text("X_API_BASE_URL=https://api.x.com/2\nX_API_TIMEOUT_S=30\n", encoding="utf-8")
            src = Path(d) / "token.json"
            src.write_text('{"access_token":"SECRET"}\n', encoding="utf-8")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env),
                        "--apply",
                        "--yes",
                        "--ack-no-snapshot",
                        "auth",
                        "token",
                        "set",
                        "--file",
                        str(src),
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertFalse(payload.get("refused", False))
            self.assertTrue((Path(d) / ".state" / "token.json").exists())
            self.assertEqual(payload["receipt"]["before_state"]["status"], "no_snapshot_available")
            self.assertNotIn("SECRET", json.dumps(payload))

    def test_pkce_start_apply_with_ack_no_snapshot_writes_state_without_verifier_in_output(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            env = Path(d) / ".env"
            env.write_text(
                "\n".join(
                    [
                        "X_API_BASE_URL=https://api.x.com/2",
                        "X_API_TIMEOUT_S=30",
                        "X_API_OAUTH2_CLIENT_ID=client123",
                        "X_API_OAUTH2_REDIRECT_URI=https://example.com/callback",
                        "X_API_OAUTH2_SCOPES=users.read tweet.read",
                        "",
                    ]
                ),
                encoding="utf-8",
            )

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        str(env),
                        "--apply",
                        "--yes",
                        "--ack-no-snapshot",
                        "auth",
                        "pkce",
                        "start",
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertFalse(payload.get("refused", False))
            self.assertTrue((Path(d) / ".state" / "pkce.json").exists())
            self.assertIn("authorization_url", payload["receipt"]["result"])
            self.assertNotIn("code_verifier", json.dumps(payload))

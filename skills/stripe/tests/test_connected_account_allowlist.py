from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from stripe_api_tool.cli import main


def _write_env(tmpdir: str, *, api_key: str, allowlist: str) -> str:
    p = Path(tmpdir) / ".env"
    p.write_text(
        "\n".join(
            [
                f"STRIPE_API_KEY={api_key}",
                "STRIPE_TIMEOUT_S=30",
                f"STRIPE_ACCOUNT_ALLOWLIST={allowlist}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return str(p)


class TestConnectedAccountAllowlist(unittest.TestCase):
    def test_refuses_out_of_allowlist(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_file = _write_env(td, api_key="sk_test_dummy_123", allowlist="acct_allowed")
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        env_file,
                        "api",
                        "--stripe-account",
                        "acct_not_allowed",
                        "post-customers",
                        "--data",
                        "name=Alice",
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload.get("refused"))
            self.assertIn("allowlist", " ".join(payload.get("reasons") or []).lower())


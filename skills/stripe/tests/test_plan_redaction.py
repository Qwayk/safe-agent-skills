from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from stripe_api_tool.cli import main


def _write_env(tmpdir: str, *, api_key: str, allowlist: str | None = None) -> str:
    p = Path(tmpdir) / ".env"
    lines = [f"STRIPE_API_KEY={api_key}", "STRIPE_TIMEOUT_S=30"]
    if allowlist is not None:
        lines.append(f"STRIPE_ACCOUNT_ALLOWLIST={allowlist}")
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return str(p)


class TestPlanRedaction(unittest.TestCase):
    def test_plan_never_includes_api_key_or_authorization_value(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            dummy_key = "sk_test_dummy_123"
            env_file = _write_env(td, api_key=dummy_key)
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--output",
                        "json",
                        "--env-file",
                        env_file,
                        "api",
                        "post-customers",
                        "--data",
                        "name=Alice",
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload.get("dry_run"))
            plan = payload["plan"]
            plan_json = json.dumps(plan, sort_keys=True)
            self.assertNotIn(dummy_key, plan_json)
            headers = plan.get("headers") or {}
            self.assertEqual(str(headers.get("authorization") or ""), "<REDACTED>")


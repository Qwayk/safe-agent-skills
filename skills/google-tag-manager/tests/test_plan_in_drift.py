from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from gtm_api_tool.cli import main


class TestPlanInDrift(unittest.TestCase):
    def test_apply_refuses_if_plan_fingerprint_changed(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text("GTM_AUTH_MODE=adc\nGTM_TIMEOUT_S=30\n", encoding="utf-8")
            plan_path = root / "plan.json"

            # Create a plan.
            buf0 = io.StringIO()
            with redirect_stdout(buf0):
                _ = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--plan-out",
                        str(plan_path),
                        "accounts",
                        "update",
                        "--path",
                        "accounts/123",
                        "--body-json",
                        "{}",
                    ]
                )
            plan = json.loads(plan_path.read_text(encoding="utf-8"))
            plan["request"]["request_fingerprint"] = "0" * 64
            plan_path.write_text(json.dumps(plan, indent=2, sort_keys=True) + "\n", encoding="utf-8")

            # Apply should require explicit no-snapshot approval before any network.
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--plan-in",
                        str(plan_path),
                        "accounts",
                        "update",
                        "--path",
                        "accounts/123",
                        "--body-json",
                        "{}",
                    ]
                )
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])

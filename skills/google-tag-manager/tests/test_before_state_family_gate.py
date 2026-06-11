from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from gtm_api_tool.cli import main


class TestBeforeStateFamilyGate(unittest.TestCase):
    def _write_env(self, root: Path) -> Path:
        p = root / ".env"
        p.write_text("GTM_AUTH_MODE=adc\nGTM_TIMEOUT_S=30\n", encoding="utf-8")
        return p

    def test_mutating_family_without_before_state_read_is_apply_refused(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = self._write_env(root)
            plan_path = root / "plan.json"

            # Dry-run path keeps being usable for review.
            buf0 = io.StringIO()
            with redirect_stdout(buf0):
                rc0 = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--plan-out",
                        str(plan_path),
                        "accounts",
                        "containers",
                        "workspaces",
                        "built-in-variables",
                        "delete",
                        "--path",
                        "accounts/1/containers/2/workspaces/3/built_in_variables",
                    ]
                )
            payload0 = json.loads(buf0.getvalue())
            self.assertEqual(rc0, 0)
            self.assertTrue(payload0["ok"])
            self.assertTrue(payload0["dry_run"])
            self.assertTrue(plan_path.exists())

            buf1 = io.StringIO()
            with redirect_stdout(buf1):
                rc1 = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--yes",
                        "--ack-irreversible",
                        "--plan-in",
                        str(plan_path),
                        "accounts",
                        "containers",
                        "workspaces",
                        "built-in-variables",
                        "delete",
                        "--path",
                        "accounts/1/containers/2/workspaces/3/built_in_variables",
                    ]
                )
            payload1 = json.loads(buf1.getvalue())
            self.assertEqual(rc1, 0)
            self.assertTrue(payload1["ok"])
            self.assertTrue(payload1["refused"])
            joined = " ".join(str(reason) for reason in payload1["reasons"])
            self.assertIn("before-state snapshot", joined)
            self.assertIn("ack-no-snapshot", joined)

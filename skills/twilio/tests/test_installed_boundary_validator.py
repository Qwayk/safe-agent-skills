from __future__ import annotations

import os
import subprocess
import sys
import unittest
from pathlib import Path

TOOL_ROOT = Path(__file__).resolve().parents[1]


class TestInstalledBoundaryValidator(unittest.TestCase):
    def test_validator_binds_plans_to_installed_package_version(self) -> None:
        source = (TOOL_ROOT / "scripts" / "validate_installed_boundary.py").read_text(
            encoding="utf-8"
        )
        self.assertIn("from twilio_safe_agent_cli import __version__", source)
        self.assertNotIn('tool_version="0.1.0"', source)

    def test_validator_accepts_current_packaged_boundary_and_guards(self) -> None:
        env = os.environ.copy()
        env["PYTHONPATH"] = str(TOOL_ROOT / "src")
        result = subprocess.run(
            [sys.executable, str(TOOL_ROOT / "scripts" / "validate_installed_boundary.py")],
            cwd=TOOL_ROOT,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
        self.assertIn("accurate help", result.stdout)


if __name__ == "__main__":
    unittest.main()

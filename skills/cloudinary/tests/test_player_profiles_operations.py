from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from ._helpers import build_cli_args_for_spec, env_for_spec, run_cli, spec_for_area


class TestPlayerProfilesOperations(unittest.TestCase):
    def test_player_profiles_area_has_a_runnable_explicit_command(self) -> None:
        spec = spec_for_area("player_profiles")
        self.assertTrue(spec.is_write)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            env_path = env_for_spec(root, spec)
            rc, payload = run_cli(build_cli_args_for_spec(root, spec, env_path))
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["dry_run"])

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from ._helpers import FakeResponse, build_cli_args_for_spec, env_for_spec, run_cli, spec_for_area


class TestAnalyzeOperations(unittest.TestCase):
    def test_analyze_area_calls_the_api_for_read_like_post(self) -> None:
        spec = spec_for_area("analyze")
        self.assertFalse(spec.is_write)

        def _fake_request(*args, **kwargs):  # noqa: ANN001, ANN003
            return FakeResponse(payload={"request_id": "demo", "data": {"analysis": "ok"}})

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            env_path = env_for_spec(root, spec)
            rc, payload = run_cli(
                build_cli_args_for_spec(root, spec, env_path),
                request_side_effect=_fake_request,
            )
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertIn("response", payload)

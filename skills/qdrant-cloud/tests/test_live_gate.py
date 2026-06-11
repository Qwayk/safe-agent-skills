from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from qdrant_cloud_api_tool.cli import main


class TestLiveGate(unittest.TestCase):
    def test_apply_refuses_without_live(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text("QDRANT_CLOUD_API_BASE_URL=http://example.invalid\nQDRANT_CLOUD_TIMEOUT_S=30\n", encoding="utf-8")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["--output", "json", "--env-file", str(env_path), "--apply", "account-v1", "create-account"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            self.assertIn("--live", " ".join(payload.get("reasons") or []))


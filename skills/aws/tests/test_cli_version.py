from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout

from aws_safe_agent_cli.cli import main


class TestCliVersion(unittest.TestCase):
    def test_version_json_no_env_needed(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = main(["--output", "json", "--version"])
        self.assertEqual(rc, 0)
        payload = json.loads(buf.getvalue())
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["tool"], "qwayk-aws-safe-agent-cli")
        self.assertIn("version", payload)
        self.assertEqual(payload["boto3_version"], "1.43.36")
        self.assertEqual(payload["botocore_version"], "1.43.36")
        self.assertEqual(payload["inventory_counts"]["service_count"], 428)
        self.assertEqual(payload["inventory_counts"]["operation_count"], 18727)

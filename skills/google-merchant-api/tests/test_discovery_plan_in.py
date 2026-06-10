from __future__ import annotations

import io
import json
import tempfile
import unittest
from pathlib import Path
from contextlib import redirect_stdout

from google_merchant_api_tool.cli import main


class TestDiscoveryPlanInRules(unittest.TestCase):
    def test_irreversible_delete_requires_plan_in_yes_and_ack(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(
                "\n".join(
                    [
                        "GOOGLE_MERCHANT_API_BASE_URL=http://example.invalid",
                        "GOOGLE_MERCHANT_API_TIMEOUT_S=30",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--yes",
                        "accounts",
                        "conversion-sources",
                        "delete",
                        "--name",
                        "accounts/123456/conversionSources/abc",
                    ]
                )
            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            self.assertIn("Refusing irreversible write", payload["reasons"][0])

    def test_high_risk_manual_method_requires_plan_in(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text(
                "\n".join(["GOOGLE_MERCHANT_API_BASE_URL=http://example.invalid", "GOOGLE_MERCHANT_API_TIMEOUT_S=30"]) + "\n",
                encoding="utf-8",
            )

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(
                    [
                        "--env-file",
                        str(env_path),
                        "--apply",
                        "--yes",
                        "accounts",
                        "v1alpha",
                        "loyalty-customers",
                        "manage",
                        "--parent",
                        "accounts/123456",
                        "--body-json",
                        '{"dummy": true}',
                    ]
                )
            payload = json.loads(buf.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["refused"])
            self.assertIn("without --plan-in", payload["reasons"][0])

from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from qwayk_woocommerce_safe_agent_cli.cli import main
from qwayk_woocommerce_safe_agent_cli.config import load_config
from qwayk_woocommerce_safe_agent_cli.errors import ValidationError


class TestConfigCli(unittest.TestCase):
    def test_config_json_merges_with_env_and_cli_timeout_wins(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            env_file = root / "custom.env"
            config_file = root / "defaults.json"

            env_file.write_text("WOOCOMMERCE_STORE_URL=https://from-env.example\n", encoding="utf-8")
            config_file.write_text(
                json.dumps(
                    {
                        "WOOCOMMERCE_STORE_URL": "https://from-config.example",
                        "WOOCOMMERCE_TIMEOUT_S": 8,
                        "WOOCOMMERCE_QUERY_STRING_AUTH": True,
                    }
                ),
                encoding="utf-8",
            )

            calls: dict[str, object] = {}

            def fake_operation(_args, ctx):
                calls["timeout_s"] = ctx["timeout_s"]
                calls["store_url"] = ctx["cfg"].store_url
                ctx["out"].emit({"ok": True})
                return 0

            with patch(
                "qwayk_woocommerce_safe_agent_cli.cli.operations_cmd.cmd_execute_operation",
                fake_operation,
            ):
                buffer = io.StringIO()
                with redirect_stdout(buffer):
                    rc = main(
                        [
                            "--env-file",
                            str(env_file),
                            "--config",
                            str(config_file),
                            "--timeout-s",
                            "12",
                            "--output",
                            "json",
                            "products",
                            "list",
                        ]
                    )
            self.assertEqual(rc, 0)
            self.assertEqual(calls["timeout_s"], 12.0)
            self.assertEqual(calls["store_url"], "https://from-env.example")

            calls.clear()
            with patch(
                "qwayk_woocommerce_safe_agent_cli.cli.operations_cmd.cmd_execute_operation",
                fake_operation,
            ):
                buffer = io.StringIO()
                with redirect_stdout(buffer):
                    rc = main(
                        [
                            "--env-file",
                            str(env_file),
                            "--config",
                            str(config_file),
                            "--output",
                            "json",
                            "products",
                            "list",
                        ]
                    )
            self.assertEqual(rc, 0)
            self.assertEqual(calls["timeout_s"], 8.0)

    def test_config_json_rejects_consumer_secrets(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "bad-secrets.json"
            config_file.write_text(
                json.dumps(
                    {
                        "WOOCOMMERCE_STORE_URL": "https://shop.example.com",
                        "WOOCOMMERCE_CONSUMER_KEY": "do-not-store-key",
                        "WOOCOMMERCE_TIMEOUT_S": 10,
                    }
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValidationError, "non-secret"):
                load_config(env_file=None, config_file=str(config_file))

from __future__ import annotations

import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from amazon_creators_api_tool.cli import (
    _REQUIRED_GLOBAL_FLAG_SPECS,
    _collect_global_flag_metadata,
    _normalize_global_flags,
    build_parser,
    main,
)


class CliGlobalFlagOrderTests(unittest.TestCase):
    def _write_env(self, base: str) -> str:
        env_path = os.path.join(base, ".env")
        with open(env_path, "w", encoding="utf-8") as f:
            f.write("AMAZON_CREATORS_API_BASE_URL=https://creatorsapi.amazon/catalog/v1\n")
            f.write("AMAZON_CREATORS_CREDENTIAL_ID=cred-id\n")
            f.write("AMAZON_CREATORS_CREDENTIAL_SECRET=secret\n")
            f.write("AMAZON_CREATORS_CREDENTIAL_VERSION=2\n")
            f.write("AMAZON_CREATORS_LOCALE=en_US\n")
            f.write("AMAZON_CREATORS_TIMEOUT_S=30\n")
            f.write("AMAZON_CREATORS_PARTNER_TAG=partner-tag\n")
        return env_path

    def _run_json(self, args: list[str]) -> dict[str, object]:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = main(["--output", "json"] + args)
        self.assertEqual(rc, 0)
        return json.loads(buf.getvalue())

    def test_auth_token_status_accepts_global_flags_after_subcommand(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            payload = self._run_json(
                [
                    "auth",
                    "token",
                    "status",
                    "--env-file",
                    env_path,
                    "--apply",
                ]
            )
            self.assertTrue(payload["ok"])
            self.assertIn("token_status", payload)

    def test_items_get_calls_operation_when_apply_follows_command(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            captured: dict[str, object] = {}

            def fake_call(cfg, ctx, operation, body, locale):
                captured["operation"] = operation
                captured["body"] = body
                return {"items": [{"asin": "B0TEST"}]}

            with patch(
                "amazon_creators_api_tool.commands.catalog._call_operation",
                side_effect=fake_call,
            ):
                payload = self._run_json(
                    [
                        "items",
                        "get",
                        "--item-id",
                        "B0TEST",
                        "--resource",
                        "ItemInfo",
                        "--env-file",
                        env_path,
                        "--apply",
                    ]
                )

            self.assertEqual(captured.get("operation"), "GetItems")
            self.assertEqual(captured["body"]["itemIds"], ["B0TEST"])
            self.assertEqual(payload["operation"], "GetItems")
            self.assertEqual(payload["items"][0]["asin"], "B0TEST")

    def test_plan_out_flag_after_command_still_works(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            plan_path = os.path.join(td, "plan.json")
            with patch(
                "amazon_creators_api_tool.commands.catalog._call_operation",
                return_value={"items": [{"asin": "B0TEST"}]},
            ):
                payload = self._run_json(
                    [
                        "items",
                        "get",
                        "--item-id",
                        "B0TEST",
                        "--env-file",
                        env_path,
                        "--plan-out",
                        plan_path,
                        "--resource",
                        "ItemInfo",
                    ]
                )
            self.assertTrue(os.path.exists(plan_path))
            self.assertEqual(payload["operation"], "GetItems")

    def test_plan_in_and_confirmation_flags_are_inactive_for_catalog_dry_run(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            env_path = self._write_env(td)
            with patch(
                "amazon_creators_api_tool.commands.catalog._call_operation",
            ) as mock_call:
                payload = self._run_json(
                    [
                        "items",
                        "get",
                        "--item-id",
                        "B0TEST",
                        "--plan-in",
                        os.path.join(td, "plan.json"),
                        "--yes",
                        "--ack-irreversible",
                        "--env-file",
                        env_path,
                    ]
                )

            mock_call.assert_not_called()
            self.assertTrue(payload["dry_run"])
            self.assertIn("plan", payload)
            self.assertNotIn("receipt", payload)

    def test_global_flag_normalizer_handles_all_global_options(self) -> None:
        parser = build_parser()
        global_flags_with_value, global_flags = _collect_global_flag_metadata(parser)
        sample_values: dict[str, str] = {
            "--artifacts-dir": "/tmp/artifacts",
            "--config": "sample-config.json",
            "--env-file": ".env",
            "--locale": "en_US",
            "--log-file": "log.json",
            "--output": "json",
            "--plan-in": "existing-plan.json",
            "--plan-out": "plan.json",
            "--project-dir": "/tmp/project",
            "--receipt-out": "receipt.json",
            "--resource": "ItemInfo",
            "--resource-preset": "book-media",
            "--run-id": "run-123",
            "--timeout-s": "15",
        }
        examples: list[tuple[str, str | None]] = []
        for flag, needs_value in _REQUIRED_GLOBAL_FLAG_SPECS:
            value = sample_values.get(flag) if needs_value else None
            examples.append((flag, value))
        for flag, value in examples:
            with self.subTest(flag=flag):
                argv = ["items", "get", "--item-id", "B0TEST", flag]
                if value:
                    argv.append(value)
                normalized = _normalize_global_flags(argv, global_flags, global_flags_with_value)
                items_index = normalized.index("items")
                flag_index = normalized.index(flag)
                self.assertLess(flag_index, items_index, msg=f"{flag} should move ahead of the command")
                if value is not None:
                    self.assertEqual(normalized[flag_index + 1], value)

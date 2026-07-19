from __future__ import annotations

import contextlib
import io
import json
import sys
import unittest
from pathlib import Path

TOOL_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOL_ROOT / "src"))


class TestRegistryAndCli(unittest.TestCase):
    def test_packaged_registry_has_only_fixed_command_rows(self) -> None:
        from twilio_safe_agent_cli.registry import load_registry

        registry = load_registry()
        self.assertEqual(registry.summary()["raw_operations"], 1_550)
        self.assertEqual(registry.summary()["commands"], 1_325)
        self.assertEqual(registry.summary()["legacy_eol"], 205)
        self.assertEqual(registry.summary()["canonical_duplicates"], 9)
        self.assertEqual(registry.summary()["developer_preview"], 5)
        self.assertEqual(registry.summary()["private_or_unavailable"], 6)
        self.assertEqual(
            registry.get("api-v2010.create-message")["operation_id"],
            "CreateMessage",
        )
        self.assertIsNone(registry.get("chat-v2.create-message"))
        self.assertIsNone(registry.get("notify-v1.create-notification"))
        self.assertIsNone(registry.get("https://api.twilio.com"))

    def test_cli_inventory_summary_is_one_json_object(self) -> None:
        from twilio_safe_agent_cli.cli import main

        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            rc = main(["--output", "json", "inventory", "summary"])
        payload = json.loads(stdout.getvalue())
        self.assertEqual(rc, 0)
        self.assertEqual(payload["commands"], 1_325)
        self.assertEqual(stdout.getvalue().count("\n"), 1)

    def test_inventory_show_explains_one_fixed_input_contract_without_credentials(self) -> None:
        from twilio_safe_agent_cli.cli import main

        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            rc = main(
                [
                    "inventory",
                    "show",
                    "--command",
                    "api-v2010.create-message",
                ]
            )
        payload = json.loads(stdout.getvalue())
        self.assertEqual(rc, 0)
        self.assertEqual(payload["command"], "api-v2010.create-message")
        self.assertEqual(payload["method"], "POST")
        self.assertEqual(payload["input"]["body"]["required_fields"], ["To"])
        self.assertIn("Body", payload["input"]["body"]["fields"])
        self.assertNotIn("description", json.dumps(payload).lower())

    def test_inventory_show_keeps_conditional_body_requirements_separate(self) -> None:
        from twilio_safe_agent_cli.registry import load_registry

        body = load_registry().describe("video-v1.create-composition")["input"]["body"]
        self.assertEqual(body["required_fields"], ["RoomSid"])
        self.assertEqual(body["required_any_of"], [["VideoLayout"], ["AudioSources"]])

    def test_inventory_show_marks_scim_and_porting_snapshots_as_required(self) -> None:
        from twilio_safe_agent_cli.registry import load_registry

        registry = load_registry()
        for command in (
            "iam-organizations.patch-organization-user",
            "numbers-v1.create-porting-webhook-configuration",
        ):
            with self.subTest(command=command):
                payload = registry.describe(command)
                self.assertTrue(payload["snapshot_required"])
                self.assertEqual(payload["snapshot_strategy"], "fetch_before_change")

    def test_unknown_generated_command_fails_before_http(self) -> None:
        from twilio_safe_agent_cli.cli import main

        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            rc = main(["api-v2010", "raw-request"])
        payload = json.loads(stdout.getvalue())
        self.assertEqual(rc, 1)
        self.assertFalse(payload["ok"])
        self.assertIn("invalid choice", payload["error"])

    def test_version_and_operation_help_use_accurate_product_language(self) -> None:
        from twilio_safe_agent_cli.cli import build_parser, main

        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            rc = main(["--version"])
        payload = json.loads(stdout.getvalue())
        self.assertEqual(rc, 0)
        self.assertEqual(payload["tool"], "qwayk-twilio-safe-agent-cli")

        help_stdout = io.StringIO()
        with contextlib.redirect_stdout(help_stdout), self.assertRaises(SystemExit) as context:
            build_parser().parse_args(["api-v2010", "fetch-account", "--help"])
        self.assertEqual(context.exception.code, 0)
        help_text = help_stdout.getvalue().lower()
        self.assertIn("protected current-state snapshot", help_text)
        self.assertIn("sensitive provider output", help_text)
        self.assertNotIn("reversible update", help_text)
        self.assertNotIn("full provider result", help_text)


if __name__ == "__main__":
    unittest.main()

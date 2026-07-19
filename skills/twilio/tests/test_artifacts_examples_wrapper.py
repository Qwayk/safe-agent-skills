from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

from twilio_safe_agent_cli.registry import load_registry

TOOL_ROOT = Path(__file__).resolve().parents[1]


class TestArtifactsExamplesAndWrapper(unittest.TestCase):
    def test_every_committed_json_example_parses_and_contains_no_secret_value(self) -> None:
        paths = sorted((TOOL_ROOT / "examples").rglob("*.json"))
        paths += sorted((TOOL_ROOT / "docs/examples").rglob("*.json"))
        paths += sorted((TOOL_ROOT / "tests/fixtures").rglob("*.json"))
        self.assertGreaterEqual(len(paths), 8)
        for path in paths:
            value = json.loads(path.read_text(encoding="utf-8"))
            serialized = json.dumps(value).lower()
            self.assertNotIn("twilio_auth_token", serialized, str(path))
            self.assertNotIn("api_key_secret", serialized, str(path))
            self.assertNotIn("oauth_access_token", serialized, str(path))
            self.assertNotIn("private-secret", serialized, str(path))

    def test_test_credential_fixtures_are_reserved_and_never_claim_live_execution(self) -> None:
        from twilio_safe_agent_cli.config import Config
        from twilio_safe_agent_cli.runtime import prepare_request

        cfg = Config(
            account_sid="AC" + "0" * 32,
            api_key_sid=None,
            api_key_secret=None,
            auth_token="test-token-placeholder",
            oauth_access_token=None,
            region=None,
            edge=None,
            timeout_s=30,
        )
        fixture_dir = TOOL_ROOT / "tests/fixtures/twilio_test_credentials"
        fixtures = sorted(fixture_dir.glob("*.json"))
        self.assertEqual(
            {path.name for path in fixtures},
            {
                "call-success.json",
                "lookup-success.json",
                "message-success.json",
                "number-purchase-success.json",
            },
        )
        for path in fixtures:
            value = json.loads(path.read_text(encoding="utf-8"))
            self.assertFalse(value["live_executed"])
            self.assertEqual(value["credential_mode"], "twilio_test_credentials")
            operation = load_registry().get(value["command"])
            self.assertIsNotNone(operation)
            request = prepare_request(operation, value["input"], cfg)
            if path.name == "lookup-success.json":
                self.assertEqual(request.method, "GET")
                self.assertEqual(value["command"], "lookups-v2.fetch-phone-number")
                self.assertEqual(value["input"]["path"]["PhoneNumber"], "+12345678924")
                self.assertEqual(value["input"]["query"]["Fields"], "sim_swap")
            else:
                self.assertEqual(request.method, "POST")
                self.assertIn("+1500555000", json.dumps(value))

    def test_plan_example_is_the_actual_current_dry_run_contract(self) -> None:
        from twilio_safe_agent_cli.config import Config
        from twilio_safe_agent_cli.safety import build_plan

        cfg = Config(
            account_sid="AC" + "0" * 32,
            api_key_sid="SK" + "0" * 32,
            api_key_secret="example-placeholder-not-a-secret",
            auth_token=None,
            oauth_access_token=None,
            region=None,
            edge=None,
            timeout_s=30,
        )
        registry = load_registry()
        operation = registry.get("api-v2010.create-message")
        input_obj = json.loads(
            (TOOL_ROOT / "examples/inputs/create-message-plan.json").read_text(encoding="utf-8")
        )
        paired = registry.paired_read(operation)
        expected = build_plan(
            operation,
            input_obj,
            cfg,
            registry.inventory_hash,
            "0.1.0",
            snapshot_command=paired["command"] if paired else None,
        )
        actual = json.loads(
            (TOOL_ROOT / "docs/examples/plan.example.json").read_text(encoding="utf-8")
        )
        self.assertEqual(actual, expected)

    def test_receipt_example_matches_the_reviewed_plan_example(self) -> None:
        plan = json.loads(
            (TOOL_ROOT / "docs/examples/plan.example.json").read_text(encoding="utf-8")
        )
        receipt = json.loads(
            (TOOL_ROOT / "docs/examples/receipt.example.json").read_text(encoding="utf-8")
        )
        self.assertEqual(receipt["plan_id"], plan["plan_id"])
        self.assertEqual(
            receipt["account_fingerprint"],
            plan["operation"]["account_fingerprint"],
        )
        self.assertEqual(receipt["command"], plan["operation"]["command"])

    def test_skill_wrapper_uses_only_real_fixed_commands_and_has_minimal_frontmatter(self) -> None:
        wrapper = TOOL_ROOT / "skills/twilio/SKILL.md"
        if not wrapper.exists():
            wrapper = TOOL_ROOT / "SKILL.md"
        text = wrapper.read_text(encoding="utf-8")
        frontmatter = text.split("---", 2)[1]
        keys = [line.split(":", 1)[0].strip() for line in frontmatter.splitlines() if ":" in line]
        self.assertEqual(keys, ["name", "description"])
        self.assertIn("name: twilio", frontmatter)
        self.assertNotRegex(text.lower(), r"raw[- ]request|arbitrary (url|endpoint|method)")
        self.assertIn(
            "inventory show --command api-v2010.create-message",
            text,
        )

        registry = load_registry()
        commands = re.findall(
            r"qwayk-twilio-safe-agent-cli[ \t]+([a-z][a-z0-9-]*)[ \t]+([a-z][a-z0-9-]*)",
            text,
        )
        generated_commands = [item for item in commands if item[0] in registry.by_spec]
        self.assertGreaterEqual(len(generated_commands), 2)
        for spec_id, operation_name in generated_commands:
            self.assertIn(f"{spec_id}.{operation_name}", registry.commands)

    def test_wrapper_and_examples_keep_live_contact_behind_review(self) -> None:
        wrapper = TOOL_ROOT / "skills/twilio/SKILL.md"
        if not wrapper.exists():
            wrapper = TOOL_ROOT / "SKILL.md"
        text = wrapper.read_text(encoding="utf-8").lower()
        for concept in (
            "dry-run",
            "--plan-in",
            "--apply",
            "--yes",
            "--ack-contact",
            "--ack-spend",
            "queued",
            "delivered",
            "protected",
        ):
            self.assertIn(concept, text)


if __name__ == "__main__":
    unittest.main()

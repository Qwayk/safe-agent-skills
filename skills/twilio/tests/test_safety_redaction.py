from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

TOOL_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOL_ROOT / "src"))


class TestSafetyAndRedaction(unittest.TestCase):
    def setUp(self) -> None:
        from twilio_safe_agent_cli.config import Config

        self.cfg = Config(
            account_sid="AC" + "a" * 32,
            api_key_sid="SK" + "b" * 32,
            api_key_secret="private-secret",
            auth_token=None,
            oauth_access_token=None,
            region=None,
            edge=None,
            timeout_s=30.0,
        )

    def test_message_plan_requires_all_relevant_acknowledgements(self) -> None:
        from twilio_safe_agent_cli.registry import load_registry
        from twilio_safe_agent_cli.safety import build_plan

        operation = load_registry().get("api-v2010.create-message")
        input_obj = {
            "body": {
                "To": "+15005550006",
                "From": "+15005550006",
                "Body": "private message",
            }
        }
        plan = build_plan(operation, input_obj, self.cfg, load_registry().inventory_hash, "0.1.0")
        self.assertEqual(
            plan["required_acknowledgements"],
            ["ack_contact", "ack_no_snapshot", "ack_spend"],
        )
        serialized = json.dumps(plan)
        self.assertNotIn("private message", serialized)
        self.assertNotIn("+15005550006", serialized)

    def test_scim_and_porting_plans_require_bound_snapshots_and_exact_risk_acks(self) -> None:
        from twilio_safe_agent_cli.registry import load_registry
        from twilio_safe_agent_cli.safety import build_plan

        registry = load_registry()
        snapshot = {
            "path": "/protected/before.json",
            "sha256": "a" * 64,
            "bytes": 80,
            "protected_mode": "0o600",
        }
        scim = registry.get("iam-organizations.patch-organization-user")
        scim_input = {
            "path": {"OrganizationSid": "OR" + "0" * 32, "UserSid": "US" + "0" * 32},
            "headers": {"If-Match": "W/13"},
            "content_type": "application/scim+json",
            "body": {
                "schemas": ["urn:ietf:params:scim:api:messages:2.0:PatchOp"],
                "Operations": [
                    {"op": "replace", "path": "displayName", "value": "Private Name"}
                ],
            },
        }
        scim_plan = build_plan(
            scim,
            scim_input,
            self.cfg,
            registry.inventory_hash,
            "0.1.0",
            snapshot_command="iam-organizations.fetch-organization-user",
            snapshot_receipt=snapshot,
        )
        self.assertEqual(
            scim_plan["required_acknowledgements"],
            ["ack_auth", "ack_identity", "ack_preview", "ack_production", "snapshot_in"],
        )
        self.assertNotIn("Private Name", json.dumps(scim_plan))

        porting = registry.get("numbers-v1.create-porting-webhook-configuration")
        porting_plan = build_plan(
            porting,
            {"body": {"port_in_target_url": "https://hooks.example.com/in"}},
            self.cfg,
            registry.inventory_hash,
            "0.1.0",
            snapshot_command="numbers-v1.fetch-porting-webhook-configuration-fetch",
            snapshot_receipt=snapshot,
        )
        self.assertEqual(
            porting_plan["required_acknowledgements"],
            ["ack_identity", "ack_preview", "ack_production", "snapshot_in"],
        )
        self.assertEqual(
            porting_plan["expected_effect"],
            "POST overwrites the existing Porting webhook configuration.",
        )

    def test_every_goal_risk_family_maps_to_its_own_acknowledgement(self) -> None:
        from twilio_safe_agent_cli.safety import required_acknowledgements

        expected = {
            "outbound_contact": "ack_contact",
            "spend": "ack_spend",
            "bulk": "ack_bulk",
            "destructive": "ack_destructive",
            "auth_or_permission": "ack_auth",
            "identity_or_compliance": "ack_identity",
            "production_change": "ack_production",
        }
        for risk, acknowledgement in expected.items():
            operation = {
                "method": "POST",
                "risk_flags": [risk, "write"],
                "snapshot_strategy": "no_snapshot_action",
            }
            required = required_acknowledgements(operation, {})
            self.assertIn(acknowledgement, required, risk)

    def test_plan_fingerprint_detects_input_or_environment_drift(self) -> None:
        from twilio_safe_agent_cli.errors import SafetyError
        from twilio_safe_agent_cli.registry import load_registry
        from twilio_safe_agent_cli.safety import build_plan, verify_plan

        registry = load_registry()
        operation = registry.get("api-v2010.create-message")
        original = {"body": {"To": "+15005550006", "Body": "first"}}
        changed = {"body": {"To": "+15005550006", "Body": "changed"}}
        plan = build_plan(operation, original, self.cfg, registry.inventory_hash, "0.1.0")
        with self.assertRaises(SafetyError):
            verify_plan(plan, operation, changed, self.cfg, registry.inventory_hash, "0.1.0")

    def test_reviewed_plan_cannot_remove_risks_or_required_acknowledgements(self) -> None:
        import copy

        from twilio_safe_agent_cli.errors import SafetyError
        from twilio_safe_agent_cli.registry import load_registry
        from twilio_safe_agent_cli.safety import build_plan, verify_plan

        registry = load_registry()
        operation = registry.get("api-v2010.create-message")
        input_obj = {"body": {"To": "+15005550006", "Body": "first"}}
        plan = build_plan(operation, input_obj, self.cfg, registry.inventory_hash, "0.1.0")
        tampered = copy.deepcopy(plan)
        tampered["risks"] = []
        tampered["required_acknowledgements"] = []
        with self.assertRaises(SafetyError):
            verify_plan(
                tampered,
                operation,
                input_obj,
                self.cfg,
                registry.inventory_hash,
                "0.1.0",
            )

    def test_snapshot_hash_is_bound_without_copying_before_state_into_plan(self) -> None:
        from twilio_safe_agent_cli.redaction import file_receipt, write_protected_json
        from twilio_safe_agent_cli.registry import load_registry
        from twilio_safe_agent_cli.safety import build_plan

        registry = load_registry()
        operation = registry.get("api-v2010.update-account")
        input_obj = {"path": {"Sid": self.cfg.account_sid}, "body": {"FriendlyName": "new"}}
        with tempfile.TemporaryDirectory() as tmp:
            snapshot = Path(tmp) / "before.json"
            write_protected_json(snapshot, {"friendly_name": "private old name"})
            plan = build_plan(
                operation,
                input_obj,
                self.cfg,
                registry.inventory_hash,
                "0.1.0",
                snapshot_receipt=file_receipt(snapshot),
            )
        serialized = json.dumps(plan)
        self.assertNotIn("private old name", serialized)
        self.assertEqual(plan["binding"]["snapshot_sha256"], plan["snapshot"]["file"]["sha256"])

    def test_spend_reads_are_plan_first_even_when_method_is_get(self) -> None:
        from twilio_safe_agent_cli.registry import load_registry
        from twilio_safe_agent_cli.safety import build_plan, is_effectful

        registry = load_registry()
        lookup = registry.get("lookups-v2.fetch-phone-number")
        self.assertEqual(lookup["method"], "GET")
        self.assertIn("spend", lookup["risk_flags"])
        self.assertTrue(is_effectful(lookup, {}))
        plan = build_plan(
            lookup,
            {"path": {"PhoneNumber": "+12345678924"}, "query": {"Fields": "sim_swap"}},
            self.cfg,
            registry.inventory_hash,
            "0.1.0",
        )
        self.assertEqual(plan["required_acknowledgements"], ["ack_spend"])

    def test_studio_definition_string_escalates_nested_contact_and_spend_risks(self) -> None:
        from twilio_safe_agent_cli.registry import load_registry
        from twilio_safe_agent_cli.runtime import prepare_request
        from twilio_safe_agent_cli.safety import classify_risks

        operation = load_registry().get("studio-v2.create-flow")
        definition = json.dumps(
            {
                "initial_state": "Send",
                "states": [
                    {
                        "type": "send-message",
                        "name": "Send",
                        "properties": {
                            "from": "+15005550007",
                            "to": "+15005550006",
                            "body": "Hello",
                        },
                        "transitions": [],
                    }
                ],
            }
        )
        input_obj = {
            "body": {
                "FriendlyName": "Risk classification test",
                "Status": "draft",
                "Definition": definition,
            }
        }
        prepared = prepare_request(operation, input_obj, self.cfg)
        self.assertEqual(prepared.form["Definition"], definition)
        risks = classify_risks(operation, input_obj)
        self.assertTrue({"outbound_contact", "spend"}.issubset(risks))

    def test_bulk_eligibility_is_plan_first_and_capped_at_25_targets(self) -> None:
        from twilio_safe_agent_cli.errors import SafetyError
        from twilio_safe_agent_cli.registry import load_registry
        from twilio_safe_agent_cli.safety import build_plan, is_effectful

        registry = load_registry()
        operation = registry.get("numbers-v1.create-bulk-eligibility")
        two = {
            "body": {
                "friendly_name": "Safe test",
                "phone_numbers": [
                    {"phone_number": "+15005550006"},
                    {"phone_number": "+15005550007"},
                ],
            }
        }
        self.assertTrue(is_effectful(operation, two))
        plan = build_plan(operation, two, self.cfg, registry.inventory_hash, "0.1.0")
        self.assertEqual(plan["target_count"], 2)
        self.assertIn("ack_bulk", plan["required_acknowledgements"])

        too_many = {
            "body": {
                "friendly_name": "Safe test",
                "phone_numbers": [
                    {"phone_number": "+15005550006"} for _ in range(26)
                ],
            }
        }
        with self.assertRaises(SafetyError):
            build_plan(operation, too_many, self.cfg, registry.inventory_hash, "0.1.0")

    def test_bulk_status_reads_remain_ordinary_reads(self) -> None:
        from twilio_safe_agent_cli.registry import load_registry
        from twilio_safe_agent_cli.safety import is_effectful

        registry = load_registry()
        for command in (
            "numbers-v1.fetch-bulk-eligibility",
            "numbers-v2.fetch-bulk-hosted-number-order",
        ):
            operation = registry.get(command)
            self.assertNotIn("bulk", operation["risk_flags"])
            self.assertFalse(is_effectful(operation, {}))

    def test_multiple_contact_targets_are_refused(self) -> None:
        from twilio_safe_agent_cli.errors import SafetyError
        from twilio_safe_agent_cli.registry import load_registry
        from twilio_safe_agent_cli.safety import classify_risks

        operation = load_registry().get("api-v2010.create-message")
        with self.assertRaises(SafetyError):
            classify_risks(operation, {"body": {"To": ["+15005550006", "+15005550007"]}})

    def test_nested_send_action_escalates_contact_spend_and_bulk(self) -> None:
        from twilio_safe_agent_cli.registry import load_registry
        from twilio_safe_agent_cli.safety import classify_risks

        operation = dict(load_registry().get("api-v2010.create-message"))
        operation["risk_flags"] = ["write"]
        risks = classify_risks(
            operation,
            {
                "body": {
                    "type": "SEND_MESSAGE",
                    "payload": {
                        "to": [
                            {"address": "+15005550006"},
                            {"address": "+15005550007"},
                        ]
                    },
                }
            },
        )
        self.assertTrue({"outbound_contact", "spend", "bulk"}.issubset(risks))

    def test_bulk_approval_count_must_match_the_bound_input(self) -> None:
        from twilio_safe_agent_cli.errors import SafetyError
        from twilio_safe_agent_cli.registry import load_registry
        from twilio_safe_agent_cli.safety import build_plan, enforce_approvals

        registry = load_registry()
        operation = dict(registry.get("api-v2010.create-message"))
        operation["risk_flags"] = ["write"]
        input_obj = {
            "body": {
                "type": "SEND_MESSAGE",
                "payload": {
                    "to": [
                        {"address": "+15005550006"},
                        {"address": "+15005550007"},
                    ]
                },
            }
        }
        plan = build_plan(operation, input_obj, self.cfg, registry.inventory_hash, "0.1.0")
        self.assertEqual(plan["target_count"], 2)
        acks = {
            "ack_bulk": True,
            "ack_contact": True,
            "ack_no_snapshot": True,
            "ack_spend": True,
        }
        with self.assertRaises(SafetyError):
            enforce_approvals(
                plan,
                acks,
                apply=True,
                yes=True,
                snapshot_in=None,
                target_count=1,
            )
        enforce_approvals(
            plan,
            acks,
            apply=True,
            yes=True,
            snapshot_in=None,
            target_count=2,
        )

    def test_bulk_plan_derives_the_exact_count_and_refuses_more_than_25(self) -> None:
        from twilio_safe_agent_cli.errors import SafetyError
        from twilio_safe_agent_cli.registry import load_registry
        from twilio_safe_agent_cli.safety import build_plan

        registry = load_registry()
        operation = registry.get("lookups-v2.create-bulk-lookup")
        two = {
            "body": {
                "phone_numbers": [
                    {"correlation_id": "one", "phone_number": "+15005550006"},
                    {"correlation_id": "two", "phone_number": "+15005550007"},
                ]
            }
        }
        plan = build_plan(operation, two, self.cfg, registry.inventory_hash, "0.1.0")
        self.assertEqual(plan["target_count"], 2)
        self.assertEqual(plan["binding"]["target_count"], 2)

        too_many = {
            "body": {
                "phone_numbers": [
                    {
                        "correlation_id": str(index),
                        "phone_number": "+15005550006",
                    }
                    for index in range(26)
                ]
            }
        }
        with self.assertRaises(SafetyError):
            build_plan(operation, too_many, self.cfg, registry.inventory_hash, "0.1.0")

    def test_redaction_covers_keys_values_phones_emails_and_secret_urls(self) -> None:
        from twilio_safe_agent_cli.redaction import redact

        payload = {
            "auth_token": "private-secret",
            "to": "+15005550006",
            "email": "person@example.com",
            "url": "https://example.com/hook?token=private-secret",
            "oauth_url": "https://example.com/callback?access_token=another-secret&safe=yes",
            "encoded_url": "https://lookups.twilio.com/v2/PhoneNumbers/%2B15005550006",
            "displayName": "Private Person",
            "phoneNumbers": [{"value": "555-000-1234"}],
            "emails": [{"value": "private.person@example.com"}],
            "nested": {"body": "private communication"},
        }
        redacted = redact(
            payload,
            pii_fields={"body", "to", "email"},
            secret_values=self.cfg.redaction_values(),
        )
        serialized = json.dumps(redacted)
        for forbidden in (
            "private-secret",
            "another-secret",
            "+15005550006",
            "person@example.com",
            "private communication",
            "%2B15005550006",
            "Private Person",
            "555-000-1234",
        ):
            self.assertNotIn(forbidden, serialized)

    def test_redaction_recurses_into_stringified_json_fields(self) -> None:
        from twilio_safe_agent_cli.redaction import REDACTED, redact

        value = json.dumps(
            {
                "nested": {
                    "api_key": "nested-secret",
                    "contact": "+14155550123",
                    "owner": "person@example.com",
                }
            }
        )
        result = redact(value)
        self.assertIsInstance(result, str)
        decoded = json.loads(result)
        self.assertEqual(decoded["nested"]["api_key"], REDACTED)
        self.assertEqual(decoded["nested"]["contact"], REDACTED)
        self.assertEqual(decoded["nested"]["owner"], REDACTED)

    def test_documented_read_through_post_does_not_require_write_approval(self) -> None:
        from twilio_safe_agent_cli.registry import load_registry
        from twilio_safe_agent_cli.safety import is_effectful, required_acknowledgements

        registry = load_registry()
        operation = registry.get("taskrouter-v1.create-task-queue-bulk-real-time-statistics")
        input_obj = {
            "path": {"WorkspaceSid": "WS" + "0" * 32},
            "body": {"queueSids": ["WQ" + "0" * 32]},
        }
        self.assertFalse(is_effectful(operation, input_obj))
        self.assertEqual(required_acknowledgements(operation, input_obj), [])

    def test_environment_fingerprint_binds_oauth_credential_identity(self) -> None:
        from dataclasses import replace

        first = replace(self.cfg, account_sid="UNSCOPED", oauth_access_token="token-one")
        second = replace(self.cfg, account_sid="UNSCOPED", oauth_access_token="token-two")
        self.assertNotEqual(first.fingerprint, second.fingerprint)

    def test_protected_json_is_mode_600(self) -> None:
        from twilio_safe_agent_cli.redaction import write_protected_json

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "result.json"
            write_protected_json(path, {"private": "value"})
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)

    def test_status_wording_does_not_promote_queued_to_delivered(self) -> None:
        from twilio_safe_agent_cli.safety import provider_status_summary

        queued = provider_status_summary({"status": "queued"})
        delivered = provider_status_summary({"status": "delivered"})
        self.assertEqual(queued["provider_status"], "queued")
        self.assertFalse(queued["delivered"])
        self.assertTrue(delivered["delivered"])


if __name__ == "__main__":
    unittest.main()

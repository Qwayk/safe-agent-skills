from __future__ import annotations

import json
import unittest

from twilio_safe_agent_cli.config import Config
from twilio_safe_agent_cli.errors import ValidationError
from twilio_safe_agent_cli.registry import load_registry
from twilio_safe_agent_cli.runtime import prepare_request


class TestManualCommandBehavior(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.registry = load_registry()
        cls.cfg = Config(
            account_sid="AC" + "0" * 32,
            api_key_sid=None,
            api_key_secret=None,
            auth_token="test-placeholder",
            oauth_access_token=None,
            region=None,
            edge=None,
            timeout_s=30,
        )

    def prepare(self, command: str, input_obj: dict[str, object]):
        operation = self.registry.get(command)
        self.assertIsNotNone(operation)
        return prepare_request(operation, input_obj, self.cfg)

    def test_scim_patch_uses_only_fixed_path_specific_operations(self) -> None:
        oauth_cfg = Config(
            account_sid=self.cfg.account_sid,
            api_key_sid=None,
            api_key_secret=None,
            auth_token=None,
            oauth_access_token="test-oauth-placeholder",
            region=None,
            edge=None,
            timeout_s=30,
        )
        operation = self.registry.get("iam-organizations.patch-organization-user")
        self.assertIsNotNone(operation)
        base = {
            "path": {
                "OrganizationSid": "OR" + "0" * 32,
                "UserSid": "US" + "0" * 32,
            },
            "headers": {"If-Match": "W/13"},
            "content_type": "application/scim+json",
            "body": {
                "schemas": ["urn:ietf:params:scim:api:messages:2.0:PatchOp"],
                "Operations": [
                    {"op": "replace", "path": "active", "value": False},
                    {"op": "replace", "path": "name.givenName", "value": "Private"},
                    {"op": "replace", "path": "name.familyName", "value": "Person"},
                    {"op": "replace", "path": "displayName", "value": "Private Person"},
                    {"op": "replace", "path": "timezone", "value": "UTC"},
                    {"op": "replace", "path": "locale", "value": "en-US"},
                ],
            },
        }
        request = prepare_request(operation, base, oauth_cfg)
        self.assertEqual(len(request.json_body["Operations"]), 6)

        refusal_cases = {
            "empty operations": [],
            "unknown path": [{"op": "replace", "path": "title", "value": "owner"}],
            "wrong active type": [{"op": "replace", "path": "active", "value": "false"}],
            "untyped emails": [{"op": "replace", "path": "emails", "value": []}],
            "unknown operation field": [
                {"op": "replace", "path": "active", "value": False, "raw": True}
            ],
            "oversized string": [
                {"op": "replace", "path": "displayName", "value": "x" * 256}
            ],
            "wrong operation": [{"op": "add", "path": "displayName", "value": "Name"}],
            "duplicate path": [
                {"op": "replace", "path": "displayName", "value": "One"},
                {"op": "replace", "path": "displayName", "value": "Two"},
            ],
            "missing paired email": [
                {"op": "replace", "path": "userName", "value": "person@example.com"}
            ],
            "unequal paired email": [
                {"op": "replace", "path": "userName", "value": "one@example.com"},
                {
                    "op": "replace",
                    "path": "emails[primary eq true].value",
                    "value": "two@example.com",
                },
            ],
            "invalid paired email": [
                {"op": "replace", "path": "userName", "value": "not-an-email"},
                {
                    "op": "replace",
                    "path": "emails[primary eq true].value",
                    "value": "not-an-email",
                },
            ],
            "oversized primary email": [
                {
                    "op": "replace",
                    "path": "userName",
                    "value": "x" * 150 + "@example.com",
                },
                {
                    "op": "replace",
                    "path": "emails[primary eq true].value",
                    "value": "x" * 150 + "@example.com",
                },
            ],
        }
        for label, operations in refusal_cases.items():
            with self.subTest(label=label):
                candidate = json.loads(json.dumps(base))
                candidate["body"]["Operations"] = operations
                with self.assertRaises(ValidationError):
                    prepare_request(operation, candidate, oauth_cfg)

        for label, body_change in (
            ("wrong schema identifier", {"schemas": ["wrong"]}),
            ("unknown root field", {"raw": True}),
        ):
            with self.subTest(label=label):
                candidate = json.loads(json.dumps(base))
                candidate["body"].update(body_change)
                with self.assertRaises(ValidationError):
                    prepare_request(operation, candidate, oauth_cfg)

        oversized = json.loads(json.dumps(base))
        oversized["body"]["Operations"] = [
            {"op": "replace", "path": "displayName", "value": str(index)}
            for index in range(9)
        ]
        with self.assertRaises(ValidationError):
            prepare_request(operation, oversized, oauth_cfg)

        paired = json.loads(json.dumps(base))
        paired["body"]["Operations"] = [
            {"op": "replace", "path": "userName", "value": "person@example.com"},
            {
                "op": "replace",
                "path": "emails[primary eq true].value",
                "value": "person@example.com",
            },
        ]
        self.assertIsNotNone(prepare_request(operation, paired, oauth_cfg).json_body)

        missing_lock = json.loads(json.dumps(base))
        missing_lock.pop("headers")
        with self.assertRaisesRegex(ValidationError, "If-Match"):
            prepare_request(operation, missing_lock, oauth_cfg)

    def test_porting_webhook_configuration_is_a_fixed_https_overwrite(self) -> None:
        command = "numbers-v1.create-porting-webhook-configuration"
        notification_values = [
            "PortInWaitingForSignature",
            "PortInInProgress",
            "PortInCompleted",
            "PortInActionRequired",
            "PortInCanceled",
            "PortInPhoneNumberWaitingForSignature",
            "PortInPhoneNumberSubmitted",
            "PortInPhoneNumberPending",
            "PortInPhoneNumberCompleted",
            "PortInPhoneNumberRejected",
            "PortInPhoneNumberCanceled",
            "PortOutPhoneNumberCompleted",
        ]
        request = self.prepare(
            command,
            {
                "body": {
                    "port_in_target_url": "https://hooks.example.com/port-in",
                    "notifications_of": notification_values,
                }
            },
        )
        self.assertEqual(request.json_body["notifications_of"], notification_values)
        empty_filter = self.prepare(
            command,
            {"body": {"port_out_target_url": "https://hooks.example.com/out", "notifications_of": []}},
        )
        self.assertEqual(empty_filter.json_body["notifications_of"], [])

        refusal_bodies = {
            "empty": {},
            "unknown field": {"port_in_target_url": "https://example.com/in", "raw": True},
            "http": {"port_in_target_url": "http://example.com/in"},
            "relative": {"port_in_target_url": "/in"},
            "credentials": {"port_in_target_url": "https://user:pass@example.com/in"},
            "fragment": {"port_in_target_url": "https://example.com/in#secret"},
            "private host": {"port_in_target_url": "https://127.0.0.1/in"},
            "single-label host": {"port_in_target_url": "https://intranet/in"},
            "underscore host": {"port_in_target_url": "https://bad_host.example/in"},
            "space in host": {"port_in_target_url": "https://bad host.example/in"},
            "space in path": {"port_in_target_url": "https://example.com/bad path"},
            "leading hyphen host": {"port_in_target_url": "https://-bad.example/in"},
            "wrong target type": {"port_in_target_url": ["https://example.com/in"]},
            "wrong notifications type": {
                "port_in_target_url": "https://example.com/in",
                "notifications_of": "PortInCompleted",
            },
            "duplicate notification": {
                "port_in_target_url": "https://example.com/in",
                "notifications_of": ["PortInCompleted", "PortInCompleted"],
            },
            "unknown notification": {
                "port_in_target_url": "https://example.com/in",
                "notifications_of": ["PortInExpired"],
            },
        }
        for label, body in refusal_bodies.items():
            with self.subTest(label=label):
                with self.assertRaises(ValidationError):
                    self.prepare(command, {"body": body})

    def test_verify_start_accepts_fixed_fields_and_refuses_unknown_body_fields(self) -> None:
        input_obj = {
            "path": {"ServiceSid": "VA" + "0" * 32},
            "body": {
                "To": "+14155550123",
                "Channel": "sms",
                "RateLimits": json.dumps({"customer": "account-1"}),
            },
        }
        request = self.prepare("verify-v2.create-verification", input_obj)
        self.assertEqual(request.form["Channel"], "sms")
        input_obj["body"]["RawOptions"] = {}
        with self.assertRaisesRegex(ValidationError, "Unknown body fields"):
            self.prepare("verify-v2.create-verification", input_obj)

    def test_studio_flow_and_execution_validate_their_exact_json_strings(self) -> None:
        definition = json.dumps(
            {
                "description": "Safe test flow",
                "initial_state": "Trigger",
                "states": [{"type": "trigger", "name": "Trigger", "transitions": []}],
            }
        )
        flow = self.prepare(
            "studio-v2.create-flow",
            {"body": {"FriendlyName": "Safe test", "Status": "draft", "Definition": definition}},
        )
        self.assertEqual(flow.form["Definition"], definition)
        with self.assertRaisesRegex(
            ValidationError,
            r"body.Definition.states\[0\] does not match any pinned request schema",
        ):
            self.prepare(
                "studio-v2.create-flow",
                {
                    "body": {
                        "FriendlyName": "Safe test",
                        "Status": "draft",
                        "Definition": json.dumps(
                            {"initial_state": "Trigger", "states": [{"name": "Trigger"}]}
                        ),
                    }
                },
            )

        execution = {
            "path": {"FlowSid": "FW" + "0" * 32},
            "body": {
                "To": "+14155550123",
                "From": "+14155550124",
                "Parameters": json.dumps({"customer": {"id": "123"}}),
            },
        }
        self.assertIsNotNone(self.prepare("studio-v2.create-execution", execution).form)
        execution["body"]["Parameters"] = "{broken"
        with self.assertRaisesRegex(ValidationError, "valid JSON"):
            self.prepare("studio-v2.create-execution", execution)

    def test_studio_flow_refuses_unknown_widgets_and_unknown_state_fields(self) -> None:
        base = {
            "body": {
                "FriendlyName": "Safe test",
                "Status": "draft",
                "Definition": json.dumps(
                    {
                        "description": "Safe test flow",
                        "initial_state": "Trigger",
                        "states": [
                            {
                                "type": "not-a-twilio-widget",
                                "name": "Trigger",
                                "properties": {},
                                "transitions": [],
                            }
                        ],
                    }
                ),
            }
        }
        with self.assertRaisesRegex(ValidationError, "does not match any pinned request schema"):
            self.prepare("studio-v2.create-flow", base)

        definition = json.loads(base["body"]["Definition"])
        definition["states"][0]["type"] = "trigger"
        definition["states"][0]["raw"] = {"arbitrary": True}
        base["body"]["Definition"] = json.dumps(definition)
        with self.assertRaisesRegex(
            ValidationError,
            r"body.Definition.states\[0\] does not match any pinned request schema",
        ):
            self.prepare("studio-v2.create-flow", base)

        definition["states"][0].pop("raw")
        definition["states"][0]["type"] = "send-message"
        definition["states"][0]["properties"] = {"from": "+15005550006", "raw": True}
        base["body"]["Definition"] = json.dumps(definition)
        with self.assertRaisesRegex(ValidationError, "does not match any pinned request schema"):
            self.prepare("studio-v2.create-flow", base)

    def test_sync_data_checks_object_shape_and_documented_size(self) -> None:
        base = {
            "path": {"ServiceSid": "IS" + "0" * 32},
            "body": {"Data": json.dumps({"nested": {"value": 1}})},
        }
        self.assertIsNotNone(self.prepare("sync-v1.create-document", base).form)
        base["body"]["Data"] = "[]"
        with self.assertRaisesRegex(ValidationError, "JSON object"):
            self.prepare("sync-v1.create-document", base)
        base["body"]["Data"] = json.dumps({"value": "x" * 17_000})
        with self.assertRaisesRegex(ValidationError, "16384 bytes"):
            self.prepare("sync-v1.create-document", base)

    def test_proxy_session_refuses_undocumented_inline_participants(self) -> None:
        base = {
            "path": {"ServiceSid": "KS" + "0" * 32},
            "body": {"UniqueName": "order-123", "Mode": "message-only"},
        }
        self.assertIsNotNone(self.prepare("proxy-v1.create-session", base).form)
        base["body"]["Participants"] = [{"Identifier": "+14155550123"}]
        with self.assertRaisesRegex(ValidationError, "Unknown body fields: Participants"):
            self.prepare("proxy-v1.create-session", base)

    def test_event_sink_and_subscription_use_fixed_nested_shapes(self) -> None:
        sink = {
            "body": {
                "Description": "Safe webhook",
                "SinkType": "webhook",
                "SinkConfiguration": json.dumps(
                    {"destination": "https://example.com/twilio", "method": "POST"}
                ),
            }
        }
        request = self.prepare("events-v1.create-sink", sink)
        self.assertEqual(request.form["SinkType"], "webhook")
        sink["body"]["SinkType"] = "email"
        with self.assertRaisesRegex(ValidationError, "pinned enum"):
            self.prepare("events-v1.create-sink", sink)
        sink["body"]["SinkType"] = "webhook"
        sink["body"]["SinkConfiguration"] = json.dumps({"unknown": True})
        with self.assertRaisesRegex(ValidationError, "does not match any pinned request schema"):
            self.prepare("events-v1.create-sink", sink)

        subscription = self.prepare(
            "events-v1.create-subscription",
            {
                "body": {
                    "Description": "Voice events",
                    "SinkSid": "DG" + "0" * 32,
                    "Types": [{"type": "com.twilio.voice.insights.call-summary.complete", "schema_version": 1}],
                }
            },
        )
        self.assertEqual(
            subscription.form["Types"],
            ['{"type":"com.twilio.voice.insights.call-summary.complete","schema_version":1}'],
        )

    def test_video_rules_are_structured_and_sender_registration_flexibility_is_scoped(self) -> None:
        room = {
            "body": {
                "Type": "group",
                "RecordingRules": json.dumps([{"type": "include", "kind": "audio"}]),
            }
        }
        self.assertIsNotNone(self.prepare("video-v1.create-room", room).form)
        room["body"]["RecordingRules"] = json.dumps(
            [{"type": "include", "kind": "audio", "raw": "not documented"}]
        )
        with self.assertRaisesRegex(
            ValidationError,
            r"body.RecordingRules\[0\] does not match any pinned request schema",
        ):
            self.prepare("video-v1.create-room", room)

        for invalid_rules in (
            [{"type": "include"}],
            [{"type": "include", "all": True, "kind": "audio"}],
            [
                {"type": "include", "kind": "audio"},
                {"type": "include", "kind": "audio"},
            ],
        ):
            room["body"]["RecordingRules"] = json.dumps(invalid_rules)
            with self.assertRaises(ValidationError):
                self.prepare("video-v1.create-room", room)

        with self.assertRaisesRegex(ValidationError, "does not match any pinned request schema"):
            self.prepare(
                "video-v1.create-composition",
                {"body": {"RoomSid": "RM" + "0" * 32}},
            )

        composition = self.prepare(
            "video-v1.create-composition",
            {
                "body": {
                    "RoomSid": "RM" + "0" * 32,
                    "AudioSources": ["*"],
                }
            },
        )
        self.assertEqual(composition.form["AudioSources"], ["*"])

        hook_cases = (
            (
                "video-v1.create-composition-hook",
                {},
                {"FriendlyName": "Safe hook", "AudioSources": ["*"]},
            ),
            (
                "video-v1.update-composition-hook",
                {"Sid": "HK" + "0" * 32},
                {"FriendlyName": "Safe hook", "AudioSources": ["*"]},
            ),
        )
        for command, path, body in hook_cases:
            with self.subTest(command=command, input="missing composition source"):
                with self.assertRaisesRegex(
                    ValidationError,
                    "does not match any pinned request schema",
                ):
                    self.prepare(
                        command,
                        {"path": path, "body": {"FriendlyName": "Safe hook"}},
                    )
            with self.subTest(command=command, input="audio source"):
                hook = self.prepare(command, {"path": path, "body": body})
                self.assertEqual(hook.form["AudioSources"], ["*"])

        registration = self.prepare(
            "numbers-v1.create-sender-id-registration",
            {
                "body": {
                    "regulationId": "RN" + "0" * 32,
                    "regulationVersion": 1,
                    "friendlyName": "Example registration",
                    "data": {"business": {"legalName": "Example"}},
                }
            },
        )
        self.assertEqual(registration.json_body["data"]["business"]["legalName"], "Example")


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any
from unittest.mock import Mock

TOOL_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOL_ROOT / "src"))


class TestRuntimeBehavior(unittest.TestCase):
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

    def snapshot_payload(
        self,
        *,
        read_command: str,
        cfg: Any,
        read_input: dict[str, Any],
        provider_state: Any,
    ) -> dict[str, Any]:
        raw = json.dumps(read_input, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        return {
            "schema_version": 1,
            "snapshot_binding": {
                "read_command": read_command,
                "account_fingerprint": cfg.fingerprint,
                "input_sha256": hashlib.sha256(raw.encode("utf-8")).hexdigest(),
            },
            "provider_state": provider_state,
        }

    def test_fetch_account_uses_configured_account_sid_and_escapes_paths(self) -> None:
        from twilio_safe_agent_cli.registry import load_registry
        from twilio_safe_agent_cli.runtime import prepare_request

        operation = load_registry().get("api-v2010.fetch-account")
        request = prepare_request(operation, {}, self.cfg)
        self.assertEqual(
            request.url,
            f"https://api.twilio.com/2010-04-01/Accounts/{self.cfg.account_sid}.json",
        )

    def test_form_body_and_query_array_serialization_follow_catalog(self) -> None:
        from twilio_safe_agent_cli.registry import load_registry
        from twilio_safe_agent_cli.runtime import prepare_request

        operation = load_registry().get("api-v2010.create-message")
        request = prepare_request(
            operation,
            {
                "path": {"AccountSid": self.cfg.account_sid},
                "body": {
                    "To": "+15005550006",
                    "Body": "hello",
                    "MediaUrl": ["https://example.com/a.jpg", "https://example.com/b.jpg"],
                },
            },
            self.cfg,
        )
        self.assertEqual(request.content_type, "application/x-www-form-urlencoded")
        self.assertEqual(request.form["To"], "+15005550006")
        self.assertEqual(len(request.form["MediaUrl"]), 2)

    def test_unknown_input_fields_fail_closed(self) -> None:
        from twilio_safe_agent_cli.errors import ValidationError
        from twilio_safe_agent_cli.registry import load_registry
        from twilio_safe_agent_cli.runtime import prepare_request

        operation = load_registry().get("api-v2010.fetch-account")
        with self.assertRaises(ValidationError):
            prepare_request(operation, {"query": {"RawUrl": "https://evil.invalid"}}, self.cfg)

    def test_path_and_query_values_follow_the_pinned_parameter_schemas(self) -> None:
        from twilio_safe_agent_cli.errors import ValidationError
        from twilio_safe_agent_cli.registry import load_registry
        from twilio_safe_agent_cli.runtime import prepare_request

        registry = load_registry()
        with self.assertRaises(ValidationError):
            prepare_request(
                registry.get("api-v2010.fetch-call"),
                {"path": {"Sid": "not-a-call-sid"}},
                self.cfg,
            )
        with self.assertRaises(ValidationError):
            prepare_request(
                registry.get("api-v2010.list-call"),
                {"query": {"Status": "definitely-not-a-call-status"}},
                self.cfg,
            )

    def test_required_query_account_sid_is_auto_scoped(self) -> None:
        from twilio_safe_agent_cli.registry import load_registry
        from twilio_safe_agent_cli.runtime import prepare_request

        operation = load_registry().get("iam-v1.list-get-keys")
        request = prepare_request(operation, {}, self.cfg)
        self.assertIn(("AccountSid", self.cfg.account_sid), request.query)

    def test_one_of_json_body_uses_the_pinned_schema(self) -> None:
        from twilio_safe_agent_cli.registry import load_registry
        from twilio_safe_agent_cli.runtime import prepare_request

        operation = load_registry().get("messaging-v3.create-v3-typing-indicator")
        request = prepare_request(
            operation,
            {
                "body": {
                    "channel": "APPLE",
                    "from": "apple:business",
                    "to": "apple:customer",
                    "event": "START",
                },
            },
            self.cfg,
        )
        self.assertEqual(request.content_type, "application/json")
        self.assertEqual(request.json_body["channel"], "APPLE")

    def test_one_of_json_body_rejects_unknown_top_level_fields(self) -> None:
        from twilio_safe_agent_cli.errors import ValidationError
        from twilio_safe_agent_cli.registry import load_registry
        from twilio_safe_agent_cli.runtime import prepare_request

        operation = load_registry().get("messaging-v3.create-v3-typing-indicator")
        with self.assertRaises(ValidationError):
            prepare_request(
                operation,
                {
                    "body": {
                        "channel": "APPLE",
                        "from": "apple:business",
                        "to": "apple:customer",
                        "rawUrl": "https://evil.invalid",
                    },
                },
                self.cfg,
            )

    def test_safe_read_redacts_stdout_result_and_can_save_protected_full_result(self) -> None:
        from twilio_safe_agent_cli.registry import load_registry
        from twilio_safe_agent_cli.runtime import execute_read

        operation = load_registry().get("api-v2010.fetch-account")
        response = Mock()
        response.status_code = 200
        response.headers = {"Content-Type": "application/json"}
        response.json.return_value = {
            "sid": self.cfg.account_sid,
            "friendly_name": "private project",
            "auth_token": "private-secret",
        }
        response.text = json.dumps(response.json.return_value)
        session = Mock()
        session.request.return_value = response
        with tempfile.TemporaryDirectory() as tmp:
            sensitive_out = Path(tmp) / "full.json"
            result = execute_read(
                operation,
                {},
                self.cfg,
                session=session,
                sensitive_out=sensitive_out,
            )
            self.assertTrue(result["ok"])
            self.assertNotIn("private project", json.dumps(result))
            self.assertNotIn("private-secret", json.dumps(result))
            self.assertEqual(sensitive_out.stat().st_mode & 0o777, 0o600)
            self.assertIn("private project", sensitive_out.read_text(encoding="utf-8"))

    def test_scim_snapshot_keeps_only_version_and_redacts_all_user_data(self) -> None:
        from dataclasses import replace

        from twilio_safe_agent_cli.registry import load_registry
        from twilio_safe_agent_cli.runtime import execute_read

        cfg = replace(
            self.cfg,
            api_key_sid=None,
            api_key_secret=None,
            oauth_access_token="test-oauth-placeholder",
        )
        operation = load_registry().get("iam-organizations.fetch-organization-user")
        private_user = {
            "id": "US" + "0" * 32,
            "userName": "private.person@example.com",
            "displayName": "Private Person",
            "name": {"givenName": "Private", "familyName": "Person"},
            "emails": [{"primary": True, "value": "private.person@example.com"}],
            "meta": {"version": "W/13", "location": "https://example.invalid/private"},
        }
        response = Mock(status_code=200, headers={"Content-Type": "application/json"}, text="{}")
        response.json.return_value = private_user
        session = Mock()
        session.request.return_value = response
        with tempfile.TemporaryDirectory() as tmp:
            snapshot = Path(tmp) / "before.json"
            result = execute_read(
                operation,
                {
                    "path": {
                        "OrganizationSid": "OR" + "0" * 32,
                        "UserSid": "US" + "0" * 32,
                    }
                },
                cfg,
                session=session,
                sensitive_out=snapshot,
            )
            saved = snapshot.read_text(encoding="utf-8")
        saved_payload = json.loads(saved)
        self.assertEqual(saved_payload["provider_state"]["meta"]["version"], "W/13")
        self.assertEqual(
            saved_payload["snapshot_binding"]["read_command"],
            "iam-organizations.fetch-organization-user",
        )
        self.assertEqual(saved_payload["snapshot_binding"]["account_fingerprint"], cfg.fingerprint)
        for private_value in ("Private Person", "private.person@example.com", "example.invalid"):
            self.assertNotIn(private_value, saved)
            self.assertNotIn(private_value, json.dumps(result))
        self.assertEqual(result["data"]["meta"]["version"], "W/13")

    def test_porting_read_and_scim_errors_do_not_expose_private_values(self) -> None:
        from dataclasses import replace

        from twilio_safe_agent_cli.errors import ToolError
        from twilio_safe_agent_cli.registry import load_registry
        from twilio_safe_agent_cli.runtime import execute_read

        registry = load_registry()
        porting = registry.get("numbers-v1.fetch-porting-webhook-configuration-fetch")
        porting_response = Mock(
            status_code=200,
            headers={"Content-Type": "application/json"},
            text="{}",
        )
        porting_response.json.return_value = {
            "port_in_target_url": "https://private.example.com/hooks/customer-secret",
            "port_out_target_url": "https://private.example.com/hooks/other-secret",
        }
        porting_session = Mock()
        porting_session.request.return_value = porting_response
        with tempfile.TemporaryDirectory() as tmp:
            snapshot = Path(tmp) / "porting-before.json"
            porting_result = execute_read(
                porting,
                {},
                self.cfg,
                session=porting_session,
                sensitive_out=snapshot,
            )
            protected = json.loads(snapshot.read_text(encoding="utf-8"))
        self.assertNotIn("customer-secret", json.dumps(porting_result))
        self.assertNotIn("other-secret", json.dumps(porting_result))
        self.assertEqual(
            protected["snapshot_binding"]["read_command"],
            "numbers-v1.fetch-porting-webhook-configuration-fetch",
        )
        self.assertIn("customer-secret", protected["provider_state"]["port_in_target_url"])

        oauth_cfg = replace(
            self.cfg,
            api_key_sid=None,
            api_key_secret=None,
            oauth_access_token="test-oauth-placeholder",
        )
        scim = registry.get("iam-organizations.fetch-organization-user")
        scim_response = Mock(
            status_code=400,
            headers={"Content-Type": "application/scim+json"},
            text="{}",
        )
        scim_response.json.return_value = {
            "detail": "Private Person private.person@example.com is invalid"
        }
        scim_session = Mock()
        scim_session.request.return_value = scim_response
        with self.assertRaises(ToolError) as context:
            execute_read(
                scim,
                {
                    "path": {
                        "OrganizationSid": "OR" + "0" * 32,
                        "UserSid": "US" + "0" * 32,
                    }
                },
                oauth_cfg,
                session=scim_session,
            )
        self.assertNotIn("Private Person", str(context.exception))
        self.assertNotIn("private.person@example.com", str(context.exception))

    def test_failed_porting_write_redacts_provider_detail_in_receipt(self) -> None:
        from twilio_safe_agent_cli.errors import ToolError
        from twilio_safe_agent_cli.redaction import REDACTED, write_protected_json
        from twilio_safe_agent_cli.registry import load_registry
        from twilio_safe_agent_cli.runtime import execute_operation

        registry = load_registry()
        operation = registry.get("numbers-v1.create-porting-webhook-configuration")
        input_obj = {
            "body": {"port_in_target_url": "https://hooks.example.com/customer-secret"}
        }
        failure = Mock(
            status_code=400,
            headers={"Content-Type": "application/json"},
            text="{}",
        )
        failure.json.return_value = {
            "detail": "Webhook https://hooks.example.com/customer-secret was rejected"
        }
        session = Mock()
        session.request.return_value = failure
        with tempfile.TemporaryDirectory() as tmp:
            snapshot = Path(tmp) / "before.json"
            plan = Path(tmp) / "plan.json"
            receipt = Path(tmp) / "receipt.json"
            write_protected_json(
                snapshot,
                self.snapshot_payload(
                    read_command="numbers-v1.fetch-porting-webhook-configuration-fetch",
                    cfg=self.cfg,
                    read_input={},
                    provider_state={
                        "port_in_target_url": "https://hooks.example.com/previous-secret"
                    },
                ),
            )
            execute_operation(
                operation,
                input_obj,
                self.cfg,
                registry=registry,
                tool_version="0.1.0",
                apply=False,
                yes=False,
                plan_out=str(plan),
                plan_in=None,
                receipt_out=None,
                snapshot_in=str(snapshot),
                acknowledgements={},
                target_count=None,
                sensitive_out=None,
                session=session,
            )
            with self.assertRaises(ToolError) as context:
                execute_operation(
                    operation,
                    input_obj,
                    self.cfg,
                    registry=registry,
                    tool_version="0.1.0",
                    apply=True,
                    yes=True,
                    plan_out=None,
                    plan_in=str(plan),
                    receipt_out=str(receipt),
                    snapshot_in=str(snapshot),
                    acknowledgements={
                        "ack_identity": True,
                        "ack_preview": True,
                        "ack_production": True,
                    },
                    target_count=None,
                    sensitive_out=None,
                    session=session,
                )
            saved_receipt = json.loads(receipt.read_text(encoding="utf-8"))
        self.assertEqual(saved_receipt["attempt"]["status"], "failed")
        self.assertEqual(saved_receipt["response"], {"provider_error": REDACTED})
        self.assertNotIn("customer-secret", json.dumps(saved_receipt))
        self.assertNotIn("customer-secret", str(context.exception))
        self.assertEqual(session.request.call_count, 1)

    def test_scim_patch_requires_current_snapshot_version_before_http(self) -> None:
        from dataclasses import replace

        from twilio_safe_agent_cli.errors import SafetyError
        from twilio_safe_agent_cli.redaction import write_protected_json
        from twilio_safe_agent_cli.registry import load_registry
        from twilio_safe_agent_cli.runtime import execute_operation

        cfg = replace(
            self.cfg,
            api_key_sid=None,
            api_key_secret=None,
            oauth_access_token="test-oauth-placeholder",
        )
        registry = load_registry()
        operation = registry.get("iam-organizations.patch-organization-user")
        input_obj = {
            "path": {"OrganizationSid": "OR" + "0" * 32, "UserSid": "US" + "0" * 32},
            "headers": {"If-Match": "W/13"},
            "content_type": "application/scim+json",
            "body": {
                "schemas": ["urn:ietf:params:scim:api:messages:2.0:PatchOp"],
                "Operations": [{"op": "replace", "path": "active", "value": False}],
            },
        }
        session = Mock()
        with self.assertRaisesRegex(SafetyError, "requires --snapshot-in"):
            execute_operation(
                operation,
                input_obj,
                cfg,
                registry=registry,
                tool_version="0.1.0",
                apply=False,
                yes=False,
                plan_out=None,
                plan_in=None,
                receipt_out=None,
                snapshot_in=None,
                acknowledgements={},
                target_count=None,
                sensitive_out=None,
                session=session,
            )
        with tempfile.TemporaryDirectory() as tmp:
            stale = Path(tmp) / "stale.json"
            read_input = {
                "path": {
                    "OrganizationSid": "OR" + "0" * 32,
                    "UserSid": "US" + "0" * 32,
                }
            }
            write_protected_json(
                stale,
                self.snapshot_payload(
                    read_command="iam-organizations.fetch-organization-user",
                    cfg=cfg,
                    read_input=read_input,
                    provider_state={"meta": {"version": "W/12"}, "user": "<REDACTED>"},
                ),
            )
            with self.assertRaisesRegex(SafetyError, "If-Match"):
                execute_operation(
                    operation,
                    input_obj,
                    cfg,
                    registry=registry,
                    tool_version="0.1.0",
                    apply=False,
                    yes=False,
                    plan_out=None,
                    plan_in=None,
                    receipt_out=None,
                    snapshot_in=str(stale),
                    acknowledgements={},
                    target_count=None,
                    sensitive_out=None,
                    session=session,
                )
            current = Path(tmp) / "current.json"
            current_payload = self.snapshot_payload(
                read_command="iam-organizations.fetch-organization-user",
                cfg=cfg,
                read_input=read_input,
                provider_state={"meta": {"version": "W/13"}, "user": "<REDACTED>"},
            )
            arbitrary = Path(tmp) / "arbitrary.json"
            write_protected_json(arbitrary, {"meta": {"version": "W/13"}})
            with self.assertRaisesRegex(SafetyError, "provenance"):
                execute_operation(
                    operation,
                    input_obj,
                    cfg,
                    registry=registry,
                    tool_version="0.1.0",
                    apply=False,
                    yes=False,
                    plan_out=None,
                    plan_in=None,
                    receipt_out=None,
                    snapshot_in=str(arbitrary),
                    acknowledgements={},
                    target_count=None,
                    sensitive_out=None,
                    session=session,
                )
            wrong_account = Path(tmp) / "wrong-account.json"
            wrong_account_payload = json.loads(json.dumps(current_payload))
            wrong_account_payload["snapshot_binding"]["account_fingerprint"] = "0" * 64
            write_protected_json(wrong_account, wrong_account_payload)
            with self.assertRaisesRegex(SafetyError, "account, or target"):
                execute_operation(
                    operation,
                    input_obj,
                    cfg,
                    registry=registry,
                    tool_version="0.1.0",
                    apply=False,
                    yes=False,
                    plan_out=None,
                    plan_in=None,
                    receipt_out=None,
                    snapshot_in=str(wrong_account),
                    acknowledgements={},
                    target_count=None,
                    sensitive_out=None,
                    session=session,
                )
            wrong_target = Path(tmp) / "wrong-target.json"
            wrong_target_payload = json.loads(json.dumps(current_payload))
            wrong_target_payload["snapshot_binding"]["input_sha256"] = "0" * 64
            write_protected_json(wrong_target, wrong_target_payload)
            with self.assertRaisesRegex(SafetyError, "account, or target"):
                execute_operation(
                    operation,
                    input_obj,
                    cfg,
                    registry=registry,
                    tool_version="0.1.0",
                    apply=False,
                    yes=False,
                    plan_out=None,
                    plan_in=None,
                    receipt_out=None,
                    snapshot_in=str(wrong_target),
                    acknowledgements={},
                    target_count=None,
                    sensitive_out=None,
                    session=session,
                )
            write_protected_json(current, current_payload)
            result = execute_operation(
                operation,
                input_obj,
                cfg,
                registry=registry,
                tool_version="0.1.0",
                apply=False,
                yes=False,
                plan_out=None,
                plan_in=None,
                receipt_out=None,
                snapshot_in=str(current),
                acknowledgements={},
                target_count=None,
                sensitive_out=None,
                session=session,
            )
        self.assertTrue(result["dry_run"])
        self.assertEqual(result["plan"]["binding"]["snapshot_sha256"], result["plan"]["snapshot"]["file"]["sha256"])
        session.request.assert_not_called()

    def test_porting_apply_requires_snapshot_and_refetches_after_overwrite(self) -> None:
        from twilio_safe_agent_cli.errors import SafetyError
        from twilio_safe_agent_cli.redaction import write_protected_json
        from twilio_safe_agent_cli.registry import load_registry
        from twilio_safe_agent_cli.runtime import execute_operation

        registry = load_registry()
        operation = registry.get("numbers-v1.create-porting-webhook-configuration")
        input_obj = {"body": {"port_in_target_url": "https://hooks.example.com/in"}}
        session = Mock()
        with self.assertRaisesRegex(SafetyError, "requires --snapshot-in"):
            execute_operation(
                operation,
                input_obj,
                self.cfg,
                registry=registry,
                tool_version="0.1.0",
                apply=False,
                yes=False,
                plan_out=None,
                plan_in=None,
                receipt_out=None,
                snapshot_in=None,
                acknowledgements={},
                target_count=None,
                sensitive_out=None,
                session=session,
            )
        first = Mock(status_code=201, headers={"Content-Type": "application/json"}, text="{}")
        first.json.return_value = {"port_in_target_url": "https://hooks.example.com/in"}
        second = Mock(status_code=200, headers={"Content-Type": "application/json"}, text="{}")
        second.json.return_value = {"port_in_target_url": "https://hooks.example.com/in"}
        session.request.side_effect = [first, second]
        with tempfile.TemporaryDirectory() as tmp:
            snapshot = Path(tmp) / "before.json"
            plan = Path(tmp) / "plan.json"
            receipt = Path(tmp) / "receipt.json"
            wrong_snapshot = Path(tmp) / "wrong-before.json"
            write_protected_json(
                wrong_snapshot,
                self.snapshot_payload(
                    read_command="iam-organizations.fetch-organization-user",
                    cfg=self.cfg,
                    read_input={},
                    provider_state={"port_in_target_url": "https://old.example.com/in"},
                ),
            )
            with self.assertRaisesRegex(SafetyError, "paired GET, account, or target"):
                execute_operation(
                    operation,
                    input_obj,
                    self.cfg,
                    registry=registry,
                    tool_version="0.1.0",
                    apply=False,
                    yes=False,
                    plan_out=None,
                    plan_in=None,
                    receipt_out=None,
                    snapshot_in=str(wrong_snapshot),
                    acknowledgements={},
                    target_count=None,
                    sensitive_out=None,
                    session=session,
                )
            write_protected_json(
                snapshot,
                self.snapshot_payload(
                    read_command="numbers-v1.fetch-porting-webhook-configuration-fetch",
                    cfg=self.cfg,
                    read_input={},
                    provider_state={"port_in_target_url": "https://old.example.com/in"},
                ),
            )
            execute_operation(
                operation,
                input_obj,
                self.cfg,
                registry=registry,
                tool_version="0.1.0",
                apply=False,
                yes=False,
                plan_out=str(plan),
                plan_in=None,
                receipt_out=None,
                snapshot_in=str(snapshot),
                acknowledgements={},
                target_count=None,
                sensitive_out=None,
                session=session,
            )
            result = execute_operation(
                operation,
                input_obj,
                self.cfg,
                registry=registry,
                tool_version="0.1.0",
                apply=True,
                yes=True,
                plan_out=None,
                plan_in=str(plan),
                receipt_out=str(receipt),
                snapshot_in=str(snapshot),
                acknowledgements={
                    "ack_identity": True,
                    "ack_preview": True,
                    "ack_production": True,
                },
                target_count=None,
                sensitive_out=None,
                session=session,
            )
        self.assertEqual(session.request.call_count, 2)
        self.assertEqual(session.request.call_args_list[0].args[0], "POST")
        self.assertEqual(session.request.call_args_list[1].args[0], "GET")
        self.assertEqual(result["receipt"]["verification"]["result"], "refetched")

    def test_scim_patch_applies_if_match_once_and_refetches_user(self) -> None:
        from dataclasses import replace

        from twilio_safe_agent_cli.redaction import write_protected_json
        from twilio_safe_agent_cli.registry import load_registry
        from twilio_safe_agent_cli.runtime import execute_operation

        cfg = replace(
            self.cfg,
            api_key_sid=None,
            api_key_secret=None,
            oauth_access_token="test-oauth-placeholder",
        )
        registry = load_registry()
        operation = registry.get("iam-organizations.patch-organization-user")
        input_obj = {
            "path": {"OrganizationSid": "OR" + "0" * 32, "UserSid": "US" + "0" * 32},
            "headers": {"If-Match": "W/13"},
            "content_type": "application/scim+json",
            "body": {
                "schemas": ["urn:ietf:params:scim:api:messages:2.0:PatchOp"],
                "Operations": [{"op": "replace", "path": "active", "value": False}],
            },
        }
        patch_response = Mock(
            status_code=200,
            headers={"Content-Type": "application/scim+json"},
            text="{}",
        )
        patch_response.json.return_value = {
            "active": False,
            "displayName": "Private Person",
            "userName": "private.person@example.com",
            "meta": {"version": "W/14"},
        }
        get_response = Mock(
            status_code=200,
            headers={"Content-Type": "application/scim+json"},
            text="{}",
        )
        get_response.json.return_value = {"active": False, "meta": {"version": "W/14"}}
        session = Mock()
        session.request.side_effect = [patch_response, get_response]
        with tempfile.TemporaryDirectory() as tmp:
            snapshot = Path(tmp) / "before.json"
            plan = Path(tmp) / "plan.json"
            write_protected_json(
                snapshot,
                self.snapshot_payload(
                    read_command="iam-organizations.fetch-organization-user",
                    cfg=cfg,
                    read_input={
                        "path": {
                            "OrganizationSid": "OR" + "0" * 32,
                            "UserSid": "US" + "0" * 32,
                        }
                    },
                    provider_state={"meta": {"version": "W/13"}, "user": "<REDACTED>"},
                ),
            )
            execute_operation(
                operation,
                input_obj,
                cfg,
                registry=registry,
                tool_version="0.1.0",
                apply=False,
                yes=False,
                plan_out=str(plan),
                plan_in=None,
                receipt_out=None,
                snapshot_in=str(snapshot),
                acknowledgements={},
                target_count=None,
                sensitive_out=None,
                session=session,
            )
            result = execute_operation(
                operation,
                input_obj,
                cfg,
                registry=registry,
                tool_version="0.1.0",
                apply=True,
                yes=True,
                plan_out=None,
                plan_in=str(plan),
                receipt_out=str(Path(tmp) / "receipt.json"),
                snapshot_in=str(snapshot),
                acknowledgements={
                    "ack_auth": True,
                    "ack_identity": True,
                    "ack_preview": True,
                    "ack_production": True,
                },
                target_count=None,
                sensitive_out=None,
                session=session,
            )
        self.assertEqual([call.args[0] for call in session.request.call_args_list], ["PATCH", "GET"])
        self.assertEqual(session.request.call_args_list[0].kwargs["headers"]["If-Match"], "W/13")
        self.assertNotIn("If-Match", session.request.call_args_list[1].kwargs["headers"])
        self.assertEqual(result["receipt"]["verification"]["result"], "refetched")
        self.assertNotIn("Private Person", json.dumps(result))
        self.assertNotIn("private.person@example.com", json.dumps(result))

    def test_non_json_provider_text_is_not_printed_as_safe_output(self) -> None:
        from twilio_safe_agent_cli.registry import load_registry
        from twilio_safe_agent_cli.runtime import execute_read

        operation = load_registry().get("api-v2010.fetch-account")
        response = Mock(status_code=200, headers={})
        response.json.side_effect = ValueError("not json")
        response.text = "private transcript from a provider"
        session = Mock()
        session.request.return_value = response
        result = execute_read(operation, {}, self.cfg, session=session)
        self.assertNotIn("private transcript", json.dumps(result))

    def test_non_idempotent_write_is_never_retried(self) -> None:
        from twilio_safe_agent_cli.http import send_request
        from twilio_safe_agent_cli.registry import load_registry
        from twilio_safe_agent_cli.runtime import prepare_request

        operation = load_registry().get("api-v2010.create-message")
        request = prepare_request(
            operation,
            {"body": {"To": "+15005550006", "Body": "hello"}},
            self.cfg,
        )
        response = Mock(status_code=500, headers={"Content-Type": "application/json"}, text="{}")
        response.json.return_value = {"message": "temporary"}
        session = Mock()
        session.request.return_value = response
        send_request(request, session=session, timeout_s=30, retry_safe=False)
        self.assertEqual(session.request.call_count, 1)

    def test_dry_run_never_calls_the_provider(self) -> None:
        from twilio_safe_agent_cli.registry import load_registry
        from twilio_safe_agent_cli.runtime import execute_operation

        registry = load_registry()
        operation = registry.get("api-v2010.create-message")
        session = Mock()
        result = execute_operation(
            operation,
            {"body": {"To": "+15005550006", "Body": "hello"}},
            self.cfg,
            registry=registry,
            tool_version="0.1.0",
            apply=False,
            yes=False,
            plan_out=None,
            plan_in=None,
            receipt_out=None,
            snapshot_in=None,
            acknowledgements={},
            target_count=None,
            sensitive_out=None,
            session=session,
        )
        self.assertTrue(result["dry_run"])
        session.request.assert_not_called()

    def test_dry_run_refuses_input_outside_the_fixed_request_contract(self) -> None:
        from twilio_safe_agent_cli.errors import ValidationError
        from twilio_safe_agent_cli.registry import load_registry
        from twilio_safe_agent_cli.runtime import execute_operation

        registry = load_registry()
        operation = registry.get("api-v2010.create-message")
        session = Mock()
        with self.assertRaises(ValidationError):
            execute_operation(
                operation,
                {"body": {"To": "+15005550006", "CompletelyUndeclared": "anything"}},
                self.cfg,
                registry=registry,
                tool_version="0.1.0",
                apply=False,
                yes=False,
                plan_out=None,
                plan_in=None,
                receipt_out=None,
                snapshot_in=None,
                acknowledgements={},
                target_count=None,
                sensitive_out=None,
                session=session,
            )
        session.request.assert_not_called()

    def test_unwritable_receipt_destination_refuses_before_http(self) -> None:
        from twilio_safe_agent_cli.registry import load_registry
        from twilio_safe_agent_cli.runtime import execute_operation

        registry = load_registry()
        operation = registry.get("api-v2010.create-message")
        input_obj = {"body": {"To": "+15005550006", "Body": "hello"}}
        session = Mock()
        with tempfile.TemporaryDirectory() as tmp:
            plan_path = Path(tmp) / "plan.json"
            execute_operation(
                operation,
                input_obj,
                self.cfg,
                registry=registry,
                tool_version="0.1.0",
                apply=False,
                yes=False,
                plan_out=str(plan_path),
                plan_in=None,
                receipt_out=None,
                snapshot_in=None,
                acknowledgements={},
                target_count=None,
                sensitive_out=None,
                session=session,
            )
            with self.assertRaises(OSError):
                execute_operation(
                    operation,
                    input_obj,
                    self.cfg,
                    registry=registry,
                    tool_version="0.1.0",
                    apply=True,
                    yes=True,
                    plan_out=None,
                    plan_in=str(plan_path),
                    receipt_out=tmp,
                    snapshot_in=None,
                    acknowledgements={
                        "ack_contact": True,
                        "ack_spend": True,
                        "ack_no_snapshot": True,
                    },
                    target_count=None,
                    sensitive_out=None,
                    session=session,
                )
        session.request.assert_not_called()

    def test_existing_receipt_destination_refuses_before_http(self) -> None:
        from twilio_safe_agent_cli.registry import load_registry
        from twilio_safe_agent_cli.runtime import execute_operation

        registry = load_registry()
        operation = registry.get("api-v2010.create-message")
        input_obj = {"body": {"To": "+15005550006", "Body": "hello"}}
        session = Mock()
        with tempfile.TemporaryDirectory() as tmp:
            plan_path = Path(tmp) / "plan.json"
            receipt_path = Path(tmp) / "receipt.json"
            execute_operation(
                operation,
                input_obj,
                self.cfg,
                registry=registry,
                tool_version="0.1.0",
                apply=False,
                yes=False,
                plan_out=str(plan_path),
                plan_in=None,
                receipt_out=None,
                snapshot_in=None,
                acknowledgements={},
                target_count=None,
                sensitive_out=None,
                session=session,
            )
            receipt_path.write_text("old receipt", encoding="utf-8")
            with self.assertRaises(FileExistsError):
                execute_operation(
                    operation,
                    input_obj,
                    self.cfg,
                    registry=registry,
                    tool_version="0.1.0",
                    apply=True,
                    yes=True,
                    plan_out=None,
                    plan_in=str(plan_path),
                    receipt_out=str(receipt_path),
                    snapshot_in=None,
                    acknowledgements={
                        "ack_contact": True,
                        "ack_spend": True,
                        "ack_no_snapshot": True,
                    },
                    target_count=None,
                    sensitive_out=None,
                    session=session,
                )
            self.assertEqual(receipt_path.read_text(encoding="utf-8"), "old receipt")
        session.request.assert_not_called()

    def test_failed_write_response_is_saved_in_protected_receipt(self) -> None:
        from twilio_safe_agent_cli.errors import ToolError
        from twilio_safe_agent_cli.registry import load_registry
        from twilio_safe_agent_cli.runtime import execute_operation

        registry = load_registry()
        operation = registry.get("api-v2010.create-message")
        input_obj = {"body": {"To": "+15005550006", "Body": "hello"}}
        response = Mock(status_code=500, headers={"Content-Type": "application/json"}, text="{}")
        response.json.return_value = {"message": "provider rejected request"}
        session = Mock()
        session.request.return_value = response
        with tempfile.TemporaryDirectory() as tmp:
            plan_path = Path(tmp) / "plan.json"
            receipt_path = Path(tmp) / "receipt.json"
            execute_operation(
                operation,
                input_obj,
                self.cfg,
                registry=registry,
                tool_version="0.1.0",
                apply=False,
                yes=False,
                plan_out=str(plan_path),
                plan_in=None,
                receipt_out=None,
                snapshot_in=None,
                acknowledgements={},
                target_count=None,
                sensitive_out=None,
                session=session,
            )
            with self.assertRaises(ToolError):
                execute_operation(
                    operation,
                    input_obj,
                    self.cfg,
                    registry=registry,
                    tool_version="0.1.0",
                    apply=True,
                    yes=True,
                    plan_out=None,
                    plan_in=str(plan_path),
                    receipt_out=str(receipt_path),
                    snapshot_in=None,
                    acknowledgements={
                        "ack_contact": True,
                        "ack_spend": True,
                        "ack_no_snapshot": True,
                    },
                    target_count=None,
                    sensitive_out=None,
                    session=session,
                )
            receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
            self.assertEqual(receipt["attempt"]["status"], "failed")
            self.assertEqual(receipt["http_status"], 500)
            self.assertEqual(receipt_path.stat().st_mode & 0o777, 0o600)

    def test_write_exception_is_saved_as_uncertain_attempt(self) -> None:
        from twilio_safe_agent_cli.errors import ToolError
        from twilio_safe_agent_cli.registry import load_registry
        from twilio_safe_agent_cli.runtime import execute_operation

        registry = load_registry()
        operation = registry.get("api-v2010.create-message")
        input_obj = {"body": {"To": "+15005550006", "Body": "hello"}}
        session = Mock()
        session.request.side_effect = TimeoutError("connection outcome unknown")
        with tempfile.TemporaryDirectory() as tmp:
            plan_path = Path(tmp) / "plan.json"
            receipt_path = Path(tmp) / "receipt.json"
            execute_operation(
                operation,
                input_obj,
                self.cfg,
                registry=registry,
                tool_version="0.1.0",
                apply=False,
                yes=False,
                plan_out=str(plan_path),
                plan_in=None,
                receipt_out=None,
                snapshot_in=None,
                acknowledgements={},
                target_count=None,
                sensitive_out=None,
                session=session,
            )
            with self.assertRaises(ToolError):
                execute_operation(
                    operation,
                    input_obj,
                    self.cfg,
                    registry=registry,
                    tool_version="0.1.0",
                    apply=True,
                    yes=True,
                    plan_out=None,
                    plan_in=str(plan_path),
                    receipt_out=str(receipt_path),
                    snapshot_in=None,
                    acknowledgements={
                        "ack_contact": True,
                        "ack_spend": True,
                        "ack_no_snapshot": True,
                    },
                    target_count=None,
                    sensitive_out=None,
                    session=session,
                )
            receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
            self.assertEqual(receipt["attempt"]["status"], "uncertain")
            self.assertFalse(receipt["attempt"]["provider_response_received"])
            self.assertEqual(receipt["attempt"]["error_type"], "TimeoutError")

    def test_update_refetch_verification_drops_the_write_body(self) -> None:
        from twilio_safe_agent_cli.registry import load_registry
        from twilio_safe_agent_cli.runtime import execute_operation

        registry = load_registry()
        operation = registry.get("api-v2010.update-account")
        input_obj = {"path": {"Sid": self.cfg.account_sid}, "body": {"FriendlyName": "new"}}
        first = Mock(status_code=200, headers={"Content-Type": "application/json"}, text="{}")
        first.json.return_value = {"sid": self.cfg.account_sid, "friendly_name": "new"}
        second = Mock(status_code=200, headers={"Content-Type": "application/json"}, text="{}")
        second.json.return_value = {"sid": self.cfg.account_sid, "friendly_name": "new"}
        session = Mock()
        session.request.side_effect = [first, second]
        with tempfile.TemporaryDirectory() as tmp:
            plan_path = Path(tmp) / "plan.json"
            dry_run = execute_operation(
                operation,
                input_obj,
                self.cfg,
                registry=registry,
                tool_version="0.1.0",
                apply=False,
                yes=False,
                plan_out=str(plan_path),
                plan_in=None,
                receipt_out=None,
                snapshot_in=None,
                acknowledgements={},
                target_count=None,
                sensitive_out=None,
                session=session,
            )
            self.assertTrue(dry_run["dry_run"])
            result = execute_operation(
                operation,
                input_obj,
                self.cfg,
                registry=registry,
                tool_version="0.1.0",
                apply=True,
                yes=True,
                plan_out=None,
                plan_in=str(plan_path),
                receipt_out=str(Path(tmp) / "receipt.json"),
                snapshot_in=None,
                acknowledgements={"ack_no_snapshot": True},
                target_count=None,
                sensitive_out=None,
                session=session,
            )
        self.assertEqual(session.request.call_count, 2)
        self.assertEqual(result["receipt"]["attempt"]["status"], "succeeded")
        self.assertTrue(result["receipt"]["verification"]["performed"])
        self.assertEqual(result["receipt"]["verification"]["result"], "refetched")

    def test_apply_requires_a_protected_plan_and_saved_receipt_before_http(self) -> None:
        from twilio_safe_agent_cli.errors import SafetyError
        from twilio_safe_agent_cli.registry import load_registry
        from twilio_safe_agent_cli.runtime import execute_operation

        registry = load_registry()
        operation = registry.get("api-v2010.create-message")
        input_obj = {"body": {"To": "+15005550006", "Body": "hello"}}
        session = Mock()
        with tempfile.TemporaryDirectory() as tmp:
            plan_path = Path(tmp) / "plan.json"
            receipt_path = Path(tmp) / "receipt.json"
            execute_operation(
                operation,
                input_obj,
                self.cfg,
                registry=registry,
                tool_version="0.1.0",
                apply=False,
                yes=False,
                plan_out=str(plan_path),
                plan_in=None,
                receipt_out=None,
                snapshot_in=None,
                acknowledgements={},
                target_count=None,
                sensitive_out=None,
                session=session,
            )
            with self.assertRaises(SafetyError):
                execute_operation(
                    operation,
                    input_obj,
                    self.cfg,
                    registry=registry,
                    tool_version="0.1.0",
                    apply=True,
                    yes=True,
                    plan_out=None,
                    plan_in=str(plan_path),
                    receipt_out=None,
                    snapshot_in=None,
                    acknowledgements={
                        "ack_contact": True,
                        "ack_spend": True,
                        "ack_no_snapshot": True,
                    },
                    target_count=None,
                    sensitive_out=None,
                    session=session,
                )
            plan_path.chmod(0o644)
            with self.assertRaises(SafetyError):
                execute_operation(
                    operation,
                    input_obj,
                    self.cfg,
                    registry=registry,
                    tool_version="0.1.0",
                    apply=True,
                    yes=True,
                    plan_out=None,
                    plan_in=str(plan_path),
                    receipt_out=str(receipt_path),
                    snapshot_in=None,
                    acknowledgements={
                        "ack_contact": True,
                        "ack_spend": True,
                        "ack_no_snapshot": True,
                    },
                    target_count=None,
                    sensitive_out=None,
                    session=session,
                )
        session.request.assert_not_called()


if __name__ == "__main__":
    unittest.main()

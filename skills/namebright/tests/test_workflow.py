from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from collections import deque
from pathlib import Path
from typing import Any
from unittest.mock import patch

from namebright_safe_cli.audit_log import AuditLogger
from namebright_safe_cli.client import NameBrightClient
from namebright_safe_cli.config import Config
from namebright_safe_cli.errors import SafetyError, ValidationError
from namebright_safe_cli.operations import OPERATIONS, OperationSpec, get_operation
from namebright_safe_cli.runs import build_deterministic_summary, write_summary_md
from namebright_safe_cli.workflow import apply_plan, create_plan


class FakeResponse:
    def __init__(self, payload: Any):
        self.payload = payload
        blob = json.dumps(
            payload,
            sort_keys=True,
            ensure_ascii=False,
            separators=(",", ":"),
        )
        self.snapshot_sha256 = hashlib.sha256(blob.encode("utf-8")).hexdigest()


class FakeHttpResponse:
    def __init__(self, payload: Any):
        self.status_code = 200
        self.headers: dict[str, str] = {}
        self.url = "https://api.namebright.com/rest/test"
        self.content = json.dumps(payload).encode("utf-8")
        self.text = self.content.decode("utf-8")


class FakeHttpSession:
    def __init__(self, responses: list[FakeHttpResponse]):
        self.responses = deque(responses)
        self.calls: list[dict[str, Any]] = []

    def request(self, **kwargs: Any) -> FakeHttpResponse:
        self.calls.append(dict(kwargs))
        if not self.responses:
            raise RuntimeError("No fake response remains")
        return self.responses.popleft()


class FakeClient:
    def __init__(
        self,
        *,
        fail_refs: set[tuple[str, str]] | None = None,
        availability: dict[str, Any] | None = None,
        account_show: dict[str, Any] | None = None,
        domains_get: dict[str, Any] | None = None,
        defaults: dict[str, Any] | None = None,
        write_overrides: dict[tuple[str, str], Any] | None = None,
    ) -> None:
        self.calls: list[tuple[str, str, dict[str, Any]]] = []
        self.fail_refs = fail_refs or set()
        self.availability = availability or {
            "Status": "Available",
            "AvailableForRegistration": "true",
            "UnitPrice": 10,
            "PromotionPrice": 8,
        }
        self.account_show = account_show or {
            "AccountBalance": "9.99",
            "FundedBalance": "25",
            "NonRefundable": "True",
        }
        self.domains_get = domains_get or {"DomainName": "example.com", "Status": "ok"}
        self.defaults = defaults or {}
        self.write_overrides = write_overrides or {}

    def execute_operation(self, spec: OperationSpec, values: dict[str, Any] | None = None):
        values = dict(values or {})
        self.calls.append((spec.family, spec.command, values))

        if (spec.family, spec.command) in self.fail_refs:
            raise RuntimeError("forced failure")
        if (spec.family, spec.command) in self.write_overrides:
            return FakeResponse(self.write_overrides[(spec.family, spec.command)])

        if spec.family == "purchase" and spec.command == "purchase availability":
            return FakeResponse(dict(self.availability))
        if spec.family == "account" and spec.command == "account show":
            return FakeResponse(dict(self.account_show))
        if spec.family == "domains" and spec.command == "domains get":
            return FakeResponse(dict(self.domains_get))

        if "ok" in self.defaults:
            return FakeResponse(self.defaults)

        return FakeResponse({"ok": True, "family": spec.family, "command": spec.command})


class WorkflowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.write_specs = [op for op in OPERATIONS if op.write_capable]

    def _write_acks(self, spec: OperationSpec) -> dict[str, bool]:
        required = set(spec.required_acks)
        if spec.no_snapshot:
            required.add("ack_no_snapshot")
        if spec.external_message:
            required.add("ack_external_message")
        return {name: True for name in required}

    def _secret_values(self, spec: OperationSpec) -> dict[str, str]:
        return {field.api_name: f"secret-{field.api_name}" for field in spec.fields if field.kind == "secret_file"}

    def _synthetic_values(self, spec: OperationSpec) -> dict[str, Any]:
        values: dict[str, Any] = {}
        for field in spec.fields:
            if field.source != "cli":
                continue
            if field.kind == "secret_file":
                continue
            if field.api_name in {"DomainName", "domain"}:
                values[field.api_name] = "example.com"
            elif field.api_name in {"Email", "EmailAddress", "PhoneNumber"}:
                values[field.api_name] = "ops@example.com"
            elif field.api_name == "PhoneNumberVerificationMethod":
                values[field.api_name] = "Sms"
            elif field.kind == "int":
                values[field.api_name] = 2
            elif field.kind == "bool":
                values[field.api_name] = True
            elif field.choices:
                values[field.api_name] = field.choices[0]
            else:
                values[field.api_name] = "x"

        if "Years" in values:
            values["Years"] = 2
        if "domain" in values and "DomainName" not in values:
            values["domain"] = "example.com"

        return values

    def test_all_write_specs_have_plan_and_receipt(self) -> None:
        self.assertEqual(len(self.write_specs), 37)
        for spec in self.write_specs:
            values = self._synthetic_values(spec)
            with self.subTest(spec=f"{spec.family}:{spec.command}"):
                with tempfile.TemporaryDirectory() as d:
                    p = Path(d)
                    plan_path = p / "plan.json"
                    receipt_path = p / "receipt.json"
                    client_plan = FakeClient()

                    plan = create_plan(spec, values, plan_out=str(plan_path), client=client_plan, tool_version="0.1.0")
                    self.assertTrue(plan_path.exists())
                    self.assertEqual(plan_path.stat().st_mode & 0o777, 0o600)
                    self.assertEqual(plan["tool"], "namebright-safe-cli")
                    self.assertEqual(plan["tool_version"], "0.1.0")
                    if spec.family == "contacts":
                        self.assertEqual(
                            plan["values"]["domain"],
                            values["domain"],
                        )
                        self.assertTrue(
                            all(
                                plan["values"][field.api_name]
                                == "***REDACTED***"
                                for field in spec.fields
                                if field.location == "body"
                            )
                        )
                        self.assertRegex(
                            plan["contact_values_sha256"],
                            r"^[0-9a-f]{64}$",
                        )
                    else:
                        self.assertEqual(plan["values"], values)
                    self.assertIsInstance(plan["fingerprint"], str)

                    client_apply = FakeClient()
                    receipt = apply_plan(
                        spec,
                        values,
                        plan_in=str(plan_path),
                        receipt_out=str(receipt_path),
                        client=client_apply,
                        yes=True,
                        acknowledgements=self._write_acks(spec),
                        secret_values=self._secret_values(spec),
                        tool_version="0.1.0",
                    )
                    self.assertTrue(receipt_path.exists())
                    self.assertEqual(receipt_path.stat().st_mode & 0o777, 0o600)
                    self.assertTrue(receipt["applied"])
                    self.assertFalse(receipt["rollback_supported"])
                    write_calls = [c for c in client_apply.calls if c[0] == spec.family and c[1] == spec.command]
                    self.assertEqual(len(write_calls), 1)

    def test_call_order_is_snapshots_then_write_then_verification(self) -> None:
        spec = next(op for op in self.write_specs if op.family == "domains" and op.command == "domains update")
        values = self._synthetic_values(spec)

        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            plan_path = p / "plan.json"
            receipt_path = p / "receipt.json"
            create_plan(spec, values, plan_out=str(plan_path), client=FakeClient())
            client = FakeClient()
            apply_plan(
                spec,
                values,
                plan_in=str(plan_path),
                receipt_out=str(receipt_path),
                client=client,
                yes=True,
                acknowledgements=self._write_acks(spec),
                secret_values=self._secret_values(spec),
            )

            calls = [(family, command) for family, command, _ in client.calls]
            write_index = calls.index((spec.family, spec.command))
            self.assertGreaterEqual(write_index, 1)
            self.assertTrue(all(call != (spec.family, spec.command) for call in calls[:write_index]))

    def test_no_snapshot_warning_and_markers(self) -> None:
        spec = next(op for op in self.write_specs if op.no_snapshot)
        values = self._synthetic_values(spec)
        with tempfile.TemporaryDirectory() as d:
            plan_path = Path(d) / "plan.json"
            client = FakeClient()
            plan = create_plan(spec, values, plan_out=str(plan_path), client=client)
            self.assertIn(
                "Readable before-state is included when available, but it is not a reliable restore path.",
                plan["warnings"],
            )
            self.assertTrue(plan["snapshots"][0]["ok"])
            self.assertTrue(client.calls)

    def test_snapshot_failures_are_marked(self) -> None:
        spec = next(op for op in self.write_specs if not op.no_snapshot and op.snapshot_commands)
        values = self._synthetic_values(spec)
        fail = spec.snapshot_commands[0]
        fail_ref = tuple(fail.split(":", 1))
        with tempfile.TemporaryDirectory() as d:
            plan_path = Path(d) / "plan.json"
            plan = create_plan(spec, values, plan_out=str(plan_path), client=FakeClient(fail_refs={fail_ref}))
            self.assertEqual(plan["snapshots"][0]["note"], "snapshot_unavailable")
            self.assertFalse(plan["snapshots"][0]["ok"])

    def test_external_message_rejects_bulk(self) -> None:
        spec = next(op for op in self.write_specs if op.external_message)
        values = self._synthetic_values(spec)
        values["Email"] = ["ops@example.com", "admin@example.com"]
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValidationError):
                create_plan(spec, values, plan_out=str(Path(d) / "plan.json"), client=FakeClient())

    def test_missing_acknowledgements(self) -> None:
        required = sorted({ack for op in self.write_specs for ack in op.required_acks})
        required.extend(["ack_no_snapshot", "ack_external_message"])
        required = sorted(set(required))

        for ack in required:
            spec = next(
                op
                for op in self.write_specs
                if (ack in op.required_acks) or (ack == "ack_no_snapshot" and op.no_snapshot) or (ack == "ack_external_message" and op.external_message)
            )
            values = self._synthetic_values(spec)
            with tempfile.TemporaryDirectory() as d:
                plan_path = Path(d) / "plan.json"
                create_plan(spec, values, plan_out=str(plan_path), client=FakeClient())
                acks = self._write_acks(spec)
                acks[ack] = False
                with self.assertRaises(SafetyError):
                    apply_plan(
                        spec,
                        values,
                        plan_in=str(plan_path),
                        receipt_out=str(Path(d) / "receipt.json"),
                        client=FakeClient(),
                        yes=True,
                        acknowledgements=acks,
                        secret_values=self._secret_values(spec),
                    )

    def test_fingerprint_tamper_is_refused(self) -> None:
        spec = next(op for op in self.write_specs if op.family == "domains" and op.command == "domains update")
        values = self._synthetic_values(spec)
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            plan_path = p / "plan.json"
            create_plan(spec, values, plan_out=str(plan_path), client=FakeClient())
            obj = json.loads(plan_path.read_text(encoding="utf-8"))
            obj["fingerprint"] = "0" * 64
            plan_path.write_text(json.dumps(obj, indent=2, sort_keys=True), encoding="utf-8")
            with self.assertRaises(SafetyError):
                apply_plan(
                    spec,
                    values,
                    plan_in=str(plan_path),
                    receipt_out=str(p / "receipt.json"),
                    client=FakeClient(),
                    yes=True,
                    acknowledgements=self._write_acks(spec),
                    secret_values=self._secret_values(spec),
                )

    def test_exact_target_mismatch_is_refused(self) -> None:
        spec = next(op for op in self.write_specs if op.family == "domains" and op.command == "domains update")
        base = self._synthetic_values(spec)
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            plan_path = p / "plan.json"
            create_plan(spec, base, plan_out=str(plan_path), client=FakeClient())
            bad = dict(base)
            bad["domain"] = "different.example"
            with self.assertRaises(ValidationError):
                apply_plan(
                    spec,
                    bad,
                    plan_in=str(plan_path),
                    receipt_out=str(p / "receipt.json"),
                    client=FakeClient(),
                    yes=True,
                    acknowledgements=self._write_acks(spec),
                    secret_values=self._secret_values(spec),
                )

    def test_purchase_refuses_status_or_price_drift(self) -> None:
        spec = next(op for op in self.write_specs if op.family == "purchase" and op.command == "purchase register")
        values = self._synthetic_values(spec)

        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            plan_path = p / "plan.json"
            plan = create_plan(
                spec,
                values,
                plan_out=str(plan_path),
                client=FakeClient(),
                tool_version="0.1.0",
            )
            self.assertIn("purchase_quote", plan)
            self.assertIn("NameBright charges the account's funded balance.", plan["warnings"])
            drift_client = FakeClient(
                availability={"Status": "Unavailable", "AvailableForRegistration": "false", "UnitPrice": 10, "PromotionPrice": 8},
                account_show={"AccountBalance": "9.99", "FundedBalance": "25", "NonRefundable": "True"},
            )
            with self.assertRaises(SafetyError):
                apply_plan(
                    spec,
                    values,
                    plan_in=str(plan_path),
                    receipt_out=str(p / "receipt.json"),
                    client=drift_client,
                    yes=True,
                    acknowledgements=self._write_acks(spec),
                    secret_values=self._secret_values(spec),
                    tool_version="0.1.0",
                )

    def test_purchase_register_refuses_not_available(self) -> None:
        spec = next(op for op in self.write_specs if op.family == "purchase" and op.command == "purchase register")
        values = self._synthetic_values(spec)

        with tempfile.TemporaryDirectory() as d:
            plan_path = Path(d) / "plan.json"
            with self.assertRaises(SafetyError):
                create_plan(
                    spec,
                    values,
                    plan_out=str(plan_path),
                    client=FakeClient(
                        availability={"Status": "Available", "AvailableForRegistration": "false", "UnitPrice": 10, "PromotionPrice": 8},
                    ),
                )

    def test_purchase_quote_includes_nested_promotion_and_domain_years(self) -> None:
        spec = next(op for op in self.write_specs if op.family == "purchase" and op.command == "purchase register")
        values = self._synthetic_values(spec)

        with tempfile.TemporaryDirectory() as d:
            plan_path = Path(d) / "plan.json"
            plan = create_plan(
                spec,
                values,
                plan_out=str(plan_path),
                client=FakeClient(
                    availability={
                        "Status": "Available",
                        "AvailableForRegistration": "true",
                        "UnitPrice": 15,
                        "Promotion": {"PromotionPrice": 7},
                    },
                ),
            )
            self.assertEqual(plan["purchase_quote"]["status"], "Available")
            self.assertEqual(plan["purchase_quote"]["promotion_price"], 7)
            self.assertEqual(plan["purchase_quote"]["quoted_unit_price"], 7)
            self.assertEqual(plan["purchase_quote"]["quoted_total_price"], 14)
            self.assertEqual(plan["purchase_quote"]["domain"], "example.com")
            self.assertEqual(plan["purchase_quote"]["years"], 2)

    def test_purchase_warning_keys_are_namebright_specific(self) -> None:
        spec = next(op for op in self.write_specs if op.family == "purchase" and op.command == "purchase register")
        values = self._synthetic_values(spec)

        with tempfile.TemporaryDirectory() as d:
            plan_path = Path(d) / "plan.json"
            plan = create_plan(
                spec,
                values,
                plan_out=str(plan_path),
                client=FakeClient(
                    account_show={
                        "AccountBalance": "1",
                        "FundedBalance": "25",
                        "NonRefundable": "True",
                    },
                ),
            )
            warnings = plan["warnings"]
            self.assertIn("NameBright charges the account's funded balance.", warnings)
            self.assertIn("NameBright purchases are non-refundable.", warnings)
            self.assertIn(
                "Approval is limited to the exact domain and duration in this plan.",
                warnings,
            )
            self.assertTrue(all("AccountBalance" not in item for item in warnings))

    def test_apply_plan_compares_snapshot_drift_for_non_purchase(self) -> None:
        spec = next(op for op in self.write_specs if op.family == "domains" and op.command == "domains update")
        values = self._synthetic_values(spec)

        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            plan_path = p / "plan.json"
            create_plan(spec, values, plan_out=str(plan_path), client=FakeClient())
            obj = json.loads(plan_path.read_text(encoding="utf-8"))
            snapshot = obj["snapshots"][0]
            payload = dict(snapshot["payload"])
            payload["Status"] = "tampered"
            snapshot["payload"] = payload
            plan_path.write_text(json.dumps(obj, indent=2, sort_keys=True), encoding="utf-8")

            client = FakeClient(domains_get={"DomainName": "example.com", "Status": "ok"})
            with self.assertRaises(SafetyError):
                apply_plan(
                    spec,
                    values,
                    plan_in=str(plan_path),
                    receipt_out=str(p / "receipt.json"),
                    client=client,
                    yes=True,
                    acknowledgements=self._write_acks(spec),
                    secret_values=self._secret_values(spec),
                )
            write_calls = [call for call in client.calls if call[0] == spec.family and call[1] == spec.command]
            self.assertEqual(write_calls, [])

    def test_contact_snapshot_raw_drift_refuses_without_pii_artifacts(self) -> None:
        write_spec = get_operation("contacts", "contacts update-administrative")
        read_spec = get_operation("contacts", "contacts get-administrative")
        self.assertIsNotNone(write_spec)
        self.assertIsNotNone(read_spec)
        assert write_spec is not None
        assert read_spec is not None

        first_contact = {
            "FirstName": "Alice-Plan-Only",
            "LastName": "Owner-One",
            "Organization": "First Private Company",
            "Department": "Legal",
            "Email": "alice-private@example.com",
            "Address1": "11 Hidden Street",
            "Address2": "Suite 101",
            "City": "Austin",
            "Region": "TX",
            "Country": "US",
            "PostalCode": "78701",
            "PhoneCountry": 1,
            "Phone": "5125550101",
            "FaxCountry": 1,
            "Fax": "5125550102",
        }
        second_contact = {
            "FirstName": "Bob-Apply-Only",
            "LastName": "Owner-Two",
            "Organization": "Second Private Company",
            "Department": "Legal",
            "Email": "bob-private@example.net",
            "Address1": "99 Secret Avenue",
            "Address2": "Floor 9",
            "City": "Denver",
            "Region": "CO",
            "Country": "US",
            "PostalCode": "80202",
            "PhoneCountry": 1,
            "Phone": "3035550199",
            "FaxCountry": 1,
            "Fax": "3035550188",
        }
        values = {"domain": "example.com", **first_contact}
        cfg = Config(
            base_url="https://api.namebright.com/rest",
            token_url="https://api.namebright.com/auth/token",
            timeout_s=10.0,
            client_id="client-id",
            client_secret="client-secret",
        )

        with tempfile.TemporaryDirectory() as d, patch.object(NameBrightClient, "_throttle"):
            root = Path(d)
            plan_path = root / "plan.json"
            receipt_path = root / "receipt.json"
            plan_session = FakeHttpSession(
                [
                    FakeHttpResponse({"access_token": "plan-token", "expires_in": 900}),
                    FakeHttpResponse(first_contact),
                    FakeHttpResponse(first_contact),
                ]
            )
            plan_client = NameBrightClient(
                cfg=cfg,
                timeout_s=10.0,
                verbose=False,
                user_agent="test",
                transport=plan_session,
            )

            normal_read = plan_client.execute_operation(
                read_spec,
                values={"domain": "example.com"},
            )
            self.assertEqual(normal_read.payload["Email"], "***REDACTED***")
            self.assertNotIn(first_contact["Email"], json.dumps(normal_read.payload))

            create_plan(
                write_spec,
                values,
                plan_out=str(plan_path),
                client=plan_client,
            )

            apply_session = FakeHttpSession(
                [
                    FakeHttpResponse({"access_token": "apply-token", "expires_in": 900}),
                    FakeHttpResponse(second_contact),
                    FakeHttpResponse({"ok": True}),
                    FakeHttpResponse(second_contact),
                    FakeHttpResponse({"Administrative": second_contact}),
                ]
            )
            apply_client = NameBrightClient(
                cfg=cfg,
                timeout_s=10.0,
                verbose=False,
                user_agent="test",
                transport=apply_session,
            )

            with self.assertRaisesRegex(SafetyError, "snapshot drift"):
                apply_plan(
                    write_spec,
                    values,
                    plan_in=str(plan_path),
                    receipt_out=str(receipt_path),
                    client=apply_client,
                    yes=True,
                    acknowledgements={"ack_high_risk": True},
                    secret_values={},
                )

            self.assertFalse(any(call.get("method") == "PUT" for call in apply_session.calls))
            self.assertFalse(receipt_path.exists())

            plan = json.loads(plan_path.read_text(encoding="utf-8"))
            self.assertRegex(
                plan["snapshots"][0]["raw_snapshot_sha256"],
                r"^[0-9a-f]{64}$",
            )
            artifact_text = "\n".join(
                path.read_text(encoding="utf-8")
                for path in root.rglob("*")
                if path.is_file()
            )
            for contact in (first_contact, second_contact):
                for value in contact.values():
                    if isinstance(value, str) and value:
                        self.assertNotIn(value, artifact_text)

    def test_contact_post_write_verification_exposes_only_field_names(self) -> None:
        write_spec = get_operation("contacts", "contacts update-administrative")
        self.assertIsNotNone(write_spec)
        assert write_spec is not None
        values = self._synthetic_values(write_spec)
        values["Email"] = "post-write-private@example.com"
        values["Phone"] = "5125550147"
        raw_contact = {
            field.api_name: values[field.api_name]
            for field in write_spec.fields
            if field.location == "body"
        }
        cfg = Config(
            base_url="https://api.namebright.com/rest",
            token_url="https://api.namebright.com/auth/token",
            timeout_s=10.0,
            client_id="client-id",
            client_secret="client-secret",
        )

        with tempfile.TemporaryDirectory() as d, patch.object(NameBrightClient, "_throttle"):
            root = Path(d)
            plan_path = root / "plan.json"
            receipt_path = root / "receipt.json"
            plan_client = NameBrightClient(
                cfg=cfg,
                timeout_s=10.0,
                verbose=False,
                user_agent="test",
                transport=FakeHttpSession(
                    [
                        FakeHttpResponse({"access_token": "plan-token", "expires_in": 900}),
                        FakeHttpResponse(raw_contact),
                    ]
                ),
            )
            create_plan(
                write_spec,
                values,
                plan_out=str(plan_path),
                client=plan_client,
            )

            apply_client = NameBrightClient(
                cfg=cfg,
                timeout_s=10.0,
                verbose=False,
                user_agent="test",
                transport=FakeHttpSession(
                    [
                        FakeHttpResponse({"access_token": "apply-token", "expires_in": 900}),
                        FakeHttpResponse(raw_contact),
                        FakeHttpResponse({"ok": True}),
                        FakeHttpResponse(raw_contact),
                        FakeHttpResponse({"Administrative": raw_contact}),
                    ]
                ),
            )
            receipt = apply_plan(
                write_spec,
                values,
                plan_in=str(plan_path),
                receipt_out=str(receipt_path),
                client=apply_client,
                yes=True,
                acknowledgements={"ack_high_risk": True},
                secret_values={},
            )

            first_result = receipt["verification"]["results"][0]
            expected_names = sorted(raw_contact)
            self.assertEqual(first_result["field_matches"], expected_names)
            self.assertEqual(first_result["field_mismatches"], [])
            self.assertEqual(first_result["field_unavailable"], [])
            self.assertNotIn(
                "field_matches",
                receipt["verification"]["results"][1],
            )
            receipt_text = receipt_path.read_text(encoding="utf-8")
            self.assertNotIn(values["Email"], receipt_text)
            self.assertNotIn(values["Phone"], receipt_text)

    def test_secret_values_never_saved_or_logged(self) -> None:
        spec = next(
            op
            for op in self.write_specs
            if op.family == "contact-verification" and op.command == "contact-verification verify-email"
        )
        values = self._synthetic_values(spec)
        secret = self._secret_values(spec)

        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            plan_path = p / "plan.json"
            receipt_path = p / "receipt.json"
            create_plan(spec, values, plan_out=str(plan_path), client=FakeClient())
            apply_plan(
                spec,
                values,
                plan_in=str(plan_path),
                receipt_out=str(receipt_path),
                client=FakeClient(),
                yes=True,
                acknowledgements=self._write_acks(spec),
                secret_values=secret,
            )

            plan_text = plan_path.read_text(encoding="utf-8")
            receipt_text = receipt_path.read_text(encoding="utf-8")
            secret_token = next(iter(secret.values()))
            self.assertNotIn(secret_token, plan_text)
            self.assertNotIn(secret_token, receipt_text)

            with tempfile.TemporaryDirectory() as ad:
                ap = Path(ad) / "audit.jsonl"
                log = AuditLogger(path=str(ap), enabled=True)
                log.bind_context({"tool": "namebright-safe-cli"})
                log.write(
                    "test",
                    {
                        "token": "secret-token",
                        "VerificationCode": "verify-secret",
                        "accountBalance": "9.99",
                        "clientSecret": "abc",
                    },
                )
                log.close()
                payload = json.loads(ap.read_text(encoding="utf-8"))
                payload_text = json.dumps(payload)
                self.assertNotIn("secret-token", payload_text)
                self.assertNotIn("verify-secret", payload_text)

            summary = build_deterministic_summary(
                tool="namebright-safe-cli",
                version="0.1.0",
                run_id="run-1",
                env_fingerprint="example",
                command="namebright-safe-cli apply",
                output_obj={"ok": True},
                plan_path=str(plan_path),
                receipt_path=str(receipt_path),
                audit_log_path=str(ap),
                audit_log_global_path=str(ap),
                runs_index_path="/tmp/index",
            )
            summary_path = p / "summary.md"
            write_summary_md(path=summary_path, lines=summary)
            summary_text = summary_path.read_text(encoding="utf-8")
            self.assertNotIn("secret-token", summary_text)

    def test_purchase_apply_is_exact_quote_rechecked(self) -> None:
        spec = next(op for op in self.write_specs if op.family == "purchase" and op.command == "purchase renew")
        values = self._synthetic_values(spec)

        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            plan_path = p / "plan.json"
            create_plan(spec, values, plan_out=str(plan_path), client=FakeClient())
            drift_client = FakeClient(availability={"Status": values["DomainName"], "UnitPrice": 11, "PromotionPrice": 11})
            with self.assertRaises(SafetyError):
                apply_plan(
                    spec,
                    values,
                    plan_in=str(plan_path),
                    receipt_out=str(p / "receipt.json"),
                    client=drift_client,
                    yes=True,
                    acknowledgements=self._write_acks(spec),
                    secret_values=self._secret_values(spec),
                )

    def test_refused_before_write_when_mismatched_secret_fields(self) -> None:
        spec = next(op for op in self.write_specs if any(field.kind == "secret_file" for field in op.fields))
        values = self._synthetic_values(spec)

        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            plan_path = p / "plan.json"
            create_plan(spec, values, plan_out=str(plan_path), client=FakeClient())
            with self.assertRaises(ValidationError):
                apply_plan(
                    spec,
                    values,
                    plan_in=str(plan_path),
                    receipt_out=str(p / "receipt.json"),
                    client=FakeClient(),
                    yes=True,
                    acknowledgements=self._write_acks(spec),
                    secret_values={},
                )

    def test_apply_refuses_missing_receipt_out_without_client_calls(self) -> None:
        spec = next(op for op in self.write_specs if op.family == "domains" and op.command == "domains update")
        values = self._synthetic_values(spec)
        client = FakeClient()

        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            plan_path = p / "plan.json"
            create_plan(spec, values, plan_out=str(plan_path), client=client)
            with self.assertRaises(ValidationError):
                apply_plan(
                    spec,
                    values,
                    plan_in=str(plan_path),
                    receipt_out="",
                    client=client,
                    yes=True,
                    acknowledgements=self._write_acks(spec),
                    secret_values=self._secret_values(spec),
                )
            self.assertEqual([c for c in client.calls if c[0] == spec.family and c[1] == spec.command], [])

    def test_verify_exception_is_captured_in_receipt(self) -> None:
        spec = next(op for op in self.write_specs if op.family == "domains" and op.command == "domains update")
        values = self._synthetic_values(spec)
        fail_ref = ("domains", "domains get")
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            plan_path = p / "plan.json"
            create_plan(spec, values, plan_out=str(plan_path), client=FakeClient())
            receipt_path = p / "receipt.json"

            receipt = apply_plan(
                spec,
                values,
                plan_in=str(plan_path),
                receipt_out=str(receipt_path),
                client=FakeClient(fail_refs={fail_ref}),
                yes=True,
                acknowledgements=self._write_acks(spec),
                secret_values=self._secret_values(spec),
            )

            self.assertTrue(receipt["verification"]["ok"] is False)
            self.assertTrue(any(item.get("note") == "verification_error" for item in receipt["verification"]["results"]))
            self.assertTrue(receipt_path.exists())

    def test_write_ok_is_true_when_payload_missing(self) -> None:
        spec = next(op for op in self.write_specs if op.family == "domains" and op.command == "domains update")
        values = self._synthetic_values(spec)

        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            plan_path = p / "plan.json"
            receipt_path = p / "receipt.json"
            create_plan(spec, values, plan_out=str(plan_path), client=FakeClient())
            client = FakeClient(write_overrides={(spec.family, spec.command): None})
            receipt = apply_plan(
                spec,
                values,
                plan_in=str(plan_path),
                receipt_out=str(receipt_path),
                client=client,
                yes=True,
                acknowledgements=self._write_acks(spec),
                secret_values=self._secret_values(spec),
            )
            self.assertTrue(receipt["write"]["ok"])
            self.assertIsNone(receipt["write"]["response"])

    def test_secret_values_with_path_characters_are_allowed(self) -> None:
        spec = next(
            op
            for op in self.write_specs
            if op.family == "contact-verification" and op.command == "contact-verification verify-email"
        )
        values = self._synthetic_values(spec)
        secret = self._secret_values(spec)
        key = next(iter(secret))
        secret[key] = "a/b\\c"
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            plan_path = p / "plan.json"
            receipt_path = p / "receipt.json"
            create_plan(spec, values, plan_out=str(plan_path), client=FakeClient())
            apply_plan(
                spec,
                values,
                plan_in=str(plan_path),
                receipt_out=str(receipt_path),
                client=FakeClient(),
                yes=True,
                acknowledgements=self._write_acks(spec),
                secret_values=secret,
            )
            self.assertNotIn("a/b\\c", plan_path.read_text(encoding="utf-8"))
            self.assertNotIn("a/b\\c", receipt_path.read_text(encoding="utf-8"))

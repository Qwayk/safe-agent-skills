from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from typing import Any

from xero_safe_agent_cli.auth import TokenStore
from xero_safe_agent_cli.http import HttpResponse
from xero_safe_agent_cli.registry import load_registry
from xero_safe_agent_cli.runtime import ExecutionOptions, XeroRuntime
from xero_safe_agent_cli.tenants import TenantStore

TENANT_ID = "11111111-1111-4111-8111-111111111111"
INVOICE_ID = "22222222-2222-4222-8222-222222222222"
CONTACT_ID = "33333333-3333-4333-8333-333333333333"
PROJECT_ID = "44444444-4444-4444-8444-444444444444"
TASK_ID = "55555555-5555-4555-8555-555555555555"
OBJECT_IDS = [
    "66666666-6666-4666-8666-666666666666",
    "77777777-7777-4777-8777-777777777777",
]


class FakeTransport:
    def __init__(self, responses: list[HttpResponse]):
        self.responses = list(responses)
        self.calls: list[dict[str, Any]] = []

    def request(self, method: str, url: str, **kwargs: Any) -> HttpResponse:
        self.calls.append({"method": method, "url": url, **kwargs})
        if not self.responses:
            raise AssertionError("unexpected provider request")
        return self.responses.pop(0)


class TestRuntimeSafety(unittest.TestCase):
    def _stores(self, root: Path, scopes: str) -> tuple[TokenStore, TenantStore]:
        token_store = TokenStore(root / "token.json")
        token_store.write(
            {
                "access_token": "top-secret-token",
                "refresh_token": "top-secret-refresh",
                "expires_in": 1800,
                "scope": scopes,
            }
        )
        tenant_store = TenantStore(root / "tenant.json")
        tenant_store.write(
            {
                "connection_id": "connection-1",
                "tenant_id": TENANT_ID,
                "tenant_name": "Demo AU",
                "tenant_type": "ORGANISATION",
                "region": "AU",
            }
        )
        return token_store, tenant_store

    def test_sensitive_read_redacts_stdout_and_can_write_protected_raw_output(self) -> None:
        body = json.dumps(
            {
                "Invoices": [
                    {
                        "InvoiceNumber": "INV-123",
                        "Contact": {"EmailAddress": "person@example.com"},
                        "BankAccountNumber": "123456789",
                    }
                ]
            }
        ).encode()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            token_store, tenant_store = self._stores(root, "accounting.invoices.read")
            transport = FakeTransport(
                [
                    HttpResponse(
                        status=200,
                        headers={
                            "content-type": "application/json",
                            "X-DayLimit-Remaining": "4999",
                            "X-MinLimit-Remaining": "59",
                            "X-AppMinLimit-Remaining": "9999",
                            "X-Rate-Limit-Problem": "none",
                            "Authorization": "must-not-be-returned",
                        },
                        body=body,
                        url="https://api.xero.com/api.xro/2.0/Invoices",
                    )
                ]
            )
            runtime = XeroRuntime(load_registry(), transport, token_store, tenant_store)
            result = runtime.execute(
                "accounting.get-invoices",
                {"query": {"Statuses": ["AUTHORISED"]}},
                ExecutionOptions(),
            )
            rendered = json.dumps(result)
            self.assertNotIn("person@example.com", rendered)
            self.assertNotIn("123456789", rendered)
            self.assertNotIn("top-secret-token", rendered)
            self.assertEqual(
                result["rate_limit_headers"],
                {
                    "X-DayLimit-Remaining": "4999",
                    "X-MinLimit-Remaining": "59",
                    "X-AppMinLimit-Remaining": "9999",
                    "X-Rate-Limit-Problem": "none",
                },
            )

            protected = root / "invoices.json"
            transport.responses.append(
                HttpResponse(status=200, headers={}, body=body, url="https://api.xero.com/api.xro/2.0/Invoices")
            )
            saved = runtime.execute(
                "accounting.get-invoices",
                {},
                ExecutionOptions(protected_output=protected),
            )
            self.assertEqual(protected.read_bytes(), body)
            self.assertEqual(saved["protected_output"], str(protected))
            self.assertNotIn("person@example.com", json.dumps(saved))

    def test_write_is_plan_first_and_apply_requires_every_matching_approval(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            token_store, tenant_store = self._stores(root, "accounting.invoices")
            transport = FakeTransport([])
            runtime = XeroRuntime(load_registry(), transport, token_store, tenant_store)
            plan_path = root / "plan.json"
            input_data = {"body": {"Invoices": [{"Type": "ACCREC", "Status": "DRAFT"}]}}
            planned = runtime.execute(
                "accounting.create-invoices",
                input_data,
                ExecutionOptions(plan_out=plan_path),
            )
            self.assertTrue(planned["dry_run"])
            self.assertTrue(planned["no_snapshot"])
            self.assertEqual(transport.calls, [])
            plan = json.loads(plan_path.read_text(encoding="utf-8"))
            self.assertEqual(plan["tenant"]["tenant_id"], TENANT_ID)
            self.assertEqual(plan["command"], "accounting.create-invoices")

            with self.assertRaisesRegex(Exception, "--approve"):
                runtime.execute(
                    "accounting.create-invoices",
                    {},
                    ExecutionOptions(apply=True, plan_in=plan_path),
                )
            with self.assertRaisesRegex(Exception, "high-risk"):
                runtime.execute(
                    "accounting.create-invoices",
                    {},
                    ExecutionOptions(apply=True, plan_in=plan_path, approve=True),
                )
            with self.assertRaisesRegex(Exception, "no-snapshot"):
                runtime.execute(
                    "accounting.create-invoices",
                    {},
                    ExecutionOptions(
                        apply=True,
                        plan_in=plan_path,
                        approve=True,
                        approve_high_risk=True,
                    ),
                )

            transport.responses.append(
                HttpResponse(
                    status=200,
                    headers={},
                    body=json.dumps({"Invoices": [{"ValidationErrors": []}]}).encode(),
                    url="https://api.xero.com/api.xro/2.0/Invoices",
                )
            )
            receipt_path = root / "receipt.json"
            applied = runtime.execute(
                "accounting.create-invoices",
                {},
                ExecutionOptions(
                    apply=True,
                    plan_in=plan_path,
                    receipt_out=receipt_path,
                    approve=True,
                    approve_high_risk=True,
                    ack_no_snapshot=True,
                ),
            )
            self.assertTrue(applied["ok"])
            self.assertEqual(applied["provider_outcome"], "accepted_not_stronger_state")
            self.assertTrue(receipt_path.exists())
            self.assertEqual(len(transport.calls), 1)
            self.assertEqual(transport.calls[0]["method"], "PUT")
            self.assertNotIn("top-secret-token", receipt_path.read_text(encoding="utf-8"))

    def test_region_mismatch_and_tampered_plan_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            token_store, tenant_store = self._stores(root, "payroll.employees.read")
            tenant = tenant_store.read()
            tenant["region"] = "NZ"
            tenant_store.write(tenant)
            runtime = XeroRuntime(load_registry(), FakeTransport([]), token_store, tenant_store)
            with self.assertRaisesRegex(Exception, "requires region AU"):
                runtime.execute("payroll-au.get-employees", {}, ExecutionOptions())

            token_store.write(
                {"access_token": "secret", "refresh_token": "refresh", "scope": "accounting.invoices"}
            )
            tenant["region"] = "AU"
            tenant_store.write(tenant)
            plan_path = root / "plan.json"
            runtime.execute(
                "accounting.create-invoices",
                {"body": {"Invoices": [{"Type": "ACCREC"}]}},
                ExecutionOptions(plan_out=plan_path),
            )
            plan = json.loads(plan_path.read_text(encoding="utf-8"))
            plan["command"] = "accounting.create-payments"
            plan_path.write_text(json.dumps(plan), encoding="utf-8")
            with self.assertRaisesRegex(Exception, "plan integrity"):
                runtime.execute(
                    "accounting.create-invoices",
                    {},
                    ExecutionOptions(
                        apply=True,
                        plan_in=plan_path,
                        approve=True,
                        approve_high_risk=True,
                        ack_no_snapshot=True,
                    ),
                )

    def test_fixed_contract_rejects_unknown_query_path_header_and_body_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            token_store, tenant_store = self._stores(root, "accounting.invoices.read")
            runtime = XeroRuntime(load_registry(), FakeTransport([]), token_store, tenant_store)
            for bad_input, expected in (
                ({"query": {"notDocumented": "x"}}, "query"),
                ({"path": {"InvoiceID": "x"}}, "path"),
                ({"headers": {"X-Not-Documented": "x"}}, "header"),
            ):
                with self.subTest(bad_input=bad_input):
                    with self.assertRaisesRegex(Exception, expected):
                        runtime.execute("accounting.get-invoices", bad_input, ExecutionOptions())

            token_store.write(
                {"access_token": "secret", "scope": "accounting.invoices"}
            )
            with self.assertRaisesRegex(Exception, "body field"):
                runtime.execute(
                    "accounting.create-invoices",
                    {"body": {"NotARealInvoicesField": []}},
                    ExecutionOptions(),
                )

    def test_missing_scope_and_protected_header_overrides_make_zero_provider_calls(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            token_store, tenant_store = self._stores(root, "accounting.contacts.read")
            transport = FakeTransport([])
            runtime = XeroRuntime(load_registry(), transport, token_store, tenant_store)
            with self.assertRaisesRegex(Exception, "missing required scope"):
                runtime.execute("accounting.get-invoices", {}, ExecutionOptions())
            for name in ("Authorization", "xero-tenant-id"):
                with self.subTest(name=name), self.assertRaisesRegex(
                    Exception, "protected header"
                ):
                    runtime.execute(
                        "accounting.get-contacts",
                        {"headers": {name: "attacker-controlled"}},
                        ExecutionOptions(),
                    )
            self.assertEqual(transport.calls, [])
            with self.assertRaisesRegex(Exception, "Invoices must be a JSON array"):
                runtime.execute(
                    "accounting.create-invoices",
                    {"body": {"Invoices": "not-a-list"}},
                    ExecutionOptions(),
                )
            with self.assertRaisesRegex(Exception, "LineItems must be a JSON array"):
                runtime.execute(
                    "accounting.create-invoices",
                    {"body": {"Invoices": [{"LineItems": "not-a-list"}]}},
                    ExecutionOptions(),
                )
            with self.assertRaisesRegex(Exception, r"Invoices\[0\] must be a JSON object"):
                runtime.execute(
                    "accounting.create-invoices",
                    {"body": {"Invoices": [123]}},
                    ExecutionOptions(),
                )
            with self.assertRaisesRegex(Exception, r"Invoices\[0\]\.Type must be one of"):
                runtime.execute(
                    "accounting.create-invoices",
                    {"body": {"Invoices": [{"Type": "NOT_A_XERO_INVOICE_TYPE"}]}},
                    ExecutionOptions(),
                )
            with self.assertRaisesRegex(
                Exception, r"Addresses\[0\]\.AddressLine1 must contain at most 500"
            ):
                runtime.execute(
                    "accounting.create-contacts",
                    {
                        "body": {
                            "Contacts": [
                                {"Addresses": [{"AddressLine1": "x" * 501}]}
                            ]
                        }
                    },
                    ExecutionOptions(),
                )
            with self.assertRaisesRegex(
                Exception, r"Contact\.ContactID must be a canonical UUID"
            ):
                runtime.execute(
                    "accounting.create-invoices",
                    {"body": {"Invoices": [{"Contact": {"ContactID": "bad-uuid"}}]}},
                    ExecutionOptions(),
                )

    def test_payroll_uk_ni_category_one_of_contract_is_enforced(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            token_store, tenant_store = self._stores(root, "payroll.employees")
            tenant = tenant_store.read()
            tenant["region"] = "UK"
            tenant_store.write(tenant)
            runtime = XeroRuntime(load_registry(), FakeTransport([]), token_store, tenant_store)
            body = {
                "address": {
                    "addressLine1": "Private street",
                    "city": "Private city",
                    "postCode": "AB1 2CD",
                },
                "dateOfBirth": "1990-01-01",
                "firstName": "Private",
                "gender": "F",
                "lastName": "Employee",
                "title": "Mx",
                "niCategories": [
                    {"niCategory": "V", "workplacePostcode": "SW1A 1AA"}
                ],
            }
            with self.assertRaisesRegex(Exception, "one documented oneOf shape"):
                runtime.execute(
                    "payroll-uk.create-employee",
                    {"body": body},
                    ExecutionOptions(),
                )
            body["niCategories"][0]["dateFirstEmployedAsCivilian"] = "2024-12-02"
            planned = runtime.execute(
                "payroll-uk.create-employee",
                {"body": body},
                ExecutionOptions(plan_out=root / "valid-plan.json"),
            )
            self.assertTrue(planned["dry_run"])

    def test_numeric_query_bounds_are_enforced_before_provider_calls(self) -> None:
        cases = (
            ("files.get-files", "files.read", {"pagesize": 101}, "at most 100"),
            ("files.get-files", "files.read", {"page": 0}, "at least 1"),
            ("projects.get-projects", "projects.read", {"pageSize": 0}, "at least 1"),
            ("projects.get-projects", "projects.read", {"pageSize": 501}, "at most 500"),
        )
        for command, scope, query, expected in cases:
            with self.subTest(command=command, query=query), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                token_store, tenant_store = self._stores(root, scope)
                transport = FakeTransport([])
                runtime = XeroRuntime(load_registry(), transport, token_store, tenant_store)
                with self.assertRaisesRegex(Exception, expected):
                    runtime.execute(command, {"query": query}, ExecutionOptions())
                self.assertEqual(transport.calls, [])

    def test_documented_uuid_parameters_are_checked_for_scalars_and_array_items(self) -> None:
        cases = (
            (
                "accounting.get-invoice",
                "accounting.invoices.read",
                {"path": {"InvoiceID": "not-a-uuid"}},
                "InvoiceID must be a canonical UUID",
            ),
            (
                "files.get-associations-count",
                "files.read",
                {"query": {"ObjectIds": ["1270bf7c-5d18-473a-9231-1e36c4bd33ed", "bad"]}},
                r"ObjectIds\[1\] must be a canonical UUID",
            ),
            (
                "projects.get-projects",
                "projects.read",
                {"query": {"projectIds": ["bad"]}},
                r"projectIds\[0\] must be a canonical UUID",
            ),
        )
        for command, scope, input_data, expected in cases:
            with self.subTest(command=command), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                token_store, tenant_store = self._stores(root, scope)
                transport = FakeTransport([])
                runtime = XeroRuntime(load_registry(), transport, token_store, tenant_store)
                with self.assertRaisesRegex(Exception, expected):
                    runtime.execute(command, input_data, ExecutionOptions())
                self.assertEqual(transport.calls, [])

    def test_manual_multi_region_command_is_limited_to_au_or_nz(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            token_store, tenant_store = self._stores(root, "einvoicing")
            selected = tenant_store.read()
            selected["region"] = "UK"
            tenant_store.write(selected)
            runtime = XeroRuntime(load_registry(), FakeTransport([]), token_store, tenant_store)
            with self.assertRaisesRegex(Exception, "requires region AU or NZ"):
                runtime.execute(
                    "einvoicing.get-registration",
                    {"path": {"organisationId": TENANT_ID}},
                    ExecutionOptions(),
                )

    def test_accounting_regional_commands_refuse_the_wrong_tenant_region(self) -> None:
        cases = (
            (
                "accounting.get-report-ten-ninety-nine",
                "accounting.reports.tenninetynine.read",
                {},
                "requires region US",
            ),
            (
                "accounting.get-organisation-cissettings",
                "accounting.settings.read",
                {"path": {"OrganisationID": TENANT_ID}},
                "requires region UK",
            ),
            (
                "accounting.get-contact-cissettings",
                "accounting.contacts.read",
                {"path": {"ContactID": CONTACT_ID}},
                "requires region UK",
            ),
            (
                "accounting.get-reports-list",
                "accounting.reports.taxreports.read",
                {},
                "requires region AU or NZ",
            ),
        )
        for command, scope, input_data, expected in cases:
            with self.subTest(command=command), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                token_store, tenant_store = self._stores(root, scope)
                if command == "accounting.get-reports-list":
                    tenant = tenant_store.read()
                    tenant["region"] = "UK"
                    tenant_store.write(tenant)
                transport = FakeTransport([])
                runtime = XeroRuntime(load_registry(), transport, token_store, tenant_store)
                with self.assertRaisesRegex(Exception, expected):
                    runtime.execute(command, input_data, ExecutionOptions())
                self.assertEqual(transport.calls, [])

    def test_finance_cashflow_refuses_us_but_allows_a_supported_non_us_region(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            token_store, tenant_store = self._stores(root, "finance.statements.read")
            tenant = tenant_store.read()
            tenant["region"] = "US"
            tenant_store.write(tenant)
            transport = FakeTransport([])
            runtime = XeroRuntime(load_registry(), transport, token_store, tenant_store)
            with self.assertRaisesRegex(Exception, "unavailable in region US"):
                runtime.execute(
                    "finance.get-financial-statement-cashflow", {}, ExecutionOptions()
                )
            self.assertEqual(transport.calls, [])

            tenant["region"] = "AU"
            tenant_store.write(tenant)
            transport.responses.append(
                HttpResponse(
                    200,
                    {"content-type": "application/json"},
                    b'{"statements":[]}',
                    "https://api.xero.com/finance.xro/1.0/FinancialStatements/Cashflow",
                )
            )
            result = runtime.execute(
                "finance.get-financial-statement-cashflow", {}, ExecutionOptions()
            )
            self.assertTrue(result["ok"])
            self.assertEqual(len(transport.calls), 1)

    def test_tenant_bound_organisation_path_must_match_selected_tenant(self) -> None:
        cases = (
            (
                "einvoicing.get-registration",
                "einvoicing",
                {"path": {"organisationId": INVOICE_ID}},
            ),
            (
                "accounting.get-organisation-cissettings",
                "accounting.settings.read",
                {"path": {"OrganisationID": INVOICE_ID}},
            ),
        )
        for command, scope, input_data in cases:
            with self.subTest(command=command), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                token_store, tenant_store = self._stores(root, scope)
                transport = FakeTransport([])
                runtime = XeroRuntime(load_registry(), transport, token_store, tenant_store)
                with self.assertRaisesRegex(Exception, "selected tenant"):
                    runtime.execute(command, input_data, ExecutionOptions())
                self.assertEqual(transport.calls, [])

    def test_custom_connection_keeps_exact_target_but_omits_tenant_header(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            token_store, tenant_store = self._stores(root, "accounting.settings.read")
            selected = tenant_store.read()
            selected["credential_fingerprint"] = token_store.read()["credential_fingerprint"]
            tenant_store.write(selected)
            transport = FakeTransport(
                [
                    HttpResponse(
                        status=200,
                        headers={"content-type": "application/json"},
                        body=b'{"Organisations": []}',
                        url="https://api.xero.com/api.xro/2.0/Organisation",
                    )
                ]
            )
            runtime = XeroRuntime(
                load_registry(),
                transport,
                token_store,
                tenant_store,
                auth_profile="custom",
            )
            result = runtime.execute("accounting.get-organisations", {}, ExecutionOptions())
            self.assertTrue(result["ok"])
            self.assertEqual(result["tenant"]["tenant_id"], TENANT_ID)
            self.assertNotIn("xero-tenant-id", transport.calls[0]["headers"])

    def test_custom_connection_token_rotation_requires_target_rediscovery(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            token_store = TokenStore(root / "custom-token.json")
            token_store.write(
                {"access_token": "first-custom-token", "scope": "accounting.settings.read"}
            )
            tenant_store = TenantStore(root / "custom-tenant.json")
            tenant_store.select_custom(
                {
                    "OrganisationID": "organisation-1",
                    "Name": "First Organisation",
                    "CountryCode": "AU",
                },
                credential_fingerprint=token_store.read()["credential_fingerprint"],
            )
            token_store.write(
                {"access_token": "second-custom-token", "scope": "accounting.settings.read"}
            )
            transport = FakeTransport([])
            runtime = XeroRuntime(
                load_registry(),
                transport,
                token_store,
                tenant_store,
                auth_profile="custom",
            )
            with self.assertRaisesRegex(Exception, "custom-discover"):
                runtime.execute("accounting.get-organisations", {}, ExecutionOptions())
            self.assertEqual(transport.calls, [])

    def test_custom_connection_refuses_an_unsupported_saved_tenant_region(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            token_store = TokenStore(root / "custom-token.json")
            token_store.write(
                {"access_token": "custom-token", "scope": "accounting.settings.read"}
            )
            tenant_store = TenantStore(root / "custom-tenant.json")
            tenant_store.write(
                {
                    "connection_id": "custom-connection",
                    "tenant_id": "organisation-1",
                    "tenant_name": "Unsupported Organisation",
                    "tenant_type": "ORGANISATION",
                    "region": "GLOBAL",
                    "credential_fingerprint": token_store.read()["credential_fingerprint"],
                }
            )
            transport = FakeTransport([])
            runtime = XeroRuntime(
                load_registry(),
                transport,
                token_store,
                tenant_store,
                auth_profile="custom",
            )
            with self.assertRaisesRegex(Exception, "only AU, NZ, UK, or US"):
                runtime.execute("accounting.get-organisations", {}, ExecutionOptions())
            self.assertEqual(transport.calls, [])

    def test_file_apply_refuses_content_changed_after_plan(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            token_store, tenant_store = self._stores(root, "files")
            transport = FakeTransport([])
            runtime = XeroRuntime(load_registry(), transport, token_store, tenant_store)
            upload = root / "invoice.pdf"
            upload.write_bytes(b"reviewed file bytes")
            plan_path = root / "file-plan.json"

            runtime.execute(
                "files.upload-file",
                {"file_path": str(upload)},
                ExecutionOptions(plan_out=plan_path),
            )
            upload.write_bytes(b"different bytes after review")

            with self.assertRaisesRegex(Exception, "file changed after planning"):
                runtime.execute(
                    "files.upload-file",
                    {},
                    ExecutionOptions(
                        apply=True,
                        plan_in=plan_path,
                        approve=True,
                        approve_high_risk=True,
                        ack_no_snapshot=True,
                    ),
                )
            self.assertEqual(transport.calls, [])

    def test_oversized_json_and_file_requests_stop_before_provider_calls(self) -> None:
        oversized = "x" * (10 * 1024 * 1024 + 1)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            token_store, tenant_store = self._stores(root, "accounting.settings")
            transport = FakeTransport([])
            runtime = XeroRuntime(load_registry(), transport, token_store, tenant_store)
            with self.assertRaisesRegex(Exception, "10 MB global limit"):
                runtime.execute(
                    "accounting.create-account",
                    {"body": {"Description": oversized}},
                    ExecutionOptions(plan_out=root / "json-plan.json"),
                )
            self.assertEqual(transport.calls, [])

            token_store.write({"access_token": "secret", "scope": "files"})
            upload = root / "oversized.bin"
            upload.write_bytes(oversized.encode())
            with self.assertRaisesRegex(Exception, "10 MB global request limit"):
                runtime.execute(
                    "files.upload-file",
                    {"file_path": str(upload)},
                    ExecutionOptions(plan_out=root / "file-plan.json"),
                )
            self.assertEqual(transport.calls, [])

    def test_files_upload_uses_the_documented_multipart_field_shape(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            token_store, tenant_store = self._stores(root, "files")
            transport = FakeTransport(
                [
                    HttpResponse(
                        status=201,
                        headers={"content-type": "application/json"},
                        body=b'{"Files":[]}',
                        url="https://api.xero.com/files.xro/1.0/Files",
                    )
                ]
            )
            runtime = XeroRuntime(load_registry(), transport, token_store, tenant_store)
            upload = root / "invoice.pdf"
            upload.write_bytes(b"pdf bytes")
            plan_path = root / "upload-plan.json"
            runtime.execute(
                "files.upload-file",
                {"file_path": str(upload)},
                ExecutionOptions(plan_out=plan_path),
            )
            runtime.execute(
                "files.upload-file",
                {},
                ExecutionOptions(
                    apply=True,
                    plan_in=plan_path,
                    approve=True,
                    approve_high_risk=True,
                    ack_no_snapshot=True,
                ),
            )
            sent = transport.calls[0]
            self.assertEqual(set(sent["files"]), {"body", "name", "filename", "mimeType"})
            self.assertEqual(sent["files"]["body"], ("invoice.pdf", b"pdf bytes", "application/pdf"))
            self.assertEqual(sent["files"]["name"], (None, "invoice.pdf"))
            self.assertEqual(sent["files"]["filename"], (None, "invoice.pdf"))
            self.assertEqual(sent["files"]["mimeType"], (None, "application/pdf"))
            self.assertIsNone(sent["data"])

    def test_accounting_attachment_remains_raw_octet_stream(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            token_store, tenant_store = self._stores(root, "accounting.attachments")
            transport = FakeTransport([])
            runtime = XeroRuntime(load_registry(), transport, token_store, tenant_store)
            upload = root / "invoice.pdf"
            upload.write_bytes(b"pdf bytes")
            operation = load_registry().get("accounting.create-invoice-attachment-by-file-name")
            assert operation is not None
            input_data = {
                "path": {"InvoiceID": INVOICE_ID, "FileName": "invoice.pdf"},
                "file_path": str(upload),
            }
            runtime._validate_input(operation, input_data)
            try:
                runtime._request(
                    operation,
                    input_data,
                    token_store.read(),
                    tenant_store.read(),
                    idempotency_key="idempotency-1",
                )
            except AssertionError:
                pass
            sent = transport.calls[0]
            self.assertEqual(sent["data"], b"pdf bytes")
            self.assertIsNone(sent["files"])
            self.assertEqual(sent["headers"]["Content-Type"], "application/octet-stream")

    def test_attachment_snapshot_supplies_required_content_type(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            token_store, tenant_store = self._stores(root, "accounting.attachments")
            transport = FakeTransport(
                [
                    HttpResponse(
                        status=200,
                        headers={"content-type": "application/octet-stream"},
                        body=b"existing attachment",
                        url="https://api.xero.com/api.xro/2.0/Invoices/invoice-1/Attachments/invoice.pdf",
                    )
                ]
            )
            runtime = XeroRuntime(load_registry(), transport, token_store, tenant_store)
            upload = root / "invoice.pdf"
            upload.write_bytes(b"replacement attachment")
            planned = runtime.execute(
                "accounting.update-invoice-attachment-by-file-name",
                {
                    "path": {"InvoiceID": INVOICE_ID, "FileName": "invoice.pdf"},
                    "file_path": str(upload),
                },
                ExecutionOptions(plan_out=root / "attachment-plan.json"),
            )
            self.assertFalse(planned["no_snapshot"])
            self.assertEqual(transport.calls[0]["headers"]["contentType"], "application/pdf")

    def test_query_arrays_follow_each_parameters_explode_rule(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            token_store, tenant_store = self._stores(
                root, "accounting.invoices.read files.read"
            )
            transport = FakeTransport(
                [
                    HttpResponse(
                        status=200,
                        headers={"content-type": "application/json"},
                        body=b'{"Invoices":[]}',
                        url="https://api.xero.com/api.xro/2.0/Invoices",
                    ),
                    HttpResponse(
                        status=200,
                        headers={"content-type": "application/json"},
                        body=b'{"Count":0}',
                        url="https://api.xero.com/files.xro/1.0/Associations/Count",
                    ),
                ]
            )
            runtime = XeroRuntime(load_registry(), transport, token_store, tenant_store)
            runtime.execute(
                "accounting.get-invoices",
                {"query": {"Statuses": ["AUTHORISED", "DRAFT"]}},
                ExecutionOptions(),
            )
            runtime.execute(
                "files.get-associations-count",
                {"query": {"ObjectIds": OBJECT_IDS}},
                ExecutionOptions(),
            )
            self.assertEqual(transport.calls[0]["params"]["Statuses"], "AUTHORISED,DRAFT")
            self.assertEqual(
                transport.calls[1]["params"]["ObjectIds"],
                OBJECT_IDS,
            )

    def test_accept_header_matches_json_pdf_and_binary_contracts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            token_store, tenant_store = self._stores(
                root, "accounting.invoices.read accounting.attachments.read"
            )
            transport = FakeTransport(
                [
                    HttpResponse(200, {"content-type": "application/json"}, b"{}", "json"),
                    HttpResponse(200, {"content-type": "application/pdf"}, b"pdf", "pdf"),
                    HttpResponse(
                        200,
                        {"content-type": "application/octet-stream"},
                        b"attachment",
                        "attachment",
                    ),
                ]
            )
            runtime = XeroRuntime(load_registry(), transport, token_store, tenant_store)
            runtime.execute("accounting.get-invoices", {}, ExecutionOptions())
            runtime.execute(
                "accounting.get-invoice-as-pdf",
                {"path": {"InvoiceID": INVOICE_ID}},
                ExecutionOptions(),
            )
            runtime.execute(
                "accounting.get-invoice-attachment-by-file-name",
                {
                    "path": {"InvoiceID": INVOICE_ID, "FileName": "invoice.pdf"},
                    "headers": {"contentType": "application/pdf"},
                },
                ExecutionOptions(),
            )
            self.assertEqual(transport.calls[0]["headers"]["Accept"], "application/json")
            self.assertEqual(transport.calls[1]["headers"]["Accept"], "application/pdf")
            self.assertEqual(
                transport.calls[2]["headers"]["Accept"], "application/octet-stream"
            )

    def test_required_documented_header_names_are_case_insensitive(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            token_store, tenant_store = self._stores(root, "accounting.attachments.read")
            transport = FakeTransport(
                [
                    HttpResponse(
                        200,
                        {"content-type": "application/octet-stream"},
                        b"attachment",
                        "https://api.xero.com/attachment",
                    )
                ]
            )
            runtime = XeroRuntime(load_registry(), transport, token_store, tenant_store)
            result = runtime.execute(
                "accounting.get-invoice-attachment-by-file-name",
                {
                    "path": {"InvoiceID": INVOICE_ID, "FileName": "invoice.pdf"},
                    "headers": {"contenttype": "application/pdf"},
                },
                ExecutionOptions(),
            )
            self.assertTrue(result["ok"])
            self.assertEqual(transport.calls[0]["headers"]["contenttype"], "application/pdf")

    def test_non_tenanted_connection_command_uses_client_credentials_and_target_header(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            token_store = TokenStore(root / "app-store-token.json")
            token_store.write({"access_token": "app-token", "scope": "app.connections"})
            tenant_store = TenantStore(root / "unused-tenant.json")
            transport = FakeTransport(
                [
                    HttpResponse(
                        status=200,
                        headers={"content-type": "application/json"},
                        body=b"[]",
                        url="https://api.xero.com/Connections",
                    )
                ]
            )
            runtime = XeroRuntime(
                load_registry(),
                transport,
                token_store,
                tenant_store,
                auth_profile="app-store",
            )
            with self.assertRaisesRegex(Exception, "requires one of"):
                runtime.execute("identity.get-connections", {}, ExecutionOptions())
            result = runtime.execute(
                "identity.get-connections",
                {"headers": {"Xero-Tenant-Id": TENANT_ID}},
                ExecutionOptions(),
            )
            self.assertTrue(result["ok"])
            self.assertIsNone(result["tenant"])
            self.assertEqual(transport.calls[0]["headers"]["Xero-Tenant-Id"], TENANT_ID)
            self.assertNotIn("xero-tenant-id", transport.calls[0]["headers"])

    def test_asset_finance_and_project_reads_do_not_expose_private_values(self) -> None:
        cases = (
            (
                "assets.get-assets",
                "assets.read",
                {"query": {"status": "REGISTERED"}},
                {
                    "Assets": [
                        {
                            "AssetId": "private-asset-id",
                            "AssetName": "Private laptop",
                            "PurchasePrice": 1234.56,
                        }
                    ]
                },
                ("private-asset-id", "Private laptop", "1234.56"),
            ),
            (
                "finance.get-cash-validation",
                "finance.cashvalidation.read",
                {},
                {
                    "CashValidation": {
                        "AccountId": "private-account-id",
                        "Balance": 9876.54,
                    }
                },
                ("private-account-id", "9876.54"),
            ),
            (
                "projects.get-project-users",
                "projects.read",
                {},
                {
                    "items": [
                        {
                            "userId": "private-user-id",
                            "name": "Private User",
                            "email": "private-user@example.com",
                        }
                    ]
                },
                ("private-user-id", "Private User", "private-user@example.com"),
            ),
        )
        for command, scope, input_data, body, private_values in cases:
            with self.subTest(command=command), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                token_store, tenant_store = self._stores(root, scope)
                transport = FakeTransport(
                    [
                        HttpResponse(
                            status=200,
                            headers={"content-type": "application/json"},
                            body=json.dumps(body).encode(),
                            url="https://api.xero.com/fixed-test",
                        )
                    ]
                )
                runtime = XeroRuntime(load_registry(), transport, token_store, tenant_store)
                rendered = json.dumps(runtime.execute(command, input_data, ExecutionOptions()))
                for private_value in private_values:
                    self.assertNotIn(private_value, rendered)

    def test_payroll_reads_mask_every_provider_leaf_in_normal_stdout(self) -> None:
        cases = (
            (
                "payroll-uk.get-employees",
                "payroll.employees.read",
                "UK",
                {
                    "employees": [
                        {
                            "NationalInsuranceNumber": "QQ123456C",
                            "MiddleNames": "Private Middle",
                            "Gender": "F",
                            "StartDate": "2026-01-02",
                            "TerminationDate": "2026-07-03",
                            "JobTitle": "Private Job",
                        }
                    ]
                },
            ),
            (
                "payroll-nz.get-employees",
                "payroll.employees.read",
                "NZ",
                {"employees": [{"IRDNumber": "123-456-789", "JobTitle": "Private NZ Job"}]},
            ),
        )
        for command, scope, region, body in cases:
            with self.subTest(command=command), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                token_store, tenant_store = self._stores(root, scope)
                tenant = tenant_store.read()
                tenant["region"] = region
                tenant_store.write(tenant)
                transport = FakeTransport(
                    [
                        HttpResponse(
                            200,
                            {"content-type": "application/json"},
                            json.dumps(body).encode(),
                            "https://api.xero.com/payroll-test",
                        )
                    ]
                )
                runtime = XeroRuntime(load_registry(), transport, token_store, tenant_store)
                rendered = json.dumps(runtime.execute(command, {}, ExecutionOptions()))
                for leaf in (
                    "QQ123456C",
                    "Private Middle",
                    "F",
                    "2026-01-02",
                    "2026-07-03",
                    "Private Job",
                    "123-456-789",
                    "Private NZ Job",
                ):
                    self.assertNotIn(leaf, rendered)

    def test_sensitive_write_receipt_masks_every_provider_leaf(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            token_store, tenant_store = self._stores(root, "payroll.employees")
            tenant = tenant_store.read()
            tenant["region"] = "UK"
            tenant_store.write(tenant)
            response = {
                "employee": {
                    "NationalInsuranceNumber": "QQ123456C",
                    "MiddleNames": "Private Middle",
                    "Gender": "F",
                    "JobTitle": "Private Job",
                }
            }
            transport = FakeTransport(
                [
                    HttpResponse(
                        200,
                        {"content-type": "application/json"},
                        json.dumps(response).encode(),
                        "https://api.xero.com/payroll.xro/2.0/Employees",
                    )
                ]
            )
            runtime = XeroRuntime(load_registry(), transport, token_store, tenant_store)
            plan_path = root / "employee-plan.json"
            receipt_path = root / "employee-receipt.json"
            runtime.execute(
                "payroll-uk.create-employee",
                {
                    "body": {
                        "address": {
                            "addressLine1": "Private street",
                            "city": "Private city",
                            "postCode": "AB1 2CD",
                        },
                        "dateOfBirth": "1990-01-01",
                        "firstName": "Private",
                        "gender": "F",
                        "lastName": "Employee",
                        "title": "Mx",
                    }
                },
                ExecutionOptions(plan_out=plan_path),
            )
            runtime.execute(
                "payroll-uk.create-employee",
                {},
                ExecutionOptions(
                    apply=True,
                    plan_in=plan_path,
                    receipt_out=receipt_path,
                    approve=True,
                    approve_high_risk=True,
                    ack_no_snapshot=True,
                ),
            )
            rendered = receipt_path.read_text(encoding="utf-8")
            for leaf in ("QQ123456C", "Private Middle", "F", "Private Job"):
                self.assertNotIn(leaf, rendered)

    def test_asset_write_plan_requires_separate_high_risk_approval(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            token_store, tenant_store = self._stores(root, "assets")
            runtime = XeroRuntime(load_registry(), FakeTransport([]), token_store, tenant_store)
            plan_path = root / "asset-plan.json"
            planned = runtime.execute(
                "assets.create-asset",
                {"body": {"assetName": "Private laptop"}},
                ExecutionOptions(plan_out=plan_path),
            )
            self.assertTrue(planned["extra_approval_required"])
            with self.assertRaisesRegex(Exception, "high-risk"):
                runtime.execute(
                    "assets.create-asset",
                    {},
                    ExecutionOptions(apply=True, plan_in=plan_path, approve=True),
                )

    def test_available_before_state_is_saved_to_a_private_snapshot(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            token_store, tenant_store = self._stores(root, "projects")
            before_body = b'{"projectId":"project-1","name":"Before name"}'
            transport = FakeTransport(
                [
                    HttpResponse(
                        status=200,
                        headers={"content-type": "application/json"},
                        body=before_body,
                        url="https://api.xero.com/projects.xro/2.0/Projects/project-1",
                    )
                ]
            )
            runtime = XeroRuntime(load_registry(), transport, token_store, tenant_store)
            plan_path = root / "project-plan.json"
            planned = runtime.execute(
                "projects.update-project",
                {"path": {"projectId": PROJECT_ID}, "body": {"name": "After name"}},
                ExecutionOptions(plan_out=plan_path),
            )
            self.assertFalse(planned["no_snapshot"])
            plan = json.loads(plan_path.read_text(encoding="utf-8"))
            snapshot_path = Path(plan["snapshot"]["protected_path"])
            self.assertEqual(snapshot_path.read_bytes(), before_body)
            self.assertEqual(snapshot_path.stat().st_mode & 0o777, 0o600)
            self.assertEqual(len(transport.calls), 1)
            self.assertEqual(transport.calls[0]["method"], "GET")

    def test_apply_refuses_when_the_provider_target_changed_after_review(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            token_store, tenant_store = self._stores(root, "projects")
            transport = FakeTransport(
                [
                    HttpResponse(
                        200,
                        {"content-type": "application/json"},
                        b'{"projectId":"project-1","name":"Reviewed"}',
                        "https://api.xero.com/projects.xro/2.0/Projects/project-1",
                    ),
                    HttpResponse(
                        200,
                        {"content-type": "application/json"},
                        b'{"projectId":"project-1","name":"Changed elsewhere"}',
                        "https://api.xero.com/projects.xro/2.0/Projects/project-1",
                    ),
                ]
            )
            runtime = XeroRuntime(load_registry(), transport, token_store, tenant_store)
            plan_path = root / "project-plan.json"
            runtime.execute(
                "projects.update-project",
                {"path": {"projectId": PROJECT_ID}, "body": {"name": "Approved change"}},
                ExecutionOptions(plan_out=plan_path),
            )
            with self.assertRaisesRegex(Exception, "target changed after planning"):
                runtime.execute(
                    "projects.update-project",
                    {},
                    ExecutionOptions(
                        apply=True,
                        plan_in=plan_path,
                        approve=True,
                        approve_high_risk=True,
                    ),
                )
            self.assertEqual([call["method"] for call in transport.calls], ["GET", "GET"])

    def test_apply_refuses_missing_or_changed_saved_snapshot(self) -> None:
        for mutation in ("changed", "missing"):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                token_store, tenant_store = self._stores(root, "projects")
                before_body = b'{"projectId":"project-1","name":"Before name"}'
                transport = FakeTransport(
                    [
                        HttpResponse(
                            status=200,
                            headers={"content-type": "application/json"},
                            body=before_body,
                            url="https://api.xero.com/projects.xro/2.0/Projects/project-1",
                        )
                    ]
                )
                runtime = XeroRuntime(load_registry(), transport, token_store, tenant_store)
                plan_path = root / "project-plan.json"
                runtime.execute(
                    "projects.update-project",
                    {
                        "path": {"projectId": PROJECT_ID},
                        "body": {"name": "After name"},
                    },
                    ExecutionOptions(plan_out=plan_path),
                )
                plan = json.loads(plan_path.read_text(encoding="utf-8"))
                snapshot_path = Path(plan["snapshot"]["protected_path"])
                if mutation == "changed":
                    snapshot_path.write_bytes(b"tampered snapshot")
                else:
                    snapshot_path.unlink()
                with self.assertRaisesRegex(Exception, "saved snapshot"):
                    runtime.execute(
                        "projects.update-project",
                        {},
                        ExecutionOptions(
                            apply=True,
                            plan_in=plan_path,
                            approve=True,
                            approve_high_risk=True,
                        ),
                    )
                self.assertEqual(len(transport.calls), 1)

    def test_delete_verification_accepts_only_expected_not_found(self) -> None:
        for verification_status, expected_outcome, expected_ok in (
            (404, "verified_absent", True),
            (403, "absence_unverified", False),
            (200, "still_present", False),
        ):
            with (
                self.subTest(verification_status=verification_status),
                tempfile.TemporaryDirectory() as tmp,
            ):
                root = Path(tmp)
                token_store, tenant_store = self._stores(root, "projects")
                transport = FakeTransport(
                    [
                        HttpResponse(
                            status=200,
                            headers={"content-type": "application/json"},
                            body=b'{"taskId":"task-1","name":"Before"}',
                            url="https://api.xero.com/projects.xro/2.0/Projects/project-1/Tasks/task-1",
                        ),
                        HttpResponse(
                            status=200,
                            headers={"content-type": "application/json"},
                            body=b'{"taskId":"task-1","name":"Before"}',
                            url="https://api.xero.com/projects.xro/2.0/Projects/project-1/Tasks/task-1",
                        ),
                        HttpResponse(
                            status=204,
                            headers={},
                            body=b"",
                            url="https://api.xero.com/projects.xro/2.0/Projects/project-1/Tasks/task-1",
                        ),
                        HttpResponse(
                            status=verification_status,
                            headers={"content-type": "application/json"},
                            body=b'{"error":"not available"}',
                            url="https://api.xero.com/projects.xro/2.0/Projects/project-1/Tasks/task-1",
                        ),
                    ]
                )
                runtime = XeroRuntime(load_registry(), transport, token_store, tenant_store)
                plan_path = root / "delete-plan.json"
                runtime.execute(
                    "projects.delete-task",
                    {"path": {"projectId": PROJECT_ID, "taskId": TASK_ID}},
                    ExecutionOptions(plan_out=plan_path),
                )
                result = runtime.execute(
                    "projects.delete-task",
                    {},
                    ExecutionOptions(
                        apply=True,
                        plan_in=plan_path,
                        approve=True,
                        approve_high_risk=True,
                    ),
                )
                self.assertEqual(result["verification"]["outcome"], expected_outcome)
                self.assertEqual(result["ok"], expected_ok)
                if expected_ok:
                    self.assertEqual(result["provider_outcome"], "accepted_not_stronger_state")
                else:
                    self.assertEqual(
                        result["provider_outcome"], "verification_failed_or_partial"
                    )
                self.assertEqual(len(transport.calls), 4)

    def test_receipt_reservation_failure_makes_zero_provider_calls(self) -> None:
        for failure in ("existing", "invalid_parent"):
            with self.subTest(failure=failure), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                token_store, tenant_store = self._stores(root, "accounting.invoices")
                transport = FakeTransport([])
                runtime = XeroRuntime(load_registry(), transport, token_store, tenant_store)
                plan_path = root / "invoice-plan.json"
                runtime.execute(
                    "accounting.create-invoices",
                    {"body": {"Invoices": [{"Type": "ACCREC", "Status": "DRAFT"}]}},
                    ExecutionOptions(plan_out=plan_path),
                )
                if failure == "existing":
                    receipt_path = root / "existing-receipt.json"
                    receipt_path.write_text("do not overwrite", encoding="utf-8")
                else:
                    blocked_parent = root / "blocked-parent"
                    blocked_parent.write_text("not a directory", encoding="utf-8")
                    receipt_path = blocked_parent / "receipt.json"
                with self.assertRaisesRegex(Exception, "Receipt path"):
                    runtime.execute(
                        "accounting.create-invoices",
                        {},
                        ExecutionOptions(
                            apply=True,
                            plan_in=plan_path,
                            receipt_out=receipt_path,
                            approve=True,
                            approve_high_risk=True,
                            ack_no_snapshot=True,
                        ),
                    )
                self.assertEqual(transport.calls, [])

    def test_reviewed_plan_cannot_be_applied_twice(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            token_store, tenant_store = self._stores(root, "accounting.invoices")
            response = HttpResponse(
                status=200,
                headers={"content-type": "application/json"},
                body=b'{"Invoices":[]}',
                url="https://api.xero.com/api.xro/2.0/Invoices",
            )
            transport = FakeTransport([response])
            runtime = XeroRuntime(load_registry(), transport, token_store, tenant_store)
            plan_path = root / "invoice-plan.json"
            runtime.execute(
                "accounting.create-invoices",
                {"body": {"Invoices": [{"Type": "ACCREC", "Status": "DRAFT"}]}},
                ExecutionOptions(plan_out=plan_path),
            )
            common = {
                "apply": True,
                "plan_in": plan_path,
                "approve": True,
                "approve_high_risk": True,
                "ack_no_snapshot": True,
            }
            runtime.execute(
                "accounting.create-invoices",
                {},
                ExecutionOptions(receipt_out=root / "first-receipt.json", **common),
            )
            transport.responses.append(response)
            with self.assertRaisesRegex(Exception, "already has an execution record"):
                runtime.execute(
                    "accounting.create-invoices",
                    {},
                    ExecutionOptions(receipt_out=root / "second-receipt.json", **common),
                )
            self.assertEqual(len(transport.calls), 1)

    def test_identical_no_idempotency_actions_can_create_two_new_reviewable_plans(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            token_store, tenant_store = self._stores(root, "accounting.contacts")
            transport = FakeTransport(
                [
                    HttpResponse(204, {}, b"", "https://api.xero.com/delete-1"),
                    HttpResponse(204, {}, b"", "https://api.xero.com/delete-2"),
                ]
            )
            runtime = XeroRuntime(load_registry(), transport, token_store, tenant_store)
            input_data = {
                "path": {
                    "ContactGroupID": "11111111-1111-4111-8111-111111111111",
                    "ContactID": "22222222-2222-4222-8222-222222222222",
                }
            }
            plan_paths = [root / "plan-1.json", root / "plan-2.json"]
            plans = []
            for path in plan_paths:
                runtime.execute(
                    "accounting.delete-contact-group-contact",
                    input_data,
                    ExecutionOptions(plan_out=path),
                )
                plans.append(json.loads(path.read_text(encoding="utf-8")))
            self.assertNotEqual(plans[0]["plan_id"], plans[1]["plan_id"])
            self.assertNotEqual(plans[0]["plan_nonce"], plans[1]["plan_nonce"])
            for index, path in enumerate(plan_paths, start=1):
                runtime.execute(
                    "accounting.delete-contact-group-contact",
                    {},
                    ExecutionOptions(
                        apply=True,
                        plan_in=path,
                        receipt_out=root / f"receipt-{index}.json",
                        approve=True,
                        approve_high_risk=True,
                        ack_no_snapshot=True,
                    ),
                )
            self.assertEqual(len(transport.calls), 2)

    def test_generated_idempotency_key_is_saved_in_plan_and_sent_unchanged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            token_store, tenant_store = self._stores(root, "accounting.settings")
            transport = FakeTransport(
                [
                    HttpResponse(
                        200,
                        {"content-type": "application/json"},
                        b'{"Accounts":[]}',
                        "https://api.xero.com/api.xro/2.0/Accounts",
                    )
                ]
            )
            runtime = XeroRuntime(load_registry(), transport, token_store, tenant_store)
            plan_path = root / "account-plan.json"
            runtime.execute(
                "accounting.create-account",
                {"body": {"Code": "999", "Name": "Test expense", "Type": "EXPENSE"}},
                ExecutionOptions(plan_out=plan_path),
            )
            plan = json.loads(plan_path.read_text(encoding="utf-8"))
            self.assertRegex(plan["idempotency_key"], r"^[0-9a-f-]{36}$")
            runtime.execute(
                "accounting.create-account",
                {},
                ExecutionOptions(
                    apply=True,
                    plan_in=plan_path,
                    approve=True,
                    approve_high_risk=True,
                    ack_no_snapshot=True,
                ),
            )
            self.assertEqual(
                transport.calls[0]["headers"]["Idempotency-Key"],
                plan["idempotency_key"],
            )

    def test_explicit_idempotency_key_is_rejected_for_unsupported_reads_and_writes(self) -> None:
        cases = (
            (
                "accounting.get-invoices",
                "accounting.invoices.read",
                {},
            ),
            (
                "accounting.delete-contact-group-contact",
                "accounting.contacts",
                {
                    "path": {
                        "ContactGroupID": "11111111-1111-4111-8111-111111111111",
                        "ContactID": "22222222-2222-4222-8222-222222222222",
                    }
                },
            ),
        )
        for command, scope, input_data in cases:
            with self.subTest(command=command), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                token_store, tenant_store = self._stores(root, scope)
                transport = FakeTransport([])
                runtime = XeroRuntime(load_registry(), transport, token_store, tenant_store)
                with self.assertRaisesRegex(Exception, "does not document Idempotency-Key"):
                    runtime.execute(
                        command,
                        input_data,
                        ExecutionOptions(idempotency_key="unsupported-key"),
                    )
                self.assertEqual(transport.calls, [])

    def test_nonempty_provider_validation_errors_fail_and_are_receipted(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            token_store, tenant_store = self._stores(root, "accounting.invoices")
            transport = FakeTransport(
                [
                    HttpResponse(
                        200,
                        {"content-type": "application/json"},
                        b'{"Invoices":[{"ValidationErrors":[{"Message":"Invalid account"}]}]}',
                        "https://api.xero.com/api.xro/2.0/Invoices",
                    )
                ]
            )
            runtime = XeroRuntime(load_registry(), transport, token_store, tenant_store)
            plan_path = root / "invoice-plan.json"
            receipt_path = root / "invoice-receipt.json"
            runtime.execute(
                "accounting.create-invoices",
                {"body": {"Invoices": [{"Type": "ACCREC", "Status": "DRAFT"}]}},
                ExecutionOptions(plan_out=plan_path),
            )
            result = runtime.execute(
                "accounting.create-invoices",
                {},
                ExecutionOptions(
                    apply=True,
                    plan_in=plan_path,
                    receipt_out=receipt_path,
                    approve=True,
                    approve_high_risk=True,
                    ack_no_snapshot=True,
                ),
            )
            self.assertFalse(result["ok"])
            self.assertEqual(result["provider_outcome"], "validation_failed_or_partial")
            receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
            self.assertEqual(receipt["provider_outcome"], "validation_failed_or_partial")
            self.assertTrue(receipt["validation_errors"])

    def test_bank_feed_2xx_rejected_items_are_partial_failures(self) -> None:
        cases = (
            (
                "bank-feeds.create-feed-connections",
                {"items": [{"status": "REJECTED", "error": {"detail": "invalid feed"}}]},
            ),
            (
                "bank-feeds.create-statements",
                {"items": [{"status": "REJECTED", "errors": [{"detail": "invalid line"}]}]},
            ),
        )
        for command, provider_body in cases:
            with self.subTest(command=command), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                token_store, tenant_store = self._stores(root, "bankfeeds")
                transport = FakeTransport(
                    [
                        HttpResponse(
                            200,
                            {"content-type": "application/json"},
                            json.dumps(provider_body).encode(),
                            "https://api.xero.com/bankfeeds.xro/1.0/test",
                        )
                    ]
                )
                runtime = XeroRuntime(load_registry(), transport, token_store, tenant_store)
                plan_path = root / "plan.json"
                receipt_path = root / "receipt.json"
                runtime.execute(command, {"body": {}}, ExecutionOptions(plan_out=plan_path))
                result = runtime.execute(
                    command,
                    {},
                    ExecutionOptions(
                        apply=True,
                        plan_in=plan_path,
                        receipt_out=receipt_path,
                        approve=True,
                        approve_high_risk=True,
                        ack_no_snapshot=True,
                    ),
                )
                self.assertFalse(result["ok"])
                self.assertEqual(
                    result["provider_outcome"], "validation_failed_or_partial"
                )
                receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
                self.assertTrue(receipt["validation_errors"])

    def test_accounting_explicit_error_flags_make_2xx_a_partial_failure(self) -> None:
        for signal in (
            {"HasErrors": True},
            {"HasValidationErrors": True},
            {"StatusAttributeString": "ERROR"},
        ):
            with self.subTest(signal=signal), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                token_store, tenant_store = self._stores(root, "accounting.invoices")
                transport = FakeTransport(
                    [
                        HttpResponse(
                            200,
                            {"content-type": "application/json"},
                            json.dumps({"Invoices": [signal]}).encode(),
                            "https://api.xero.com/api.xro/2.0/Invoices",
                        )
                    ]
                )
                runtime = XeroRuntime(load_registry(), transport, token_store, tenant_store)
                plan_path = root / "plan.json"
                runtime.execute(
                    "accounting.create-invoices",
                    {"body": {"Invoices": [{"Type": "ACCREC"}]}},
                    ExecutionOptions(plan_out=plan_path),
                )
                result = runtime.execute(
                    "accounting.create-invoices",
                    {},
                    ExecutionOptions(
                        apply=True,
                        plan_in=plan_path,
                        approve=True,
                        approve_high_risk=True,
                        ack_no_snapshot=True,
                    ),
                )
                self.assertFalse(result["ok"])
                self.assertEqual(
                    result["provider_outcome"], "validation_failed_or_partial"
                )


if __name__ == "__main__":
    unittest.main()

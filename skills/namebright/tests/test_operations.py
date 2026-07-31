from __future__ import annotations

import re
import unittest
from collections import Counter
from pathlib import Path

from namebright_safe_cli.operations import (
    OPERATIONS,
    family_counts,
    get_operation,
    method_counts,
)

DOC_PATH = Path(__file__).resolve().parents[1] / "docs" / "api_coverage.md"


def parse_coverage_rows() -> list[tuple[str, str, str, str, str, str]]:
    """Return (family, method, path, command, family, body) from docs rows."""
    text = DOC_PATH.read_text(encoding="utf-8")
    out: list[tuple[str, str, str, str, str, str]] = []
    for line in text.splitlines():
        if not re.match(r"^\|\s*\d+\s*\|", line):
            continue
        cols = [x.strip() for x in line.strip().strip("|").split("|")]
        if len(cols) < 6:
            continue
        out.append((cols[1], cols[2], cols[3], cols[4], cols[5], cols[6]))
    return out


class TestNameBrightOperations(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.doc_rows = parse_coverage_rows()
        cls.op_by_key = { (op.family, op.command): op for op in OPERATIONS }

    def test_rows_match_locked_coverage(self) -> None:
        self.assertEqual(len(self.doc_rows), 61)
        self.assertEqual(len(OPERATIONS), 61)

        keys = [(op.family, op.command) for op in OPERATIONS]
        self.assertEqual(len(set(keys)), 61)
        self.assertEqual(len(keys), len(set(keys)))

        families = [op.family for op in OPERATIONS]
        self.assertEqual(set(families), {
            "auth",
            "purchase",
            "account",
            "domains",
            "contacts",
            "nameservers",
            "host-records",
            "inbound-push",
            "outbound-push",
            "whois-accuracy",
            "contact-verification",
        })

        self.assertEqual(len(set(families)), 11)

        doc_methods = Counter(row[1] for row in self.doc_rows)
        actual_methods = method_counts()
        self.assertEqual(doc_methods, actual_methods)

        family_counter = Counter(row[0] for row in self.doc_rows)
        self.assertEqual(dict(family_counter), family_counts())

    def test_exact_path_query_and_command_variants(self) -> None:
        expected = {(row[0], row[1], row[2], row[4]) for row in self.doc_rows}
        actual = {(op.family, op.method, op.path, op.command) for op in OPERATIONS}
        self.assertEqual(expected, actual)

    def test_fields_no_raw_names(self) -> None:
        forbidden = {"url", "method", "path", "payload", "body_file"}
        for op in OPERATIONS:
            for field in op.fields:
                self.assertNotIn(field.api_name, forbidden)
                self.assertNotIn(field.cli_name, forbidden)

    def test_cli_field_names_and_secret_file_naming(self) -> None:
        for op in OPERATIONS:
            for field in op.fields:
                if field.source == "cli":
                    self.assertTrue(
                        isinstance(field.cli_name, str) and field.cli_name,
                        f"{op.family}:{op.command} field {field.api_name} missing cli_name",
                    )
                if field.kind == "secret_file":
                    self.assertIsNotNone(field.cli_name)
                    self.assertTrue(
                        field.cli_name.endswith("-file"),
                        f"{op.family}:{op.command} field {field.api_name} secret_file cli_name must end -file",
                    )

    def test_auth_token_is_post_and_non_write(self) -> None:
        token = get_operation("auth", "auth token")
        self.assertIsNotNone(token)
        assert token is not None
        self.assertEqual(token.method, "POST")
        self.assertFalse(token.write_capable)
        self.assertEqual(token.secret_response_fields, ("access_token",))
        self.assertEqual(token.snapshot_commands, tuple())
        self.assertEqual(token.verify_commands, tuple())

    def test_sensitive_response_coverage(self) -> None:
        account_show = get_operation("account", "account show")
        domains_list = get_operation("domains", "domains list")
        domains_get = get_operation("domains", "domains get")
        domains_update = get_operation("domains", "domains update")
        self.assertIsNotNone(account_show)
        self.assertIsNotNone(domains_list)
        self.assertIsNotNone(domains_get)
        self.assertIsNotNone(domains_update)
        assert account_show is not None and domains_list is not None and domains_get is not None and domains_update is not None
        self.assertEqual(account_show.secret_response_fields, ("AccountBalance",))
        self.assertEqual(domains_list.secret_response_fields, ("AuthCode",))
        self.assertEqual(domains_get.secret_response_fields, ("AuthCode",))
        self.assertEqual(domains_update.secret_response_fields, ("AuthCode",))

    def test_no_auth_code_input_fields(self) -> None:
        domains_update = get_operation("domains", "domains update")
        self.assertIsNotNone(domains_update)
        assert domains_update is not None

        body_fields = [f for f in domains_update.fields if f.location == "body"]
        self.assertFalse(any(f.api_name == "AuthCode" for f in body_fields))
        self.assertIn("AuthCode", domains_update.secret_response_fields)

        names = {f.api_name for f in body_fields}
        self.assertEqual(names, {"Locked", "AutoRenew", "WhoIsPrivacy"})

    def test_required_acks(self) -> None:
        expectations = {
            ("purchase", "purchase register"): {"ack_spend"},
            ("purchase", "purchase renew"): {"ack_spend"},
            ("domains", "domains update"): {"ack_high_risk"},
            ("inbound-push", "inbound-push accept-query"): {
                "ack_ownership",
                "ack_no_snapshot",
                "ack_irreversible",
            },
            ("inbound-push", "inbound-push accept-path"): {
                "ack_ownership",
                "ack_no_snapshot",
                "ack_irreversible",
            },
            ("inbound-push", "inbound-push decline-query"): {
                "ack_destructive",
                "ack_high_risk",
            },
            ("inbound-push", "inbound-push decline-path"): {
                "ack_destructive",
                "ack_high_risk",
            },
            ("outbound-push", "outbound-push force-query"): {
                "ack_high_risk",
                "ack_ownership",
                "ack_no_snapshot",
                "ack_irreversible",
                "ack_account_creation",
                "ack_external_message",
            },
            ("outbound-push", "outbound-push force-path"): {
                "ack_high_risk",
                "ack_ownership",
                "ack_no_snapshot",
                "ack_irreversible",
                "ack_account_creation",
                "ack_external_message",
            },
            ("outbound-push", "outbound-push initiate-query"): {
                "ack_high_risk",
                "ack_ownership",
                "ack_no_snapshot",
                "ack_irreversible",
                "ack_external_message",
            },
            ("outbound-push", "outbound-push initiate-path"): {
                "ack_high_risk",
                "ack_ownership",
                "ack_no_snapshot",
                "ack_irreversible",
                "ack_external_message",
            },
            ("outbound-push", "outbound-push cancel-query"): {"ack_destructive", "ack_high_risk"},
            ("outbound-push", "outbound-push cancel-path"): {"ack_destructive", "ack_high_risk"},
            ("contact-verification", "contact-verification send-email"): {
                "ack_high_risk",
                "ack_external_message",
            },
            ("contact-verification", "contact-verification send-phone"): {
                "ack_high_risk",
                "ack_external_message",
            },
            ("contact-verification", "contact-verification verify-contact"): {"ack_high_risk"},
            ("contact-verification", "contact-verification verify-email"): {"ack_high_risk"},
            ("contact-verification", "contact-verification verify-phone"): {"ack_high_risk"},
        }

        for (family, command), expected in expectations.items():
            spec = get_operation(family, command)
            self.assertIsNotNone(spec)
            assert spec is not None
            self.assertEqual(set(spec.required_acks), expected)

    def test_risk_and_flags(self) -> None:
        expectations = {
            ("inbound-push", "inbound-push accept-query"): ("high", True, False),
            ("inbound-push", "inbound-push accept-path"): ("high", True, False),
            ("inbound-push", "inbound-push decline-query"): ("high", False, False),
            ("inbound-push", "inbound-push decline-path"): ("high", False, False),
            ("outbound-push", "outbound-push force-query"): ("high", True, True),
            ("outbound-push", "outbound-push force-path"): ("high", True, True),
            ("outbound-push", "outbound-push initiate-query"): ("high", True, True),
            ("outbound-push", "outbound-push initiate-path"): ("high", True, True),
            ("outbound-push", "outbound-push cancel-query"): ("high", False, False),
            ("outbound-push", "outbound-push cancel-path"): ("high", False, False),
            ("contact-verification", "contact-verification send-email"): ("high", False, True),
            ("contact-verification", "contact-verification send-phone"): ("high", False, True),
            ("contact-verification", "contact-verification verify-contact"): ("high", False, False),
            ("contact-verification", "contact-verification verify-email"): ("high", False, False),
            ("contact-verification", "contact-verification verify-phone"): ("high", False, False),
        }
        for (family, command), (risk, no_snapshot, external_message) in expectations.items():
            spec = get_operation(family, command)
            self.assertIsNotNone(spec)
            assert spec is not None
            self.assertEqual(spec.risk, risk)
            self.assertEqual(spec.no_snapshot, no_snapshot)
            self.assertEqual(spec.external_message, external_message)

    def test_write_ack_profiles_for_contact_domains_nameservers_host(self) -> None:
        for op in OPERATIONS:
            if op.method in {"PUT", "POST"} and op.family in {"domains", "contacts", "nameservers", "host-records"}:
                self.assertIn("ack_high_risk", op.required_acks)
            if op.method == "DELETE" and op.family in {"host-records", "nameservers", "outbound-push", "inbound-push"}:
                self.assertIn("ack_destructive", op.required_acks)

    def test_pagination_defaults(self) -> None:
        for op in OPERATIONS:
            for field in op.fields:
                if field.api_name == "page":
                    self.assertEqual(field.location, "query")
                    self.assertFalse(field.required)
                    self.assertEqual(field.default, 1)
                    self.assertTrue(field.positive)
                if field.api_name == "domainsPerPage":
                    self.assertEqual(field.location, "query")
                    self.assertFalse(field.required)
                    self.assertEqual(field.default, 50)
                    self.assertTrue(field.positive)

    def test_verification_secret_code_fields(self) -> None:
        for command in ("verify-contact", "verify-email", "verify-phone"):
            spec = get_operation("contact-verification", f"contact-verification {command}")
            self.assertIsNotNone(spec)
            assert spec is not None

            code_field_name = "VerificationCode" if command != "verify-contact" else "LinkAuthCode"
            expected_cli_name = (
                "verification-code-file" if code_field_name == "VerificationCode" else "link-auth-code-file"
            )
            code_fields = [f for f in spec.fields if f.api_name == code_field_name]
            self.assertEqual(len(code_fields), 1)
            code_field = code_fields[0]
            self.assertEqual(code_field.kind, "secret_file")
            self.assertTrue(code_field.secret)
            self.assertEqual(code_field.cli_name, expected_cli_name)

            for f in spec.fields:
                if f.location == "body" and f.api_name == code_field_name:
                    self.assertEqual(f.kind, "secret_file")

    def test_contact_verification_send_phone_method_choices(self) -> None:
        spec = get_operation("contact-verification", "contact-verification send-phone")
        self.assertIsNotNone(spec)
        assert spec is not None
        method_field = next(f for f in spec.fields if f.api_name == "PhoneNumberVerificationMethod")
        self.assertEqual(method_field.choices, ("Sms", "Voice"))
        self.assertTrue(method_field.required)

    def test_write_requires_body_and_fields(self) -> None:
        # Domain update, contacts/nameserver/host writes, pushes, and verification actions
        # must declare a body layout and require a non-empty body.
        expected_body_commands = {
            ("domains", "domains update"),
            ("contacts", "contacts update-administrative"),
            ("contacts", "contacts update-all"),
            ("contacts", "contacts update-registrant"),
            ("contacts", "contacts update-technical"),
            ("host-records", "host-records create-a"),
            ("host-records", "host-records create-aaaa"),
            ("host-records", "host-records create-cname"),
            ("host-records", "host-records create-mx"),
            ("host-records", "host-records create-srv"),
            ("host-records", "host-records create-txt"),
            ("outbound-push", "outbound-push force-query"),
            ("outbound-push", "outbound-push force-path"),
            ("contact-verification", "contact-verification send-email"),
            ("contact-verification", "contact-verification send-phone"),
            ("contact-verification", "contact-verification verify-contact"),
            ("contact-verification", "contact-verification verify-email"),
            ("contact-verification", "contact-verification verify-phone"),
            ("purchase", "purchase register"),
            ("purchase", "purchase renew"),
            ("auth", "auth token"),
        }
        for family, command in expected_body_commands:
            spec = get_operation(family, command)
            self.assertIsNotNone(spec)
            assert spec is not None
            body_fields = tuple(f for f in spec.fields if f.location == "body")
            self.assertTrue(body_fields)
            self.assertTrue(spec.require_nonempty_body)

    def test_snapshot_and_verify_metadata(self) -> None:
        expected = {
            ("purchase", "purchase register"),
            ("purchase", "purchase renew"),
            ("domains", "domains update"),
            ("contacts", "contacts update-administrative"),
            ("contacts", "contacts update-all"),
            ("contacts", "contacts update-registrant"),
            ("contacts", "contacts update-technical"),
            ("nameservers", "nameservers add"),
            ("nameservers", "nameservers delete"),
            ("nameservers", "nameservers delete-all"),
            ("host-records", "host-records create-a"),
            ("host-records", "host-records create-aaaa"),
            ("host-records", "host-records create-cname"),
            ("host-records", "host-records create-mx"),
            ("host-records", "host-records create-srv"),
            ("host-records", "host-records create-txt"),
            ("host-records", "host-records delete-a"),
            ("host-records", "host-records delete-aaaa"),
            ("host-records", "host-records delete-cname"),
            ("host-records", "host-records delete-mx"),
            ("host-records", "host-records delete-srv"),
            ("host-records", "host-records delete-txt"),
            ("outbound-push", "outbound-push force-query"),
            ("outbound-push", "outbound-push force-path"),
            ("outbound-push", "outbound-push initiate-query"),
            ("outbound-push", "outbound-push initiate-path"),
            ("outbound-push", "outbound-push cancel-query"),
            ("outbound-push", "outbound-push cancel-path"),
            ("inbound-push", "inbound-push accept-query"),
            ("inbound-push", "inbound-push accept-path"),
            ("inbound-push", "inbound-push decline-query"),
            ("inbound-push", "inbound-push decline-path"),
            ("contact-verification", "contact-verification verify-contact"),
            ("contact-verification", "contact-verification verify-email"),
            ("contact-verification", "contact-verification verify-phone"),
        }
        for family, command in expected:
            spec = get_operation(family, command)
            self.assertIsNotNone(spec)
            assert spec is not None
            self.assertTrue(spec.snapshot_commands)
            self.assertTrue(spec.verify_commands)
            for cmd in spec.snapshot_commands + spec.verify_commands:
                self.assertIn(cmd, {f"{op.family}:{op.command}" for op in OPERATIONS})

    def test_get_operation_lookup(self) -> None:
        self.assertIsNone(get_operation("contacts", "contacts get"))
        self.assertIsNotNone(get_operation("contacts", "contacts get-administrative"))
        self.assertIsNone(get_operation("contacts", "not-a-command"))

    def test_host_record_bodies_and_forcepush_require_email(self) -> None:
        host_cases: list[tuple[str, tuple[str, ...]]] = [
            ("host-records create-a", ("Subdomain", "IPV4Address", "RecordId")),
            ("host-records create-aaaa", ("Subdomain", "IPV6Address", "RecordId")),
            ("host-records create-cname", ("Subdomain", "RedirectDomain", "RecordId")),
            ("host-records create-mx", ("Subdomain", "MailServer", "Priority", "RecordId")),
            (
                "host-records create-srv",
                ("Service", "Protocol", "Priority", "Weight", "Port", "Target", "RecordId"),
            ),
            ("host-records create-txt", ("Subdomain", "TextRecord", "RecordId")),
        ]
        for command, expected in host_cases:
            spec = get_operation("host-records", command)
            self.assertIsNotNone(spec)
            assert spec is not None
            body = tuple(f.api_name for f in spec.fields if f.location == "body")
            self.assertEqual(body, expected)
            self.assertFalse(any(f.api_name == "RecordId" and f.required for f in spec.fields if f.location == "body"))

        force_query = get_operation("outbound-push", "outbound-push force-query")
        force_path = get_operation("outbound-push", "outbound-push force-path")
        for spec in (force_query, force_path):
            self.assertIsNotNone(spec)
            assert spec is not None
            body = tuple(f.api_name for f in spec.fields if f.location == "body")
            self.assertEqual(body, (
                "FirstName",
                "LastName",
                "Organization",
                "Department",
                "Email",
                "Address1",
                "Address2",
                "City",
                "Region",
                "Country",
                "PostalCode",
                "PhoneCountry",
                "Phone",
                "FaxCountry",
                "Fax",
            ))
            email = next(f for f in spec.fields if f.api_name == "Email")
            self.assertTrue(email.required)
            for field in spec.fields:
                if field.location != "body" or field.api_name == "Email":
                    continue
                self.assertFalse(field.required)


if __name__ == "__main__":
    unittest.main()

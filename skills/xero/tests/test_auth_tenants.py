from __future__ import annotations

import json
import stat
import tempfile
import unittest
from pathlib import Path

from xero_safe_agent_cli.auth import (
    TokenStore,
    begin_pkce,
    client_credentials_token,
    exchange_pkce,
    refresh_pkce,
)
from xero_safe_agent_cli.http import HttpResponse
from xero_safe_agent_cli.registry import load_registry
from xero_safe_agent_cli.tenants import TenantStore


class TestAuthAndTenants(unittest.TestCase):
    def test_pkce_start_stores_verifier_but_never_returns_it(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = begin_pkce(
                client_id="public-client-id",
                redirect_uri="http://localhost:8765/callback",
                scopes=["accounting.invoices.read", "offline_access"],
                state_dir=Path(tmp),
                verifier="v" * 64,
                state="state-for-test",
            )
            self.assertIn("code_challenge=", result["authorization_url"])
            self.assertNotIn("v" * 20, json.dumps(result))
            self.assertEqual(result["scopes"], ["accounting.invoices.read", "offline_access"])
            stored = json.loads((Path(tmp) / "pkce.json").read_text(encoding="utf-8"))
            self.assertEqual(stored["code_verifier"], "v" * 64)
            self.assertEqual(stat.S_IMODE((Path(tmp) / "pkce.json").stat().st_mode), 0o600)

    def test_pkce_rejects_malicious_localhost_prefixes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            for redirect_uri in (
                "http://localhost.evil.example/callback",
                "http://localhost@evil.example/callback",
                "http://127.0.0.1.evil.example/callback",
                "http://127.0.0.1/callback",
                "http://[::1]/callback",
                "ftp://localhost/callback",
            ):
                with self.subTest(redirect_uri=redirect_uri):
                    with self.assertRaisesRegex(Exception, "redirect URI"):
                        begin_pkce(
                            client_id="public-client-id",
                            redirect_uri=redirect_uri,
                            scopes=["openid"],
                            state_dir=Path(tmp),
                            verifier="v" * 64,
                            state="state-for-test",
                        )

    def test_token_store_rotates_atomically_and_status_is_secret_free(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = TokenStore(Path(tmp) / "token.json")
            store.write(
                {
                    "access_token": "access-secret",
                    "refresh_token": "refresh-secret",
                    "expires_in": 1800,
                    "scope": "offline_access accounting.invoices.read",
                }
            )
            self.assertEqual(store.read()["refresh_token"], "refresh-secret")
            status = store.status()
            self.assertTrue(status["exists"])
            self.assertTrue(status["has_refresh_token"])
            self.assertNotIn("access-secret", json.dumps(status))
            self.assertNotIn("refresh-secret", json.dumps(status))
            self.assertEqual(stat.S_IMODE(store.path.stat().st_mode), 0o600)

    def test_auth_flows_preserve_requested_scopes_when_token_response_omits_them(self) -> None:
        class Transport:
            def __init__(self, access_token: str):
                self.access_token = access_token

            def request(self, *args: object, **kwargs: object) -> HttpResponse:
                body = json.dumps({"access_token": self.access_token, "expires_in": 1800}).encode()
                return HttpResponse(200, {"content-type": "application/json"}, body, "token")

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            client_store = TokenStore(root / "client-token.json")
            client_credentials_token(
                transport=Transport("client-access"),
                client_id="client-id",
                client_secret="client-secret",
                scopes=["app.connections"],
                token_store=client_store,
            )
            self.assertEqual(client_store.read()["scope"], "app.connections")

            state_dir = root / "oauth"
            begin_pkce(
                client_id="public-client",
                redirect_uri="http://localhost:8765/callback",
                scopes=["accounting.invoices.read", "offline_access"],
                state_dir=state_dir,
                verifier="v" * 64,
                state="saved-state",
            )
            code_file = state_dir / "code.txt"
            code_file.write_text("one-time-code", encoding="utf-8")
            pkce_store = TokenStore(root / "pkce-token.json")
            exchange_pkce(
                transport=Transport("pkce-access"),
                state_path=state_dir / "pkce.json",
                code_file=code_file,
                returned_state="saved-state",
                token_store=pkce_store,
            )
            self.assertEqual(
                pkce_store.read()["scope"],
                "accounting.invoices.read offline_access",
            )

            pkce_store.write(
                {
                    "access_token": "old-access",
                    "refresh_token": "old-refresh",
                    "scope": "accounting.invoices.read offline_access",
                }
            )
            refresh_pkce(
                transport=Transport("refreshed-access"),
                client_id="public-client",
                token_store=pkce_store,
            )
            refreshed = pkce_store.read()
            self.assertEqual(refreshed["scope"], "accounting.invoices.read offline_access")
            self.assertEqual(refreshed["refresh_token"], "old-refresh")

    def test_scope_union_is_minimum_for_selected_commands(self) -> None:
        registry = load_registry()
        self.assertEqual(
            registry.minimum_scopes(
                ["accounting.get-invoices", "accounting.get-contacts"],
                offline=True,
            ),
            ["accounting.contacts.read", "accounting.invoices.read", "offline_access"],
        )
        for commands, expected in (
            (
                ["accounting.get-invoices", "accounting.create-invoices"],
                ["accounting.invoices", "offline_access"],
            ),
            (
                ["files.get-files", "files.upload-file"],
                ["files", "offline_access"],
            ),
            (
                ["payroll-au.get-employees", "payroll-au.create-employee"],
                ["offline_access", "payroll.employees"],
            ),
        ):
            with self.subTest(commands=commands):
                self.assertEqual(
                    registry.minimum_scopes(commands, offline=True),
                    expected,
                )

    def test_tenant_selection_requires_an_exact_discovered_connection(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = TenantStore(Path(tmp) / "tenant.json")
            connections = [
                {"id": "connection-1", "tenantId": "tenant-1", "tenantName": "Demo NZ", "tenantType": "ORGANISATION"},
                {"id": "connection-2", "tenantId": "tenant-2", "tenantName": "Demo AU", "tenantType": "ORGANISATION"},
            ]
            with self.assertRaisesRegex(Exception, "not present in discovered connections"):
                store.select(connections, tenant_id="tenant-3", region="AU")
            selected = store.select(connections, tenant_id="tenant-2", region="AU")
            self.assertEqual(selected["tenant_id"], "tenant-2")
            self.assertEqual(store.read()["region"], "AU")
            self.assertEqual(stat.S_IMODE(store.path.stat().st_mode), 0o600)
            selected_us = store.select(connections, tenant_id="tenant-1", region="US")
            self.assertEqual(selected_us["region"], "US")
            with self.assertRaisesRegex(Exception, "organisation tenants only"):
                store.select(
                    [
                        {
                            "id": "connection-3",
                            "tenantId": "practice-1",
                            "tenantName": "Demo Practice",
                            "tenantType": "XERO_HQ",
                        }
                    ],
                    tenant_id="practice-1",
                    region="AU",
                )

    def test_custom_connection_organisation_becomes_an_exact_local_target(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = TenantStore(Path(tmp) / "custom-tenant.json")
            selected = store.select_custom(
                {
                    "OrganisationID": "organisation-1",
                    "Name": "Single Xero Org",
                    "CountryCode": "NZ",
                },
                credential_fingerprint="a" * 64,
            )
            self.assertEqual(selected["connection_id"], "custom-connection")
            self.assertEqual(selected["tenant_id"], "organisation-1")
            self.assertEqual(selected["tenant_name"], "Single Xero Org")
            self.assertEqual(selected["region"], "NZ")
            self.assertEqual(stat.S_IMODE(store.path.stat().st_mode), 0o600)
            with self.assertRaisesRegex(Exception, "only AU, NZ, UK, or US"):
                store.select_custom(
                    {
                        "OrganisationID": "organisation-2",
                        "Name": "Unsupported region",
                        "CountryCode": "CA",
                    },
                    credential_fingerprint="b" * 64,
                )

    def test_tenant_read_revalidates_required_values_and_region(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = TenantStore(Path(tmp) / "tenant.json")
            for value, expected in (
                ({}, "missing fields"),
                (
                    {
                        "connection_id": "connection-1",
                        "tenant_id": "",
                        "tenant_name": "Demo",
                        "tenant_type": "ORGANISATION",
                        "region": "AU",
                    },
                    "empty fields",
                ),
                (
                    {
                        "connection_id": "connection-1",
                        "tenant_id": "tenant-1",
                        "tenant_name": "Demo",
                        "tenant_type": "ORGANISATION",
                        "region": "XX",
                    },
                    "region must be",
                ),
            ):
                with self.subTest(expected=expected):
                    store.path.write_text(json.dumps(value), encoding="utf-8")
                    with self.assertRaisesRegex(Exception, expected):
                        store.read()


if __name__ == "__main__":
    unittest.main()

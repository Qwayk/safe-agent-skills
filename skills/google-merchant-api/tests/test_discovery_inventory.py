from __future__ import annotations

from collections import defaultdict

import unittest

from google_merchant_api_tool.discovery import (
    OFFICIAL_FAMILIES,
    STABLE_DISCOVERY_FAMILIES,
    OFFICIAL_DISCOVERY_FAMILIES,
    SHIPPED_FAMILIES,
    SHIPPED_DISCOVERY_FAMILIES,
    load_official_discovery_methods,
    load_official_methods,
    load_shipped_discovery_methods,
    load_shipped_methods,
    is_read_like_post,
    load_stable_discovery_methods,
)
from google_merchant_api_tool.method_inventory import (
    build_official_inventory,
    build_shipped_inventory,
    build_stable_inventory,
    method_id_to_command_tokens,
    method_id_to_cli_command,
)


class TestDiscoveryInventory(unittest.TestCase):
    def test_stable_discovery_methods_are_merged_and_counted(self) -> None:
        methods = load_stable_discovery_methods()
        self.assertEqual(len(methods), 124)

        methods_by_family = defaultdict(list)
        for method in methods:
            methods_by_family[method.family].append(method)

        self.assertEqual(set(methods_by_family), set(STABLE_DISCOVERY_FAMILIES))

        for family in STABLE_DISCOVERY_FAMILIES:
            self.assertGreater(len(methods_by_family[family]), 0, family)

        inventory = build_stable_inventory()
        self.assertEqual(len(inventory), 124)
        self.assertEqual(
            [(r.family, r.method_id, r.command) for r in inventory],
            sorted((r.family, r.method_id, r.command) for r in inventory),
        )

        inventory_by_family = defaultdict(list)
        for row in inventory:
            inventory_by_family[row.method.family].append(row)

        for family in STABLE_DISCOVERY_FAMILIES:
            self.assertEqual(len(inventory_by_family[family]), len(methods_by_family[family]))
            self.assertTrue(all(row.command_tokens for row in inventory_by_family[family]))

        write_families = {
            method.family
            for method in methods
            if method.http_method != "GET" and not is_read_like_post(method)
        }
        read_families = {
            method.family for method in methods if method.http_method == "GET" or is_read_like_post(method)
        }
        read_like = set(STABLE_DISCOVERY_FAMILIES) - write_families

        self.assertEqual(len(write_families) + len(read_like), len(STABLE_DISCOVERY_FAMILIES))
        self.assertSetEqual(set(STABLE_DISCOVERY_FAMILIES), read_families.union(write_families))
        self.assertIn("quota_v1", read_like)
        self.assertIn("accounts_v1", write_families)
        self.assertIn("promotions_v1", write_families)
        self.assertIn("reports_v1", read_families)

    def test_official_discovery_methods_and_families_are_loaded(self) -> None:
        methods = load_official_discovery_methods()
        self.assertEqual(len(methods), 350)
        self.assertEqual(len(OFFICIAL_DISCOVERY_FAMILIES), 30)
        self.assertEqual(len(load_official_methods()), 353)
        self.assertEqual(len(OFFICIAL_FAMILIES), 33)
        inventory = build_official_inventory()
        self.assertEqual(len(inventory), 353)

    def test_shipped_discovery_methods_and_families_are_loaded(self) -> None:
        discovery_methods = load_shipped_discovery_methods()
        self.assertEqual(len(discovery_methods), 222)
        methods_by_family = defaultdict(list)
        for method in discovery_methods:
            methods_by_family[method.family].append(method)

        self.assertEqual(set(methods_by_family), set(SHIPPED_DISCOVERY_FAMILIES))
        for family in SHIPPED_DISCOVERY_FAMILIES:
            self.assertGreater(len(methods_by_family[family]), 0, family)

        shipped_methods = load_shipped_methods()
        self.assertEqual(len(shipped_methods), 224)
        self.assertEqual({method.family for method in shipped_methods}, set(SHIPPED_FAMILIES))

        inventory = build_shipped_inventory()
        self.assertEqual(len(inventory), 224)
        self.assertEqual(
            [(r.family, r.method_id, r.command) for r in inventory],
            sorted((r.family, r.method_id, r.command) for r in inventory),
        )

        shipped_alpha = {method.family for method in discovery_methods if method.family not in STABLE_DISCOVERY_FAMILIES}
        self.assertIn("accounts_v1alpha", shipped_alpha)
        self.assertIn("productstudio_v1alpha", shipped_alpha)
        self.assertIn("reports_v1alpha", shipped_alpha)
        self.assertIn("reviews_v1alpha", shipped_alpha)
        self.assertIn("youtube_v1alpha", shipped_alpha)
        self.assertIn("loyaltycustomers_v1alpha", {method.family for method in shipped_methods})
        self.assertIn("youtubeshoppingcheckout_v1alpha", {method.family for method in shipped_methods})

    def test_non_v1_shipped_command_tokens_insert_version_token(self) -> None:
        tokens = method_id_to_command_tokens("accounts.loyaltyCustomers.manage", family="accounts_v1alpha")
        self.assertEqual(tokens, ("accounts", "v1alpha", "loyalty-customers", "manage"))

        cli_command = method_id_to_cli_command(
            "accounts.loyaltyCustomers.manage",
            family="accounts_v1alpha",
        )
        self.assertEqual(cli_command, "google-merchant-api-tool accounts v1alpha loyalty-customers manage")

    def test_method_id_to_command_tokens_is_explicit(self) -> None:
        tokens = method_id_to_command_tokens("merchantapi.accounts.developerRegistration.registerGcp")
        self.assertEqual(tokens, ("accounts", "developer-registration", "register-gcp"))

        command = method_id_to_cli_command("merchantapi.accounts.developerRegistration.unregisterGcp")
        self.assertEqual(command, "google-merchant-api-tool accounts developer-registration unregister-gcp")

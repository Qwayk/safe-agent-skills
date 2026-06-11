from __future__ import annotations

import unittest

from shopify_admin_api_tool.official import (
    camel_to_kebab,
    load_official_manifest,
    load_official_operations_list,
    validate_manifest_matches_operations,
)


class TestOfficialManifest(unittest.TestCase):
    def test_manifest_matches_operations(self) -> None:
        manifest = load_official_manifest()
        ops = load_official_operations_list()
        validate_manifest_matches_operations(manifest, ops)
        self.assertEqual(manifest.api_version, "2026-01")
        self.assertEqual(len(ops), 761)

    def test_kebab_case_examples(self) -> None:
        self.assertEqual(camel_to_kebab("draftOrderCreate"), "draft-order-create")
        self.assertEqual(camel_to_kebab("appUninstall"), "app-uninstall")

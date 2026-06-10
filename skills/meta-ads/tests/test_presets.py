from __future__ import annotations

import unittest

from meta_ads_api_tool.errors import ValidationError
from meta_ads_api_tool.presets import get_preset, list_presets, load_builtin_presets


class TestPresets(unittest.TestCase):
    def test_load_builtin_presets_has_expected_ids(self) -> None:
        schema_version, presets_by_id = load_builtin_presets()
        self.assertIsInstance(schema_version, str)
        self.assertGreaterEqual(int(schema_version), 1)
        self.assertIn("ecom_core", presets_by_id)
        self.assertIn("leadgen_core", presets_by_id)
        self.assertIn("maximal_firehose", presets_by_id)

    def test_list_presets_stable_shape(self) -> None:
        payload = list_presets()
        self.assertIn("schema_version", payload)
        self.assertIn("presets", payload)
        presets = payload["presets"]
        self.assertIsInstance(presets, list)
        self.assertGreaterEqual(len(presets), 3)
        first = presets[0]
        self.assertIn("id", first)
        self.assertIn("label", first)
        self.assertIn("description", first)
        self.assertIn("use_case_tags", first)

    def test_get_preset_returns_surfaces(self) -> None:
        payload = get_preset("ecom_core")
        self.assertIn("schema_version", payload)
        self.assertIn("preset", payload)
        preset = payload["preset"]
        self.assertEqual(preset["id"], "ecom_core")
        self.assertIn("surfaces", preset)
        self.assertIn("insights", preset["surfaces"])

    def test_get_preset_unknown_raises(self) -> None:
        with self.assertRaises(ValidationError):
            get_preset("does_not_exist")


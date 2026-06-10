from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout

from google_ads_api_tool.cli import main


class TestPresetsCommands(unittest.TestCase):
    def test_presets_list_includes_builtin(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = main(["--output", "json", "presets", "list"])
        self.assertEqual(rc, 0)
        payload = json.loads(buf.getvalue())
        self.assertTrue(payload["ok"])
        names = [p.get("name") for p in payload.get("presets", []) if isinstance(p, dict)]
        self.assertIn("analysis_pack_v1", names)
        self.assertIn("analysis_pack_v2", names)
        self.assertIn("analysis_pack_max_v1", names)
        self.assertIn("optimization_pack_v1", names)

    def test_presets_show(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = main(["--output", "json", "presets", "show", "--preset", "analysis_pack_v1"])
        self.assertEqual(rc, 0)
        payload = json.loads(buf.getvalue())
        self.assertTrue(payload["ok"])
        preset = payload.get("preset") or {}
        self.assertEqual(preset.get("name"), "analysis_pack_v1")
        groups = preset.get("query_groups") or []
        self.assertIsInstance(groups, list)
        ad_group_ads = next((g for g in groups if isinstance(g, dict) and g.get("group_id") == "ad_group_ads"), None)
        self.assertIsInstance(ad_group_ads, dict)
        templates = (ad_group_ads or {}).get("gaql_templates") or {}
        self.assertIsInstance(templates, dict)
        base = templates.get("base") or ""
        self.assertIsInstance(base, str)
        self.assertIn("ad_group_ad.ad.final_urls", base)
        self.assertIn("ad_group_ad.ad.responsive_search_ad.headlines", base)

    def test_presets_validate_builtin(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = main(["--output", "json", "presets", "validate", "--preset", "analysis_pack_v1"])
        self.assertEqual(rc, 0)
        payload = json.loads(buf.getvalue())
        self.assertTrue(payload["ok"])
        self.assertIsInstance(payload.get("results"), list)

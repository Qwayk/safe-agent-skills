from __future__ import annotations

import unittest

from google_ads_api_tool.presets.loader import PresetLoader


class TestAnalysisPackMaxV1GaqlFields(unittest.TestCase):
    def test_does_not_use_removed_or_unsupported_fields(self) -> None:
        preset = PresetLoader().load_preset("analysis_pack_max_v1")
        groups = preset.get("query_groups") or []
        templates: list[str] = []
        for g in groups:
            if not isinstance(g, dict):
                continue
            ts = g.get("gaql_templates") or {}
            if isinstance(ts, dict):
                templates.extend([v for v in ts.values() if isinstance(v, str)])
        all_gaql = "\n".join(templates)

        # These fields do not exist in GAQL for the current pinned schema.
        # Use word-boundary matches so we don't trip on *_date_time.
        self.assertNotRegex(all_gaql, r"\\bcampaign\\.start_date\\b")
        self.assertNotRegex(all_gaql, r"\\bcampaign\\.end_date\\b")
        self.assertNotRegex(all_gaql, r"\\bsegments\\.gender\\b")
        self.assertNotRegex(all_gaql, r"\\bsegments\\.age_range\\b")

        # This segment is not compatible with the preset's geo implementation.
        self.assertNotIn("segments.geo_target_country", all_gaql)

    def test_campaign_settings_uses_date_time_fields(self) -> None:
        preset = PresetLoader().load_preset("analysis_pack_max_v1")
        groups = preset.get("query_groups") or []
        campaign_settings = next((g for g in groups if isinstance(g, dict) and g.get("group_id") == "campaign_settings"), None)
        self.assertIsInstance(campaign_settings, dict)
        base = ((campaign_settings or {}).get("gaql_templates") or {}).get("base") or ""
        self.assertIn("campaign.start_date_time", base)
        self.assertIn("campaign.end_date_time", base)

    def test_hour_and_demo_queries_use_supported_resources(self) -> None:
        preset = PresetLoader().load_preset("analysis_pack_max_v1")
        groups = preset.get("query_groups") or []

        by_hour = next((g for g in groups if isinstance(g, dict) and g.get("group_id") == "ad_daily_metrics_by_hour"), None)
        self.assertIsInstance(by_hour, dict)
        by_hour_base = ((by_hour or {}).get("gaql_templates") or {}).get("base") or ""
        self.assertIn("FROM campaign", by_hour_base)

        by_gender = next((g for g in groups if isinstance(g, dict) and g.get("group_id") == "ad_daily_metrics_by_gender"), None)
        self.assertIsInstance(by_gender, dict)
        by_gender_base = ((by_gender or {}).get("gaql_templates") or {}).get("base") or ""
        self.assertIn("FROM gender_view", by_gender_base)

        by_age = next((g for g in groups if isinstance(g, dict) and g.get("group_id") == "ad_daily_metrics_by_age_range"), None)
        self.assertIsInstance(by_age, dict)
        by_age_base = ((by_age or {}).get("gaql_templates") or {}).get("base") or ""
        self.assertIn("FROM age_range_view", by_age_base)

    def test_geo_queries_use_geographic_view(self) -> None:
        preset = PresetLoader().load_preset("analysis_pack_max_v1")
        groups = preset.get("query_groups") or []

        by_country = next((g for g in groups if isinstance(g, dict) and g.get("group_id") == "ad_daily_metrics_by_country"), None)
        self.assertIsInstance(by_country, dict)
        by_country_base = ((by_country or {}).get("gaql_templates") or {}).get("base") or ""
        self.assertIn("FROM geographic_view", by_country_base)
        self.assertIn("geographic_view.location_type", by_country_base)
        self.assertIn("geographic_view.country_criterion_id", by_country_base)

        by_region = next((g for g in groups if isinstance(g, dict) and g.get("group_id") == "ad_daily_metrics_by_region"), None)
        self.assertIsInstance(by_region, dict)
        by_region_base = ((by_region or {}).get("gaql_templates") or {}).get("base") or ""
        self.assertIn("FROM geographic_view", by_region_base)
        self.assertIn("geographic_view.location_type", by_region_base)
        self.assertIn("segments.geo_target_region", by_region_base)

        by_city = next((g for g in groups if isinstance(g, dict) and g.get("group_id") == "ad_daily_metrics_by_city"), None)
        self.assertIsInstance(by_city, dict)
        by_city_base = ((by_city or {}).get("gaql_templates") or {}).get("base") or ""
        self.assertIn("FROM geographic_view", by_city_base)
        self.assertIn("geographic_view.location_type", by_city_base)
        self.assertIn("segments.geo_target_city", by_city_base)

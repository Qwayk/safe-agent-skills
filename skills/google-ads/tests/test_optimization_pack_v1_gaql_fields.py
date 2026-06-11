from __future__ import annotations

import unittest

from google_ads_api_tool.presets.loader import PresetLoader


class TestOptimizationPackV1GaqlFields(unittest.TestCase):
    def test_required_groups_exist(self) -> None:
        preset = PresetLoader().load_preset("optimization_pack_v1")
        groups = preset.get("query_groups") or []
        required_group_ids = {
            "customer_overview",
            "campaign_inventory",
            "campaign_settings",
            "campaign_budgets",
            "campaign_pressure_daily",
            "ad_group_inventory",
            "ad_group_ads",
            "ad_daily_metrics",
            "keyword_daily_metrics",
            "keyword_quality_snapshot",
            "search_terms_daily",
            "conversion_actions",
            "recommendations",
        }
        actual = {str(group.get("group_id")) for group in groups if isinstance(group, dict)}
        self.assertTrue(required_group_ids.issubset(actual))

    def test_optimization_fields_are_present(self) -> None:
        preset = PresetLoader().load_preset("optimization_pack_v1")
        groups = preset.get("query_groups") or []
        templates: list[str] = []
        for group in groups:
            if not isinstance(group, dict):
                continue
            gaql_templates = group.get("gaql_templates") or {}
            if isinstance(gaql_templates, dict):
                templates.extend(str(value) for value in gaql_templates.values() if isinstance(value, str))
        all_gaql = "\n".join(templates)

        self.assertIn("customer.optimization_score", all_gaql)
        self.assertIn("campaign.optimization_score", all_gaql)
        self.assertIn("metrics.search_impression_share", all_gaql)
        self.assertIn("metrics.search_budget_lost_impression_share", all_gaql)
        self.assertIn("metrics.search_rank_lost_impression_share", all_gaql)
        self.assertIn("metrics.search_exact_match_impression_share", all_gaql)
        self.assertIn("metrics.search_top_impression_share", all_gaql)
        self.assertIn("metrics.search_absolute_top_impression_share", all_gaql)
        self.assertIn("ad_group_criterion.quality_info.quality_score", all_gaql)
        self.assertIn("ad_group_criterion.quality_info.search_predicted_ctr", all_gaql)
        self.assertIn("ad_group_ad.ad_strength", all_gaql)
        self.assertIn("recommendation.resource_name", all_gaql)
        self.assertIn("recommendation.type", all_gaql)

from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from google_ads_api_tool.cli import main


def _write_pack_with_tables(
    pack_dir: Path,
    *,
    tables: dict[str, list[dict]],
    preset: str = "optimization_pack_v1",
) -> None:
    pack_dir.mkdir(parents=True, exist_ok=True)
    (pack_dir / "tables").mkdir(parents=True, exist_ok=True)
    (pack_dir / "queries").mkdir(parents=True, exist_ok=True)
    (pack_dir / "errors").mkdir(parents=True, exist_ok=True)
    (pack_dir / "queries" / "queries.json").write_text("{}", encoding="utf-8")
    (pack_dir / "errors" / "errors.jsonl").write_text("", encoding="utf-8")

    manifest_tables = []
    groups = []
    for name, rows in tables.items():
        rel = f"tables/{name}.jsonl"
        payload = "\n".join(json.dumps(row, ensure_ascii=False, sort_keys=True) for row in rows)
        (pack_dir / rel).write_text((payload + "\n") if payload else "", encoding="utf-8")
        manifest_tables.append(
            {
                "name": name,
                "path": rel,
                "row_count": len(rows),
                "truncated": False,
                "join_keys": ["customer.id"],
                "source_group_id": name,
            }
        )
        groups.append(
            {
                "group_id": name,
                "required": True,
                "status": "ok",
                "error_count": 0,
                "row_count": len(rows),
                "truncated": False,
            }
        )

    manifest = {
        "schema_version": 1,
        "tool": "google-ads-api-tool",
        "tool_version": "0.7.0",
        "generated_at_utc": "2026-04-28T00:00:00Z",
        "preset": preset,
        "customer_id": "123",
        "since": "2026-04-01",
        "until": "2026-04-30",
        "segmentation": "base",
        "join_map": {"customer.id": {"description": "x", "fields": ["customer.id"]}},
        "tables": manifest_tables,
        "groups": groups,
        "warnings": [],
        "errors_path": "errors/errors.jsonl",
        "queries_path": "queries/queries.json",
    }
    (pack_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _run_diagnose(pack_dir: Path) -> dict:
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = main(["--output", "json", "snapshot", "analyze", "diagnose", "--pack-dir", str(pack_dir)])
    if rc != 0:
        raise AssertionError(buf.getvalue())
    payload = json.loads(buf.getvalue())
    if not payload.get("ok"):
        raise AssertionError(payload)
    return payload


def _base_tables() -> dict[str, list[dict]]:
    return {
        "customer_overview": [
            {
                "customer": {
                    "id": "123",
                    "resource_name": "customers/123",
                    "descriptive_name": "Test Account",
                    "optimization_score": 0.74,
                    "optimization_score_weight": 1.0,
                }
            }
        ],
        "campaign_inventory": [
            {
                "campaign": {
                    "id": "1",
                    "resource_name": "customers/123/campaigns/1",
                    "name": "Search Core",
                    "optimization_score": 0.74,
                    "status": "ENABLED",
                }
            }
        ],
        "campaign_settings": [
            {
                "campaign": {
                    "id": "1",
                    "resource_name": "customers/123/campaigns/1",
                    "name": "Search Core",
                    "bidding_strategy_type": "TARGET_SPEND",
                }
            }
        ],
        "campaign_budgets": [
            {
                "campaign_budget": {
                    "resource_name": "customers/123/campaignBudgets/9",
                    "id": "9",
                    "amount_micros": "50000000",
                    "status": "ENABLED",
                }
            }
        ],
        "ad_group_inventory": [
            {
                "campaign": {"resource_name": "customers/123/campaigns/1"},
                "ad_group": {
                    "id": "2",
                    "resource_name": "customers/123/adGroups/2",
                    "name": "Tracks",
                    "primary_status": "ELIGIBLE",
                },
            }
        ],
        "ad_group_ads": [
            {
                "campaign": {"resource_name": "customers/123/campaigns/1", "name": "Search Core"},
                "ad_group": {"resource_name": "customers/123/adGroups/2", "name": "Tracks"},
                "ad_group_ad": {
                    "resource_name": "customers/123/adGroupAds/2~99",
                    "status": "ENABLED",
                    "ad_strength": "POOR",
                    "policy_summary": {"approval_status": "APPROVED", "review_status": "REVIEWED"},
                    "ad": {"id": "99", "type_": "RESPONSIVE_SEARCH_AD"},
                },
            }
        ],
        "ad_daily_metrics": [
            {
                "campaign": {"resource_name": "customers/123/campaigns/1"},
                "ad_group": {"resource_name": "customers/123/adGroups/2"},
                "ad_group_ad": {"resource_name": "customers/123/adGroupAds/2~99", "ad": {"id": "99"}},
                "segments": {"date": "2026-04-28"},
                "metrics": {
                    "impressions": 100,
                    "clicks": 20,
                    "cost_micros": 21000000,
                    "conversions": 0.0,
                    "conversions_value": 0.0,
                },
            }
        ],
        "conversion_actions": [],
        "recommendations": [],
    }


class TestSnapshotAnalyzeDiagnose(unittest.TestCase):
    def test_reports_rank_pressure_rsa_issue_and_quality_issue(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            pack_dir = Path(td) / "pack"
            tables = _base_tables()
            tables["campaign_pressure_daily"] = [
                {
                    "campaign": {"id": "1", "resource_name": "customers/123/campaigns/1"},
                    "segments": {"date": "2026-04-28"},
                    "metrics": {
                        "impressions": 120,
                        "clicks": 20,
                        "cost_micros": 22000000,
                        "conversions": 0.0,
                        "conversions_value": 0.0,
                        "search_impression_share": 0.18,
                        "search_budget_lost_impression_share": 0.05,
                        "search_rank_lost_impression_share": 0.55,
                        "search_top_impression_share": 0.2,
                        "search_absolute_top_impression_share": 0.05,
                    },
                }
            ]
            tables["keyword_quality_snapshot"] = [
                {
                    "campaign": {"resource_name": "customers/123/campaigns/1", "name": "Search Core"},
                    "ad_group": {"resource_name": "customers/123/adGroups/2", "name": "Tracks"},
                    "ad_group_criterion": {
                        "resource_name": "customers/123/adGroupCriteria/2~7",
                        "keyword": {"text": "sliding door track replacement", "match_type": "PHRASE"},
                        "quality_info": {
                            "quality_score": 2,
                            "search_predicted_ctr": "BELOW_AVERAGE",
                            "creative_quality_score": "AVERAGE",
                            "post_click_quality_score": "BELOW_AVERAGE",
                        },
                    },
                    "metrics": {"impressions": "22", "clicks": "1", "cost_micros": "11680000", "conversions": 1.0},
                }
            ]
            _write_pack_with_tables(pack_dir, tables=tables)
            payload = _run_diagnose(pack_dir)
            categories = {finding["category"] for finding in payload["findings"]}
            self.assertIn("rank_pressure", categories)
            self.assertIn("rsa_issue", categories)
            self.assertIn("quality_score_issue", categories)
            rsa_finding = next(f for f in payload["findings"] if f["category"] == "rsa_issue")
            self.assertEqual(rsa_finding["evidence"]["impressions"], 100)
            self.assertEqual(rsa_finding["evidence"]["clicks"], 20)
            self.assertEqual(rsa_finding["evidence"]["cost_micros"], 21000000)

    def test_reports_budget_pressure(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            pack_dir = Path(td) / "pack"
            tables = _base_tables()
            tables["campaign_pressure_daily"] = [
                {
                    "campaign": {"id": "1", "resource_name": "customers/123/campaigns/1"},
                    "segments": {"date": "2026-04-28"},
                    "metrics": {
                        "impressions": 80,
                        "clicks": 8,
                        "cost_micros": 8000000,
                        "conversions": 0.0,
                        "conversions_value": 0.0,
                        "search_impression_share": 0.19,
                        "search_budget_lost_impression_share": 0.65,
                        "search_rank_lost_impression_share": 0.05,
                    },
                }
            ]
            _write_pack_with_tables(pack_dir, tables=tables)
            payload = _run_diagnose(pack_dir)
            categories = {finding["category"] for finding in payload["findings"]}
            self.assertIn("budget_pressure", categories)

    def test_reports_mixed_pressure(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            pack_dir = Path(td) / "pack"
            tables = _base_tables()
            tables["campaign_pressure_daily"] = [
                {
                    "campaign": {"id": "1", "resource_name": "customers/123/campaigns/1"},
                    "segments": {"date": "2026-04-28"},
                    "metrics": {
                        "impressions": 90,
                        "clicks": 9,
                        "cost_micros": 9000000,
                        "conversions": 0.0,
                        "conversions_value": 0.0,
                        "search_impression_share": 0.1,
                        "search_budget_lost_impression_share": 0.35,
                        "search_rank_lost_impression_share": 0.4,
                    },
                }
            ]
            _write_pack_with_tables(pack_dir, tables=tables)
            payload = _run_diagnose(pack_dir)
            categories = {finding["category"] for finding in payload["findings"]}
            self.assertIn("mixed_pressure", categories)

    def test_reports_low_volume_or_targeting_limited(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            pack_dir = Path(td) / "pack"
            tables = _base_tables()
            tables["campaign_pressure_daily"] = [
                {
                    "campaign": {"id": "1", "resource_name": "customers/123/campaigns/1"},
                    "segments": {"date": "2026-04-28"},
                    "metrics": {
                        "impressions": 12,
                        "clicks": 1,
                        "cost_micros": 1200000,
                        "conversions": 0.0,
                        "conversions_value": 0.0,
                        "search_impression_share": 0.11,
                        "search_budget_lost_impression_share": 0.01,
                        "search_rank_lost_impression_share": 0.02,
                    },
                }
            ]
            _write_pack_with_tables(pack_dir, tables=tables)
            payload = _run_diagnose(pack_dir)
            categories = {finding["category"] for finding in payload["findings"]}
            self.assertIn("low_volume_or_targeting_limited", categories)

    def test_reports_tracking_risk_when_primary_conversions_missing(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            pack_dir = Path(td) / "pack"
            tables = _base_tables()
            tables["campaign_pressure_daily"] = []
            _write_pack_with_tables(pack_dir, tables=tables)
            payload = _run_diagnose(pack_dir)
            categories = {finding["category"] for finding in payload["findings"]}
            self.assertIn("tracking_risk", categories)

    def test_reports_recommendation_review(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            pack_dir = Path(td) / "pack"
            tables = _base_tables()
            tables["campaign_pressure_daily"] = []
            tables["conversion_actions"] = [
                {
                    "conversion_action": {
                        "resource_name": "customers/123/conversionActions/1",
                        "name": "Calls from ads",
                        "status": "ENABLED",
                        "primary_for_goal": True,
                        "include_in_conversions_metric": True,
                    }
                }
            ]
            tables["recommendations"] = [
                {
                    "campaign": {"id": "1", "resource_name": "customers/123/campaigns/1", "name": "Search Core"},
                    "recommendation": {
                        "resource_name": "customers/123/recommendations/abc",
                        "type_": "RESPONSIVE_SEARCH_AD_IMPROVE_AD_STRENGTH",
                        "dismissed": False,
                    },
                }
            ]
            _write_pack_with_tables(pack_dir, tables=tables)
            payload = _run_diagnose(pack_dir)
            categories = {finding["category"] for finding in payload["findings"]}
            self.assertIn("recommendation_review", categories)

    def test_reports_cleanup_candidates_from_optional_tables(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            pack_dir = Path(td) / "pack"
            tables = _base_tables()
            tables["campaign_pressure_daily"] = []
            tables["search_terms_daily"] = [
                {
                    "search_term_view": {"search_term": "free sliding door repair"},
                    "metrics": {"impressions": 120, "clicks": 4, "cost_micros": 9000000, "conversions": 0.0, "conversions_value": 0.0},
                }
            ]
            tables["keyword_daily_metrics"] = [
                {
                    "ad_group_criterion": {"keyword": {"text": "cheap sliding door repair", "match_type": "PHRASE"}},
                    "metrics": {"impressions": 140, "clicks": 4, "cost_micros": 9000000, "conversions": 0.0, "conversions_value": 0.0},
                }
            ]
            tables["landing_pages_daily"] = [
                {
                    "landing_page_view": {"unexpanded_final_url": "https://example.com/landing"},
                    "metrics": {"impressions": 50, "clicks": 4, "cost_micros": 9000000, "conversions": 0.0, "conversions_value": 0.0},
                }
            ]
            tables["placements_daily"] = [
                {
                    "detail_placement_view": {"placement": "mobileapp::example"},
                    "metrics": {"impressions": 60, "clicks": 5, "cost_micros": 9000000, "conversions": 0.0, "conversions_value": 0.0},
                }
            ]
            _write_pack_with_tables(pack_dir, tables=tables)
            payload = _run_diagnose(pack_dir)
            categories = [finding["category"] for finding in payload["findings"]]
            self.assertIn("search_term_cleanup", categories)
            self.assertIn("keyword_pause_candidate", categories)
            self.assertIn("landing_page_review", categories)
            self.assertIn("placement_review", categories)

    def test_skips_zero_signal_quality_rows_and_routes_pause_candidates_to_books(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            pack_dir = Path(td) / "pack"
            tables = _base_tables()
            tables["campaign_pressure_daily"] = []
            tables["conversion_actions"] = [
                {
                    "conversion_action": {
                        "resource_name": "customers/123/conversionActions/1",
                        "name": "Calls from ads",
                        "status": "ENABLED",
                        "primary_for_goal": True,
                        "include_in_conversions_metric": True,
                    }
                }
            ]
            tables["keyword_quality_snapshot"] = [
                {
                    "campaign": {"resource_name": "customers/123/campaigns/1", "name": "Search Core"},
                    "ad_group": {"resource_name": "customers/123/adGroups/2", "name": "Tracks"},
                    "ad_group_criterion": {
                        "resource_name": "customers/123/adGroupCriteria/2~skip",
                        "keyword": {"text": "no signal keyword", "match_type": "PHRASE"},
                        "quality_info": {
                            "quality_score": 2,
                            "search_predicted_ctr": "BELOW_AVERAGE",
                            "creative_quality_score": "AVERAGE",
                            "post_click_quality_score": "BELOW_AVERAGE",
                        },
                    },
                    "metrics": {"impressions": "0", "clicks": "0", "cost_micros": "0", "conversions": 0.0},
                },
                {
                    "campaign": {"resource_name": "customers/123/campaigns/1", "name": "Search Core"},
                    "ad_group": {"resource_name": "customers/123/adGroups/2", "name": "Tracks"},
                    "ad_group_criterion": {
                        "resource_name": "customers/123/adGroupCriteria/2~keep",
                        "keyword": {"text": "real signal keyword", "match_type": "PHRASE"},
                        "quality_info": {
                            "quality_score": 3,
                            "search_predicted_ctr": "BELOW_AVERAGE",
                            "creative_quality_score": "AVERAGE",
                            "post_click_quality_score": "BELOW_AVERAGE",
                        },
                    },
                    "metrics": {"impressions": "30", "clicks": "3", "cost_micros": "7000000", "conversions": 0.0},
                },
            ]
            tables["keyword_daily_metrics"] = [
                {
                    "campaign": {"resource_name": "customers/123/campaigns/1"},
                    "ad_group": {"resource_name": "customers/123/adGroups/2"},
                    "ad_group_criterion": {"keyword": {"text": "pause me", "match_type": "PHRASE"}},
                    "metrics": {"impressions": 120, "clicks": 4, "cost_micros": 9000000, "conversions": 0.0, "conversions_value": 0.0},
                }
            ]
            _write_pack_with_tables(pack_dir, tables=tables)
            payload = _run_diagnose(pack_dir)

            quality_ids = {
                finding["id"]
                for finding in payload["findings"]
                if finding["category"] == "quality_score_issue"
            }
            self.assertNotIn("quality_score_issue:2~skip", quality_ids)
            self.assertIn("quality_score_issue:2~keep", quality_ids)

            pause_finding = next(f for f in payload["findings"] if f["category"] == "keyword_pause_candidate")
            self.assertEqual(pause_finding["support_route"], "books_or_human")
            self.assertEqual(pause_finding["recommended_doc_queries"], [])

    def test_demotes_thin_signal_quality_rows_to_medium(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            pack_dir = Path(td) / "pack"
            tables = _base_tables()
            tables["campaign_pressure_daily"] = []
            tables["conversion_actions"] = [
                {
                    "conversion_action": {
                        "resource_name": "customers/123/conversionActions/1",
                        "name": "Calls from ads",
                        "status": "ENABLED",
                        "primary_for_goal": True,
                        "include_in_conversions_metric": True,
                    }
                }
            ]
            tables["keyword_quality_snapshot"] = [
                {
                    "campaign": {"resource_name": "customers/123/campaigns/1", "name": "Search Core"},
                    "ad_group": {"resource_name": "customers/123/adGroups/2", "name": "Tracks"},
                    "ad_group_criterion": {
                        "resource_name": "customers/123/adGroupCriteria/2~thin",
                        "keyword": {"text": "thin signal keyword", "match_type": "PHRASE"},
                        "quality_info": {
                            "quality_score": 3,
                            "search_predicted_ctr": "BELOW_AVERAGE",
                            "creative_quality_score": "AVERAGE",
                            "post_click_quality_score": "BELOW_AVERAGE",
                        },
                    },
                    "metrics": {"impressions": "2", "clicks": "1", "cost_micros": "9340000", "conversions": 0.0},
                }
            ]
            _write_pack_with_tables(pack_dir, tables=tables)
            payload = _run_diagnose(pack_dir)

            finding = next(f for f in payload["findings"] if f["category"] == "quality_score_issue")
            self.assertEqual(finding["id"], "quality_score_issue:2~thin")
            self.assertEqual(finding["level"], "medium")
            self.assertEqual(finding["evidence"]["evidence_strength"], "early_signal")

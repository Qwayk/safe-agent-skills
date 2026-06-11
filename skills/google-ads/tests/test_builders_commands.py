from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from google_ads_api_tool.cli import build_parser
from google_ads_api_tool.commands.builders import (
    build_competitor_search_request,
    build_dsa_feed_search_request,
    build_search_campaign_request,
    cmd_builder_search_campaign_from_spec,
)
from google_ads_api_tool.errors import ValidationError
from google_ads_api_tool.protobuf_json import parse_request_json


class _CaptureOut:
    def __init__(self) -> None:
        self.last = None

    def emit(self, obj):  # noqa: ANN001
        self.last = obj


class _FakeCfg:
    max_mutate_operations_per_request = 100
    max_mutate_operations_per_run = 1000


def _search_spec() -> dict:
    return {
        "customer_id": "1234567890",
        "budget": {"name": "Search Budget | Test", "amount": "70"},
        "campaign": {
            "name": "Search Campaign | Test",
            "status": "PAUSED",
            "max_clicks_cpc_ceiling_amount": "12",
        },
        "targeting": {
            "locations": ["9059448"],
            "languages": ["1000"],
            "ad_schedule": [
                {
                    "day_of_week": "MONDAY",
                    "start_hour": 7,
                    "end_hour": 19,
                }
            ],
        },
        "campaign_negatives": ["glass repair"],
        "asset_creates": [
            {
                "alias": "callout_main",
                "type": "CALLOUT",
                "name": "Callout | Repair First",
                "callout_text": "Repair First",
            }
        ],
        "campaign_asset_links": [
            {
                "asset_alias": "callout_main",
                "field_type": "CALLOUT",
            }
        ],
        "ad_groups": [
            {
                "alias": "general",
                "name": "General",
                "keywords": [
                    {"text": "sliding door repair", "match_type": "EXACT"},
                ],
                "negative_keywords": ["screen repair"],
                "ads": [
                    {
                        "final_urls": ["https://example.com/repair"],
                        "headlines": ["Sliding Door Repair", "Repair First", "Call Today"],
                        "descriptions": [
                            "We fix sliding doors across DFW.",
                            "Call during business hours.",
                        ],
                    }
                ],
            }
        ],
        "cross_campaign_negatives": [
            {
                "campaign_id": "555",
                "text": "competitor one",
                "match_type": "EXACT",
            }
        ],
    }


def _dsa_spec() -> dict:
    return {
        "customer_id": "1234567890",
        "budget": {"name": "Search Budget | DSA", "amount": "50"},
        "campaign": {
            "name": "DSA Campaign | Test",
            "status": "PAUSED",
            "max_clicks_cpc_ceiling_amount": "12",
        },
        "targeting": {
            "locations": ["9059448"],
            "languages": ["1000"],
            "ad_schedule": [
                {
                    "day_of_week": "MONDAY",
                    "start_hour": 7,
                    "end_hour": 19,
                }
            ],
        },
        "campaign_negatives": ["broken glass"],
        "page_feed": {
            "asset_set_name": "DSA Page Feed | Test",
            "label": "test_dsa_label",
            "urls": [
                "https://example.com/",
                "https://example.com/roller-replacement",
            ],
        },
        "ad_group": {"name": "Phase 1 Mechanical", "status": "PAUSED"},
        "ad": {
            "status": "PAUSED",
            "description": "Sliding door repair across DFW.",
            "description2": "Call 7am-7pm.",
        },
        "webpage_target": {
            "criterion_name": "Phase 1 Mechanical Feed",
            "label": "test_dsa_label",
        },
    }


class TestBuilderCommands(unittest.TestCase):
    def test_builder_commands_are_registered(self) -> None:
        args = build_parser().parse_args(
            ["builders", "search-campaign", "from-spec", "--spec", "./spec.json"]
        )
        self.assertTrue(args.write_capable)
        self.assertEqual(args.func.__name__, "cmd_builder_search_campaign_from_spec")

    def test_search_builder_compiles_valid_mutate_request(self) -> None:
        compilation = build_search_campaign_request(_search_spec())
        parse_request_json(
            service="GoogleAdsService",
            request_type="MutateGoogleAdsRequest",
            obj=compilation.request_obj,
        )
        self.assertEqual(compilation.manifest["builder_kind"], "search-campaign")
        self.assertGreater(compilation.manifest["operation_count"], 5)
        self.assertIn("campaign_operation", compilation.manifest["operation_action_counts"])

    def test_dsa_builder_compiles_valid_mutate_request(self) -> None:
        compilation = build_dsa_feed_search_request(_dsa_spec())
        parse_request_json(
            service="GoogleAdsService",
            request_type="MutateGoogleAdsRequest",
            obj=compilation.request_obj,
        )
        self.assertEqual(compilation.manifest["builder_kind"], "dsa-feed-search")
        self.assertEqual(compilation.manifest["page_url_count"], 2)
        self.assertIn("asset_set_operation", compilation.manifest["operation_action_counts"])

    def test_competitor_builder_rejects_non_exact_positive_keywords(self) -> None:
        spec = _search_spec()
        spec["ad_groups"][0]["keywords"][0]["match_type"] = "PHRASE"
        with self.assertRaises(ValidationError):
            build_competitor_search_request(spec)

    def test_search_builder_dry_run_writes_clean_bundle(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            spec_path = Path(td) / "spec.json"
            artifacts_dir = Path(td) / "artifacts"
            spec = _search_spec()
            spec_path.write_text(json.dumps(spec), encoding="utf-8")

            args = build_parser().parse_args(
                ["builders", "search-campaign", "from-spec", "--spec", str(spec_path)]
            )
            out = _CaptureOut()
            ctx = {
                "cfg": _FakeCfg(),
                "out": out,
                "apply": False,
                "yes": False,
                "plan_out": None,
                "plan_in": None,
                "receipt_out": None,
                "ack_irreversible": False,
                "ack_spend": False,
                "include_rpc_payload": False,
                "ack_sensitive_payload": False,
                "artifacts_dir": artifacts_dir,
                "timeout_s": 30.0,
            }
            rc = cmd_builder_search_campaign_from_spec(args, ctx)
            self.assertEqual(rc, 0)
            self.assertTrue((artifacts_dir / "spec.json").exists())
            self.assertTrue((artifacts_dir / "request.json").exists())
            self.assertTrue((artifacts_dir / "builder_manifest.json").exists())
            self.assertTrue((artifacts_dir / "plan.json").exists())
            self.assertTrue((artifacts_dir / "README.md").exists())
            self.assertTrue(out.last["dry_run"])
            self.assertEqual(out.last["builder"]["kind"], "search-campaign")
            self.assertEqual(
                out.last["plan"]["operations_count"],
                out.last["builder"]["manifest"]["operation_count"],
            )
            self.assertEqual(out.last["plan"]["risk"]["level"], "high")

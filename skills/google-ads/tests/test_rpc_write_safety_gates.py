from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from google_ads_api_tool.config import Config
from google_ads_api_tool.errors import SafetyError
from google_ads_api_tool.protobuf_json import parse_request_json
from google_ads_api_tool.rpc_commands import _cmd_write
from google_ads_api_tool.rpc_v22_registry import RPC_METHODS_V22


class _Out:
    def __init__(self) -> None:
        self.last = None

    def emit(self, obj):  # noqa: ANN001
        self.last = obj


def _spec(service: str, method: str):
    for s in RPC_METHODS_V22:
        if s.service == service and s.method == method:
            return s
    raise AssertionError(f"Missing spec: {service}.{method}")


class TestRpcWriteSafetyGates(unittest.TestCase):
    def test_spend_impacting_write_requires_ack_spend_before_client_call(self) -> None:
        spec = _spec("CampaignBudgetService", "MutateCampaignBudgets")
        request_msg = parse_request_json(
            service=spec.service,
            request_type=spec.request_type,
            obj={"customer_id": "123", "operations": [{}]},
        )

        cfg = Config(
            developer_token="devtoken",
            client_id="clientid",
            client_secret="clientsecret",
            refresh_token="refreshtoken",
            login_customer_id=None,
            timeout_s=30.0,
            external_writes_disabled=False,
            write_customer_id_allowlist={"123"},
            max_mutate_operations_per_request=100,
            max_mutate_operations_per_run=1000,
            retry_max_attempts=1,
            retry_base_delay_s=0.0,
        )
        out = _Out()

        with tempfile.TemporaryDirectory() as td:
            plan_path = Path(td) / "plan.json"
            ctx_dry_run = {
                "cfg": cfg,
                "apply": False,
                "out": out,
                "plan_out": str(plan_path),
                "plan_in": None,
                "receipt_out": None,
                "yes": True,
                "ack_irreversible": True,
                "ack_spend": False,
                "timeout_s": 1.0,
                "artifacts_dir": None,
            }
            _cmd_write(
                spec=spec,
                request_msg=request_msg,
                in_path="request.json",
                ctx=ctx_dry_run,
                customer_id_override="123",
            )
            self.assertTrue(plan_path.exists())
            self.assertIn("plain_english_summary", out.last["plan"])

            ctx_apply = dict(ctx_dry_run)
            ctx_apply["apply"] = True
            ctx_apply["plan_out"] = None
            ctx_apply["plan_in"] = str(plan_path)

            with mock.patch("google_ads_api_tool.rpc_commands.build_google_ads_client") as build_client:
                build_client.side_effect = AssertionError("Client should not be constructed for missing --ack-spend")
                with self.assertRaises(SafetyError) as cm:
                    _cmd_write(
                        spec=spec,
                        request_msg=request_msg,
                        in_path="request.json",
                        ctx=ctx_apply,
                        customer_id_override="123",
                    )

            self.assertIn("--ack-spend", str(cm.exception))

    def test_google_ads_mutate_budget_write_requires_ack_spend_before_client_call(self) -> None:
        spec = _spec("GoogleAdsService", "Mutate")
        request_msg = parse_request_json(
            service=spec.service,
            request_type=spec.request_type,
            obj={
                "customer_id": "123",
                "mutate_operations": [
                    {
                        "campaign_budget_operation": {
                            "create": {
                                "resource_name": "customers/123/campaignBudgets/-1",
                                "name": "Budget | Test",
                                "amount_micros": "70000000",
                                "delivery_method": "STANDARD",
                                "explicitly_shared": True,
                            }
                        }
                    },
                    {
                        "campaign_operation": {
                            "create": {
                                "resource_name": "customers/123/campaigns/-2",
                                "name": "Campaign | Test",
                                "status": "PAUSED",
                                "advertising_channel_type": "SEARCH",
                                "campaign_budget": "customers/123/campaignBudgets/-1",
                            }
                        }
                    },
                ],
            },
        )

        cfg = Config(
            developer_token="devtoken",
            client_id="clientid",
            client_secret="clientsecret",
            refresh_token="refreshtoken",
            login_customer_id=None,
            timeout_s=30.0,
            external_writes_disabled=False,
            write_customer_id_allowlist={"123"},
            max_mutate_operations_per_request=100,
            max_mutate_operations_per_run=1000,
            retry_max_attempts=1,
            retry_base_delay_s=0.0,
        )
        out = _Out()

        with tempfile.TemporaryDirectory() as td:
            plan_path = Path(td) / "plan.json"
            ctx_dry_run = {
                "cfg": cfg,
                "apply": False,
                "out": out,
                "plan_out": str(plan_path),
                "plan_in": None,
                "receipt_out": None,
                "yes": True,
                "ack_irreversible": False,
                "ack_spend": False,
                "timeout_s": 1.0,
                "artifacts_dir": None,
            }
            _cmd_write(
                spec=spec,
                request_msg=request_msg,
                in_path="request.json",
                ctx=ctx_dry_run,
                customer_id_override="123",
            )
            self.assertTrue(plan_path.exists())
            self.assertEqual(out.last["plan"]["operations_count"], 2)
            self.assertIn("plain_english_summary", out.last["plan"])

            ctx_apply = dict(ctx_dry_run)
            ctx_apply["apply"] = True
            ctx_apply["plan_out"] = None
            ctx_apply["plan_in"] = str(plan_path)

            with mock.patch("google_ads_api_tool.rpc_commands.build_google_ads_client") as build_client:
                build_client.side_effect = AssertionError("Client should not be constructed for missing --ack-spend")
                with self.assertRaises(SafetyError) as cm:
                    _cmd_write(
                        spec=spec,
                        request_msg=request_msg,
                        in_path="request.json",
                        ctx=ctx_apply,
                        customer_id_override="123",
                    )

            self.assertIn("--ack-spend", str(cm.exception))

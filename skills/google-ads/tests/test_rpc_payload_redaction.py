from __future__ import annotations

import tempfile
import unittest

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


def _cfg() -> Config:
    return Config(
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


class TestRpcPayloadRedaction(unittest.TestCase):
    def test_dry_run_plan_omits_raw_request_by_default(self) -> None:
        spec = _spec("CampaignService", "MutateCampaigns")
        request_msg = parse_request_json(
            service=spec.service,
            request_type=spec.request_type,
            obj={"customer_id": "123", "operations": [{"create": {"name": "Example campaign (synthetic)"}}]},
        )

        out = _Out()
        with tempfile.TemporaryDirectory() as td:
            ctx = {
                "cfg": _cfg(),
                "apply": False,
                "out": out,
                "plan_out": f"{td}/plan.json",
                "plan_in": None,
                "receipt_out": None,
                "yes": True,
                "ack_irreversible": True,
                "ack_spend": True,
                "include_rpc_payload": False,
                "ack_sensitive_payload": False,
                "timeout_s": 1.0,
                "artifacts_dir": None,
            }
            _cmd_write(
                spec=spec,
                request_msg=request_msg,
                in_path="request.json",
                ctx=ctx,
                customer_id_override="123",
            )

        plan = out.last["plan"]
        self.assertIn("request_digest", plan)
        self.assertIn("request_summary", plan)
        self.assertNotIn("request", plan)

    def test_include_rpc_payload_requires_ack_sensitive_payload(self) -> None:
        spec = _spec("CampaignService", "MutateCampaigns")
        request_msg = parse_request_json(
            service=spec.service,
            request_type=spec.request_type,
            obj={"customer_id": "123", "operations": [{"create": {"name": "Example campaign (synthetic)"}}]},
        )
        out = _Out()
        ctx = {
            "cfg": _cfg(),
            "apply": False,
            "out": out,
            "plan_out": None,
            "plan_in": None,
            "receipt_out": None,
            "yes": True,
            "ack_irreversible": True,
            "ack_spend": True,
            "include_rpc_payload": True,
            "ack_sensitive_payload": False,
            "timeout_s": 1.0,
            "artifacts_dir": None,
        }
        with self.assertRaises(SafetyError):
            _cmd_write(
                spec=spec,
                request_msg=request_msg,
                in_path="request.json",
                ctx=ctx,
                customer_id_override="123",
            )

    def test_include_rpc_payload_includes_request_when_acknowledged(self) -> None:
        spec = _spec("CampaignService", "MutateCampaigns")
        request_msg = parse_request_json(
            service=spec.service,
            request_type=spec.request_type,
            obj={"customer_id": "123", "operations": [{"create": {"name": "Example campaign (synthetic)"}}]},
        )
        out = _Out()
        ctx = {
            "cfg": _cfg(),
            "apply": False,
            "out": out,
            "plan_out": None,
            "plan_in": None,
            "receipt_out": None,
            "yes": True,
            "ack_irreversible": True,
            "ack_spend": True,
            "include_rpc_payload": True,
            "ack_sensitive_payload": True,
            "timeout_s": 1.0,
            "artifacts_dir": None,
        }
        _cmd_write(
            spec=spec,
            request_msg=request_msg,
            in_path="request.json",
            ctx=ctx,
            customer_id_override="123",
        )
        plan = out.last["plan"]
        self.assertIn("request", plan)


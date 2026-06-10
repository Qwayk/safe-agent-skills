from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from ga4_api_tool.cli import build_parser
from ga4_api_tool.config import load_config
from ga4_api_tool.errors import SafetyError


class _DummyAudit:
    def write(self, event: str, payload: dict) -> None:  # type: ignore[no-untyped-def]
        _ = event, payload


class _DummyOut:
    def __init__(self) -> None:
        self.last = None

    def emit(self, obj) -> None:  # type: ignore[no-untyped-def]
        self.last = obj


class _NeverCallApiClient:
    def request(self, **kwargs):  # type: ignore[no-untyped-def]
        raise AssertionError("API client must not be called when plan drift is detected")


class TestPlanInDrift(unittest.TestCase):
    def test_plan_in_drift_refuses_before_network(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = root / ".env"
            env_path.write_text("GA4_API_BASE_URL=http://example.invalid\nGA4_TIMEOUT_S=30\n", encoding="utf-8")
            cfg = load_config(str(env_path))

            parser = build_parser()
            plan_path = root / "plan.json"

            # First run: generate a plan (dry-run)
            args1 = parser.parse_args(
                [
                    "--env-file",
                    str(env_path),
                    "data",
                    "v1beta",
                    "properties",
                    "audience-exports",
                    "create",
                    "--parent",
                    "properties/123",
                ]
            )
            out1 = _DummyOut()
            ctx1 = {
                "cfg": cfg,
                "tool": "ga4-api-tool",
                "tool_version": "0.0.0",
                "command_str": "ga4-api-tool ...",
                "timeout_s": 30.0,
                "verbose": False,
                "apply": False,
                "yes": False,
                "plan_in": None,
                "plan_out": str(plan_path),
                "receipt_out": None,
                "ack_irreversible": False,
                "audit": _DummyAudit(),
                "out": out1,
            }
            rc1 = args1.func(args1, ctx1)
            self.assertEqual(rc1, 0)
            self.assertTrue(plan_path.exists())

            # Second run: attempt apply with a different request (fields changes fingerprint)
            args2 = parser.parse_args(
                [
                    "--env-file",
                    str(env_path),
                    "--apply",
                    "--plan-in",
                    str(plan_path),
                    "--fields",
                    "somethingElse",
                    "data",
                    "v1beta",
                    "properties",
                    "audience-exports",
                    "create",
                    "--parent",
                    "properties/123",
                ]
            )
            ctx2 = dict(ctx1)
            ctx2.update(
                {
                    "apply": True,
                    "plan_in": str(plan_path),
                    "plan_out": None,
                    "receipt_out": None,
                    "api_client": _NeverCallApiClient(),
                }
            )
            with self.assertRaises(SafetyError):
                args2.func(args2, ctx2)

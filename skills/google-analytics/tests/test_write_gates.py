from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from ga4_api_tool.cli import build_parser
from ga4_api_tool.config import load_config
from ga4_api_tool.errors import SafetyError


class _NeverCallApiClient:
    def request(self, **kwargs):  # type: ignore[no-untyped-def]
        raise AssertionError("API client must not be called for refused operations")


class TestWriteGates(unittest.TestCase):
    def _env_file(self, root: Path) -> Path:
        p = root / ".env"
        p.write_text("GA4_API_BASE_URL=http://example.invalid\nGA4_TIMEOUT_S=30\n", encoding="utf-8")
        return p

    def test_high_risk_requires_yes_and_plan_in(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = self._env_file(root)
            cfg = load_config(str(env_path))

            parser = build_parser()
            args = parser.parse_args(
                [
                    "--env-file",
                    str(env_path),
                    "--apply",
                    "admin",
                    "v1alpha",
                    "accounts",
                    "access-bindings",
                    "batch-create",
                    "--parent",
                    "accounts/123",
                ]
            )
            ctx = {
                "cfg": cfg,
                "tool": "ga4-api-tool",
                "tool_version": "0.0.0",
                "command_str": "ga4-api-tool ...",
                "timeout_s": 30.0,
                "verbose": False,
                "apply": True,
                "yes": False,
                "plan_in": None,
                "plan_out": None,
                "receipt_out": None,
                "ack_irreversible": False,
                "api_client": _NeverCallApiClient(),
                "audit": object(),
                "out": object(),
            }
            with self.assertRaises(SafetyError):
                args.func(args, ctx)

    def test_irreversible_requires_ack(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            env_path = self._env_file(root)
            cfg = load_config(str(env_path))

            parser = build_parser()
            args = parser.parse_args(
                [
                    "--env-file",
                    str(env_path),
                    "--apply",
                    "--yes",
                    "--plan-in",
                    "plan.json",
                    "admin",
                    "v1alpha",
                    "accounts",
                    "delete",
                    "--name",
                    "accounts/123",
                ]
            )
            ctx = {
                "cfg": cfg,
                "tool": "ga4-api-tool",
                "tool_version": "0.0.0",
                "command_str": "ga4-api-tool ...",
                "timeout_s": 30.0,
                "verbose": False,
                "apply": True,
                "yes": True,
                "plan_in": "plan.json",
                "plan_out": None,
                "receipt_out": None,
                "ack_irreversible": False,
                "api_client": _NeverCallApiClient(),
                "audit": object(),
                "out": object(),
            }
            with self.assertRaises(SafetyError):
                args.func(args, ctx)

from __future__ import annotations

import unittest

from google_ads_api_tool.cli import _normalize_global_flags


class TestCliGlobalFlagNormalization(unittest.TestCase):
    def test_ack_spend_is_normalized_like_other_global_flags(self) -> None:
        argv = [
            "campaign-budget-service",
            "mutate-campaign-budgets",
            "--in",
            "request.json",
            "--apply",
            "--yes",
            "--ack-spend",
        ]
        out = _normalize_global_flags(argv)
        self.assertEqual(out[:3], ["--apply", "--yes", "--ack-spend"])
        self.assertEqual(out[3:], ["campaign-budget-service", "mutate-campaign-budgets", "--in", "request.json"])

    def test_include_rpc_payload_flags_are_normalized(self) -> None:
        argv = [
            "campaign-service",
            "mutate-campaigns",
            "--in",
            "request.json",
            "--apply",
            "--yes",
            "--include-rpc-payload",
            "--ack-sensitive-payload",
        ]
        out = _normalize_global_flags(argv)
        self.assertEqual(
            out[:4],
            ["--apply", "--yes", "--include-rpc-payload", "--ack-sensitive-payload"],
        )
        self.assertEqual(out[4:], ["campaign-service", "mutate-campaigns", "--in", "request.json"])

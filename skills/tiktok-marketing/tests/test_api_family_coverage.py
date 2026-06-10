from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from tiktok_marketing_safe_agent_cli.api_dispatch import load_operations_from_pinned_snapshot
from tiktok_marketing_safe_agent_cli.cli import main


class TestApiFamilyCoverage(unittest.TestCase):
    def _run_main(self, argv: list[str]) -> tuple[int, dict[str, object]]:
        import io
        from contextlib import redirect_stdout

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = main(argv)
        payload = json.loads(buf.getvalue() or "{}")
        return rc, payload

    def _write_env(self, dir_path: Path) -> Path:
        env_path = dir_path / ".env"
        env_path.write_text(
            "\n".join(
                [
                    "TIKTOK_MARKETING_API_BASE_URL=http://example.invalid",
                    "TIKTOK_MARKETING_APP_ID=family-coverage-app",
                    "TIKTOK_MARKETING_APP_SECRET=family-coverage-secret",
                    "TIKTOK_MARKETING_ACCESS_TOKEN=family-coverage-token",
                    "TIKTOK_MARKETING_TIMEOUT_S=30",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        return env_path

    def _sample_value_for_query(self, name: str) -> str:
        if name == "advertiser_id" or name == "advertiser_ids":
            return "adv-123"
        if name == "benchmark_custom_audience_id":
            return "bac-123"
        if name == "comparison_custom_audience_ids":
            return "cca-123"
        if name == "blocked_words":
            return "sample"
        if name == "country_code":
            return "US"
        if name == "date_range":
            return "2026-01-01|2026-01-07"
        if name == "discovery_type":
            return "CUSTOM_AUDIENCE"
        if name == "hashtag_id":
            return "hashtag-1"
        if name == "optimization_goal":
            return "CLICK"
        if name == "shopping_ads_type":
            return "SHOP"
        if name == "store_id":
            return "store-1"
        if name == "identity_id":
            return "identity-1"
        if name == "item_group_ids":
            return "group-1"
        if name == "report_type":
            return "AUCTION"
        if name == "service_type":
            return "SERVICE"
        if name == "term_type":
            return "HASHTAG"
        if name == "language":
            return "en"
        if name == "advertiser_id" in name:
            return "adv-123"
        return f"value-for-{name}"

    def test_one_representative_operation_per_family_has_required_inputs(self) -> None:
        operations = load_operations_from_pinned_snapshot()
        by_family: dict[str, object] = {}
        for op in operations:
            if op.family is None:
                continue
            by_family.setdefault(op.family, op)

        self.assertEqual(len(by_family), 28)
        for family in sorted(by_family):
            op = by_family[family]
            with tempfile.TemporaryDirectory() as d:
                root = Path(d)
                env = self._write_env(root)

                required_queries: dict[str, str] = {}
                for query_name in op.required_query_params:
                    if str(query_name).lower() in {"access-token", "access_token"}:
                        continue
                    required_queries[query_name] = self._sample_value_for_query(str(query_name))

                argv = ["--env-file", str(env), "--output", "json", "api", op.operation_command]
                if required_queries:
                    query_path = root / "query.json"
                    query_path.write_text(json.dumps(required_queries), encoding="utf-8")
                    argv += ["--query-json", str(query_path)]

                rc, payload = self._run_main(argv)

            self.assertEqual(rc, 0, msg=f"family {family} failed")
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["plan"]["operation"]["family"], family)
            self.assertEqual(payload["plan"]["operation"]["operation_command"], op.operation_command)
            self.assertEqual(payload["plan"]["requirements"]["missing_required"], [])

            plan_query = payload["plan"]["inputs"]["query"]
            for query_name, query_value in required_queries.items():
                self.assertEqual(plan_query.get(query_name), query_value)

            header_keys = {str(name).lower() for name in op.required_header_params}
            if "access-token" in header_keys:
                self.assertEqual(payload["plan"]["headers"]["provided"]["Access-Token"], "***REDACTED***")

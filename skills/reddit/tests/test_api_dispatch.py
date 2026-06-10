from __future__ import annotations

from unittest import TestCase

from qwayk_reddit_safe_agent_cli.api_dispatch import build_api_call_plan
from qwayk_reddit_safe_agent_cli.official_inventory import OperationSpec


class TestApiDispatch(TestCase):
    def test_colon_style_required_path_is_detected_without_metadata(self) -> None:
        op = OperationSpec(
            operation_command="sample",
            method="GET",
            path="/api/mod/conversations/:conversation_id",
            doc_url="https://example/",
            section="",
            oauth_scope="",
            required_path_params=(),
        )
        plan = build_api_call_plan(
            tool="qwayk-reddit-safe-agent-cli",
            tool_version="0.0.0",
            env_fingerprint="env-a",
            op=op,
            base_url="https://oauth.reddit.com",
            path_json=None,
            query_json=None,
            body_json=None,
            path_pairs=["conversation_id=abc"],
            query_pairs=None,
            body_pairs=None,
            file_pairs=None,
            body_format="form",
        )
        self.assertEqual(plan["operation"]["path_filled"], "/api/mod/conversations/abc")
        self.assertEqual(plan["requirements"]["missing_required"], [])

    def test_colon_style_required_path_missing_is_reported(self) -> None:
        op = OperationSpec(
            operation_command="sample",
            method="GET",
            path="/api/mod/conversations/:conversation_id",
            doc_url="https://example/",
            section="",
            oauth_scope="",
            required_path_params=(),
        )
        plan = build_api_call_plan(
            tool="qwayk-reddit-safe-agent-cli",
            tool_version="0.0.0",
            env_fingerprint="env-a",
            op=op,
            base_url="https://oauth.reddit.com",
            path_json=None,
            query_json=None,
            body_json=None,
            path_pairs=[],
            query_pairs=None,
            body_pairs=None,
            file_pairs=None,
            body_format="form",
        )
        self.assertEqual(plan["operation"]["path_filled"], "/api/mod/conversations/{conversation_id}")
        self.assertEqual(plan["requirements"]["missing_required"], [{"in": "path", "name": "conversation_id"}])

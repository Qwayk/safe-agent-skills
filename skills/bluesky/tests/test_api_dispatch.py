from __future__ import annotations

from unittest import TestCase

from bluesky_safe_agent_cli.api_dispatch import build_api_call_plan
from bluesky_safe_agent_cli.config import load_config
from bluesky_safe_agent_cli.official_inventory import OperationSpec


class TestApiDispatch(TestCase):
    def test_query_required_param_missing_is_reported(self) -> None:
        cfg = load_config(None)
        op = OperationSpec(
            lexicon_id="app.bsky.actor.getProfile",
            operation_command="app-bsky-actor-get-profile",
            namespace="app.bsky",
            group="actor",
            kind="query",
            http_method="GET",
            path="/xrpc/app.bsky.actor.getProfile",
            doc_url="https://docs.bsky.app/docs/api/app-bsky-actor-get-profile.api",
            docs_source="http-reference",
            stability="stable",
            route_hint="entryway-or-pds",
            primary_cli="bluesky-safe-cli api app-bsky-actor-get-profile",
            query_params=("actor",),
            required_query_params=("actor",),
        )
        plan = build_api_call_plan(
            tool="bluesky-safe-cli",
            tool_version="0.1.0",
            env_fingerprint=cfg.base_url,
            op=op,
            cfg=cfg,
            query_json=None,
            body_json=None,
            query_pairs=None,
            body_pairs=None,
            input_file=None,
            input_content_type=None,
            service_url=None,
        )
        self.assertEqual(plan["requirements"]["missing_required"], [{"in": "query", "name": "actor"}])


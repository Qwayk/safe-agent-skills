from __future__ import annotations

import unittest

from tests import bootstrap  # noqa: F401

from salesforce_platform_safe_agent_cli.commands import salesforce


class TestCommandFamilies(unittest.TestCase):
    def test_core_platform_families_are_present(self) -> None:
        shipped = salesforce.actions()
        for family in [
            "versions",
            "resources",
            "limits",
            "query",
            "query-all",
            "search",
            "sobjects-object",
            "sobjects-row",
            "support",
            "composite",
            "jobs-ingest",
            "jobs-query",
            "openapi-sobjects",
        ]:
            self.assertIn(family, shipped)

    def test_out_of_scope_product_families_are_not_shipped(self) -> None:
        shipped = salesforce.actions()
        for family in [
            "analytics",
            "chatter",
            "connect",
            "commerce",
            "metadata",
            "tooling",
            "ui-api",
        ]:
            self.assertNotIn(family, shipped)

    def test_specific_actions_cover_known_scope_edges(self) -> None:
        shipped = salesforce.actions()
        self.assertIn("delete", shipped["sobjects-event-series"])
        self.assertIn("create", shipped["openapi-sobjects"])
        self.assertIn("results", shipped["openapi-sobjects"])
        self.assertIn("upload", shipped["jobs-ingest"])
        self.assertIn("results", shipped["jobs-query"])

    def test_command_count_is_large_enough_for_platform_rest_surface(self) -> None:
        count = sum(len(actions) for actions in salesforce.actions().values())
        self.assertGreaterEqual(count, 170)

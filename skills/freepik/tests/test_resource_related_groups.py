from __future__ import annotations

import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from freepik_api_tool.commands.resource import cmd_resource_related
from freepik_api_tool.config import Config
from freepik_api_tool.freepik_api import FreepikApi


class TestResourceRelatedGroups(unittest.TestCase):
    def _cfg(self) -> Config:
        return Config(
            base_url="https://api.freepik.com/v1",
            api_key="k",
            timeout_s=1.0,
            auth_header="x-freepik-api-key",
            auth_prefix="",
            accept_language=None,
            image_size=None,
            download_url_jsonpath=None,
            license_url_jsonpath=None,
        )

    def test_related_groups_are_included_without_breaking_old_fields(self) -> None:
        args = SimpleNamespace(id="root", limit=10)
        out = Mock()
        ctx = {"cfg": self._cfg(), "timeout_s": 1.0, "verbose": False, "out": out}

        detail = {
            "data": {
                "id": "root",
                "related_resources": {
                    "suggested": [{"id": "2"}, {"id": "1"}],
                    "same_series": [{"id": "10"}, {"id": "9"}],
                },
                "related_tags": [{"name": "x"}],
            }
        }

        with patch.object(FreepikApi, "get_resource", autospec=True, return_value=detail):
            rc = cmd_resource_related(args, ctx)

        self.assertEqual(rc, 0)
        emitted = out.emit.call_args[0][0]
        self.assertIn("related_resources", emitted)
        self.assertIn("related_tags", emitted)
        self.assertIn("related_groups", emitted)
        self.assertEqual(emitted["related_groups"]["same_series"], ["10", "9"])


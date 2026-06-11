from __future__ import annotations

import unittest

from gsc_api_tool.commands.discovery_methods import is_irreversible_delete, is_write_capable


class TestSafetyClassificationDefaults(unittest.TestCase):
    def test_get_is_read_only(self) -> None:
        self.assertFalse(is_write_capable("any.method", "GET"))

    def test_post_is_write_by_default(self) -> None:
        self.assertTrue(is_write_capable("webmasters.any.newWrite", "POST"))

    def test_read_like_post_allowlist_is_read_only(self) -> None:
        self.assertFalse(is_write_capable("webmasters.searchanalytics.query", "POST"))

    def test_put_patch_delete_are_writes(self) -> None:
        self.assertTrue(is_write_capable("any.method", "PUT"))
        self.assertTrue(is_write_capable("any.method", "PATCH"))
        self.assertTrue(is_write_capable("any.method", "DELETE"))

    def test_unknown_http_method_is_write_capable(self) -> None:
        self.assertTrue(is_write_capable("any.method", "WEIRD"))

    def test_delete_is_irreversible(self) -> None:
        self.assertTrue(is_irreversible_delete("DELETE"))
        self.assertFalse(is_irreversible_delete("GET"))


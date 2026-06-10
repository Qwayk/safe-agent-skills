from __future__ import annotations

import unittest

from gtm_api_tool.cli import build_parser
from gtm_api_tool.commands.discovery_methods import registered_method_ids
from gtm_api_tool.method_inventory import official_method_ids


class TestCliMethodRegistration(unittest.TestCase):
    def test_every_discovery_method_is_registered(self) -> None:
        _ = build_parser()
        self.assertEqual(registered_method_ids(), official_method_ids())


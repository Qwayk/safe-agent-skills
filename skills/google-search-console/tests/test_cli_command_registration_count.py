from __future__ import annotations

import unittest

from gsc_api_tool.cli import build_parser
from gsc_api_tool.discovery import DEFAULT_DISCOVERY_SNAPSHOT


class TestCliCommandRegistrationCount(unittest.TestCase):
    def test_registers_one_command_per_discovery_method(self) -> None:
        parser = build_parser()
        registered = sorted(getattr(parser, "_registered_method_ids", []))
        self.assertEqual(len(registered), 11)

        methods_path = DEFAULT_DISCOVERY_SNAPSHOT.parent / "official_methods_searchconsole_v1_2026-03-05.txt"
        official_method_ids = [ln.strip() for ln in methods_path.read_text(encoding="utf-8").splitlines() if ln.strip()]
        self.assertEqual(registered, official_method_ids)


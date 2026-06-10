from __future__ import annotations

import unittest
from pathlib import Path

from gsc_api_tool.command_naming import method_id_to_command_str
from gsc_api_tool.discovery import DEFAULT_DISCOVERY_SNAPSHOT, list_method_ids, load_discovery_snapshot


class TestOfficialInventory(unittest.TestCase):
    def test_snapshot_and_derived_inventories_match(self) -> None:
        discovery = load_discovery_snapshot(DEFAULT_DISCOVERY_SNAPSHOT)
        snapshot_method_ids = list_method_ids(discovery)
        self.assertEqual(len(snapshot_method_ids), 11)

        methods_path = DEFAULT_DISCOVERY_SNAPSHOT.parent / "official_methods_searchconsole_v1_2026-03-05.txt"
        commands_path = DEFAULT_DISCOVERY_SNAPSHOT.parent / "official_commands_searchconsole_v1_2026-03-05.txt"

        official_method_ids = [ln.strip() for ln in methods_path.read_text(encoding="utf-8").splitlines() if ln.strip()]
        official_commands = [ln.strip() for ln in commands_path.read_text(encoding="utf-8").splitlines() if ln.strip()]

        self.assertEqual(official_method_ids, snapshot_method_ids)
        self.assertEqual(official_commands, [method_id_to_command_str(mid) for mid in snapshot_method_ids])

    def test_snapshot_files_exist(self) -> None:
        self.assertTrue(Path(DEFAULT_DISCOVERY_SNAPSHOT).exists())


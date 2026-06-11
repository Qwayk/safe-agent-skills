from __future__ import annotations

import unittest

from cloudinary_safe_agent_cli.cli import build_parser
from cloudinary_safe_agent_cli.inventory import load_specs_by_area


class TestOperationsParser(unittest.TestCase):
    def test_dynamic_operation_subcommands_exist(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "--output",
                "json",
                "operations",
                "upload",
                "context-add",
                "--form-field",
                "sample=value",
            ]
        )
        self.assertEqual(args.cmd, "operations")
        self.assertEqual(args.operations_cmd, "upload")
        self.assertEqual(args.operation_key, "context-add")
        self.assertTrue(args.write_capable)

    def test_every_area_has_operations(self) -> None:
        grouped = load_specs_by_area()
        self.assertGreaterEqual(len(grouped.keys()), 8)
        for area, specs in grouped.items():
            self.assertGreater(len(specs), 0, area)

    def test_restore_and_download_backup_parser_flags_are_classified(self) -> None:
        parser = build_parser()
        restore_args = parser.parse_args(
            [
                "--output",
                "json",
                "operations",
                "admin",
                "resources-restore-resources-by-public-id",
                "--path-param",
                "resource_type=image",
                "--path-param",
                "type=upload",
                "--path-param",
                "public_id=sample",
            ]
        )
        self.assertEqual(restore_args.operation_key, "resources-restore-resources-by-public-id")
        self.assertTrue(restore_args.write_capable)

        download_args = parser.parse_args(
            [
                "--output",
                "json",
                "operations",
                "upload",
                "download-backup",
                "--query",
                "public_id=sample",
            ]
        )
        self.assertEqual(download_args.operation_key, "download-backup")
        self.assertFalse(download_args.write_capable)

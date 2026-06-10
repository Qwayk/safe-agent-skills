from __future__ import annotations

import re
import unittest

from linkedin_ads_api_tool.cli import build_parser
from linkedin_ads_api_tool.operation_catalog import OPERATIONS_BY_FAMILY


_PATH_PLACEHOLDER_RE = re.compile(r"{([^{}]+)}")


class TestOperationCatalogRuntime(unittest.TestCase):
    def _build_argv_for_spec(self, family: str, spec) -> list[str]:
        argv = [family, spec.command]
        placeholders = sorted(set(_PATH_PLACEHOLDER_RE.findall(spec.path)))
        for placeholder in placeholders:
            argv.append(f"--{placeholder.replace('_', '-')}")
            argv.append(f"urn:li:test:{placeholder}")
        return argv

    def test_each_family_has_a_parsable_command(self) -> None:
        parser = build_parser()
        for family, operations in OPERATIONS_BY_FAMILY.items():
            for spec in operations:
                with self.subTest(family=family, operation=spec.command):
                    argv = self._build_argv_for_spec(family, spec)
                    parsed = parser.parse_args(argv)
                    self.assertEqual(parsed.cmd, family)
                    self.assertEqual(parsed.operation, spec.command)

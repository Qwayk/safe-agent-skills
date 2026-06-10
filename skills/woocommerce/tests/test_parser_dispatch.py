from __future__ import annotations

import unittest

from qwayk_woocommerce_safe_agent_cli.catalog import load_operation_catalog
from qwayk_woocommerce_safe_agent_cli.cli import build_parser


def _sample_value(name: str) -> str:
    return {
        "id": "1",
        "note_id": "2",
        "refund_id": "3",
        "product_id": "10",
        "attribute_id": "11",
        "group_id": "general",
        "zone_id": "12",
        "slug": "standard",
        "location": "US",
        "currency": "USD",
    }.get(name, "1")


class TestParserDispatch(unittest.TestCase):
    def test_every_catalog_command_has_a_callable_parser(self) -> None:
        parser = build_parser()
        for spec in load_operation_catalog():
            argv = [spec.family, spec.action]
            for path_param in spec.path_parameters:
                argv.extend([f"--{path_param.replace('_', '-')}", _sample_value(path_param)])
            if spec.body_mode == "required":
                argv.extend(["--body-json", "{}"])
            parsed = parser.parse_args(argv)
            self.assertEqual(parsed.operation_spec.key, spec.key)
            self.assertTrue(callable(parsed.func))

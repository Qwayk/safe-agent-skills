from __future__ import annotations

import unittest

from google_merchant_api_tool.cli import build_parser
from google_merchant_api_tool.discovery import SHIPPED_FAMILIES, load_shipped_methods
from google_merchant_api_tool.method_inventory import method_id_to_command_tokens


class TestCliDiscoveryCommands(unittest.TestCase):
    def test_nested_discovery_commands_are_reachable_for_all_families(self) -> None:
        parser = build_parser()
        methods_by_family = {
            family: [m for m in load_shipped_methods() if m.family == family]
            for family in SHIPPED_FAMILIES
        }
        for family in SHIPPED_FAMILIES:
            self.assertTrue(methods_by_family[family], f"No commands loaded for family: {family}")

        for family, methods in methods_by_family.items():
            representative = sorted(methods, key=lambda m: m.command_id)[0]
            argv = ["--output", "json", *_discover_argv(method=representative)]
            args = parser.parse_args(argv)
            self.assertEqual(args.discovery_method.command_id, representative.command_id)
            self.assertTrue(callable(args.func))
            self.assertTrue(hasattr(args, "discovery_method"))

    def test_non_v1_discovery_commands_parse_with_version_token(self) -> None:
        parser = build_parser()
        methods = load_shipped_methods()
        target = next(
            m
            for m in methods
            if m.family == "loyaltycustomers_v1alpha"
            and m.command_id == "accounts.loyaltyCustomers.manage"
        )
        args = parser.parse_args(["--output", "json", *_discover_argv(method=target)])
        self.assertEqual(args.discovery_method.command_id, target.command_id)

    def test_product_inputs_insert_requires_payload_flags_to_parse(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "--output",
                "json",
                "accounts",
                "product-inputs",
                "insert",
                "--parent",
                "accounts/123456",
                "--body-file",
                "product.json",
            ]
        )
        self.assertEqual(args.discovery_method.command_id, "accounts.productInputs.insert")
        self.assertEqual(args.body_file, "product.json")


def _to_cli_flag(param_name: str) -> str:
    flag = ["--"]
    for i, ch in enumerate(param_name):
        if ch == "_":
            flag.append("-")
            continue
        if ch.isupper():
            if i > 0:
                flag.append("-")
            flag.append(ch.lower())
            continue
        flag.append(ch)
    return "".join(flag)


def _sample_value_for_param(param_name: str) -> str:
    if param_name == "parent":
        return "accounts/123456"
    if "id" in param_name.lower():
        return "123456"
    if param_name.lower() == "name":
        return "product-123"
    return "sample"


def _discover_argv(*, method) -> list[str]:
    argv: list[str] = list(method_id_to_command_tokens(method.command_id, family=method.family))
    for param in sorted(method.parameters, key=lambda p: p.name):
        if not param.required or (param.location or "").lower() != "path":
            continue
        argv.extend([_to_cli_flag(param.name), _sample_value_for_param(param.name)])
    return argv

from __future__ import annotations

import argparse
import unittest

from ga4_api_tool.cli import build_parser
from ga4_api_tool.commands.discovery_methods import OperationKey
from ga4_api_tool.method_inventory import official_method_ids, snapshots


def _collect_operation_keys(parser: argparse.ArgumentParser) -> set[OperationKey]:
    ops: set[OperationKey] = set()

    def walk(p: argparse.ArgumentParser) -> None:
        defaults = getattr(p, "_defaults", {}) or {}
        op = defaults.get("ga4_operation_key")
        if isinstance(op, OperationKey):
            ops.add(op)

        for action in getattr(p, "_actions", []):
            if isinstance(action, argparse._SubParsersAction):
                for child in action.choices.values():
                    walk(child)

    walk(parser)
    return ops


class TestCliMethodRegistration(unittest.TestCase):
    def test_all_official_operations_registered(self) -> None:
        parser = build_parser()
        got_ops = _collect_operation_keys(parser)
        self.assertTrue(got_ops)

        expected_ops: set[OperationKey] = set()
        for spec in snapshots():
            for mid in official_method_ids(spec):
                expected_ops.add(
                    OperationKey(
                        service=spec.service_token,
                        version=spec.version_token,
                        method_id=mid,
                    )
                )

        self.assertEqual(expected_ops, got_ops)


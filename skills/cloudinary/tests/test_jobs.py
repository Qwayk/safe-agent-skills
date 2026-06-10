from __future__ import annotations

import unittest

from cloudinary_safe_agent_cli.inventory import load_operation_specs


class TestOperationSurface(unittest.TestCase):
    def test_no_duplicate_area_op_keys(self) -> None:
        seen: set[tuple[str, str]] = set()
        for spec in load_operation_specs():
            key = (spec.area, spec.op_key)
            self.assertNotIn(key, seen)
            seen.add(key)

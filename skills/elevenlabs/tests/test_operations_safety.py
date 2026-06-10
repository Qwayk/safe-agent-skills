from __future__ import annotations

import unittest

from elevenlabs_api_tool.operations import OPERATIONS


class TestOperationSafety(unittest.TestCase):
    def test_write_gate_requires_tagged_post_like_methods(self) -> None:
        override_tag = "post_read"
        gated_methods = {"POST", "PUT", "PATCH"}
        for op in OPERATIONS:
            method = op.method.upper()
            if method not in gated_methods:
                continue
            safety_tags = set(op.safety)
            has_write = "write" in safety_tags
            has_override = override_tag in safety_tags
            self.assertTrue(
                has_write or has_override,
                msg=f"{op.cli_command} ({method}) must include 'write' or '{override_tag}'",
            )
            self.assertFalse(
                has_write and has_override,
                msg=f"{op.cli_command} ({method}) must not mix 'write' and '{override_tag}'",
            )

    def test_delete_operations_require_write_and_irreversible(self) -> None:
        delete_tag = "DELETE"
        for op in OPERATIONS:
            method = op.method.upper()
            if method != delete_tag:
                continue
            safety_tags = set(op.safety)
            self.assertIn(
                "write",
                safety_tags,
                msg=f"{op.cli_command} ({method}) must include 'write'",
            )
            self.assertIn(
                "irreversible",
                safety_tags,
                msg=f"{op.cli_command} ({method}) must include 'irreversible'",
            )
            self.assertNotIn(
                "post_read",
                safety_tags,
                msg=f"{op.cli_command} ({method}) must not include 'post_read'",
            )

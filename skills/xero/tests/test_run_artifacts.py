from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from xero_safe_agent_cli.state import read_json_object, write_private_bytes, write_private_json


class TestProtectedArtifacts(unittest.TestCase):
    def test_json_plan_or_receipt_is_atomic_private_and_readable(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "receipts" / "receipt.json"
            write_private_json(path, {"ok": True, "tenant_id": "tenant-1"})
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)
            self.assertEqual(read_json_object(path)["tenant_id"], "tenant-1")

    def test_protected_binary_output_is_private(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "protected" / "xero-file.bin"
            write_private_bytes(path, b"private-xero-content")
            self.assertEqual(path.read_bytes(), b"private-xero-content")
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)

    def test_non_object_json_is_rejected_for_saved_state(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.json"
            path.write_text(json.dumps(["not", "an", "object"]), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "JSON object"):
                read_json_object(path)


if __name__ == "__main__":
    unittest.main()

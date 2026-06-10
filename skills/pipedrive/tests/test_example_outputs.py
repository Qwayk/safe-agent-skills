from __future__ import annotations

import json
import unittest
from pathlib import Path


class TestExampleOutputs(unittest.TestCase):
    def test_auth_check_example_matches_runtime_shape(self) -> None:
        root = Path(__file__).resolve().parents[1]
        payload = json.loads((root / "docs" / "examples" / "outputs" / "auth_check.json").read_text(encoding="utf-8"))
        self.assertEqual(payload["operation"], "GET /api/v1/users/me")
        self.assertEqual(payload["http"]["method"], "GET")
        self.assertEqual(payload["request"]["path"], "/users/me")
        self.assertIsInstance(payload["data"], list)
        self.assertFalse(payload["response"]["binary"])

    def test_files_download_example_matches_runtime_shape(self) -> None:
        root = Path(__file__).resolve().parents[1]
        payload = json.loads((root / "docs" / "examples" / "outputs" / "files_download_metadata.json").read_text(encoding="utf-8"))
        self.assertEqual(payload["operation"], "GET /files/{id}/download")
        self.assertEqual(payload["http"]["method"], "HEAD")
        self.assertEqual(payload["request"]["path"], "/files/12345/download")
        self.assertEqual(payload["data"]["path"], "/files/12345/download")
        self.assertTrue(payload["response"]["binary"])

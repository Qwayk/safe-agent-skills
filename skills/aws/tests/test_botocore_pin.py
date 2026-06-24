from __future__ import annotations

import tomllib
import unittest
from pathlib import Path

import boto3
import botocore


class TestBotocorePin(unittest.TestCase):
    def test_boto3_and_botocore_are_exactly_pinned(self) -> None:
        self.assertEqual(boto3.__version__, "1.43.36")
        self.assertEqual(botocore.__version__, "1.43.36")

    def test_pyproject_contains_exact_pins(self) -> None:
        pyproject = Path(__file__).resolve().parents[1] / "pyproject.toml"
        data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
        deps = data["project"]["dependencies"]

        self.assertIn("boto3==1.43.36", deps)
        self.assertIn("botocore==1.43.36", deps)

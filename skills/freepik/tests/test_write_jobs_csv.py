from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from freepik_api_tool.jobs_csv import write_jobs_csv


class TestWriteJobsCsv(unittest.TestCase):
    def test_deterministic_sorted_and_deduped(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "jobs.csv"
            res = write_jobs_csv(p, resource_ids=["3", "1", "2", "2"], fmt="jpg")
            self.assertEqual(res.columns, ["resource_id", "format"])
            self.assertEqual(res.rows, 3)
            text = p.read_text(encoding="utf-8").splitlines()
            self.assertEqual(text[0], "resource_id,format")
            self.assertEqual(text[1:], ["1,jpg", "2,jpg", "3,jpg"])

    def test_optional_image_size_column(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "jobs.csv"
            res = write_jobs_csv(p, resource_ids=["2", "1"], fmt="jpg", image_size="2000px")
            self.assertEqual(res.columns, ["resource_id", "format", "image_size"])
            text = p.read_text(encoding="utf-8").splitlines()
            self.assertEqual(text[0], "resource_id,format,image_size")
            self.assertEqual(text[1:], ["1,jpg,2000px", "2,jpg,2000px"])


from __future__ import annotations

import datetime as dt
import unittest

from pinterest_api_tool.api import build_analytics_params


class TestApiParams(unittest.TestCase):
    def test_build_analytics_params_defaults(self) -> None:
        params = build_analytics_params(
            start_date=None,
            end_date=None,
            metrics=None,
            extra_params=None,
            default_days=90,
            default_metrics=["impression"],
        )
        self.assertIn("start_date", params)
        self.assertIn("end_date", params)
        self.assertIn("metric_types", params)
        self.assertEqual(params["metric_types"], "IMPRESSION")

        start = dt.date.fromisoformat(params["start_date"])
        end = dt.date.fromisoformat(params["end_date"])
        self.assertLessEqual(start, end)

    def test_build_analytics_params_rejects_bad_date(self) -> None:
        with self.assertRaises(RuntimeError):
            build_analytics_params(
                start_date="not-a-date",
                end_date="2025-01-01",
                metrics=["impression"],
                extra_params=None,
            )

    def test_build_analytics_params_accepts_extra_params(self) -> None:
        params = build_analytics_params(
            start_date="2025-01-01",
            end_date="2025-01-31",
            metrics=["impression", "save"],
            extra_params=["split_field=source", "split_field=app_type", "foo=bar"],
        )
        # split_field appears twice -> list
        self.assertEqual(params["split_field"], ["source", "app_type"])
        self.assertEqual(params["foo"], "bar")
        self.assertEqual(params["metric_types"], "IMPRESSION,SAVE")

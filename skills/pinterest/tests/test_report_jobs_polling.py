from __future__ import annotations

import unittest

from pinterest_api_tool.commands import report_jobs


class TestReportJobsPolling(unittest.TestCase):
    def test_poll_stops_at_terminal_status(self) -> None:
        calls: list[str] = []

        def get_fn(token: str) -> dict:
            calls.append(token)
            if len(calls) == 1:
                return {"report_status": "IN_PROGRESS"}
            return {"report_status": "FINISHED", "url": "https://example.com/report.csv"}

        slept: list[float] = []

        def sleep_fn(s: float) -> None:
            slept.append(float(s))

        data = report_jobs.poll_report_status(
            get_fn,
            token="tok_1",
            max_attempts=10,
            max_seconds=60.0,
            poll_interval_s=0.0,
            sleep_fn=sleep_fn,
        )
        self.assertEqual(data["report_status"], "FINISHED")
        self.assertEqual(calls, ["tok_1", "tok_1"])
        self.assertEqual(slept, [0.0])

    def test_poll_attempt_cap_exceeded(self) -> None:
        calls = 0

        def get_fn(token: str) -> dict:
            nonlocal calls
            calls += 1
            return {"status": "IN_PROGRESS"}

        with self.assertRaises(report_jobs.PollingCapExceededError) as ctx:
            report_jobs.poll_report_status(
                get_fn,
                token="tok",
                max_attempts=3,
                max_seconds=60.0,
                poll_interval_s=0.0,
                sleep_fn=lambda _s: None,
            )
        self.assertIn("max_attempts", str(ctx.exception))
        self.assertEqual(calls, 3)

    def test_poll_time_cap_exceeded(self) -> None:
        calls = 0
        now_values = iter([0.0, 0.0, 2.0])

        def now_fn() -> float:
            return float(next(now_values))

        def get_fn(token: str) -> dict:
            nonlocal calls
            calls += 1
            return {"status": "IN_PROGRESS"}

        with self.assertRaises(report_jobs.PollingCapExceededError) as ctx:
            report_jobs.poll_report_status(
                get_fn,
                token="tok",
                max_attempts=10,
                max_seconds=1.0,
                poll_interval_s=0.0,
                sleep_fn=lambda _s: None,
                now_fn=now_fn,
            )
        self.assertIn("max_seconds", str(ctx.exception))
        self.assertEqual(calls, 1)

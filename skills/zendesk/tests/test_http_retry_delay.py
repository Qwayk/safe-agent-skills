from __future__ import annotations

import random
import unittest

from zendesk_api_tool.http import HttpClient


class TestHttpRetryDelay(unittest.TestCase):
    def test_retry_after_is_honored_and_bounded(self) -> None:
        random.seed(0)
        d = HttpClient._retry_delay_s(attempt=1, status=429, headers={"Retry-After": "2"})  # noqa: SLF001
        self.assertGreaterEqual(d, 1.0)
        self.assertLessEqual(d, 30.0)

    def test_backoff_increases_with_attempt(self) -> None:
        random.seed(1)
        d1 = HttpClient._retry_delay_s(attempt=1, status=500, headers={})  # noqa: SLF001
        random.seed(1)
        d2 = HttpClient._retry_delay_s(attempt=2, status=500, headers={})  # noqa: SLF001
        self.assertGreater(d2, d1)


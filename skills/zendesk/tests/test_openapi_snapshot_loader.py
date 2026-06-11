from __future__ import annotations

import unittest

from zendesk_api_tool.openapi_snapshot import load_pinned_openapi_snapshot


class TestOpenApiSnapshotLoader(unittest.TestCase):
    def test_load_pinned_openapi_snapshot_succeeds(self) -> None:
        snap = load_pinned_openapi_snapshot()
        self.assertIsInstance(snap.obj, dict)
        paths = snap.obj.get("paths")
        self.assertIsInstance(paths, dict)


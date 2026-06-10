from __future__ import annotations

import unittest

from ga4_api_tool.commands.discovery_methods import classify_risk
from ga4_api_tool.method_inventory import methods_for_snapshot, snapshots


def _find_method(method_id: str):
    for snap in snapshots():
        for m in methods_for_snapshot(snap):
            if m.method_id == method_id:
                return snap, m
    raise AssertionError(f"Method not found in snapshots: {method_id}")


class TestRiskClassifier(unittest.TestCase):
    def test_data_report_posts_are_low_risk(self) -> None:
        snap, m = _find_method("analyticsdata.properties.runReport")
        risk = classify_risk(snapshot=snap, method_id=m.method_id, http_method=m.http_method, method_name=m.method_name)
        self.assertEqual(risk["level"], "low")

    def test_data_funnel_report_post_is_low_risk(self) -> None:
        snap, m = _find_method("analyticsdata.properties.runFunnelReport")
        risk = classify_risk(snapshot=snap, method_id=m.method_id, http_method=m.http_method, method_name=m.method_name)
        self.assertEqual(risk["level"], "low")

    def test_admin_access_report_post_is_low_risk(self) -> None:
        snap, m = _find_method("analyticsadmin.accounts.runAccessReport")
        risk = classify_risk(snapshot=snap, method_id=m.method_id, http_method=m.http_method, method_name=m.method_name)
        self.assertEqual(risk["level"], "low")

    def test_audience_exports_create_is_not_low_risk(self) -> None:
        snap, m = _find_method("analyticsdata.properties.audienceExports.create")
        risk = classify_risk(snapshot=snap, method_id=m.method_id, http_method=m.http_method, method_name=m.method_name)
        self.assertIn(risk["level"], {"medium", "high", "irreversible"})

    def test_access_bindings_are_high_risk(self) -> None:
        snap, m = _find_method("analyticsadmin.accounts.accessBindings.batchCreate")
        risk = classify_risk(snapshot=snap, method_id=m.method_id, http_method=m.http_method, method_name=m.method_name)
        self.assertEqual(risk["level"], "high")

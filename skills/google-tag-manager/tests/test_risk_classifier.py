from __future__ import annotations

import unittest

from gtm_api_tool.commands.discovery_methods import _before_state_read_path, _build_write_recovery, _risk_level, method_spec


class TestRiskClassifier(unittest.TestCase):
    def test_get_is_low(self) -> None:
        m = method_spec("tagmanager.accounts.list")
        level, _ = _risk_level(m)
        self.assertEqual(level, "low")

    def test_read_like_post_is_low(self) -> None:
        m = method_spec("tagmanager.accounts.containers.workspaces.folders.entities")
        level, _ = _risk_level(m)
        self.assertEqual(level, "low")

    def test_patch_is_medium(self) -> None:
        m = method_spec("tagmanager.accounts.update")
        level, _ = _risk_level(m)
        self.assertEqual(level, "medium")

    def test_bulk_update_is_high(self) -> None:
        m = method_spec("tagmanager.accounts.containers.workspaces.bulk_update")
        level, _ = _risk_level(m)
        self.assertEqual(level, "high")

    def test_delete_is_irreversible(self) -> None:
        m = method_spec("tagmanager.accounts.containers.workspaces.tags.delete")
        level, _ = _risk_level(m)
        self.assertEqual(level, "irreversible")

    def test_publish_is_irreversible(self) -> None:
        m = method_spec("tagmanager.accounts.containers.versions.publish")
        level, _ = _risk_level(m)
        self.assertEqual(level, "irreversible")

    def test_recovery_for_revert_backed_workspace_entity_write(self) -> None:
        m = method_spec("tagmanager.accounts.containers.workspaces.tags.update")
        recovery = _build_write_recovery(method=m, request_path="tagmanager/v2/accounts/1/containers/2/workspaces/3/tags/4")
        self.assertEqual(recovery["end_state"], "rollback_by_inverse_action")
        self.assertEqual(recovery["strategy"], "revert")
        self.assertEqual(recovery["rollback_plan"]["method_id"], "tagmanager.accounts.containers.workspaces.tags.revert")
        self.assertTrue(recovery["rollback_ready"])

    def test_recovery_for_delete_using_undelete(self) -> None:
        m = method_spec("tagmanager.accounts.containers.versions.delete")
        recovery = _build_write_recovery(method=m, request_path="tagmanager/v2/accounts/1/containers/2/versions/3")
        self.assertEqual(recovery["end_state"], "rollback_by_inverse_action")
        self.assertEqual(recovery["strategy"], "undelete")
        self.assertEqual(recovery["rollback_plan"]["method_id"], "tagmanager.accounts.containers.versions.undelete")
        self.assertTrue(recovery["rollback_ready"])

    def test_recovery_for_create_using_delete(self) -> None:
        m = method_spec("tagmanager.accounts.containers.create")
        recovery = _build_write_recovery(method=m, request_path="tagmanager/v2/accounts/1/containers")
        self.assertEqual(recovery["end_state"], "rollback_by_inverse_action")
        self.assertEqual(recovery["strategy"], "delete_after_create")
        self.assertEqual(recovery["rollback_plan"]["method_id"], "tagmanager.accounts.containers.delete")
        self.assertFalse(recovery["rollback_ready"])

        recovery_after_apply = _build_write_recovery(
            method=m,
            request_path="tagmanager/v2/accounts/1/containers",
            created_resource_path="accounts/1/containers/2",
        )
        self.assertTrue(recovery_after_apply["rollback_ready"])
        self.assertEqual(
            recovery_after_apply["rollback_plan"]["path"],
            "tagmanager/v2/accounts/1/containers/2",
        )

    def test_recovery_irreversible_case(self) -> None:
        m = method_spec("tagmanager.accounts.containers.versions.publish")
        recovery = _build_write_recovery(method=m, request_path="tagmanager/v2/accounts/1/containers/2/versions/3")
        self.assertEqual(recovery["end_state"], "irreversible_and_clearly_labeled")
        self.assertFalse(recovery["rollback_ready"])

    def test_publish_before_state_read_path_strips_action(self) -> None:
        method = method_spec("tagmanager.accounts.containers.versions.publish")
        path = _before_state_read_path(
            method=method,
            request_path="tagmanager/v2/accounts/1/containers/2/versions/3:publish",
        )
        self.assertEqual(path, "tagmanager/v2/accounts/1/containers/2/versions/3")

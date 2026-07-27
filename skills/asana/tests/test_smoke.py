from __future__ import annotations

import unittest

from asana_safe_agent_cli.inventory import command_names, manifest, operations


class TestInventorySmoke(unittest.TestCase):
    def test_pinned_boundary_and_fixed_commands(self) -> None:
        info = manifest()
        self.assertEqual(info["path_count"], 175)
        self.assertEqual(info["operation_count"], 249)
        self.assertEqual(info["family_count"], 49)
        self.assertEqual(info["command_count"], 248)
        self.assertEqual(len(command_names()), 248)
        self.assertEqual(len(set(command_names())), 248)

    def test_batch_is_the_only_in_spec_exclusion(self) -> None:
        excluded = [item for item in operations() if not item.get("command")]
        self.assertEqual([(item["method"], item["path"]) for item in excluded], [("POST", "/batch")])

    def test_oauth_scope_guidance_is_preserved(self) -> None:
        get_tasks = next(item for item in operations() if item["operation_id"] == "getTasksForProject")
        self.assertEqual(get_tasks["oauth_scopes"], ["tasks:read"])
        self.assertIn("personalAccessToken", get_tasks["auth_schemes"])
        self.assertIn("oauth2", get_tasks["auth_schemes"])

    def test_preview_deprecated_and_visible_collaboration_are_classified(self) -> None:
        items = {item["operation_id"]: item for item in operations()}
        self.assertEqual(
            items["getProjectBrief"]["status"],
            "implemented_developer_preview_live_unverified",
        )
        self.assertEqual(
            items["getProjectStatus"]["status"],
            "implemented_deprecated_live_unverified",
        )
        self.assertEqual(items["createStatusForObject"]["risk_class"], "write_stronger_approval")
        self.assertEqual(items["addFollowersForTask"]["risk_class"], "write_stronger_approval")


if __name__ == "__main__":
    unittest.main()

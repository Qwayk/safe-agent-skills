# Asana REST API coverage

This ledger accounts for every callable operation in Asana's pinned official REST specification.
The command column names the fixed CLI command; it never accepts a method, URL, or arbitrary path.

## Pinned boundary

- Official source: `Asana/openapi` commit `56796a67a3c093eedf55fd9682357957a2ebfd85`
- File: `defs/asana_oas.yaml` (vendored as `specs/asana_oas.yaml`)
- SHA-256: `cb3b90f4e0af56035eab0c648974f625b942a28a7144aa6c2326e38ca0bb3d56`
- Paths: **175**
- Operations: **249**
- Tagged REST families: **49**
- Shipped fixed commands: **248**
- App Components and SCIM: outside this product boundary
- Live Asana proof: not run; every shipped operation is live-unverified

## Classification key

- `implemented_live_unverified`: fixed command is shipped from the official spec; no live credential was used.
- `implemented_access_gated_live_unverified`: fixed command is shipped, but official text identifies a plan, permission, OAuth-app, admin, or service-account gate.
- `implemented_developer_preview_live_unverified`: fixed command is shipped, but Asana marks the family as preview and subject to change.
- `implemented_deprecated_live_unverified`: fixed command is shipped for boundary completeness, but Asana directs new integrations to a replacement family.
- `intentionally_excluded`: represented in the ledger but not callable by product choice.

## Operation ledger

| Family | Method | Path | Operation ID | Fixed command | Status | Risk / access |
| --- | --- | --- | --- | --- | --- | --- |
| Access requests | GET | `/access_requests` | `getAccessRequests` | `asana-safe api get-access-requests` | `implemented_live_unverified` | read; standard bearer access |
| Access requests | POST | `/access_requests` | `createAccessRequest` | `asana-safe api create-access-request` | `implemented_live_unverified` | write_stronger_approval; standard bearer access |
| Access requests | POST | `/access_requests/{access_request_gid}/approve` | `approveAccessRequest` | `asana-safe api approve-access-request` | `implemented_live_unverified` | write_stronger_approval; standard bearer access |
| Access requests | POST | `/access_requests/{access_request_gid}/reject` | `rejectAccessRequest` | `asana-safe api reject-access-request` | `implemented_live_unverified` | write_stronger_approval; standard bearer access |
| Agents | GET | `/workspaces/{workspace_gid}/agents` | `getAgentsForWorkspace` | `asana-safe api get-agents-for-workspace` | `implemented_live_unverified` | read; standard bearer access |
| Agents | GET | `/agents/{agent_gid}` | `getAgent` | `asana-safe api get-agent` | `implemented_live_unverified` | read; standard bearer access |
| AI Studio usage API | GET | `/workspaces/{workspace_gid}/ai_studio/runs` | `getAiStudioRuns` | `asana-safe api get-ai-studio-runs` | `implemented_access_gated_live_unverified` | read; service_account, admin_permission, restricted_access |
| AI Studio usage API | GET | `/workspaces/{workspace_gid}/ai_studio/seats` | `getAiStudioSeats` | `asana-safe api get-ai-studio-seats` | `implemented_access_gated_live_unverified` | read; service_account, admin_permission, restricted_access |
| Allocations | GET | `/allocations/{allocation_gid}` | `getAllocation` | `asana-safe api get-allocation` | `implemented_live_unverified` | read; standard bearer access |
| Allocations | PUT | `/allocations/{allocation_gid}` | `updateAllocation` | `asana-safe api update-allocation` | `implemented_live_unverified` | write; standard bearer access |
| Allocations | DELETE | `/allocations/{allocation_gid}` | `deleteAllocation` | `asana-safe api delete-allocation` | `implemented_live_unverified` | write_stronger_approval; standard bearer access |
| Allocations | GET | `/allocations` | `getAllocations` | `asana-safe api get-allocations` | `implemented_live_unverified` | read; standard bearer access |
| Allocations | POST | `/allocations` | `createAllocation` | `asana-safe api create-allocation` | `implemented_live_unverified` | write; standard bearer access |
| Attachments | GET | `/attachments/{attachment_gid}` | `getAttachment` | `asana-safe api get-attachment` | `implemented_live_unverified` | read; standard bearer access |
| Attachments | DELETE | `/attachments/{attachment_gid}` | `deleteAttachment` | `asana-safe api delete-attachment` | `implemented_live_unverified` | write_stronger_approval; standard bearer access |
| Attachments | GET | `/attachments` | `getAttachmentsForObject` | `asana-safe api get-attachments-for-object` | `implemented_live_unverified` | read; standard bearer access |
| Attachments | POST | `/attachments` | `createAttachmentForObject` | `asana-safe api create-attachment-for-object` | `implemented_live_unverified` | write_stronger_approval; standard bearer access |
| Audit log API | GET | `/workspaces/{workspace_gid}/audit_log_events` | `getAuditLogEvents` | `asana-safe api get-audit-log-events` | `implemented_access_gated_live_unverified` | sensitive_read; service_account, enterprise_plan, paid_plan |
| Batch API | POST | `/batch` | `createBatchRequest` | — | `intentionally_excluded` | Arbitrary relative-path batch bridge is outside the fixed-command product boundary. |
| Budgets | GET | `/budgets` | `getBudgets` | `asana-safe api get-budgets` | `implemented_live_unverified` | read; standard bearer access |
| Budgets | POST | `/budgets` | `createBudget` | `asana-safe api create-budget` | `implemented_live_unverified` | write_stronger_approval; standard bearer access |
| Budgets | GET | `/budgets/{budget_gid}` | `getBudget` | `asana-safe api get-budget` | `implemented_live_unverified` | read; standard bearer access |
| Budgets | PUT | `/budgets/{budget_gid}` | `updateBudget` | `asana-safe api update-budget` | `implemented_live_unverified` | write_stronger_approval; standard bearer access |
| Budgets | DELETE | `/budgets/{budget_gid}` | `deleteBudget` | `asana-safe api delete-budget` | `implemented_live_unverified` | write_stronger_approval; standard bearer access |
| Custom field settings | GET | `/projects/{project_gid}/custom_field_settings` | `getCustomFieldSettingsForProject` | `asana-safe api get-custom-field-settings-for-project` | `implemented_live_unverified` | read; standard bearer access |
| Custom field settings | GET | `/portfolios/{portfolio_gid}/custom_field_settings` | `getCustomFieldSettingsForPortfolio` | `asana-safe api get-custom-field-settings-for-portfolio` | `implemented_live_unverified` | read; standard bearer access |
| Custom field settings | GET | `/goals/{goal_gid}/custom_field_settings` | `getCustomFieldSettingsForGoal` | `asana-safe api get-custom-field-settings-for-goal` | `implemented_live_unverified` | read; standard bearer access |
| Custom field settings | GET | `/teams/{team_gid}/custom_field_settings` | `getCustomFieldSettingsForTeam` | `asana-safe api get-custom-field-settings-for-team` | `implemented_live_unverified` | read; standard bearer access |
| Custom fields | POST | `/custom_fields` | `createCustomField` | `asana-safe api create-custom-field` | `implemented_access_gated_live_unverified` | write_stronger_approval; paid_plan |
| Custom fields | GET | `/custom_fields/{custom_field_gid}` | `getCustomField` | `asana-safe api get-custom-field` | `implemented_access_gated_live_unverified` | read; paid_plan |
| Custom fields | PUT | `/custom_fields/{custom_field_gid}` | `updateCustomField` | `asana-safe api update-custom-field` | `implemented_access_gated_live_unverified` | write_stronger_approval; paid_plan |
| Custom fields | DELETE | `/custom_fields/{custom_field_gid}` | `deleteCustomField` | `asana-safe api delete-custom-field` | `implemented_access_gated_live_unverified` | write_stronger_approval; paid_plan |
| Custom fields | GET | `/workspaces/{workspace_gid}/custom_fields` | `getCustomFieldsForWorkspace` | `asana-safe api get-custom-fields-for-workspace` | `implemented_access_gated_live_unverified` | read; paid_plan |
| Custom fields | POST | `/custom_fields/{custom_field_gid}/enum_options` | `createEnumOptionForCustomField` | `asana-safe api create-enum-option-for-custom-field` | `implemented_access_gated_live_unverified` | write_stronger_approval; paid_plan |
| Custom fields | POST | `/custom_fields/{custom_field_gid}/enum_options/insert` | `insertEnumOptionForCustomField` | `asana-safe api insert-enum-option-for-custom-field` | `implemented_access_gated_live_unverified` | write_stronger_approval; paid_plan |
| Custom fields | PUT | `/enum_options/{enum_option_gid}` | `updateEnumOption` | `asana-safe api update-enum-option` | `implemented_access_gated_live_unverified` | write_stronger_approval; paid_plan |
| Custom types | GET | `/custom_types` | `getCustomTypes` | `asana-safe api get-custom-types` | `implemented_live_unverified` | read; standard bearer access |
| Custom types | GET | `/custom_types/{custom_type_gid}` | `getCustomType` | `asana-safe api get-custom-type` | `implemented_live_unverified` | read; standard bearer access |
| Events | GET | `/events` | `getEvents` | `asana-safe api get-events` | `implemented_live_unverified` | read; standard bearer access |
| Exports | POST | `/exports/graph` | `createGraphExport` | `asana-safe api create-graph-export` | `implemented_access_gated_live_unverified` | write_stronger_approval; service_account, enterprise_plan, paid_plan, availability_gate |
| Exports | POST | `/exports/resource` | `createResourceExport` | `asana-safe api create-resource-export` | `implemented_access_gated_live_unverified` | write_stronger_approval; service_account, enterprise_plan, paid_plan, availability_gate |
| Goal relationships | GET | `/goal_relationships/{goal_relationship_gid}` | `getGoalRelationship` | `asana-safe api get-goal-relationship` | `implemented_live_unverified` | read; standard bearer access |
| Goal relationships | PUT | `/goal_relationships/{goal_relationship_gid}` | `updateGoalRelationship` | `asana-safe api update-goal-relationship` | `implemented_live_unverified` | write; standard bearer access |
| Goal relationships | GET | `/goal_relationships` | `getGoalRelationships` | `asana-safe api get-goal-relationships` | `implemented_live_unverified` | read; standard bearer access |
| Goal relationships | POST | `/goals/{goal_gid}/addSupportingRelationship` | `addSupportingRelationship` | `asana-safe api add-supporting-relationship` | `implemented_live_unverified` | write; standard bearer access |
| Goal relationships | POST | `/goals/{goal_gid}/removeSupportingRelationship` | `removeSupportingRelationship` | `asana-safe api remove-supporting-relationship` | `implemented_live_unverified` | write; standard bearer access |
| Goals | GET | `/goals/{goal_gid}` | `getGoal` | `asana-safe api get-goal` | `implemented_live_unverified` | read; standard bearer access |
| Goals | PUT | `/goals/{goal_gid}` | `updateGoal` | `asana-safe api update-goal` | `implemented_live_unverified` | write; standard bearer access |
| Goals | DELETE | `/goals/{goal_gid}` | `deleteGoal` | `asana-safe api delete-goal` | `implemented_live_unverified` | write_stronger_approval; standard bearer access |
| Goals | GET | `/goals` | `getGoals` | `asana-safe api get-goals` | `implemented_live_unverified` | read; standard bearer access |
| Goals | POST | `/goals` | `createGoal` | `asana-safe api create-goal` | `implemented_live_unverified` | write; standard bearer access |
| Goals | POST | `/goals/{goal_gid}/setMetric` | `createGoalMetric` | `asana-safe api create-goal-metric` | `implemented_live_unverified` | write; standard bearer access |
| Goals | POST | `/goals/{goal_gid}/setMetricCurrentValue` | `updateGoalMetric` | `asana-safe api update-goal-metric` | `implemented_live_unverified` | write; standard bearer access |
| Goals | POST | `/goals/{goal_gid}/addFollowers` | `addFollowers` | `asana-safe api add-followers` | `implemented_live_unverified` | write_stronger_approval; standard bearer access |
| Goals | POST | `/goals/{goal_gid}/removeFollowers` | `removeFollowers` | `asana-safe api remove-followers` | `implemented_live_unverified` | write_stronger_approval; standard bearer access |
| Goals | GET | `/goals/{goal_gid}/parentGoals` | `getParentGoalsForGoal` | `asana-safe api get-parent-goals-for-goal` | `implemented_live_unverified` | read; standard bearer access |
| Goals | POST | `/goals/{goal_gid}/addCustomFieldSetting` | `addCustomFieldSettingForGoal` | `asana-safe api add-custom-field-setting-for-goal` | `implemented_live_unverified` | write; standard bearer access |
| Goals | POST | `/goals/{goal_gid}/removeCustomFieldSetting` | `removeCustomFieldSettingForGoal` | `asana-safe api remove-custom-field-setting-for-goal` | `implemented_live_unverified` | write; standard bearer access |
| Jobs | GET | `/jobs/{job_gid}` | `getJob` | `asana-safe api get-job` | `implemented_live_unverified` | read; standard bearer access |
| Memberships | GET | `/memberships` | `getMemberships` | `asana-safe api get-memberships` | `implemented_live_unverified` | read; standard bearer access |
| Memberships | POST | `/memberships` | `createMembership` | `asana-safe api create-membership` | `implemented_live_unverified` | write_stronger_approval; standard bearer access |
| Memberships | GET | `/memberships/{membership_gid}` | `getMembership` | `asana-safe api get-membership` | `implemented_live_unverified` | read; standard bearer access |
| Memberships | PUT | `/memberships/{membership_gid}` | `updateMembership` | `asana-safe api update-membership` | `implemented_live_unverified` | write_stronger_approval; standard bearer access |
| Memberships | DELETE | `/memberships/{membership_gid}` | `deleteMembership` | `asana-safe api delete-membership` | `implemented_live_unverified` | write_stronger_approval; standard bearer access |
| Ooo entries | GET | `/ooo_entries/{ooo_entry_gid}` | `getOooEntry` | `asana-safe api get-ooo-entry` | `implemented_live_unverified` | read; standard bearer access |
| Ooo entries | PUT | `/ooo_entries/{ooo_entry_gid}` | `updateOooEntry` | `asana-safe api update-ooo-entry` | `implemented_live_unverified` | write_stronger_approval; standard bearer access |
| Ooo entries | DELETE | `/ooo_entries/{ooo_entry_gid}` | `deleteOooEntry` | `asana-safe api delete-ooo-entry` | `implemented_live_unverified` | write_stronger_approval; standard bearer access |
| Ooo entries | GET | `/ooo_entries` | `getOooEntries` | `asana-safe api get-ooo-entries` | `implemented_live_unverified` | read; standard bearer access |
| Ooo entries | POST | `/ooo_entries` | `createOooEntry` | `asana-safe api create-ooo-entry` | `implemented_live_unverified` | write_stronger_approval; standard bearer access |
| Organization exports | POST | `/organization_exports` | `createOrganizationExport` | `asana-safe api create-organization-export` | `implemented_access_gated_live_unverified` | write_stronger_approval; service_account, enterprise_plan, paid_plan, availability_gate |
| Organization exports | GET | `/organization_exports/{organization_export_gid}` | `getOrganizationExport` | `asana-safe api get-organization-export` | `implemented_access_gated_live_unverified` | sensitive_read; service_account, enterprise_plan, paid_plan, availability_gate |
| Portfolio memberships | GET | `/portfolio_memberships` | `getPortfolioMemberships` | `asana-safe api get-portfolio-memberships` | `implemented_live_unverified` | read; standard bearer access |
| Portfolio memberships | GET | `/portfolio_memberships/{portfolio_membership_gid}` | `getPortfolioMembership` | `asana-safe api get-portfolio-membership` | `implemented_live_unverified` | read; standard bearer access |
| Portfolio memberships | GET | `/portfolios/{portfolio_gid}/portfolio_memberships` | `getPortfolioMembershipsForPortfolio` | `asana-safe api get-portfolio-memberships-for-portfolio` | `implemented_live_unverified` | read; standard bearer access |
| Portfolios | GET | `/portfolios` | `getPortfolios` | `asana-safe api get-portfolios` | `implemented_access_gated_live_unverified` | read; service_account, oauth_scope_or_app |
| Portfolios | POST | `/portfolios` | `createPortfolio` | `asana-safe api create-portfolio` | `implemented_live_unverified` | write; standard bearer access |
| Portfolios | GET | `/portfolios/{portfolio_gid}` | `getPortfolio` | `asana-safe api get-portfolio` | `implemented_live_unverified` | read; standard bearer access |
| Portfolios | PUT | `/portfolios/{portfolio_gid}` | `updatePortfolio` | `asana-safe api update-portfolio` | `implemented_live_unverified` | write; standard bearer access |
| Portfolios | DELETE | `/portfolios/{portfolio_gid}` | `deletePortfolio` | `asana-safe api delete-portfolio` | `implemented_live_unverified` | write_stronger_approval; standard bearer access |
| Portfolios | GET | `/portfolios/{portfolio_gid}/items` | `getItemsForPortfolio` | `asana-safe api get-items-for-portfolio` | `implemented_live_unverified` | read; standard bearer access |
| Portfolios | POST | `/portfolios/{portfolio_gid}/addItem` | `addItemForPortfolio` | `asana-safe api add-item-for-portfolio` | `implemented_live_unverified` | write; standard bearer access |
| Portfolios | POST | `/portfolios/{portfolio_gid}/removeItem` | `removeItemForPortfolio` | `asana-safe api remove-item-for-portfolio` | `implemented_live_unverified` | write; standard bearer access |
| Portfolios | POST | `/portfolios/{portfolio_gid}/addCustomFieldSetting` | `addCustomFieldSettingForPortfolio` | `asana-safe api add-custom-field-setting-for-portfolio` | `implemented_live_unverified` | write; standard bearer access |
| Portfolios | POST | `/portfolios/{portfolio_gid}/removeCustomFieldSetting` | `removeCustomFieldSettingForPortfolio` | `asana-safe api remove-custom-field-setting-for-portfolio` | `implemented_live_unverified` | write; standard bearer access |
| Portfolios | POST | `/portfolios/{portfolio_gid}/addMembers` | `addMembersForPortfolio` | `asana-safe api add-members-for-portfolio` | `implemented_live_unverified` | write; standard bearer access |
| Portfolios | POST | `/portfolios/{portfolio_gid}/removeMembers` | `removeMembersForPortfolio` | `asana-safe api remove-members-for-portfolio` | `implemented_live_unverified` | write; standard bearer access |
| Portfolios | POST | `/portfolios/{portfolio_gid}/duplicate` | `duplicatePortfolio` | `asana-safe api duplicate-portfolio` | `implemented_live_unverified` | write_stronger_approval; standard bearer access |
| Project briefs | GET | `/project_briefs/{project_brief_gid}` | `getProjectBrief` | `asana-safe api get-project-brief` | `implemented_developer_preview_live_unverified` | read; standard bearer access |
| Project briefs | PUT | `/project_briefs/{project_brief_gid}` | `updateProjectBrief` | `asana-safe api update-project-brief` | `implemented_developer_preview_live_unverified` | write_stronger_approval; standard bearer access |
| Project briefs | DELETE | `/project_briefs/{project_brief_gid}` | `deleteProjectBrief` | `asana-safe api delete-project-brief` | `implemented_developer_preview_live_unverified` | write_stronger_approval; standard bearer access |
| Project briefs | POST | `/projects/{project_gid}/project_briefs` | `createProjectBrief` | `asana-safe api create-project-brief` | `implemented_developer_preview_live_unverified` | write_stronger_approval; standard bearer access |
| Project memberships | GET | `/project_memberships/{project_membership_gid}` | `getProjectMembership` | `asana-safe api get-project-membership` | `implemented_live_unverified` | read; standard bearer access |
| Project memberships | GET | `/projects/{project_gid}/project_memberships` | `getProjectMembershipsForProject` | `asana-safe api get-project-memberships-for-project` | `implemented_live_unverified` | read; standard bearer access |
| Project portfolio settings | GET | `/project_portfolio_settings/{project_portfolio_setting_gid}` | `getProjectPortfolioSetting` | `asana-safe api get-project-portfolio-setting` | `implemented_live_unverified` | read; standard bearer access |
| Project portfolio settings | PUT | `/project_portfolio_settings/{project_portfolio_setting_gid}` | `updateProjectPortfolioSetting` | `asana-safe api update-project-portfolio-setting` | `implemented_live_unverified` | write_stronger_approval; standard bearer access |
| Project portfolio settings | GET | `/projects/{project_gid}/project_portfolio_settings` | `getProjectPortfolioSettingsForProject` | `asana-safe api get-project-portfolio-settings-for-project` | `implemented_live_unverified` | read; standard bearer access |
| Project portfolio settings | GET | `/portfolios/{portfolio_gid}/project_portfolio_settings` | `getProjectPortfolioSettingsForPortfolio` | `asana-safe api get-project-portfolio-settings-for-portfolio` | `implemented_live_unverified` | read; standard bearer access |
| Project statuses | GET | `/project_statuses/{project_status_gid}` | `getProjectStatus` | `asana-safe api get-project-status` | `implemented_deprecated_live_unverified` | read; standard bearer access |
| Project statuses | DELETE | `/project_statuses/{project_status_gid}` | `deleteProjectStatus` | `asana-safe api delete-project-status` | `implemented_deprecated_live_unverified` | write_stronger_approval; standard bearer access |
| Project statuses | GET | `/projects/{project_gid}/project_statuses` | `getProjectStatusesForProject` | `asana-safe api get-project-statuses-for-project` | `implemented_deprecated_live_unverified` | read; standard bearer access |
| Project statuses | POST | `/projects/{project_gid}/project_statuses` | `createProjectStatusForProject` | `asana-safe api create-project-status-for-project` | `implemented_deprecated_live_unverified` | write_stronger_approval; standard bearer access |
| Project templates | GET | `/project_templates/{project_template_gid}` | `getProjectTemplate` | `asana-safe api get-project-template` | `implemented_live_unverified` | read; standard bearer access |
| Project templates | DELETE | `/project_templates/{project_template_gid}` | `deleteProjectTemplate` | `asana-safe api delete-project-template` | `implemented_live_unverified` | write_stronger_approval; standard bearer access |
| Project templates | GET | `/project_templates` | `getProjectTemplates` | `asana-safe api get-project-templates` | `implemented_live_unverified` | read; standard bearer access |
| Project templates | GET | `/teams/{team_gid}/project_templates` | `getProjectTemplatesForTeam` | `asana-safe api get-project-templates-for-team` | `implemented_live_unverified` | read; standard bearer access |
| Project templates | POST | `/project_templates/{project_template_gid}/instantiateProject` | `instantiateProject` | `asana-safe api instantiate-project` | `implemented_live_unverified` | write_stronger_approval; standard bearer access |
| Projects | GET | `/projects` | `getProjects` | `asana-safe api get-projects` | `implemented_live_unverified` | read; standard bearer access |
| Projects | POST | `/projects` | `createProject` | `asana-safe api create-project` | `implemented_live_unverified` | write; standard bearer access |
| Projects | GET | `/projects/{project_gid}` | `getProject` | `asana-safe api get-project` | `implemented_live_unverified` | read; standard bearer access |
| Projects | PUT | `/projects/{project_gid}` | `updateProject` | `asana-safe api update-project` | `implemented_live_unverified` | write; standard bearer access |
| Projects | DELETE | `/projects/{project_gid}` | `deleteProject` | `asana-safe api delete-project` | `implemented_live_unverified` | write_stronger_approval; standard bearer access |
| Projects | POST | `/projects/{project_gid}/duplicate` | `duplicateProject` | `asana-safe api duplicate-project` | `implemented_live_unverified` | write_stronger_approval; standard bearer access |
| Projects | GET | `/tasks/{task_gid}/projects` | `getProjectsForTask` | `asana-safe api get-projects-for-task` | `implemented_live_unverified` | read; standard bearer access |
| Projects | GET | `/teams/{team_gid}/projects` | `getProjectsForTeam` | `asana-safe api get-projects-for-team` | `implemented_live_unverified` | read; standard bearer access |
| Projects | POST | `/teams/{team_gid}/projects` | `createProjectForTeam` | `asana-safe api create-project-for-team` | `implemented_live_unverified` | write; standard bearer access |
| Projects | GET | `/workspaces/{workspace_gid}/projects` | `getProjectsForWorkspace` | `asana-safe api get-projects-for-workspace` | `implemented_live_unverified` | read; standard bearer access |
| Projects | POST | `/workspaces/{workspace_gid}/projects` | `createProjectForWorkspace` | `asana-safe api create-project-for-workspace` | `implemented_live_unverified` | write; standard bearer access |
| Projects | GET | `/workspaces/{workspace_gid}/projects/search` | `searchProjectsForWorkspace` | `asana-safe api search-projects-for-workspace` | `implemented_access_gated_live_unverified` | read; advanced_plan, paid_plan |
| Projects | POST | `/projects/{project_gid}/addCustomFieldSetting` | `addCustomFieldSettingForProject` | `asana-safe api add-custom-field-setting-for-project` | `implemented_live_unverified` | write; standard bearer access |
| Projects | POST | `/projects/{project_gid}/removeCustomFieldSetting` | `removeCustomFieldSettingForProject` | `asana-safe api remove-custom-field-setting-for-project` | `implemented_live_unverified` | write; standard bearer access |
| Projects | GET | `/projects/{project_gid}/task_counts` | `getTaskCountsForProject` | `asana-safe api get-task-counts-for-project` | `implemented_live_unverified` | read; standard bearer access |
| Projects | POST | `/projects/{project_gid}/addMembers` | `addMembersForProject` | `asana-safe api add-members-for-project` | `implemented_live_unverified` | write; standard bearer access |
| Projects | POST | `/projects/{project_gid}/removeMembers` | `removeMembersForProject` | `asana-safe api remove-members-for-project` | `implemented_live_unverified` | write; standard bearer access |
| Projects | POST | `/projects/{project_gid}/addFollowers` | `addFollowersForProject` | `asana-safe api add-followers-for-project` | `implemented_live_unverified` | write_stronger_approval; standard bearer access |
| Projects | POST | `/projects/{project_gid}/removeFollowers` | `removeFollowersForProject` | `asana-safe api remove-followers-for-project` | `implemented_live_unverified` | write_stronger_approval; standard bearer access |
| Projects | POST | `/projects/{project_gid}/saveAsTemplate` | `projectSaveAsTemplate` | `asana-safe api project-save-as-template` | `implemented_live_unverified` | write; standard bearer access |
| Rates | GET | `/rates` | `getRates` | `asana-safe api get-rates` | `implemented_access_gated_live_unverified` | read; enterprise_plan, availability_gate |
| Rates | POST | `/rates` | `createRate` | `asana-safe api create-rate` | `implemented_live_unverified` | write_stronger_approval; standard bearer access |
| Rates | GET | `/rates/{rate_gid}` | `getRate` | `asana-safe api get-rate` | `implemented_live_unverified` | read; standard bearer access |
| Rates | PUT | `/rates/{rate_gid}` | `updateRate` | `asana-safe api update-rate` | `implemented_live_unverified` | write_stronger_approval; standard bearer access |
| Rates | DELETE | `/rates/{rate_gid}` | `deleteRate` | `asana-safe api delete-rate` | `implemented_live_unverified` | write_stronger_approval; standard bearer access |
| Reactions | GET | `/reactions` | `getReactionsOnObject` | `asana-safe api get-reactions-on-object` | `implemented_live_unverified` | read; standard bearer access |
| Roles | GET | `/roles` | `getRoles` | `asana-safe api get-roles` | `implemented_access_gated_live_unverified` | read; admin_permission |
| Roles | POST | `/roles` | `createRole` | `asana-safe api create-role` | `implemented_access_gated_live_unverified` | write_stronger_approval; admin_permission |
| Roles | GET | `/roles/{role_gid}` | `getRole` | `asana-safe api get-role` | `implemented_access_gated_live_unverified` | read; admin_permission |
| Roles | PUT | `/roles/{role_gid}` | `updateRole` | `asana-safe api update-role` | `implemented_access_gated_live_unverified` | write_stronger_approval; admin_permission |
| Roles | DELETE | `/roles/{role_gid}` | `deleteRole` | `asana-safe api delete-role` | `implemented_access_gated_live_unverified` | write_stronger_approval; admin_permission |
| Rules | POST | `/rule_triggers/{rule_trigger_gid}/run` | `triggerRule` | `asana-safe api trigger-rule` | `implemented_live_unverified` | write_stronger_approval; standard bearer access |
| Sections | GET | `/sections/{section_gid}` | `getSection` | `asana-safe api get-section` | `implemented_live_unverified` | read; standard bearer access |
| Sections | PUT | `/sections/{section_gid}` | `updateSection` | `asana-safe api update-section` | `implemented_live_unverified` | write; standard bearer access |
| Sections | DELETE | `/sections/{section_gid}` | `deleteSection` | `asana-safe api delete-section` | `implemented_live_unverified` | write_stronger_approval; standard bearer access |
| Sections | GET | `/projects/{project_gid}/sections` | `getSectionsForProject` | `asana-safe api get-sections-for-project` | `implemented_live_unverified` | read; standard bearer access |
| Sections | POST | `/projects/{project_gid}/sections` | `createSectionForProject` | `asana-safe api create-section-for-project` | `implemented_live_unverified` | write; standard bearer access |
| Sections | POST | `/sections/{section_gid}/addTask` | `addTaskForSection` | `asana-safe api add-task-for-section` | `implemented_live_unverified` | write; standard bearer access |
| Sections | POST | `/projects/{project_gid}/sections/insert` | `insertSectionForProject` | `asana-safe api insert-section-for-project` | `implemented_live_unverified` | write; standard bearer access |
| Status updates | GET | `/status_updates/{status_update_gid}` | `getStatus` | `asana-safe api get-status` | `implemented_live_unverified` | read; standard bearer access |
| Status updates | DELETE | `/status_updates/{status_update_gid}` | `deleteStatus` | `asana-safe api delete-status` | `implemented_live_unverified` | write_stronger_approval; standard bearer access |
| Status updates | GET | `/status_updates` | `getStatusesForObject` | `asana-safe api get-statuses-for-object` | `implemented_live_unverified` | read; standard bearer access |
| Status updates | POST | `/status_updates` | `createStatusForObject` | `asana-safe api create-status-for-object` | `implemented_live_unverified` | write_stronger_approval; standard bearer access |
| Stories | GET | `/stories/{story_gid}` | `getStory` | `asana-safe api get-story` | `implemented_live_unverified` | read; standard bearer access |
| Stories | PUT | `/stories/{story_gid}` | `updateStory` | `asana-safe api update-story` | `implemented_live_unverified` | write_stronger_approval; standard bearer access |
| Stories | DELETE | `/stories/{story_gid}` | `deleteStory` | `asana-safe api delete-story` | `implemented_live_unverified` | write_stronger_approval; standard bearer access |
| Stories | GET | `/tasks/{task_gid}/stories` | `getStoriesForTask` | `asana-safe api get-stories-for-task` | `implemented_live_unverified` | read; standard bearer access |
| Stories | POST | `/tasks/{task_gid}/stories` | `createStoryForTask` | `asana-safe api create-story-for-task` | `implemented_live_unverified` | write_stronger_approval; standard bearer access |
| Stories | GET | `/goals/{goal_gid}/stories` | `getStoriesForGoal` | `asana-safe api get-stories-for-goal` | `implemented_live_unverified` | read; standard bearer access |
| Stories | POST | `/goals/{goal_gid}/stories` | `createStoryForGoal` | `asana-safe api create-story-for-goal` | `implemented_live_unverified` | write_stronger_approval; standard bearer access |
| Tags | GET | `/tags` | `getTags` | `asana-safe api get-tags` | `implemented_live_unverified` | read; standard bearer access |
| Tags | POST | `/tags` | `createTag` | `asana-safe api create-tag` | `implemented_live_unverified` | write; standard bearer access |
| Tags | GET | `/tags/{tag_gid}` | `getTag` | `asana-safe api get-tag` | `implemented_live_unverified` | read; standard bearer access |
| Tags | PUT | `/tags/{tag_gid}` | `updateTag` | `asana-safe api update-tag` | `implemented_live_unverified` | write; standard bearer access |
| Tags | DELETE | `/tags/{tag_gid}` | `deleteTag` | `asana-safe api delete-tag` | `implemented_live_unverified` | write_stronger_approval; standard bearer access |
| Tags | GET | `/tasks/{task_gid}/tags` | `getTagsForTask` | `asana-safe api get-tags-for-task` | `implemented_live_unverified` | read; standard bearer access |
| Tags | GET | `/workspaces/{workspace_gid}/tags` | `getTagsForWorkspace` | `asana-safe api get-tags-for-workspace` | `implemented_live_unverified` | read; standard bearer access |
| Tags | POST | `/workspaces/{workspace_gid}/tags` | `createTagForWorkspace` | `asana-safe api create-tag-for-workspace` | `implemented_live_unverified` | write; standard bearer access |
| Task templates | GET | `/task_templates` | `getTaskTemplates` | `asana-safe api get-task-templates` | `implemented_live_unverified` | read; standard bearer access |
| Task templates | GET | `/task_templates/{task_template_gid}` | `getTaskTemplate` | `asana-safe api get-task-template` | `implemented_live_unverified` | read; standard bearer access |
| Task templates | DELETE | `/task_templates/{task_template_gid}` | `deleteTaskTemplate` | `asana-safe api delete-task-template` | `implemented_live_unverified` | write_stronger_approval; standard bearer access |
| Task templates | POST | `/task_templates/{task_template_gid}/instantiateTask` | `instantiateTask` | `asana-safe api instantiate-task` | `implemented_live_unverified` | write_stronger_approval; standard bearer access |
| Tasks | GET | `/tasks` | `getTasks` | `asana-safe api get-tasks` | `implemented_live_unverified` | read; standard bearer access |
| Tasks | POST | `/tasks` | `createTask` | `asana-safe api create-task` | `implemented_live_unverified` | write; standard bearer access |
| Tasks | GET | `/tasks/{task_gid}` | `getTask` | `asana-safe api get-task` | `implemented_live_unverified` | read; standard bearer access |
| Tasks | PUT | `/tasks/{task_gid}` | `updateTask` | `asana-safe api update-task` | `implemented_live_unverified` | write; standard bearer access |
| Tasks | DELETE | `/tasks/{task_gid}` | `deleteTask` | `asana-safe api delete-task` | `implemented_live_unverified` | write_stronger_approval; standard bearer access |
| Tasks | POST | `/tasks/{task_gid}/duplicate` | `duplicateTask` | `asana-safe api duplicate-task` | `implemented_live_unverified` | write_stronger_approval; standard bearer access |
| Tasks | GET | `/projects/{project_gid}/tasks` | `getTasksForProject` | `asana-safe api get-tasks-for-project` | `implemented_live_unverified` | read; standard bearer access |
| Tasks | GET | `/sections/{section_gid}/tasks` | `getTasksForSection` | `asana-safe api get-tasks-for-section` | `implemented_live_unverified` | read; standard bearer access |
| Tasks | GET | `/tags/{tag_gid}/tasks` | `getTasksForTag` | `asana-safe api get-tasks-for-tag` | `implemented_live_unverified` | read; standard bearer access |
| Tasks | GET | `/user_task_lists/{user_task_list_gid}/tasks` | `getTasksForUserTaskList` | `asana-safe api get-tasks-for-user-task-list` | `implemented_live_unverified` | read; standard bearer access |
| Tasks | GET | `/tasks/{task_gid}/subtasks` | `getSubtasksForTask` | `asana-safe api get-subtasks-for-task` | `implemented_live_unverified` | read; standard bearer access |
| Tasks | POST | `/tasks/{task_gid}/subtasks` | `createSubtaskForTask` | `asana-safe api create-subtask-for-task` | `implemented_live_unverified` | write; standard bearer access |
| Tasks | POST | `/tasks/{task_gid}/setParent` | `setParentForTask` | `asana-safe api set-parent-for-task` | `implemented_live_unverified` | write; standard bearer access |
| Tasks | GET | `/tasks/{task_gid}/dependencies` | `getDependenciesForTask` | `asana-safe api get-dependencies-for-task` | `implemented_live_unverified` | read; standard bearer access |
| Tasks | POST | `/tasks/{task_gid}/addDependencies` | `addDependenciesForTask` | `asana-safe api add-dependencies-for-task` | `implemented_live_unverified` | write; standard bearer access |
| Tasks | POST | `/tasks/{task_gid}/removeDependencies` | `removeDependenciesForTask` | `asana-safe api remove-dependencies-for-task` | `implemented_live_unverified` | write; standard bearer access |
| Tasks | GET | `/tasks/{task_gid}/dependents` | `getDependentsForTask` | `asana-safe api get-dependents-for-task` | `implemented_live_unverified` | read; standard bearer access |
| Tasks | POST | `/tasks/{task_gid}/addDependents` | `addDependentsForTask` | `asana-safe api add-dependents-for-task` | `implemented_live_unverified` | write; standard bearer access |
| Tasks | POST | `/tasks/{task_gid}/removeDependents` | `removeDependentsForTask` | `asana-safe api remove-dependents-for-task` | `implemented_live_unverified` | write; standard bearer access |
| Tasks | POST | `/tasks/{task_gid}/addProject` | `addProjectForTask` | `asana-safe api add-project-for-task` | `implemented_live_unverified` | write; standard bearer access |
| Tasks | POST | `/tasks/{task_gid}/removeProject` | `removeProjectForTask` | `asana-safe api remove-project-for-task` | `implemented_live_unverified` | write; standard bearer access |
| Tasks | POST | `/tasks/{task_gid}/addTag` | `addTagForTask` | `asana-safe api add-tag-for-task` | `implemented_live_unverified` | write; standard bearer access |
| Tasks | POST | `/tasks/{task_gid}/removeTag` | `removeTagForTask` | `asana-safe api remove-tag-for-task` | `implemented_live_unverified` | write; standard bearer access |
| Tasks | POST | `/tasks/{task_gid}/addFollowers` | `addFollowersForTask` | `asana-safe api add-followers-for-task` | `implemented_live_unverified` | write_stronger_approval; standard bearer access |
| Tasks | POST | `/tasks/{task_gid}/removeFollowers` | `removeFollowerForTask` | `asana-safe api remove-follower-for-task` | `implemented_live_unverified` | write_stronger_approval; standard bearer access |
| Tasks | GET | `/workspaces/{workspace_gid}/tasks/custom_id/{custom_id}` | `getTaskForCustomID` | `asana-safe api get-task-for-custom-id` | `implemented_live_unverified` | read; standard bearer access |
| Tasks | GET | `/workspaces/{workspace_gid}/tasks/search` | `searchTasksForWorkspace` | `asana-safe api search-tasks-for-workspace` | `implemented_access_gated_live_unverified` | read; advanced_plan, paid_plan |
| Team memberships | GET | `/team_memberships/{team_membership_gid}` | `getTeamMembership` | `asana-safe api get-team-membership` | `implemented_live_unverified` | read; standard bearer access |
| Team memberships | GET | `/team_memberships` | `getTeamMemberships` | `asana-safe api get-team-memberships` | `implemented_live_unverified` | read; standard bearer access |
| Team memberships | GET | `/teams/{team_gid}/team_memberships` | `getTeamMembershipsForTeam` | `asana-safe api get-team-memberships-for-team` | `implemented_live_unverified` | read; standard bearer access |
| Team memberships | GET | `/users/{user_gid}/team_memberships` | `getTeamMembershipsForUser` | `asana-safe api get-team-memberships-for-user` | `implemented_live_unverified` | read; standard bearer access |
| Teams | POST | `/teams` | `createTeam` | `asana-safe api create-team` | `implemented_live_unverified` | write_stronger_approval; standard bearer access |
| Teams | GET | `/teams/{team_gid}` | `getTeam` | `asana-safe api get-team` | `implemented_live_unverified` | read; standard bearer access |
| Teams | PUT | `/teams/{team_gid}` | `updateTeam` | `asana-safe api update-team` | `implemented_live_unverified` | write_stronger_approval; standard bearer access |
| Teams | GET | `/workspaces/{workspace_gid}/teams` | `getTeamsForWorkspace` | `asana-safe api get-teams-for-workspace` | `implemented_live_unverified` | read; standard bearer access |
| Teams | GET | `/users/{user_gid}/teams` | `getTeamsForUser` | `asana-safe api get-teams-for-user` | `implemented_live_unverified` | read; standard bearer access |
| Teams | POST | `/teams/{team_gid}/addUser` | `addUserForTeam` | `asana-safe api add-user-for-team` | `implemented_live_unverified` | write_stronger_approval; standard bearer access |
| Teams | POST | `/teams/{team_gid}/removeUser` | `removeUserForTeam` | `asana-safe api remove-user-for-team` | `implemented_live_unverified` | write_stronger_approval; standard bearer access |
| Time periods | GET | `/time_periods/{time_period_gid}` | `getTimePeriod` | `asana-safe api get-time-period` | `implemented_live_unverified` | read; standard bearer access |
| Time periods | GET | `/time_periods` | `getTimePeriods` | `asana-safe api get-time-periods` | `implemented_live_unverified` | read; standard bearer access |
| Time tracking categories | GET | `/time_tracking_categories/{time_tracking_category_gid}` | `getTimeTrackingCategory` | `asana-safe api get-time-tracking-category` | `implemented_access_gated_live_unverified` | read; admin_permission |
| Time tracking categories | PUT | `/time_tracking_categories/{time_tracking_category_gid}` | `updateTimeTrackingCategory` | `asana-safe api update-time-tracking-category` | `implemented_access_gated_live_unverified` | write_stronger_approval; admin_permission |
| Time tracking categories | DELETE | `/time_tracking_categories/{time_tracking_category_gid}` | `deleteTimeTrackingCategory` | `asana-safe api delete-time-tracking-category` | `implemented_access_gated_live_unverified` | write_stronger_approval; admin_permission |
| Time tracking categories | GET | `/time_tracking_categories/{time_tracking_category_gid}/time_tracking_entries` | `getTimeTrackingEntriesForTimeTrackingCategory` | `asana-safe api get-time-tracking-entries-for-time-tracking-category` | `implemented_access_gated_live_unverified` | read; admin_permission |
| Time tracking categories | GET | `/time_tracking_categories` | `getTimeTrackingCategories` | `asana-safe api get-time-tracking-categories` | `implemented_access_gated_live_unverified` | read; admin_permission |
| Time tracking categories | POST | `/time_tracking_categories` | `createTimeTrackingCategory` | `asana-safe api create-time-tracking-category` | `implemented_access_gated_live_unverified` | write_stronger_approval; admin_permission |
| Time tracking entries | GET | `/tasks/{task_gid}/time_tracking_entries` | `getTimeTrackingEntriesForTask` | `asana-safe api get-time-tracking-entries-for-task` | `implemented_live_unverified` | read; standard bearer access |
| Time tracking entries | POST | `/tasks/{task_gid}/time_tracking_entries` | `createTimeTrackingEntry` | `asana-safe api create-time-tracking-entry` | `implemented_live_unverified` | write_stronger_approval; standard bearer access |
| Time tracking entries | GET | `/time_tracking_entries/{time_tracking_entry_gid}` | `getTimeTrackingEntry` | `asana-safe api get-time-tracking-entry` | `implemented_live_unverified` | read; standard bearer access |
| Time tracking entries | PUT | `/time_tracking_entries/{time_tracking_entry_gid}` | `updateTimeTrackingEntry` | `asana-safe api update-time-tracking-entry` | `implemented_live_unverified` | write_stronger_approval; standard bearer access |
| Time tracking entries | DELETE | `/time_tracking_entries/{time_tracking_entry_gid}` | `deleteTimeTrackingEntry` | `asana-safe api delete-time-tracking-entry` | `implemented_live_unverified` | write_stronger_approval; standard bearer access |
| Time tracking entries | GET | `/time_tracking_entries` | `getTimeTrackingEntries` | `asana-safe api get-time-tracking-entries` | `implemented_live_unverified` | read; standard bearer access |
| Timesheet approval statuses | GET | `/timesheet_approval_statuses/{timesheet_approval_status_gid}` | `getTimesheetApprovalStatus` | `asana-safe api get-timesheet-approval-status` | `implemented_live_unverified` | read; standard bearer access |
| Timesheet approval statuses | PUT | `/timesheet_approval_statuses/{timesheet_approval_status_gid}` | `updateTimesheetApprovalStatus` | `asana-safe api update-timesheet-approval-status` | `implemented_live_unverified` | write_stronger_approval; standard bearer access |
| Timesheet approval statuses | GET | `/timesheet_approval_statuses` | `getTimesheetApprovalStatuses` | `asana-safe api get-timesheet-approval-statuses` | `implemented_live_unverified` | read; standard bearer access |
| Timesheet approval statuses | POST | `/timesheet_approval_statuses` | `createTimesheetApprovalStatus` | `asana-safe api create-timesheet-approval-status` | `implemented_live_unverified` | write_stronger_approval; standard bearer access |
| Typeahead | GET | `/workspaces/{workspace_gid}/typeahead` | `typeaheadForWorkspace` | `asana-safe api typeahead-for-workspace` | `implemented_live_unverified` | read; standard bearer access |
| User task lists | GET | `/user_task_lists/{user_task_list_gid}` | `getUserTaskList` | `asana-safe api get-user-task-list` | `implemented_live_unverified` | read; standard bearer access |
| User task lists | GET | `/users/{user_gid}/user_task_list` | `getUserTaskListForUser` | `asana-safe api get-user-task-list-for-user` | `implemented_live_unverified` | read; standard bearer access |
| Users | GET | `/users` | `getUsers` | `asana-safe api get-users` | `implemented_live_unverified` | read; standard bearer access |
| Users | GET | `/users/{user_gid}` | `getUser` | `asana-safe api get-user` | `implemented_live_unverified` | read; standard bearer access |
| Users | PUT | `/users/{user_gid}` | `updateUser` | `asana-safe api update-user` | `implemented_live_unverified` | write; standard bearer access |
| Users | GET | `/users/{user_gid}/favorites` | `getFavoritesForUser` | `asana-safe api get-favorites-for-user` | `implemented_live_unverified` | read; standard bearer access |
| Users | GET | `/teams/{team_gid}/users` | `getUsersForTeam` | `asana-safe api get-users-for-team` | `implemented_live_unverified` | read; standard bearer access |
| Users | GET | `/workspaces/{workspace_gid}/users` | `getUsersForWorkspace` | `asana-safe api get-users-for-workspace` | `implemented_live_unverified` | read; standard bearer access |
| Users | GET | `/workspaces/{workspace_gid}/users/{user_gid}` | `getUserForWorkspace` | `asana-safe api get-user-for-workspace` | `implemented_live_unverified` | read; standard bearer access |
| Users | PUT | `/workspaces/{workspace_gid}/users/{user_gid}` | `updateUserForWorkspace` | `asana-safe api update-user-for-workspace` | `implemented_live_unverified` | write; standard bearer access |
| Webhooks | GET | `/webhooks` | `getWebhooks` | `asana-safe api get-webhooks` | `implemented_live_unverified` | read; standard bearer access |
| Webhooks | POST | `/webhooks` | `createWebhook` | `asana-safe api create-webhook` | `implemented_live_unverified` | write_stronger_approval; standard bearer access |
| Webhooks | GET | `/webhooks/{webhook_gid}` | `getWebhook` | `asana-safe api get-webhook` | `implemented_live_unverified` | read; standard bearer access |
| Webhooks | PUT | `/webhooks/{webhook_gid}` | `updateWebhook` | `asana-safe api update-webhook` | `implemented_live_unverified` | write_stronger_approval; standard bearer access |
| Webhooks | DELETE | `/webhooks/{webhook_gid}` | `deleteWebhook` | `asana-safe api delete-webhook` | `implemented_live_unverified` | write_stronger_approval; standard bearer access |
| Workspace memberships | GET | `/workspace_memberships/{workspace_membership_gid}` | `getWorkspaceMembership` | `asana-safe api get-workspace-membership` | `implemented_live_unverified` | read; standard bearer access |
| Workspace memberships | GET | `/users/{user_gid}/workspace_memberships` | `getWorkspaceMembershipsForUser` | `asana-safe api get-workspace-memberships-for-user` | `implemented_live_unverified` | read; standard bearer access |
| Workspace memberships | GET | `/workspaces/{workspace_gid}/workspace_memberships` | `getWorkspaceMembershipsForWorkspace` | `asana-safe api get-workspace-memberships-for-workspace` | `implemented_live_unverified` | read; standard bearer access |
| Workspaces | GET | `/workspaces` | `getWorkspaces` | `asana-safe api get-workspaces` | `implemented_live_unverified` | read; standard bearer access |
| Workspaces | GET | `/workspaces/{workspace_gid}` | `getWorkspace` | `asana-safe api get-workspace` | `implemented_live_unverified` | read; standard bearer access |
| Workspaces | PUT | `/workspaces/{workspace_gid}` | `updateWorkspace` | `asana-safe api update-workspace` | `implemented_live_unverified` | write_stronger_approval; standard bearer access |
| Workspaces | POST | `/workspaces/{workspace_gid}/addUser` | `addUserForWorkspace` | `asana-safe api add-user-for-workspace` | `implemented_live_unverified` | write_stronger_approval; standard bearer access |
| Workspaces | POST | `/workspaces/{workspace_gid}/removeUser` | `removeUserForWorkspace` | `asana-safe api remove-user-for-workspace` | `implemented_access_gated_live_unverified` | write_stronger_approval; service_account, admin_permission |
| Workspaces | GET | `/workspaces/{workspace_gid}/events` | `getWorkspaceEvents` | `asana-safe api get-workspace-events` | `implemented_live_unverified` | read; standard bearer access |

## Intentional exclusions

`POST /batch` is the only operation inside the pinned REST file that is not shipped as a command.
It accepts arbitrary relative paths, which would recreate the raw-request bridge forbidden by the product boundary.
Its underlying REST operations remain available through their own fixed commands.

App Components use a separate official specification and SCIM uses a separate `/scim` surface; neither is part of these counts.

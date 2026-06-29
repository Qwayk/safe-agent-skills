# n8n API coverage

Last updated: **2026-06-29**

This file is the source of truth for the shipped n8n command surface. The inventory is generated from the official n8n public REST API OpenAPI files in the n8n repository at commit `0c92df794a07404d22cbc85a3c4ed6b332e442ab`. The docs repository page for `docs/api/v1/openapi.yml` was visible in GitHub search, but its raw path was not fetchable during this build, so the pinned source is the same public API spec folder from the official `n8n-io/n8n` repository: `packages/cli/src/public-api/v1/`.

The CLI intentionally does not include private `/rest` UI endpoints, n8n CLI commands, node docs, MCP setup, templates, or user-created webhook APIs.

## Summary

- Official documented operations covered: **80**
- Families covered: **15**
- Implemented with explicit generated commands: **80**
- Excluded from the chosen public REST API boundary: private `/rest` endpoints, n8n CLI, node docs, MCP setup, templates, and user-created webhook APIs

## Coverage table

| Family | Command | Official operation | Meaning | Status | Scope |
| --- | --- | --- | --- | --- | --- |
| audit | `generate-audit` | POST `/audit` | Generate an audit | implemented | `securityAudit:generate` |
| community-package | `get-installed-packages` | GET `/community-packages` | List installed community packages | implemented | `communityPackage:list` |
| community-package | `install-package` | POST `/community-packages` | Install a community package | implemented | `communityPackage:install` |
| community-package | `uninstall-package` | DELETE `/community-packages/{name}` | Uninstall a community package | implemented | `communityPackage:uninstall` |
| community-package | `update-package` | PATCH `/community-packages/{name}` | Update a community package | implemented | `communityPackage:update` |
| credential | `create-credential` | POST `/credentials` | Create a credential | implemented | `credential:create` |
| credential | `delete-credential` | DELETE `/credentials/{id}` | Delete credential by ID | implemented | `credential:delete` |
| credential | `get-credential` | GET `/credentials/{id}` | Get credential by ID | implemented | `credential:read` |
| credential | `get-credential-type` | GET `/credentials/schema/{credentialTypeName}` | Show credential data schema | implemented | `none` |
| credential | `get-credentials` | GET `/credentials` | List credentials | implemented | `credential:list` |
| credential | `test-credential` | POST `/credentials/{id}/test` | Test credential by ID | implemented | `credential:read` |
| credential | `transfer-credential` | PUT `/credentials/{id}/transfer` | Transfer a credential to another project. | implemented | `credential:move` |
| credential | `update-credential` | PATCH `/credentials/{id}` | Update credential by ID | implemented | `credential:update` |
| data-table | `create-data-table` | POST `/data-tables` | Create a new data table | implemented | `dataTable:create` |
| data-table | `create-data-table-column` | POST `/data-tables/{dataTableId}/columns` | Add a column to a data table | implemented | `dataTableColumn:create` |
| data-table | `delete-data-table` | DELETE `/data-tables/{dataTableId}` | Delete a data table | implemented | `dataTable:delete` |
| data-table | `delete-data-table-column` | DELETE `/data-tables/{dataTableId}/columns/{columnId}` | Delete a column | implemented | `dataTableColumn:delete` |
| data-table | `delete-data-table-rows` | DELETE `/data-tables/{dataTableId}/rows/delete` | Delete rows from a data table | implemented | `dataTableRow:delete` |
| data-table | `get-data-table` | GET `/data-tables/{dataTableId}` | Get a data table | implemented | `dataTable:read` |
| data-table | `get-data-table-rows` | GET `/data-tables/{dataTableId}/rows` | Retrieve rows from a data table | implemented | `dataTableRow:read` |
| data-table | `insert-data-table-rows` | POST `/data-tables/{dataTableId}/rows` | Insert rows into a data table | implemented | `dataTableRow:create` |
| data-table | `list-data-table-columns` | GET `/data-tables/{dataTableId}/columns` | List columns of a data table | implemented | `dataTableColumn:read` |
| data-table | `list-data-tables` | GET `/data-tables` | List all data tables | implemented | `dataTable:list` |
| data-table | `update-data-table` | PATCH `/data-tables/{dataTableId}` | Update a data table | implemented | `dataTable:update` |
| data-table | `update-data-table-column` | PATCH `/data-tables/{dataTableId}/columns/{columnId}` | Update a column | implemented | `dataTableColumn:update` |
| data-table | `update-data-table-rows` | PATCH `/data-tables/{dataTableId}/rows/update` | Update rows in a data table | implemented | `dataTableRow:update` |
| data-table | `upsert-data-table-row` | POST `/data-tables/{dataTableId}/rows/upsert` | Upsert a row in a data table | implemented | `dataTableRow:upsert` |
| discover | `get-discover` | GET `/discover` | Discover available API capabilities | implemented | `none` |
| execution | `delete-execution` | DELETE `/executions/{id}` | Delete an execution | implemented | `execution:delete` |
| execution | `get-execution` | GET `/executions/{id}` | Retrieve an execution | implemented | `execution:read` |
| execution | `get-execution-tags` | GET `/executions/{id}/tags` | Get execution tags | implemented | `executionTags:list` |
| execution | `get-executions` | GET `/executions` | Retrieve all executions | implemented | `execution:list` |
| execution | `retry-execution` | POST `/executions/{id}/retry` | Retry an execution | implemented | `execution:retry` |
| execution | `stop-execution` | POST `/executions/{id}/stop` | Stop an execution | implemented | `execution:stop` |
| execution | `stop-many-executions` | POST `/executions/stop` | Stop multiple executions | implemented | `execution:stop` |
| execution | `update-execution-tags` | PUT `/executions/{id}/tags` | Update tags of an execution | implemented | `executionTags:update` |
| folders | `create-folder` | POST `/projects/{projectId}/folders` | Create a folder | implemented | `folder:create` |
| folders | `delete-folder` | DELETE `/projects/{projectId}/folders/{folderId}` | Delete a folder | implemented | `folder:delete` |
| folders | `get-folder` | GET `/projects/{projectId}/folders/{folderId}` | Get folder details | implemented | `folder:read` |
| folders | `get-folders` | GET `/projects/{projectId}/folders` | Retrieve folders | implemented | `folder:list` |
| folders | `update-folder` | PATCH `/projects/{projectId}/folders/{folderId}` | Update a folder | implemented | `folder:update` |
| insights | `get-insights-summary` | GET `/insights/summary` | Retrieve insights summary | implemented | `insights:read` |
| n8n-package | `export-workflows` | POST `/n8n-packages/export` | Beta: Export workflows as an n8n package | implemented | `workflow:export` |
| n8n-package | `import-package` | POST `/n8n-packages/import` | Beta: Import an n8n package into a project | implemented | `workflow:import` |
| projects | `add-users-to-project` | POST `/projects/{projectId}/users` | Add one or more users to a project | implemented | `project:update` |
| projects | `change-user-role-in-project` | PATCH `/projects/{projectId}/users/{userId}` | Change a user's role in a project | implemented | `project:update` |
| projects | `create-project` | POST `/projects` | Create a project | implemented | `project:create` |
| projects | `delete-project` | DELETE `/projects/{projectId}` | Delete a project | implemented | `project:delete` |
| projects | `delete-user-from-project` | DELETE `/projects/{projectId}/users/{userId}` | Delete a user from a project | implemented | `project:update` |
| projects | `get-project-users` | GET `/projects/{projectId}/users` | List project members | implemented | `user:list` |
| projects | `get-projects` | GET `/projects` | Retrieve projects | implemented | `project:list` |
| projects | `update-project` | PUT `/projects/{projectId}` | Update a project | implemented | `project:update` |
| source-control | `pull` | POST `/source-control/pull` | Pull changes from the remote repository | implemented | `sourceControl:pull` |
| tags | `create-tag` | POST `/tags` | Create a tag | implemented | `tag:create` |
| tags | `delete-tag` | DELETE `/tags/{id}` | Delete a tag | implemented | `tag:delete` |
| tags | `get-tag` | GET `/tags/{id}` | Retrieves a tag | implemented | `tag:read` |
| tags | `get-tags` | GET `/tags` | Retrieve all tags | implemented | `tag:list` |
| tags | `update-tag` | PUT `/tags/{id}` | Update a tag | implemented | `tag:update` |
| user | `change-role` | PATCH `/users/{id}/role` | Change a user's global role | implemented | `user:changeRole` |
| user | `create-user` | POST `/users` | Create multiple users | implemented | `user:create` |
| user | `delete-user` | DELETE `/users/{id}` | Delete a user | implemented | `user:delete` |
| user | `get-user` | GET `/users/{id}` | Get user by ID/Email | implemented | `user:read` |
| user | `get-users` | GET `/users` | Retrieve all users | implemented | `user:list` |
| variables | `create-variable` | POST `/variables` | Create a variable | implemented | `variable:create` |
| variables | `delete-variable` | DELETE `/variables/{id}` | Delete a variable | implemented | `variable:delete` |
| variables | `get-variables` | GET `/variables` | Retrieve variables | implemented | `variable:list` |
| variables | `update-variable` | PUT `/variables/{id}` | Update a variable | implemented | `variable:update` |
| workflow | `activate-workflow` | POST `/workflows/{id}/activate` | Publish a workflow | implemented | `workflow:activate` |
| workflow | `archive-workflow` | POST `/workflows/{id}/archive` | Archive a workflow | implemented | `workflow:delete` |
| workflow | `create-workflow` | POST `/workflows` | Create a workflow | implemented | `workflow:create` |
| workflow | `deactivate-workflow` | POST `/workflows/{id}/deactivate` | Deactivate a workflow | implemented | `workflow:deactivate` |
| workflow | `delete-workflow` | DELETE `/workflows/{id}` | Delete a workflow | implemented | `workflow:delete` |
| workflow | `get-workflow` | GET `/workflows/{id}` | Retrieve a workflow | implemented | `workflow:read` |
| workflow | `get-workflow-tags` | GET `/workflows/{id}/tags` | Get workflow tags | implemented | `workflowTags:list` |
| workflow | `get-workflow-version` | GET `/workflows/{id}/{versionId}` | Retrieves a specific version of a workflow | implemented | `workflow:read` |
| workflow | `get-workflows` | GET `/workflows` | Retrieve all workflows | implemented | `workflow:list` |
| workflow | `transfer-workflow` | PUT `/workflows/{id}/transfer` | Transfer a workflow to another project | implemented | `workflow:move` |
| workflow | `unarchive-workflow` | POST `/workflows/{id}/unarchive` | Unarchive a workflow | implemented | `workflow:delete` |
| workflow | `update-workflow` | PUT `/workflows/{id}` | Update a workflow | implemented | `workflow:update` |
| workflow | `update-workflow-tags` | PUT `/workflows/{id}/tags` | Update tags of a workflow | implemented | `workflowTags:update` |

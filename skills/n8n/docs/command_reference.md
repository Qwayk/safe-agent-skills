# Command Guide

This page lists the shipped n8n command surface. Every `api <family> <command>` entry maps to one operation in the pinned official n8n public REST API inventory.

Global flags used most often:

- `--env-file .env`: load local n8n settings
- `--output json`: emit one JSON object
- `--plan-out plan.json`: save a dry-run write plan
- `--apply --yes --plan-in plan.json`: apply a reviewed write plan
- `--ack-no-snapshot`: approve a write when the plan has no verified before-state
- `--ack-irreversible`: approve destructive, permission, credential, package, source-control, or production-risk work

## Setup and local history

- `n8n-safe-agent-cli onboarding [--no-write-env]`
- `n8n-safe-agent-cli auth check`
- `n8n-safe-agent-cli api list`
- `n8n-safe-agent-cli runs list [--limit 20]`
- `n8n-safe-agent-cli runs show --run-id <id>`

## Operation input flags

Operation commands use a small common input shape:

- `--path-param name=value`: set a path parameter such as `id`, `projectId`, or `dataTableId`; repeat as needed
- `--query name=value`: set an optional query parameter such as `limit`, `cursor`, `active`, or `tags`; repeat as needed
- `--body-json ...`: pass a JSON request body
- `--body-file file.json`: read a JSON request body from a file

## Official operation commands

### `audit`

- `n8n-safe-agent-cli api audit generate-audit` - POST `/audit`. Generate an audit (write). Scope: `securityAudit:generate`.

### `community-package`

- `n8n-safe-agent-cli api community-package get-installed-packages` - GET `/community-packages`. List installed community packages (read). Scope: `communityPackage:list`.
- `n8n-safe-agent-cli api community-package install-package` - POST `/community-packages`. Install a community package (write). Scope: `communityPackage:install`. Body required.
- `n8n-safe-agent-cli api community-package uninstall-package` - DELETE `/community-packages/{name}`. Uninstall a community package (write). Scope: `communityPackage:uninstall`. Required: `path:name`.
- `n8n-safe-agent-cli api community-package update-package` - PATCH `/community-packages/{name}`. Update a community package (write). Scope: `communityPackage:update`. Required: `path:name`.

### `credential`

- `n8n-safe-agent-cli api credential create-credential` - POST `/credentials`. Create a credential (write). Scope: `credential:create`. Body required.
- `n8n-safe-agent-cli api credential delete-credential` - DELETE `/credentials/{id}`. Delete credential by ID (write). Scope: `credential:delete`. Required: `path:id`.
- `n8n-safe-agent-cli api credential get-credential` - GET `/credentials/{id}`. Get credential by ID (read). Scope: `credential:read`. Required: `path:id`.
- `n8n-safe-agent-cli api credential get-credential-type` - GET `/credentials/schema/{credentialTypeName}`. Show credential data schema (read). Scope: `none`. Required: `path:credentialTypeName`.
- `n8n-safe-agent-cli api credential get-credentials` - GET `/credentials`. List credentials (read). Scope: `credential:list`.
- `n8n-safe-agent-cli api credential test-credential` - POST `/credentials/{id}/test`. Test credential by ID (write). Scope: `credential:read`. Required: `path:id`.
- `n8n-safe-agent-cli api credential transfer-credential` - PUT `/credentials/{id}/transfer`. Transfer a credential to another project. (write). Scope: `credential:move`. Required: `path:id`. Body required.
- `n8n-safe-agent-cli api credential update-credential` - PATCH `/credentials/{id}`. Update credential by ID (write). Scope: `credential:update`. Required: `path:id`. Body required.

### `data-table`

- `n8n-safe-agent-cli api data-table create-data-table` - POST `/data-tables`. Create a new data table (write). Scope: `dataTable:create`. Body required.
- `n8n-safe-agent-cli api data-table create-data-table-column` - POST `/data-tables/{dataTableId}/columns`. Add a column to a data table (write). Scope: `dataTableColumn:create`. Required: `path:dataTableId`. Body required.
- `n8n-safe-agent-cli api data-table delete-data-table` - DELETE `/data-tables/{dataTableId}`. Delete a data table (write). Scope: `dataTable:delete`. Required: `path:dataTableId`.
- `n8n-safe-agent-cli api data-table delete-data-table-column` - DELETE `/data-tables/{dataTableId}/columns/{columnId}`. Delete a column (write). Scope: `dataTableColumn:delete`. Required: `path:dataTableId, path:columnId`.
- `n8n-safe-agent-cli api data-table delete-data-table-rows` - DELETE `/data-tables/{dataTableId}/rows/delete`. Delete rows from a data table (write). Scope: `dataTableRow:delete`. Required: `path:dataTableId, query:filter`.
- `n8n-safe-agent-cli api data-table get-data-table` - GET `/data-tables/{dataTableId}`. Get a data table (read). Scope: `dataTable:read`. Required: `path:dataTableId`.
- `n8n-safe-agent-cli api data-table get-data-table-rows` - GET `/data-tables/{dataTableId}/rows`. Retrieve rows from a data table (read). Scope: `dataTableRow:read`. Required: `path:dataTableId`.
- `n8n-safe-agent-cli api data-table insert-data-table-rows` - POST `/data-tables/{dataTableId}/rows`. Insert rows into a data table (write). Scope: `dataTableRow:create`. Required: `path:dataTableId`. Body required.
- `n8n-safe-agent-cli api data-table list-data-table-columns` - GET `/data-tables/{dataTableId}/columns`. List columns of a data table (read). Scope: `dataTableColumn:read`. Required: `path:dataTableId`.
- `n8n-safe-agent-cli api data-table list-data-tables` - GET `/data-tables`. List all data tables (read). Scope: `dataTable:list`.
- `n8n-safe-agent-cli api data-table update-data-table` - PATCH `/data-tables/{dataTableId}`. Update a data table (write). Scope: `dataTable:update`. Required: `path:dataTableId`. Body required.
- `n8n-safe-agent-cli api data-table update-data-table-column` - PATCH `/data-tables/{dataTableId}/columns/{columnId}`. Update a column (write). Scope: `dataTableColumn:update`. Required: `path:dataTableId, path:columnId`. Body required.
- `n8n-safe-agent-cli api data-table update-data-table-rows` - PATCH `/data-tables/{dataTableId}/rows/update`. Update rows in a data table (write). Scope: `dataTableRow:update`. Required: `path:dataTableId`. Body required.
- `n8n-safe-agent-cli api data-table upsert-data-table-row` - POST `/data-tables/{dataTableId}/rows/upsert`. Upsert a row in a data table (write). Scope: `dataTableRow:upsert`. Required: `path:dataTableId`. Body required.

### `discover`

- `n8n-safe-agent-cli api discover get-discover` - GET `/discover`. Discover available API capabilities (read). Scope: `none`.

### `execution`

- `n8n-safe-agent-cli api execution delete-execution` - DELETE `/executions/{id}`. Delete an execution (write). Scope: `execution:delete`. Required: `path:id`.
- `n8n-safe-agent-cli api execution get-execution` - GET `/executions/{id}`. Retrieve an execution (read). Scope: `execution:read`. Required: `path:id`.
- `n8n-safe-agent-cli api execution get-execution-tags` - GET `/executions/{id}/tags`. Get execution tags (read). Scope: `executionTags:list`. Required: `path:id`.
- `n8n-safe-agent-cli api execution get-executions` - GET `/executions`. Retrieve all executions (read). Scope: `execution:list`.
- `n8n-safe-agent-cli api execution retry-execution` - POST `/executions/{id}/retry`. Retry an execution (write). Scope: `execution:retry`. Required: `path:id`.
- `n8n-safe-agent-cli api execution stop-execution` - POST `/executions/{id}/stop`. Stop an execution (write). Scope: `execution:stop`. Required: `path:id`.
- `n8n-safe-agent-cli api execution stop-many-executions` - POST `/executions/stop`. Stop multiple executions (write). Scope: `execution:stop`. Body required.
- `n8n-safe-agent-cli api execution update-execution-tags` - PUT `/executions/{id}/tags`. Update tags of an execution (write). Scope: `executionTags:update`. Required: `path:id`. Body required.

### `folders`

- `n8n-safe-agent-cli api folders create-folder` - POST `/projects/{projectId}/folders`. Create a folder (write). Scope: `folder:create`. Required: `path:projectId`. Body required.
- `n8n-safe-agent-cli api folders delete-folder` - DELETE `/projects/{projectId}/folders/{folderId}`. Delete a folder (write). Scope: `folder:delete`. Required: `path:projectId, path:folderId`.
- `n8n-safe-agent-cli api folders get-folder` - GET `/projects/{projectId}/folders/{folderId}`. Get folder details (read). Scope: `folder:read`. Required: `path:projectId, path:folderId`.
- `n8n-safe-agent-cli api folders get-folders` - GET `/projects/{projectId}/folders`. Retrieve folders (read). Scope: `folder:list`. Required: `path:projectId`.
- `n8n-safe-agent-cli api folders update-folder` - PATCH `/projects/{projectId}/folders/{folderId}`. Update a folder (write). Scope: `folder:update`. Required: `path:projectId, path:folderId`. Body required.

### `insights`

- `n8n-safe-agent-cli api insights get-insights-summary` - GET `/insights/summary`. Retrieve insights summary (read). Scope: `insights:read`.

### `n8n-package`

- `n8n-safe-agent-cli api n8n-package export-workflows` - POST `/n8n-packages/export`. Beta: Export workflows as an n8n package (write). Scope: `workflow:export`. Body required.
- `n8n-safe-agent-cli api n8n-package import-package` - POST `/n8n-packages/import`. Beta: Import an n8n package into a project (write). Scope: `workflow:import`. Body required.

### `projects`

- `n8n-safe-agent-cli api projects add-users-to-project` - POST `/projects/{projectId}/users`. Add one or more users to a project (write). Scope: `project:update`. Required: `path:projectId`.
- `n8n-safe-agent-cli api projects change-user-role-in-project` - PATCH `/projects/{projectId}/users/{userId}`. Change a user's role in a project (write). Scope: `project:update`. Required: `path:projectId, path:userId`.
- `n8n-safe-agent-cli api projects create-project` - POST `/projects`. Create a project (write). Scope: `project:create`. Body required.
- `n8n-safe-agent-cli api projects delete-project` - DELETE `/projects/{projectId}`. Delete a project (write). Scope: `project:delete`. Required: `path:projectId`.
- `n8n-safe-agent-cli api projects delete-user-from-project` - DELETE `/projects/{projectId}/users/{userId}`. Delete a user from a project (write). Scope: `project:update`. Required: `path:projectId, path:userId`.
- `n8n-safe-agent-cli api projects get-project-users` - GET `/projects/{projectId}/users`. List project members (read). Scope: `user:list`. Required: `path:projectId`.
- `n8n-safe-agent-cli api projects get-projects` - GET `/projects`. Retrieve projects (read). Scope: `project:list`.
- `n8n-safe-agent-cli api projects update-project` - PUT `/projects/{projectId}`. Update a project (write). Scope: `project:update`. Required: `path:projectId`. Body required.

### `source-control`

- `n8n-safe-agent-cli api source-control pull` - POST `/source-control/pull`. Pull changes from the remote repository (write). Scope: `sourceControl:pull`. Body required.

### `tags`

- `n8n-safe-agent-cli api tags create-tag` - POST `/tags`. Create a tag (write). Scope: `tag:create`. Body required.
- `n8n-safe-agent-cli api tags delete-tag` - DELETE `/tags/{id}`. Delete a tag (write). Scope: `tag:delete`. Required: `path:id`.
- `n8n-safe-agent-cli api tags get-tag` - GET `/tags/{id}`. Retrieves a tag (read). Scope: `tag:read`. Required: `path:id`.
- `n8n-safe-agent-cli api tags get-tags` - GET `/tags`. Retrieve all tags (read). Scope: `tag:list`.
- `n8n-safe-agent-cli api tags update-tag` - PUT `/tags/{id}`. Update a tag (write). Scope: `tag:update`. Required: `path:id`. Body required.

### `user`

- `n8n-safe-agent-cli api user change-role` - PATCH `/users/{id}/role`. Change a user's global role (write). Scope: `user:changeRole`. Required: `path:id`. Body required.
- `n8n-safe-agent-cli api user create-user` - POST `/users`. Create multiple users (write). Scope: `user:create`. Body required.
- `n8n-safe-agent-cli api user delete-user` - DELETE `/users/{id}`. Delete a user (write). Scope: `user:delete`. Required: `path:id`.
- `n8n-safe-agent-cli api user get-user` - GET `/users/{id}`. Get user by ID/Email (read). Scope: `user:read`. Required: `path:id`.
- `n8n-safe-agent-cli api user get-users` - GET `/users`. Retrieve all users (read). Scope: `user:list`.

### `variables`

- `n8n-safe-agent-cli api variables create-variable` - POST `/variables`. Create a variable (write). Scope: `variable:create`. Body required.
- `n8n-safe-agent-cli api variables delete-variable` - DELETE `/variables/{id}`. Delete a variable (write). Scope: `variable:delete`. Required: `path:id`.
- `n8n-safe-agent-cli api variables get-variables` - GET `/variables`. Retrieve variables (read). Scope: `variable:list`.
- `n8n-safe-agent-cli api variables update-variable` - PUT `/variables/{id}`. Update a variable (write). Scope: `variable:update`. Required: `path:id`. Body required.

### `workflow`

- `n8n-safe-agent-cli api workflow activate-workflow` - POST `/workflows/{id}/activate`. Publish a workflow (write). Scope: `workflow:activate`. Required: `path:id`.
- `n8n-safe-agent-cli api workflow archive-workflow` - POST `/workflows/{id}/archive`. Archive a workflow (write). Scope: `workflow:delete`. Required: `path:id`.
- `n8n-safe-agent-cli api workflow create-workflow` - POST `/workflows`. Create a workflow (write). Scope: `workflow:create`. Body required.
- `n8n-safe-agent-cli api workflow deactivate-workflow` - POST `/workflows/{id}/deactivate`. Deactivate a workflow (write). Scope: `workflow:deactivate`. Required: `path:id`.
- `n8n-safe-agent-cli api workflow delete-workflow` - DELETE `/workflows/{id}`. Delete a workflow (write). Scope: `workflow:delete`. Required: `path:id`.
- `n8n-safe-agent-cli api workflow get-workflow` - GET `/workflows/{id}`. Retrieve a workflow (read). Scope: `workflow:read`. Required: `path:id`.
- `n8n-safe-agent-cli api workflow get-workflow-tags` - GET `/workflows/{id}/tags`. Get workflow tags (read). Scope: `workflowTags:list`. Required: `path:id`.
- `n8n-safe-agent-cli api workflow get-workflow-version` - GET `/workflows/{id}/{versionId}`. Retrieves a specific version of a workflow (read). Scope: `workflow:read`. Required: `path:id, path:versionId`.
- `n8n-safe-agent-cli api workflow get-workflows` - GET `/workflows`. Retrieve all workflows (read). Scope: `workflow:list`.
- `n8n-safe-agent-cli api workflow transfer-workflow` - PUT `/workflows/{id}/transfer`. Transfer a workflow to another project (write). Scope: `workflow:move`. Required: `path:id`. Body required.
- `n8n-safe-agent-cli api workflow unarchive-workflow` - POST `/workflows/{id}/unarchive`. Unarchive a workflow (write). Scope: `workflow:delete`. Required: `path:id`.
- `n8n-safe-agent-cli api workflow update-workflow` - PUT `/workflows/{id}`. Update a workflow (write). Scope: `workflow:update`. Required: `path:id`. Body required.
- `n8n-safe-agent-cli api workflow update-workflow-tags` - PUT `/workflows/{id}/tags`. Update tags of a workflow (write). Scope: `workflowTags:update`. Required: `path:id`. Body required.

## Write example

```bash
n8n-safe-agent-cli --env-file .env --plan-out plan.json api workflow create-workflow --body-file workflow.json
```

Review `plan.json`. Apply only after review:

```bash
n8n-safe-agent-cli --env-file .env --apply --yes --plan-in plan.json --ack-no-snapshot --ack-irreversible api workflow create-workflow --body-file workflow.json
```

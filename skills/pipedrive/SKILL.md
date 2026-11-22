---
name: pipedrive
description: Read Pipedrive deals, contacts, activities, pipelines, and other CRM records for lookups and reports.
---

# Pipedrive

Use `qwayk-pipedrive-safe-agent-cli` to read Pipedrive. Check setup with `onboarding` and `auth check`. Use the printed command if the user picked a different settings file. Keep the token out of chat.

Use `--output json` and a named command from the API coverage table. Read a small sample first, then confirm the account and records. Tell the user if more pages are available or a read failed.

Changes, OAuth-only operations, and downloading file content belong in another workflow. For a request outside this tool, say what it can do. Use `excluded by choice: read-only tool` for documented read-only exclusions. See the local docs for the exact commands and access requirements.

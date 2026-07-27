---
name: jira
description: Use when the user wants an agent to read or manage Jira Cloud Platform or Jira Software work through fixed Jira commands with review-first live changes.
---

# Jira Cloud

Use this tool for Jira Cloud issues, projects, users, groups, comments, worklogs, dashboards, filters, fields, workflows, schemes, boards, backlogs, epics, and sprints.

Do not use it for Jira Service Management, Assets, Operations, Confluence, Atlassian organization administration outside the selected Jira APIs, Jira Data Center or Server, undocumented endpoints, or arbitrary HTTP requests.

## Start safely

1. If setup is missing, run `jira-safe onboarding` and help the user fill the local `.env` file without putting credentials in chat.
2. Run `jira-safe --env-file .env auth check`.
3. Start with a read that proves the exact project, issue, board, sprint, user, or setting the user named.
4. Use `jira-safe operations show --surface SURFACE --command COMMAND` when you need the exact documented inputs or coverage status.

## Reads

Run a fixed read command directly after checking the Jira site and target. Explain the result in the user's language. Do not replace a fixed command with a raw URL, arbitrary method, SDK call, or generic request path.

## Live changes

First run the fixed write command without `--apply` and save its plan. Read the plan and explain the target, requested change, body or upload hashes, risk level, and snapshot warning.

Do not apply until the user approves that exact plan. Apply with global flags before the Platform or Software command:

- always: `--apply --plan-in PLAN --yes`
- when the plan has no reliable before-state: `--ack-no-snapshot`
- when the plan says `high_risk: true`: `--ack-high-risk`

Do not repeat operation inputs during apply; the tool reads them only from the reviewed plan. After apply, report the receipt, snapshot result, verification result, and anything Jira did not prove. Never promise rollback or undo unless a separate Jira restore action is actually available and approved.

## Finish

For exact syntax, use `docs/command_reference.md`. For all 721 official rows, use `docs/api_coverage.md`. For safety details and honest live-proof limits, use `docs/safety_model.md` and `docs/proof.md`.

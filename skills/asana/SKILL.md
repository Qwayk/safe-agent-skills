---
name: asana
description: Use when the user wants an agent to review or manage official Asana REST work through fixed commands with saved plans before live changes.
---

# Asana

Use this tool for Asana workspaces, teams, memberships, projects, portfolios, goals, tasks, sections, status updates, custom fields, time tracking, stories, attachments, webhooks, rules, exports, audit logs, budgets, rates, roles, agents, AI Studio usage, and the other official REST families in the coverage ledger.

Do not use it for App Components, SCIM, OAuth app registration or token lifecycle, browser automation, undocumented endpoints, arbitrary HTTP requests, SDK pass-through, or `POST /batch`.

## Start with a read

1. If setup is missing, run `asana-safe --env-file .env onboarding` and help the user fill `ASANA_ACCESS_TOKEN` without putting the token in chat.
2. Run `asana-safe --env-file .env auth check`.
3. Start with the fixed read that proves the exact workspace, team, project, portfolio, goal, task, or setting the user named.
4. Use `asana-safe commands show COMMAND` when you need exact parameters, OAuth scopes, access notes, body type, risk, pagination, or async behavior.

Explain the result in the user's language. A plan, permission, scope, or service-account refusal does not authorize a generic request workaround.

## Prepare live changes

Run the fixed POST, PUT, or DELETE command without `--apply`. Give it only documented `--param` values plus an exact `--data-json`, `--data-file`, or documented attachment `--file`. The CLI saves a plan instead of sending the write.

Read the plan and explain:

- the fixed command and exact target
- the proposed body or attachment hashes
- the saved before-state, or the no-snapshot warning
- stronger-risk reasons
- the available verification method
- the fact that rollback is not promised

Wait for the user to approve that exact plan ID.

Do not edit a saved plan or try to repair one that fails integrity. Plans are authenticated by a private key in the tool's local state. If the plan or key changed, create and review a new plan.

## Apply only the approved plan

Apply with:

```bash
asana-safe --env-file .env api COMMAND --plan-in PLAN_PATH --apply --approve PLAN_ID
```

Do not repeat parameters, data, or file flags during apply. Add `--acknowledge-no-snapshot` only when the reviewed plan has no reliable before-state. Add `--acknowledge-risk` only when the plan names stronger-risk reasons.

For asynchronous work, use `--wait` only when waiting is useful. Do not report accepted, queued, running, or timed-out work as completed.

## Finish from the receipt

Report whether Asana accepted the request, the asynchronous state, what readback verified, what remains unverified, and the saved receipt path. Never promise rollback or undo from a snapshot alone.

Use `docs/command_reference.md` for syntax, `docs/api_coverage.md` for all 249 rows, `docs/safety_model.md` for approval behavior, and `docs/proof.md` for tested and live-unverified limits.

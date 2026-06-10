# Skill: GA4 (Google Analytics) — `ga4-api-tool`

This page is the agent-facing rule sheet for the public Google Analytics skill.
If you just want to use the skill, start with the README plus the use-cases and onboarding docs.

This skill runs the GA4 safe CLI locally. It is **dry-run by default** for GA4 discovery methods and requires explicit apply flags for anything that might write or delete.

## Safety rules (non-negotiable)

- Never print or store secrets (OAuth refresh tokens, client secrets, Authorization headers).
- Prefer plans: generate a plan, review it, then request apply only after approval and all required flags.
- For high-risk or irreversible operations, refuse unless the required gates are present:
  - High: `--apply --yes --plan-in <file>`
  - Irreversible: `--apply --yes --ack-irreversible --plan-in <file>`
- For write-capable commands, this tool is currently plan-only: apply needs required approval before GA4 HTTP until before-state capture exists.
- `recovery` on plans always reports:
  - `automatic_rollback: false`
  - `snapshots: []`
  - `backups: []`
  - `rollback_plan: null`
- Always return redacted outputs if a payload contains secret-like fields (GA4 Measurement Protocol `secretValue` is always redacted).

## Setup (one-time)

- Create `.env` from `.env.example` next to where you will run the tool.
- Pick an auth mode in `.env`:
  - `GA4_AUTH_MODE=adc` (default), or
  - `GA4_AUTH_MODE=service_account_json` + `GA4_SERVICE_ACCOUNT_JSON=...`, or
  - `GA4_AUTH_MODE=oauth_refresh_token` + OAuth fields (or `.state/token.json` via `auth token set`)

## First command (safe)

- `ga4-api-tool --output json auth check`

If the user explicitly wants a credential refresh/network check:

- `ga4-api-tool --output json --apply auth check`

## Command naming (discovery-derived)

All GA4 discovery methods are explicit commands. Shape:

- `ga4-api-tool admin v1alpha <resource chain> <method> [flags...]`
- `ga4-api-tool data v1beta <resource chain> <method> [flags...]`
- `ga4-api-tool data v1alpha <resource chain> <method> [flags...]`

The canonical list lives at `docs/official_commands.txt`.

## Workflow for a write-like operation

1) Dry-run plan (no network):
- run the method command without `--apply`
- save the plan with `--plan-out plan.json` (or rely on the run artifacts plan file)

2) Review the plan:
- confirm the target identifiers and requested changes are correct

3) Request apply:
- medium: `--apply`
- high: `--apply --yes --plan-in plan.json`
- irreversible: `--apply --yes --ack-irreversible --plan-in plan.json`

4) Confirm refusal:
- current write apply needs required approval before GA4 HTTP and does not create a receipt

## When to refuse

- Missing required identifiers (example: required path params like `--name` / `--property`).
- Missing auth configuration for the chosen `GA4_AUTH_MODE`.
- High/irreversible apply without the required gates.
- Any GA4 provider write requested before operation-specific before-state capture exists.

# Zendesk API tool (SafeCLI) — Skill wrapper

This page is the agent-facing rule sheet for the public Zendesk skill.
If you just want to use the skill, start with the README plus the use-cases and onboarding docs.

This skill uses `zendesk-api-tool` to interact with Zendesk Support (Ticketing) safely.

Core safety loop:
1) Generate a deterministic plan (plan-first, no network calls by default).
2) Review the plan.
3) For reads only, execute with `--live` when needed.
4) For writes, review the plan first; apply attempts need `--ack-no-snapshot` before Zendesk HTTP when no before-state can be saved.
5) Save the plan, approval-gate proof, and any exact limitation for proof-first review.

## First-time setup (no secrets in chat)

1) Confirm the CLI runs:
   - `zendesk-api-tool --output json --version`
2) Create a local `.env` next to your project:
   - Copy the shipped `.env.example` file to `.env`
3) In Zendesk Admin Center, create/copy an API token (recommended):
   - Apps and integrations → APIs → Zendesk API → Add API token
4) Paste into `.env` (never share in chat):
   - `ZENDESK_SUBDOMAIN=...`
   - `ZENDESK_EMAIL=...`
   - `ZENDESK_API_TOKEN=...`

Then run:
- `zendesk-api-tool --output json --env-file .env auth check`

## How to find the right API command

This tool pins the official Zendesk Ticketing OpenAPI snapshot and exposes one explicit `api ...` command per operation.

Start with:
- `zendesk-api-tool --output json inventory validate`
- Open the canonical command list:
  - `docs/official_commands_ticketing_2026-03-05.txt`

## Plan-only (default)

All `api` operations emit a plan unless you pass `--live`.

Example (plan only; no network):
- `zendesk-api-tool --output json --env-file .env api autocomplete-tags --q-query password-reset`

## Executing (network calls)

To actually call Zendesk:
- add `--live`

For writes:
- default is plan-only
- add `--ack-no-snapshot` when no before-state can be saved
- high-risk gate tests require `--apply --yes --plan-in <plan.json>`
- deletes also require `--ack-irreversible`

Recovery behavior:
- no automatic rollback
- no snapshots
- no backups
- if a restore command exists for that operation, run it as a separate explicit command

## Output contract (for agent runtimes)

- Default output is JSON.
- On safety refusal, the tool returns exit code 0 and outputs:
  - `{"ok": true, "refused": true, ...}`
- Secrets must never appear in stdout/stderr, plans, refusals, future receipts, or audit logs.

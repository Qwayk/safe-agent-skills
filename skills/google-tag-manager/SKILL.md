# Skill: gtm-api-safe-cli

This page is the agent-facing rule sheet for the public Google Tag Manager skill.
If you just want to use the skill, start with the README plus the use-cases and onboarding docs.

Use `gtm-api-tool` to interact with the Google Tag Manager API v2 safely.

## Safety contract (non-negotiable)

- Default to **read-only** operations unless the user explicitly asks for a write.
- For any write (POST/PUT/PATCH/DELETE): run **dry-run first** (no `--apply`) and produce a plan.
- Only perform a write when the user explicitly approves the plan, then run with:
  - `--apply --plan-in <plan.json>`
  - Add `--yes` for high-risk / destructive operations.
  - Add `--ack-irreversible` for irreversible operations (deletes/publish-like actions).
- If any required gates are missing, the tool must refuse safely (no side effects).
- Never ask the user to paste secrets into chat. Never echo secrets.

## Command surface

This tool exposes one explicit command per pinned discovery method.

- Canonical commands list: `docs/official_commands_v2.txt`
- Coverage ledger: `docs/api_coverage.md`

## Auth / setup

If authentication is not configured or fails, run:

- `gtm-api-tool --output json auth check`

Configuration is via `--env-file` (defaults to `.env`). See `docs/authentication.md`.

## Output expectations

- Use `--output json` unless the user explicitly wants text.
- For dry-run writes, expect a `plan` object (and optionally a `plan_out` path).
- For apply writes, expect a `receipt` object (and optionally a `receipt_out` path).
- For supported write families (`update`, `delete`, `publish`, `set_latest`), plans and receipts include a `before_state` section and the run artifacts directory may contain `before_state.json`.

## Examples (placeholders only)

Read (accounts list):

- `gtm-api-tool --output json accounts list`

Write (dry-run plan):

- `gtm-api-tool --output json --plan-out plan.json accounts update --path accounts/ACCOUNT_ID --body-json '{}'`

Write (apply from a reviewed plan):

- `gtm-api-tool --output json --apply --plan-in plan.json accounts update --path accounts/ACCOUNT_ID --body-json '{}'`

Irreversible write (apply):

- `gtm-api-tool --output json --apply --yes --ack-irreversible --plan-in plan.json accounts containers workspaces tags delete --path accounts/ACCOUNT_ID/containers/CONTAINER_ID/workspaces/WORKSPACE_ID/tags/TAG_ID`

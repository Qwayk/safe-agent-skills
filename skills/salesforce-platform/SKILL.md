# Skill: Salesforce Platform REST API (Safe CLI)

This page is the agent-facing rule sheet for the public Salesforce skill.
If you just want to use the skill, start with the README plus the use-cases and onboarding docs.

Use this skill to work with the official Salesforce Platform REST API and Bulk API 2.0 through `qwayk-salesforce-platform-safe-agent-cli`.

## Core rules

- Never ask the user to paste Salesforce access tokens into chat.
- Use explicit Salesforce command families only.
- Reads can run directly.
- Writes must stay dry-run first.
- Treat writes as reviewed-plan first: after outside review and required safety flags, use `--ack-no-snapshot` when no before-state can be saved.

## Setup

Make sure `.env` has:

- `SALESFORCE_INSTANCE_URL=https://your-domain.my.salesforce.com`
- `SALESFORCE_API_VERSION=67.0`

For the token, use one path:

- set `SALESFORCE_ACCESS_TOKEN=...` in `.env`, or
- run `qwayk-salesforce-platform-safe-agent-cli auth token set --file token.json`

## Safe workflow

1. Verify the tool exists:
- `qwayk-salesforce-platform-safe-agent-cli --output json --version`

2. Verify auth:
- `qwayk-salesforce-platform-safe-agent-cli --output json auth check`

3. Run a read:
- `qwayk-salesforce-platform-safe-agent-cli --output json <family> <action> ...`

4. Preview a write:
- `qwayk-salesforce-platform-safe-agent-cli --output json <family> <action> ... --plan-out plan.json`

5. Request apply only after review:
- `qwayk-salesforce-platform-safe-agent-cli --output json --apply [--yes] [--ack-irreversible] --plan-in plan.json <family> <action> ...`

When no command-specific before-state can be saved, the reviewed apply path requires `--ack-no-snapshot` before Salesforce HTTP. The write plan contract is explicit:
- `plan.before_state.required` is true
- `plan.before_state.supported` is false
- `plan.recovery.automatic_rollback` is false
- `plan.recovery.backups` and `plan.recovery.snapshots` are empty
- `plan.recovery.rollback_plan` is `null`

6. Use shipped Bulk API 2.0 commands directly:
- `jobs-ingest` for object load jobs
- `jobs-query` for async query jobs

7. Use extra helpers when needed:
- `--query-param key=value`
- `--header Accept-Language=en-US`
- `--download-to file.csv`
- `--multipart-file multipart.json`

## Refusal conditions

- Missing Salesforce instance URL or access token
- Write requested without a dry-run review step
- Password set/reset apply requested without `--plan-in`
- High-risk write requested without `--yes`
- Irreversible action requested without `--ack-irreversible`
- Any Salesforce provider write requested before command-specific before-state capture exists

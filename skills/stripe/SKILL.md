# Stripe API tool (SafeCLI) — Skill wrapper

This page is the agent-facing rule sheet for the public Stripe skill.
If you just want to use the skill, start with the README plus the use-cases and onboarding docs.

This skill uses `stripe-api-tool` to interact with Stripe safely.

Core safety loop:
1) Generate a deterministic plan (no network calls by default).
2) Review the plan.
3) Use `--live` only for reads.
4) For API writes, stop for review until provider backup or no-snapshot approval is handled.

The tool does not create Stripe write backups today, so live API writes need explicit no-snapshot approval and a receipt.

## First-time setup (no secrets in chat)

1) Confirm the CLI runs:
   - `stripe-api-tool --output json --version`
2) Create a local `.env` next to your project:
   - Copy the shipped `.env.example` file to `.env`
3) In Stripe Dashboard, create/copy an API key:
   - Developers → API keys
4) Paste the key into `.env`:
   - `STRIPE_API_KEY=...`

Then run:
- `stripe-api-tool --output json auth check`

## How to find the right API command

This tool pins an official Stripe OpenAPI snapshot and exposes one explicit `api ...` command per operation.

Start with:
- `stripe-api-tool --output json inventory validate`
- Open the canonical command list:
  - `docs/official_commands_2026-02-25.clover_2026-03-05.txt`

## Plan-only (default)

All `api` operations emit a plan unless you pass `--live`.

Example (plan only):
- `stripe-api-tool --output json --env-file .env api post-customers --data name=Alice`

## Executing read-only network calls

To call Stripe for reads:
- add `--live`

For API writes:
- do not promise live apply today
- the CLI needs explicit no-snapshot approval before Stripe HTTP when no provider backup or before-state can be saved

High-risk and money-moving gates still appear in plans. The tool enforces those gates before no-snapshot approval.

### Money-moving (extra acknowledgement required)

If the plan risk requirements include `ack_spend_money: true`, attempted apply requires:
- `--live --apply --yes --plan-in <plan.json> --ack-spend-money`
Then the CLI needs explicit no-snapshot approval before Stripe HTTP when no provider backup or before-state can be saved.

### Irreversible (`DELETE`)

Attempted apply requires:
- `--live --apply --yes --plan-in <plan.json> --ack-irreversible`
Then the CLI needs explicit no-snapshot approval before Stripe HTTP when no provider backup or before-state can be saved.

## Connected accounts (Stripe-Account header)

To target a connected account:
- `stripe-api-tool --output json --env-file .env api --stripe-account acct_... <operation> ...`

If `STRIPE_ACCOUNT_ALLOWLIST` is configured, the tool refuses any `--stripe-account` not in the allowlist.

## Output contract (for agent runtimes)

- Default output is JSON.
- On safety refusal, the tool returns exit code 0 and outputs:
  - `{"ok": true, "refused": true, ...}`
- Secrets must never appear in stdout/stderr, plans, refusals, receipts, or audit logs.

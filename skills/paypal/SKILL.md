# Skill: PayPal REST API (Safe CLI)

This page is the agent-facing rule sheet for the public PayPal skill.
If you just want to use the skill, start with the README plus the use-cases and onboarding docs.

Use this skill to work with the official PayPal REST APIs through `qwayk-paypal-safe-agent-cli`.

## Core rules

- Never ask the user to paste PayPal client secrets into chat.
- Use only the shipped PayPal command families from `docs/api_coverage.md`.
- Reads can run directly.
- Writes must stay dry-run first.
- Do not request write apply until the plan has been reviewed outside the CLI.
- Write apply needs a reviewed plan and `--ack-no-snapshot` before PayPal auth or HTTP when no before-state can be saved.

## Setup

Make sure `.env` has:

- `PAYPAL_ENVIRONMENT=sandbox` or `PAYPAL_ENVIRONMENT=live`
- `PAYPAL_CLIENT_ID=...`
- `PAYPAL_CLIENT_SECRET=...`

Optional only when the PayPal integration needs them:

- `PAYPAL_PARTNER_ATTRIBUTION_ID=...`
- `PAYPAL_AUTH_ASSERTION=...`

## Safe workflow

1. Verify the tool exists:
- `qwayk-paypal-safe-agent-cli --output json --version`

2. Run onboarding if setup is not done:
- `qwayk-paypal-safe-agent-cli --output json onboarding --no-write-env`

3. Verify auth when real credentials are present:
- `qwayk-paypal-safe-agent-cli --output json auth check`

4. Find the exact command:
- open `docs/api_coverage.md`

5. Run a read:
- `qwayk-paypal-safe-agent-cli --output json <family> <action> ...`

6. Preview a write:
- `qwayk-paypal-safe-agent-cli --output json <family> <action> ... --body-file body.json --plan-out plan.json`

7. Request apply only after review:
- `qwayk-paypal-safe-agent-cli --output json --apply <family> <action> ... --body-file body.json --receipt-out receipt.json`

8. Add `--yes` for any shipped action that requires it:
- `qwayk-paypal-safe-agent-cli --output json --apply --yes payment-tokens delete --id PAYTOK-ID`
- `qwayk-paypal-safe-agent-cli --output json --apply --yes disputes accept-claim --id DISP-ID`
- `qwayk-paypal-safe-agent-cli --output json --apply --yes payments authorizations.void --authorization-id AUTH-ID`

No current shipped PayPal command in this tool uses `--ack-irreversible`.

## Notes for PayPal

- Some action names include dots because they stay close to the official PayPal resource names, such as `payments authorizations.get`.
- Some documented PayPal products are account-gated, partner-gated, or live-unverified in this repo build.
- Some `POST` endpoints are still read-only in this tool because they perform search, quote, or signature verification work.

## Output contract

- Default output is JSON.
- On safety refusal, the tool returns exit code `0` and outputs `{"ok": true, "refused": true, ...}`.
- Write plans include `before_state` and an explicit no-recovery contract.
- Missing approval produces a refusal; supported approved writes should produce a receipt.
- Secrets must never appear in stdout, stderr, plans, refusals, receipts, or audit logs.

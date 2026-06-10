# Skill: WooCommerce REST API (Safe CLI)

This page is the agent-facing rule sheet for the public WooCommerce skill.
If you just want to use the skill, start with the README plus the use-cases and onboarding docs.

Use this skill to work with the official WooCommerce REST API v3 through `qwayk-woocommerce-safe-agent-cli`.

## Core rules

- Never ask the user to paste consumer keys or secrets into chat.
- Use explicit WooCommerce command families only.
- Reads can run directly.
- Writes must stay dry-run first.
- Treat writes as reviewed-plan first: after outside review and required safety flags, use `--ack-no-snapshot` when no before-state can be saved.
- Treat every write as non-recoverable from this tool: it creates no snapshots, no provider backups, and no rollback plan.

## Setup

Make sure `.env` has:

- `WOOCOMMERCE_STORE_URL=https://shop.example.com`
- `WOOCOMMERCE_CONSUMER_KEY=...`
- `WOOCOMMERCE_CONSUMER_SECRET=...`

If the store strips `Authorization` headers, also set:

- `WOOCOMMERCE_QUERY_STRING_AUTH=true`

## Safe workflow

1. Verify the tool exists:
- `qwayk-woocommerce-safe-agent-cli --output json --version`

2. Verify auth:
- `qwayk-woocommerce-safe-agent-cli --output json auth check`

3. See what is shipped:
- `qwayk-woocommerce-safe-agent-cli --output json operations list`

4. Run a read:
- `qwayk-woocommerce-safe-agent-cli --output json <family> <action> ...`

5. Preview a write:
- `qwayk-woocommerce-safe-agent-cli --output json <family> <action> ... --body-json '{...}' --plan-out plan.json`

6. Request apply only after review:
- `qwayk-woocommerce-safe-agent-cli --output json --apply --plan-in plan.json <family> <action> ... --body-json '{...}'`

7. For high-risk writes, add `--yes`.

Missing approval stops the write before WooCommerce HTTP. Approved supported writes should produce a receipt, and the plan shows the no-snapshot limit when no before-state can be saved.

## Refusal conditions

- Missing store URL, or missing WooCommerce REST keys for reads and auth checks
- Write requested without a dry-run review step
- Apply requested without `--plan-in`
- High-risk write requested without `--yes`
- Any WooCommerce provider write requested before operation-specific before-state capture exists

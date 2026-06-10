# Skill: Shopify Admin GraphQL (SafeCLI)

This page is the agent-facing rule sheet for the public Shopify Admin skill.
If you just want to use the skill, start with the README plus the use-cases and onboarding docs.

Use this skill to interact with a Shopify store’s **Admin GraphQL API** via the safe CLI `shopify-admin-api-tool`.

## Core rules

- Never ask the user to paste tokens into chat.
- Reads: use `query ...` commands.
- Writes: use `mutation ...` commands for dry-run plans first.
- A live mutation can continue only after plan review and the required approval. When no operation-specific before-state can be saved, that approval is `--ack-no-snapshot`.
- Do not use custom return shapes unless explicitly requested and acknowledged (`--ack-unsafe-return-shape`).

## Setup (once per machine)

- Ensure `.env` exists (local-only):
  - `SHOPIFY_SHOP_DOMAIN=your-shop.myshopify.com`
  - `SHOPIFY_ADMIN_ACCESS_TOKEN=...`
  - `SHOPIFY_ADMIN_API_VERSION=2026-01`

## Safe workflow

1) Verify tool works (no secrets):
- `shopify-admin-api-tool --output json --version`

2) Verify auth (read-only):
- `shopify-admin-api-tool --output json auth check`

3) Discover what’s supported (pinned inventory):
- `shopify-admin-api-tool --output json operations list`

4) Read (query):
- `shopify-admin-api-tool --output json query <operation-kebab> --vars vars.json`

5) Write (mutation) — plan first:
- `shopify-admin-api-tool --output json mutation <operation-kebab> --vars vars.json --plan-out plan.json`

6) Write (mutation) — attempted apply:
- Do not run live apply without a reviewed plan and required approval. When no before-state can be saved, add `--ack-no-snapshot` and verify the result.

## Refusal conditions

- Missing required env keys.
- High-risk/irreversible mutation requested without the required flags shown in the plan (`--yes`, `--plan-in`, `--ack-irreversible`).
- Any live mutation missing `--ack-no-snapshot` when operation-specific before-state capture is not supported yet.

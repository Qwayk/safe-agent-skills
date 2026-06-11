---
name: awin-publisher-safe-cli
description: Awin publisher CLI helper for account checks, reporting, feeds, linkbuilder, and proof-of-purchase review-first uploads.
---

Use this skill only with these shipped command families:

- `awin-publisher-safe-cli onboarding`
- `awin-publisher-safe-cli auth check`
- `awin-publisher-safe-cli accounts list`
- `awin-publisher-safe-cli programs list ...`
- `awin-publisher-safe-cli programs details ...`
- `awin-publisher-safe-cli offers list ...`
- `awin-publisher-safe-cli transactions list ...`
- `awin-publisher-safe-cli transactions by-ids ...`
- `awin-publisher-safe-cli transaction-queries list ...`
- `awin-publisher-safe-cli reports advertiser ...`
- `awin-publisher-safe-cli reports campaign ...`
- `awin-publisher-safe-cli reports creative ...`
- `awin-publisher-safe-cli linkbuilder generate ...`
- `awin-publisher-safe-cli linkbuilder generate-batch ...`
- `awin-publisher-safe-cli linkbuilder quota ...`
- `awin-publisher-safe-cli feeds enhanced-download ...`
- `awin-publisher-safe-cli feeds legacy-list ...`
- `awin-publisher-safe-cli feeds legacy-download ...`
- `awin-publisher-safe-cli proof-of-purchase orders create ...`
- `awin-publisher-safe-cli runs list ...`
- `awin-publisher-safe-cli runs show ...`

Rules:

- Always call with `--output json`.
- Never output tokens, API keys, or raw authorization headers.
- For `proof-of-purchase orders create`, start with dry-run and saved plan. Only use `--apply --yes --plan-in <saved plan>` after the user explicitly approves the live submission.
- If the user asks for anything outside this shipped command surface, reply: "No such shipped command in this tool."

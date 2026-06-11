# Klaviyo

**Capability:** Reads + careful changes

Use this skill when you want your agent to review Klaviyo audiences, campaigns, forms, templates, catalog data, and customer events without guessing from raw docs.

You can hand it jobs like list and segment audits, profile or event checks, coupon and catalog planning, template or webhook changes, campaign-send review, and careful bulk audience work that should stop for review before apply.

Read work stays simple. Riskier Klaviyo changes slow down on purpose: the tool maps the exact operation first, builds a dry-run plan, flags the recovery limit, and requires explicit no-snapshot approval before any live Klaviyo write.

A good first ask is: "Check my Klaviyo connection, show me the safest audience and campaign reviews to start with, and preview anything risky before apply."

## Start here first

- Want ideas for real Klaviyo work? [What you can do with Klaviyo](docs/use_cases.md)
- Need setup? [Connect your Klaviyo account](docs/onboarding.md)
- Want the safety story first? [How this skill stays safe](docs/safety_model.md)

If you already want exact commands, jump straight to [Quickstart](docs/quickstart.md) and the [Command guide](docs/command_reference.md).

## What this skill helps with

- Review accounts, campaigns, flows, forms, lists, segments, profiles, tags, templates, and webhooks.
- Audit audience movement before bulk subscribe, suppress, unsubscribe, or delete work.
- Plan catalog, coupon, template, and campaign changes without sending live writes first.
- Check event, metric, review, and client-endpoint activity before you change anything.
- Use one explicit command surface across the stable Klaviyo API instead of asking the model to guess.

## What access this skill needs

- A Klaviyo private API key.
- A local `.env` file with your Klaviyo base URL and API key.
- `KLAVIYO_COMPANY_ID` only when you want `/client/*` endpoint work like signup, review, or client event flows.
- The smallest Klaviyo scopes that fit the job.

## Install and first run

Install slug: `klaviyo`

Ask your agent to install the `klaviyo` skill from `Qwayk/safe-agent-skills`.

If new skills do not appear automatically, reopen the app or attach the skill to the current workspace if your host needs that.

If your host does not let the agent install skills directly, run:

```bash
npx skills add Qwayk/safe-agent-skills@klaviyo -g -y
```

Then try a safe first ask like:

```text
Connect the Klaviyo skill to my account, confirm auth, and show me the safest list, segment, campaign, and profile reviews to start with.
```

## How this skill stays safe

- Read-only checks stay separate from live changes.
- Writes start as dry-run plans first.
- High-impact work like delete, bulk, send, cancel, suppress, unsubscribe, or relationship changes needs extra approval.
- Current Klaviyo write families do not save a useful before-state snapshot, so approved live writes also need explicit `--ack-no-snapshot`.
- Plans, receipts, audit logs, docs, tests, and examples all live together so you can inspect what the agent is using.

## What it covers today

This skill covers:

- stable Klaviyo API operations only
- account, audience, campaign, flow, form, profile, tag, template, metric, review, and webhook reads
- client endpoints for profiles, subscriptions, events, reviews, push tokens, and back-in-stock flows
- careful write planning for campaigns, audiences, catalogs, coupons, templates, forms, webhooks, and profile changes

The current shipped surface includes `308` stable operations. `87` beta operations are excluded by product choice.

## What happens before live changes

- The agent should identify the exact operation first with `api ops list` or `api ops show`.
- The tool builds a dry-run plan that shows the target, required inputs, and recovery limit.
- You review that plan before any live write.
- Live reads need `--live`.
- Live writes need `--live --apply`.
- High-impact Klaviyo writes also need `--plan-in` and `--yes`.
- Because this tool does not save before-state snapshots for writes today, approved live writes also need `--ack-no-snapshot`.

## What proof it leaves behind

- Dry-run plans can be saved with `--plan-out`.
- Apply receipts can be saved with `--receipt-out`.
- Write-capable runs save local proof files under `.state/runs/<run_id>/`.
- The proof pack, API coverage ledger, tests, and redacted examples all live in this repo.

## Limits

- This tool does not create snapshots, provider backups, or automatic rollback.
- Beta operations are excluded by product choice.
- `/client/*` workflows need `KLAVIYO_COMPANY_ID`.
- You still need valid Klaviyo scopes and permissions for real account work.

## Helpful docs

- [Browse all Klaviyo docs](docs/README.md)
- [Quickstart](docs/quickstart.md)
- [Command guide](docs/command_reference.md)
- [Proof and verification](docs/proof.md)
- [API coverage](docs/api_coverage.md)

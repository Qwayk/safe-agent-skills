# Google Ads

**Capability:** Reads + careful changes

Google Ads is where small targeting, budget, keyword, and conversion-tracking choices can turn into real spend very quickly.

This skill helps an agent check account access, export performance packs, review campaigns and keywords, validate GAQL reports, and prepare budget, negative keyword, conversion upload, or campaign-build plans before anything changes in the account.

Use it for questions like: "Which accounts can I access?", "What changed in the last 30 days?", "Which campaigns or keywords need attention?", "Can you preview this budget or negative keyword change?", or "Can you build a campaign plan from this reviewed spec?"

Google Ads reads and exports are meant to happen before account changes. Writes start as dry-run plans, spend-impacting actions need extra approval, remove actions need extra acknowledgement, and some write families still need explicit no-snapshot approval when the tool cannot save useful before-state first.

A good first ask is: "Check which Google Ads accounts I can access, export the optimization pack for the last 30 days, and summarize the biggest issues before we change anything."

## Start here first

- Want ideas for real Google Ads work? [What you can do with Google Ads](docs/use_cases.md)
- Need setup? [Connect your Google Ads account](docs/onboarding.md)
- Want the safety story first? [How this skill stays safe](docs/safety_model.md)

If you already want the faster operator path, jump to [Media buyer quickstart](docs/media_buyer_quickstart.md), [Quickstart](docs/quickstart.md), and the [Command guide](docs/command_reference.md).

## What this skill helps with

- Check account access and customer IDs before work starts.
- Export `optimization_pack_v1` or deeper analysis packs so your agent can explain campaigns, ads, budgets, placements, landing pages, devices, and other performance tables offline.
- Run GAQL safely when you need a custom read or field lookup.
- Look up campaigns, ad groups, keywords, and other entities before a change.
- Plan careful changes like budgets, negative keywords, Maximize Clicks ceilings, campaign-tree pauses, and conversion uploads.
- Build strict Search campaign plans from reviewed spec files before any live create path.

## What access this skill needs

- A Google Ads developer token.
- A Google OAuth client ID and client secret.
- A Google Ads refresh token.
- A customer ID for the account you want to inspect or change.
- A manager login customer ID when you work through an MCC or manager account.

Live writes also need the local write allowlist and tool flags to permit that customer ID.

## Install and first run

Install slug: `google-ads`

Ask your agent to install the `google-ads` skill from `Qwayk/safe-agent-skills`.

If new skills do not appear automatically, reopen the app or attach the skill to the current workspace if your host needs that.

If your host does not let the agent install skills directly, run:

```bash
npx skills add Qwayk/safe-agent-skills@google-ads -g -y
```

Then try a safe first ask like:

```text
Check which Google Ads accounts I can access, export the optimization pack for the last 30 days, and summarize the biggest issues before we plan any changes.
```

## How this skill stays safe

- It uses explicit service, helper, and builder commands instead of a generic call-anything bridge.
- Writes are dry-run first and need explicit apply flags.
- Customer ID write allowlists are default-deny, and a global kill switch can refuse all writes.
- Supported update operations and readable ad-schedule removes save before-state before mutation.
- Spend-impacting, remove, and higher-risk batch actions need extra acknowledgements.
- Plans, receipts, and read-back checks make it easier to review what was proposed and what actually happened.

## What it covers today

This skill covers:

- auth and account access checks
- GAQL reads and field discovery
- preset exports and offline diagnosis
- explicit Google Ads RPC service methods across the supported surface
- helper commands for repeated account work
- strict Search campaign builders for reviewed spec files

## What happens before live changes

- The agent should show the dry-run plan first.
- You review the customer ID, target entities, and spend or removal risk.
- Safe reads and pack exports can run immediately.
- Writes need `--apply`.
- Risky or batch applies need `--yes`.
- Spend-impacting actions need `--ack-spend`.
- Remove actions need `--ack-irreversible`.
- Some create, upload, and unreadable remove paths still need explicit no-snapshot approval before live apply.

## What proof it leaves behind

- Dry-run plans can be saved with `--plan-out`.
- Apply receipts can be saved with `--receipt-out`.
- Supported update operations and readable ad-schedule removes save before-state under `.state/runs/<run_id>/before/`.
- Read-back verification checks for presence, absence, and many changed fields after apply.
- Snapshot export packs save manifests, queries, tables, and summaries locally for review.
- The docs, tests, and API coverage ledgers are all in this repo.

## Limits

- Snapshot export packs are analysis evidence, not a restore path.
- Create, upload, unreadable remove, and builder create paths do not always have saved before-state yet.
- The tool can describe performance and diagnose patterns, but it does not prove causality.
- You still need valid Google Ads API access and an approved developer token for real account work.

## Helpful docs

- [Browse all Google Ads docs](docs/README.md)
- [Media buyer quickstart](docs/media_buyer_quickstart.md)
- [Winning ads workbook](docs/winning_ads_workbook.md)
- [KPI dictionary](docs/kpi_dictionary.md)
- [Agent recipes](docs/agent_recipes.md)
- [Presets reference](docs/presets_reference.md)
- [Proof and verification](docs/proof.md)
- [API coverage](docs/api_coverage.md)

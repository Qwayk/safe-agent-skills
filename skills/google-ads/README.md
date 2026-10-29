# Google Ads

The Google Ads API tool helps your agent review campaign performance, investigate wasted spend, and prepare account changes.

Ask it to compare campaigns, examine search terms and conversion tracking, export reports, or prepare keyword, budget, and Search campaign changes.

For example: "Which campaigns need attention?", "Check whether these search terms deserve negative keywords", or "Prepare a paused campaign for this service."

The agent reads the account first and explains its findings. Before changing campaigns, budgets, targeting, or tracking, it shows you the proposed changes and waits for approval.

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

- Google Ads API access on the Google Cloud project that owns your OAuth client.
- A Google OAuth client ID and client secret.
- A Google Ads refresh token.
- A customer ID for the account you want to inspect or change.
- A manager login customer ID when you work through an MCC or manager account.

Live writes also need the local write allowlist and tool flags to permit that customer ID.

Current release: tool 0.7.3 uses Google Ads API v25, including v25.1 definitions, through Python client 32.0.0.

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

Commands are available for the following areas. Command availability is not proof that every workflow has been run against a live account; see [tested behavior and limits](docs/proof.md).

This skill covers:

- auth and account access checks
- GAQL reads and field discovery
- preset exports, comparisons and legacy heuristic reports
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
- Direct GAQL and exports provide evidence. Legacy diagnosis/optimization commands remain for compatibility; their heuristics do not establish account truth or causality and are not a required review step.
- You still need valid Google Ads API access and an approved Google Cloud project for real account work.

## Helpful docs

- [Browse all Google Ads docs](docs/README.md)
- [Media buyer quickstart](docs/media_buyer_quickstart.md)
- [Winning ads workbook](docs/winning_ads_workbook.md)
- [KPI dictionary](docs/kpi_dictionary.md)
- [Agent recipes](docs/agent_recipes.md)
- [Presets reference](docs/presets_reference.md)
- [Proof and verification](docs/proof.md)
- [API coverage](docs/api_coverage.md)

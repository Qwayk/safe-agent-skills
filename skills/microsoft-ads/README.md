# Microsoft Ads

**Capability:** Reads + careful changes

Microsoft Ads is where search campaigns, audiences, reports, bids, and bulk jobs can affect spend across Bing and Microsoft’s ad network.

This skill helps an agent confirm access, review accounts and campaigns, pull reports, research keywords or audiences, and prepare Microsoft Ads service-operation, bulk, reporting, or customer-management changes before anything goes live.

Use it for questions like: "Which Microsoft Ads account can I reach?", "Can you pull last month’s performance?", "What keywords or audiences should we review?", "Can you preview this bulk change?", or "What approvals would this delete-like action need?"

Microsoft Ads work is careful by default. No network call happens without `--live`, writes start as dry-run plans, higher-risk changes can require a reviewed `--plan-in` plus `--yes`, delete-like actions need extra approval, and live writes still need explicit no-snapshot approval when useful before-state cannot be saved first.

A good first ask is: "Check the Microsoft Ads connection, confirm live access, and show me the safest reporting or account review steps to start with."

## Start here first

- Want ideas for real Microsoft Ads work? [What you can do with Microsoft Ads](docs/use_cases.md)
- Need setup? [Connect your Microsoft Ads account](docs/onboarding.md)
- Want the safety story first? [How this skill stays safe](docs/safety_model.md)

If you already want exact commands, jump straight to [Quickstart](docs/quickstart.md) and the [Command guide](docs/command_reference.md).

## What this skill helps with

- Check local Microsoft Ads setup and confirm live access safely.
- Review campaigns, accounts, reports, recommendations, audiences, and customer-management data.
- Run keyword, bid, and audience-estimate research before you change anything.
- Prepare careful campaign-management, bulk, reporting, ad-insight, or customer-management write plans.
- Review higher-risk budget, bid, delete-like, or batch actions before anything goes live.

## What access this skill needs

- A Microsoft Advertising developer token in `.env`.
- A local OAuth token JSON stored with `msads-api-tool auth token set --file token.json`.
- Optional customer or account IDs if you want default targets in `.env`.
- `--live` for real Microsoft Ads network calls, even for reads.
- Extra approval for higher-risk, irreversible, or no-snapshot write actions.

## Install and first run

Install slug: `microsoft-ads`

Ask your agent to install the `microsoft-ads` skill from `Qwayk/safe-agent-skills`.

If new skills do not appear automatically, reopen the app or attach the skill to the current workspace if your host needs that.

If your host does not let the agent install skills directly, run:

```bash
npx skills add Qwayk/safe-agent-skills@microsoft-ads -g -y
```

Then try a safe first ask like:

```text
Check the Microsoft Ads connection, confirm live access, and show me the safest account, campaign, or reporting reads to start with.
```

## How this skill stays safe

- No network call happens without `--live`, even for reads.
- Write-capable operations start as dry-run plans first.
- Higher-risk actions can require `--yes` and a reviewed `--plan-in`.
- Delete-like actions can also require `--ack-irreversible`.
- When no saved before-state exists, live writes also need `--ack-no-snapshot` before SOAP HTTP.
- Developer tokens, OAuth tokens, plans, receipts, and run artifacts stay redacted so secrets do not leak.
- Plans, refusals, receipts, run history, docs, and tests stay together so you can inspect what the agent used and what happened.

## What it covers today

This skill covers:

- campaign-management, bulk, reporting, ad-insight, and customer-management service operations
- local onboarding, auth checks, token status, token refresh, jobs, and run history
- explicit Microsoft Ads v13 commands instead of a generic raw-request bridge
- local proof files for plans, refusals, receipts, and run summaries

## What happens before live changes

- The agent should show the dry-run plan first.
- You review the target account, request body, risk level, and recovery limits.
- Live reads still need `--live`.
- Write-capable actions need `--live --apply`.
- Higher-risk writes can also require `--yes --plan-in`.
- Delete-like actions can also require `--ack-irreversible`.
- Writes without saved before-state also need `--ack-no-snapshot`.

## What proof it leaves behind

- Dry-run plans can be saved with `--plan-out`.
- Approved applies can save receipts with `--receipt-out`.
- Local run history can be reviewed with `runs list` and `runs show`.
- Refusals and audit logs show when a provider write did not happen because approval or another safety check was missing.
- The docs, tests, examples, and API coverage ledger are all in this repo.

## Limits

- Many live writes still do not have saved before-state or a built-in undo path.
- Some workflows still need customer IDs, account IDs, or request JSON prepared first.
- You still need a valid developer token, OAuth token, and the right Microsoft Ads permissions for real account work.
- Bulk and reporting workflows still depend on Microsoft processing time, quotas, and account-level access.

## Helpful docs

- [Browse all Microsoft Ads docs](docs/README.md)
- [Quickstart](docs/quickstart.md)
- [Command guide](docs/command_reference.md)
- [Proof and verification](docs/proof.md)
- [API coverage](docs/api_coverage.md)

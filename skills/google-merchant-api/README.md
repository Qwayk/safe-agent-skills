# Google Merchant Center

**Capability:** Reads + careful changes

Google Merchant Center is where product data, feeds, promotions, issues, regions, and conversion settings decide whether products can show up correctly across Google.

This skill helps an agent review Merchant accounts, products, promotions, issues, reports, feeds, data sources, quotas, and conversion settings, then prepare product-input or Merchant configuration changes before anything affects the catalog.

Use it for questions like: "Which products are disapproved?", "What issue clusters should we fix first?", "Are feeds or data sources set up correctly?", "Can you preview a product-input change?", or "Which Merchant account path am I using?"

Merchant reads and local auth checks can run directly. Writes start as dry-run plans, higher-risk or irreversible changes can require a reviewed `--plan-in` plus `--yes`, and live writes still need explicit no-snapshot approval when useful before-state cannot be saved first.

A good first ask is: "Check the Google Merchant Center connection, list my accounts or products safely, and show me the safest review steps before we plan any changes."

## Start here first

- Want ideas for real Merchant work? [What you can do with Google Merchant Center](docs/use_cases.md)
- Need setup? [Connect your Google Merchant Center account](docs/onboarding.md)
- Want the safety story first? [How this skill stays safe](docs/safety_model.md)

If you already want exact commands, jump straight to [Quickstart](docs/quickstart.md) and the [Command guide](docs/command_reference.md).

## What this skill helps with

- Check local Merchant auth setup and confirm which account path you are using.
- Review accounts, products, product inputs, promotions, issues, quotas, and reports.
- Find disapproved products, feed problems, missing fields, or risky catalog changes before you edit anything.
- Prepare careful write plans for product inputs, conversion sources, regions, services, data sources, and other Merchant surfaces.
- Review higher-risk, irreversible, or batch-style Merchant changes before anything goes live.

## What access this skill needs

- One Merchant auth mode in `.env`: service account, OAuth refresh token, or ADC.
- Service-account JSON for own-account access, or OAuth refresh-token credentials for client-account access.
- Optional Merchant Center account ID or GCP project ID defaults in `.env`.
- Extra approval for higher-risk, irreversible, or no-snapshot write actions.

## Install and first run

Install slug: `google-merchant-api`

Ask your agent to install the `google-merchant-api` skill from `Qwayk/safe-agent-skills`.

If new skills do not appear automatically, reopen the app or attach the skill to the current workspace if your host needs that.

If your host does not let the agent install skills directly, run:

```bash
npx skills add Qwayk/safe-agent-skills@google-merchant-api -g -y
```

Then try a safe first ask like:

```text
Check the Google Merchant Center connection, check my auth setup, and show me the safest account, catalog, or issue-review reads to start with.
```

## How this skill stays safe

- Reads and local auth checks can run directly.
- Write-capable operations start as dry-run plans first.
- Higher-risk writes can require `--yes` and a reviewed `--plan-in`.
- Irreversible actions can also require `--ack-irreversible`.
- When no saved before-state exists, live writes also need `--ack-no-snapshot` before credentials or Google HTTP.
- Plans, refusals, receipts, and logs stay secret-safe.
- Plans, run history, docs, tests, and coverage notes stay together so you can inspect what the agent used and what happened.

## What it covers today

This skill covers:

- Merchant account, product, promotion, report, quota, issue-resolution, inventory, conversion, data-source, and notification surfaces
- local onboarding, auth checks, token helpers, jobs, and run history
- explicit Merchant commands instead of a generic raw-request bridge
- local proof files for plans, refusals, receipts, and run summaries

## What happens before live changes

- The agent should show the dry-run plan first.
- You review the target account, request body, risk level, and recovery limits.
- Medium writes need `--apply`.
- Higher-risk writes can also require `--yes --plan-in`.
- Irreversible writes can also require `--ack-irreversible`.
- Writes without saved before-state also need `--ack-no-snapshot`.

## What proof it leaves behind

- Dry-run plans can be saved with `--plan-out`.
- Approved applies can save receipts with `--receipt-out`.
- Local run history can be reviewed with `runs list` and `runs show`.
- Refusals and audit logs show when a provider write did not happen because approval or another safety check was missing.
- The docs, tests, examples, and API coverage ledger are all in this repo.

## Limits

- Many live writes still do not have saved before-state or a built-in undo path.
- This tool does not support API-key auth. It supports service-account, OAuth refresh-token, or ADC paths only.
- Some Merchant workflows still need an exact account ID, product name, or request JSON prepared first.
- You still need the right Merchant Center access and Google permissions for real account work.

## Helpful docs

- [Browse all Google Merchant docs](docs/README.md)
- [Quickstart](docs/quickstart.md)
- [Command guide](docs/command_reference.md)
- [Proof and verification](docs/proof.md)
- [API coverage](docs/api_coverage.md)

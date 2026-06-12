# Qdrant Cloud

**Capability:** Reads + careful changes

Qdrant Cloud is where vector-search infrastructure decisions live: accounts, clusters, backups, regions, packages, access, billing, monitoring, and recovery options. This skill helps an agent inspect the control plane first, then prepare cluster, access, backup, billing, or serverless changes as reviewable plans.

It is useful for questions like "Which clusters and backups exist?", "Do we have the right regions and packages?", "Who has access?", "What billing or monitoring data should we review?", or "What approval is needed before this infrastructure change?"

Nothing hits the Qdrant Cloud API unless you add `--live`. Ordinary writes start as dry-run plans, many live changes still need explicit no-snapshot approval when no saved before-state or provider backup exists, and money-moving actions need extra approval. Provider backup and restore stays a narrow exception because it is the product's own recovery workflow.

A good first ask is: "Check the Qdrant Cloud skill is configured, list my accounts and clusters, and tell me what is safe to review before we plan any changes."

## Start here first

- Want ideas for real Qdrant Cloud work? [What you can do with Qdrant Cloud](docs/use_cases.md)
- Need setup? [Connect your Qdrant Cloud account](docs/onboarding.md)
- Want the safety story first? [How this skill stays safe](docs/safety_model.md)

If you already want exact commands, jump straight to [Quickstart](docs/quickstart.md) and the [Command guide](docs/command_reference.md).

## What this skill helps with

- Review accounts, clusters, releases, packages, regions, and quotas before anyone changes live infrastructure.
- Check backups, backup schedules, restore jobs, and cluster recovery options.
- Review management keys, database API keys, user roles, members, and permissions.
- Pull billing, invoice, discount, payment-method, and metering reads for account review.
- Inspect cluster logs, events, usage metrics, summary metrics, and serverless or hybrid resources.
- Preview careful Qdrant Cloud changes before anything goes live.

## What access this skill needs

- A Qdrant Cloud management API key.
- The account ID for most account-scoped, cluster, billing, and IAM work.
- A cluster ID, backup ID, collection ID, or other resource ID for deeper reads or reviewed change plans.
- Request JSON files when you want the agent to plan or apply a specific change.
- A local file path when you want to save plans, receipts, or run artifacts.

If your API key contains shell-special characters like `|`, quote it in `.env` or point the tool at the right file with `--env-file`.

## Install and first run

Install slug: `qdrant-cloud`

Ask your agent to install the `qdrant-cloud` skill from `Qwayk/safe-agent-skills`.

If new skills do not appear automatically, reopen the app or attach the skill to the current workspace if your host needs that.

If your host does not let the agent install skills directly, run:

```bash
npx skills add Qwayk/safe-agent-skills@qdrant-cloud -g -y
```

Then try a safe first ask like:

```text
Check the Qdrant Cloud skill is configured, list my accounts and clusters, and tell me what is safe to review before we plan any changes.
```

## How this skill stays safe

- Nothing calls the real Qdrant Cloud API unless you add `--live`.
- Ordinary writes start as dry-run plans first.
- Live apply needs `--live --apply`, plus any extra acknowledgement flags for destructive or billing-sensitive work.
- Many ordinary writes still need explicit no-snapshot approval before Qdrant Cloud HTTP when the tool cannot save useful before-state or provider backup first.
- Provider backup and restore workflows are explicit recovery jobs, not generic rollback for unrelated changes.
- Plans, run history, docs, tests, and coverage ledgers all live in this repo so you can inspect what the agent is using.

## What it covers today

This skill covers:

- account, auth, billing, payment, quota, IAM, and metering reads
- cluster, backup, monitoring, platform, hybrid, and serverless control-plane reads
- plan-first writes for account, auth, cluster, backup schedule, payment, IAM, hybrid, and serverless management work
- provider backup and restore workflows for `create-backup`, `restore-backup`, and `create-cluster-from-backup`

## What happens before live changes

- The agent should show the dry-run plan first.
- You review the target account, cluster, or request payload before apply.
- Offline config checks can run without `--live`.
- Real API reads need `--live`.
- Writes need `--live --apply`.
- Destructive or billing-sensitive actions can also need `--yes`, `--ack-irreversible`, or `--ack-spend-money`.
- Ordinary writes without saved before-state or provider backup also need explicit no-snapshot approval.

## What proof it leaves behind

- Dry-run plans can be saved with `--plan-out`.
- High-risk apply steps can reuse a reviewed plan with `--plan-in`.
- Provider backup or restore workflows can save receipts with `--receipt-out`.
- Write-capable runs can save local run history under `.state/runs`.
- The docs, tests, examples, and API coverage ledger all stay in this repo.

## Limits

- This skill manages the Qdrant Cloud control plane. It is not the normal vector-search query API for data inside your cluster.
- Many ordinary write families still do not have operation-specific before-state or provider backup support.
- Live reads still need a valid management key plus `--live`.
- Billing or payment actions need extra care because they can affect spend.

## Helpful docs

- [Browse all Qdrant Cloud docs](docs/README.md)
- [Quickstart](docs/quickstart.md)
- [Command guide](docs/command_reference.md)
- [Authentication details](docs/authentication.md)
- [Configuration](docs/configuration.md)
- [Troubleshooting](docs/troubleshooting.md)
- [Proof and verification](docs/proof.md)
- [API coverage](docs/api_coverage.md)

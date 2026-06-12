# Instantly

**Capability:** Reads + careful changes

Instantly is where cold email problems show up as campaign health, sending-account risk, lead quality, warmup issues, and deliverability signals. This skill helps an agent review those areas first, then prepare campaign, lead, webhook, or workspace changes only after the target and risk are clear.

It is useful for questions like "Which campaigns look weak right now?", "Which sending accounts need attention?", "Are these leads ready for cleanup?", or "What would this webhook or workspace change do before we apply it?"

Read and reporting work can start after setup. Riskier Instantly changes check auth, discover the right IDs, build dry-run plans, verify supported writes after apply, and save proof. Some supported writes save before-state first; create, send, bulk, and other no-pre-read families need explicit no-snapshot approval before HTTP.

A good first ask is: "Check my Instantly connection, list active campaigns and sending-account health, then show me the safest campaign or lead review to start with."

## Start here first

- Want ideas for real Instantly work? [What you can do with Instantly](docs/use_cases.md)
- Need setup? [Connect your Instantly account](docs/onboarding.md)
- Want the safety story first? [How this skill stays safe](docs/safety_model.md)

If you already want exact commands, jump straight to [Quickstart](docs/quickstart.md) and the [Command guide](docs/command_reference.md).

## What this skill helps with

- Review workspace health, campaign status, and deliverability signals.
- Audit campaigns, lead lists, lead labels, custom tags, and subsequences before changing them.
- Check account warmup, vitals, and other sensitive account details with file-only handling when the response can contain secrets or account internals.
- Plan or apply careful campaign, lead, webhook, and workspace changes with review-first safety.
- Run analytics, inbox placement, and webhook-event reports so you can understand what is happening before you change anything.

## What access this skill needs

- An Instantly API key.
- A local `.env` file with your Instantly base URL and API key.
- The smallest Instantly scopes you can use for the job.
- A lower-risk workspace is recommended first for bulk or irreversible changes.

## Install and first run

Install slug: `instantly`

Ask your agent to install the `instantly` skill from `Qwayk/safe-agent-skills`.

If new skills do not appear automatically, reopen the app or attach the skill to the current workspace if your host needs that.

If your host does not let the agent install skills directly, run:

```bash
npx skills add Qwayk/safe-agent-skills@instantly -g -y
```

Then try a safe first ask like:

```text
Connect the Instantly skill to my account, confirm auth, and show me my active campaigns, lead health, and the safest review-first jobs to start with.
```

## How this skill stays safe

- Read-only reporting stays separate from live changes.
- Sensitive reads and returned secrets never print raw values to chat or stdout. They stay in local files or receipts only.
- Write workflows start with dry-run plans.
- Supported live writes save before-state under `.state/runs/<run_id>/before/`.
- High-risk batch or destructive actions need extra approval, and some delete or irreversible applies also need a reviewed `--plan-in` file.
- If Instantly does not expose a safe pre-read for a write family, the tool requires explicit no-snapshot approval instead of pretending it has a rollback path.

## What it covers today

This skill covers:

- workspace health, admin, billing, and membership review
- campaigns, subsequences, leads, lead lists, lead labels, and custom tags
- analytics, inbox placement, email verification, webhook events, and background jobs
- accounts, API keys, DFY account orders, and CRM phone actions
- careful email, thread, webhook, and supersearch-enrichment workflows

## What happens before live changes

- The agent checks auth and discovers the right IDs first.
- The tool shows a dry-run plan before the write.
- You review the target, payload, and risk level.
- Sensitive reads need explicit apply approval and write their raw result to local proof files instead of stdout.
- High-risk batch or destructive actions need `--yes`.
- Some deletes and irreversible actions also need a reviewed `--plan-in` file.
- Create, send, reply, and other no-pre-read families need explicit no-snapshot approval when the tool cannot save useful before-state first.

## What proof it leaves behind

- Write-capable commands save plan, receipt, audit, and summary files under `.state/runs/`.
- Supported live writes save before-state under `.state/runs/<run_id>/before/`.
- Secret-bearing outputs stay in local `.state/sensitive/` files instead of chat or stdout.
- The docs, tests, and redacted example artifacts all live in this repo.

## Limits

- This tool does not have built-in rollback or restore.
- Some reads are intentionally file-only because they can contain sensitive account details or secrets.
- Some create, send, bulk, and irreversible families still have no safe before-state path, so they need explicit no-snapshot approval.
- You still need valid Instantly scopes for real account work.

## Helpful docs

- [Browse all Instantly docs](docs/README.md)
- [Quickstart](docs/quickstart.md)
- [Command guide](docs/command_reference.md)
- [Proof pack](docs/proof.md)
- [API coverage](docs/api_coverage.md)
- [Jobs and batch work](docs/jobs_and_batches.md)

# OpenAI

**Capability:** Reads + careful changes

Use this skill when you want your agent to work inside OpenAI more carefully: review what is there, inspect the shipped operation catalog, check live account access, and plan real API changes without guessing from raw docs.

You can hand your agent jobs like model and file checks, usage review, project or org review, assistant or thread review, vector store work, and careful OpenAI write plans for files, responses, batches, fine-tunes, or other documented API operations.

Read work stays simple. Riskier work slows down on purpose: no network call happens without `--live`, write-capable operations start as dry-run plans, spend-money actions need stronger approval, and live writes need explicit no-snapshot approval when the tool cannot save useful before-state first.

A good first ask is: "Check the OpenAI skill is configured, list the available operations, and show me the safest live read or review steps to start with."

## Start here first

- Want ideas for real OpenAI work? [What you can do with OpenAI](docs/use_cases.md)
- Need setup? [Connect your OpenAI access](docs/onboarding.md)
- Want the safety story first? [How this skill stays safe](docs/safety_model.md)

If you already want exact commands, jump straight to [Quickstart](docs/quickstart.md) and the [Command guide](docs/command_reference.md).

## What this skill helps with

- Check local OpenAI API setup and confirm live access safely.
- Review the pinned OpenAI operation catalog before making a live call.
- Inspect models, files, assistants, threads, vector stores, usage, projects, and other OpenAI resources.
- Plan careful write actions across the shipped OpenAI command surface.
- Review spend-money and delete-like actions before anything goes live.

## What access this skill needs

- Local OpenAI settings in `.env`.
- A valid OpenAI API key.
- Optional organization or project IDs if your account needs them.
- `--live` for real OpenAI network calls, even for reads.
- Billing permission for spend-money actions.
- Extra approval for spend-money, irreversible, or no-snapshot write actions.

## Install and first run

Install slug: `openai`

Ask your agent to install the `openai` skill from `Qwayk/safe-agent-skills`.

If new skills do not appear automatically, reopen the app or attach the skill to the current workspace if your host needs that.

If your host does not let the agent install skills directly, run:

```bash
npx skills add Qwayk/safe-agent-skills@openai -g -y
```

Then try a safe first ask like:

```text
Connect the OpenAI skill, list the available operations, and show me a safe live read or review path before we plan any changes.
```

## How this skill stays safe

- No network call happens without `--live`, even for reads.
- Write-capable operations start as dry-run plans first.
- Spend-money actions can require `--plan-in`, `--yes`, and `--ack-spend-money`.
- Delete-like or irreversible actions can also require `--ack-irreversible`.
- When no saved before-state exists, live writes also need `--ack-no-snapshot`.
- Approved live-write receipts can record the no-snapshot approval and recovery limit.
- Plans, receipts, logs, and run artifacts stay sanitized so keys and tokens do not leak.
- The docs, tests, coverage notes, and source code are all here in one place.

## What it covers today

This skill covers:

- the pinned OpenAI operation catalog shipped in this repo
- local onboarding, auth checks, operation discovery, and jobs
- explicit OpenAI API commands for reads and writes across the documented surface
- local run history and proof files for review

## What happens before live changes

- The agent should show the dry-run plan first.
- You review the operation, inputs, target, and recovery limits.
- Real network reads still need `--live`.
- Write-capable actions need `--live --apply`.
- Spend-money actions can also require `--plan-in`, `--yes`, and `--ack-spend-money`.
- Delete-like actions can also require `--ack-irreversible`.
- Writes without saved before-state also need `--ack-no-snapshot`.

## What proof it leaves behind

- Dry-run plans can be saved with `--plan-out`.
- Approved applies can save receipts with `--receipt-out`.
- Local run history can be reviewed with `runs list` and `runs show`.
- Receipts can also record no-snapshot approval when a live write had no saved before-state.
- Read receipts, plans, refusals, and summaries stay under local run history when artifacts are enabled.
- The docs, tests, examples, and API coverage ledger are all in this repo.

## Limits

- Many live writes still do not have saved before-state or a built-in undo path.
- The shipped surface follows the pinned OpenAI operation list in this repo, not whatever may have changed upstream later.
- Spend-money operations are intentionally slower because they need stronger approval.
- You still need valid OpenAI access, scopes, and billing permissions for real account work.

## Helpful docs

- [Browse all OpenAI docs](docs/README.md)
- [Quickstart](docs/quickstart.md)
- [Command guide](docs/command_reference.md)
- [Proof and verification](docs/proof.md)
- [API coverage](docs/api_coverage.md)

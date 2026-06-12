# Unsplash

**Capability:** Reads + careful changes

Unsplash is useful when image research needs real photo records, creator details, collections, topics, and download planning instead of a vague visual search. This skill helps an agent build shortlists, compare photos, inspect creator or collection context, and plan downloads only after the photo IDs and destination are clear.

It is useful for questions like "Find images for this article theme", "Build a consistent photo pack", "Which creator or collection fits this style?", "Can you export this search for review?", or "What would happen before these approved photos are downloaded?"

Most work is read-first. The only riskier path is `photos download`, because a real apply can trigger Unsplash download tracking and can also write a file to your machine. That path starts as a dry-run plan, needs explicit approval before apply, and still needs explicit no-snapshot approval when the tool cannot save useful prior state first.

A good first ask is: "Check the Unsplash skill is configured, find 20 photos for my topic, and build a shortlist before we plan any downloads."

## Start here first

- Want ideas for real Unsplash work? [What you can do with Unsplash](docs/use_cases.md)
- Need setup? [Connect your Unsplash access key](docs/onboarding.md)
- Want the safety story first? [How this skill stays safe](docs/safety_model.md)

If you already want exact commands, jump straight to [Quickstart](docs/quickstart.md) and the [Command guide](docs/command_reference.md).

## What this skill helps with

- Search photos for a topic, mood, product, or campaign idea.
- Build consistent photo shortlists from photos, topics, collections, and creator portfolios.
- Pull photo or user statistics for research and selection.
- Export repeatable JSON research pulls for larger review work.
- Plan careful downloads for approved photo IDs before any tracking endpoint or local file write runs.

## What access this skill needs

- An Unsplash Access Key stored locally in your `.env` file.
- The default Unsplash API base URL unless you intentionally changed it.
- A local output path only when you want exports or downloads written to your machine.

## Install and first run

Install slug: `unsplash`

Ask your agent to install the `unsplash` skill from `Qwayk/safe-agent-skills`.

If new skills do not appear automatically, reopen the app or attach the skill to the current workspace if your host needs that.

If your host does not let the agent install skills directly, run:

```bash
npx skills add Qwayk/safe-agent-skills@unsplash -g -y
```

Then try a safe first ask like:

```text
Check the Unsplash skill is configured, find 20 photos for a minimal home office article, and build a shortlist before we plan any downloads.
```

## How this skill stays safe

- Access Key reads are safe by default.
- OAuth-only endpoints stay out of scope here, so the skill does not guess across unsupported auth modes.
- `photos download` starts as a dry-run plan and does not trigger Unsplash download tracking or local file writes in plan mode.
- Real download apply needs explicit approval, and overwriting a local file also needs extra confirmation.
- When no useful saved before-state exists, approved tracked writes still need explicit no-snapshot approval before tracking or file writes.
- The docs, tests, examples, proof files, and API coverage ledger all live in this repo so you can inspect what the agent is using.

## What it covers today

This skill covers:

- photo list, get, random, search, and statistics reads
- collection, topic, user, and global statistics reads
- export helpers for repeatable local JSON pulls
- careful `photos download` planning and gated apply
- jobs and batch work for repeated research flows

## What happens before live changes

- The agent should show the dry-run plan first.
- You review the approved photo IDs, destination path, and overwrite risk.
- Normal read endpoints can run immediately.
- `photos download` only applies after explicit approval.
- Overwriting an existing file also needs `--yes`.
- When no saved before-state exists, the tracking call and local file write still need explicit no-snapshot approval.

## What proof it leaves behind

- Dry-run plans can be saved with `--plan-out`.
- Write-capable runs can save local history under `.state/runs`.
- Refusal outputs prove when download tracking or a local file write stopped before apply.
- The proof pack includes redacted examples, tests, and the API coverage ledger.

## Limits

- No OAuth or Bearer-token endpoints like `/me` or like/unlike flows.
- `photos download` does not have saved before-state or automatic undo.
- Exports, onboarding writes, and local auth-key storage write only to your own machine and need manual cleanup if you no longer want those files.
- Live reads still need a valid Unsplash Access Key and can still hit normal provider rate limits.

## Helpful docs

- [Browse all Unsplash docs](docs/README.md)
- [Quickstart](docs/quickstart.md)
- [Command guide](docs/command_reference.md)
- [Jobs and batch guide](docs/jobs_and_batches.md)
- [Authentication details](docs/authentication.md)
- [Configuration](docs/configuration.md)
- [Troubleshooting](docs/troubleshooting.md)
- [Proof and verification](docs/proof.md)
- [API coverage](docs/api_coverage.md)

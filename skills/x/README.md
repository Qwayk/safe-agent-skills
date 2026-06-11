# X

**Capability:** Reads + careful changes

Use this skill when you want your agent to review X accounts, users, posts, lists, mentions, DMs, and careful X API v2 changes without guessing from raw docs.

You can hand your agent jobs like account and token checks, user or post lookups, mention reviews, list work, explicit endpoint planning, DM safety checks, and controlled write plans for supported X API v2 actions.

Read work stays simple. Riskier work slows down on purpose: live reads need explicit `--live`, write-capable actions start as dry-run plans, and provider or local token writes need explicit no-snapshot approval when the tool cannot save useful before-state first.

A good first ask is: "Check the X skill is connected, show my account and recent mentions, list the main safe read options, and stop before any writes."

## Start here first

- Want ideas for real X work? [What you can do with X](docs/use_cases.md)
- Need setup? [Connect your X account](docs/onboarding.md)
- Want the safety story first? [How this skill stays safe](docs/safety_model.md)

If you already want exact commands, jump straight to [Quickstart](docs/quickstart.md) and the [Command guide](docs/command_reference.md).

## What this skill helps with

- Check auth readiness, token state, and which X auth mode is available.
- Review users, posts, mentions, lists, trends, Spaces, and other pinned X API v2 reads.
- Inspect the exact supported endpoint inventory through the pinned operation list.
- Plan careful post, follow, like, bookmark, list, or moderation writes before anything goes live.
- Check DM reachability, plan DM sends, and enforce safer bulk DM rules with local opt-out protection.
- Run batch jobs from CSV with the same review-first safety pattern.

## What access this skill needs

- An X app bearer token for many app-level reads.
- An OAuth user token for user-context reads, DMs, and most live writes.
- Your OAuth client ID and redirect URI if you want to use the PKCE helper flow.
- The right X scopes for DMs, follows, likes, bookmarks, list work, or other write-capable families.

## Install and first run

Install slug: `x`

Ask your agent to install the `x` skill from `Qwayk/safe-agent-skills`.

If new skills do not appear automatically, reopen the app or attach the skill to the current workspace if your host needs that.

If your host does not let the agent install skills directly, run:

```bash
npx skills add Qwayk/safe-agent-skills@x -g -y
```

Then try a safe first ask like:

```text
Connect the X skill, show my account, recent mentions, and DM safety status, then stop before any writes.
```

## How this skill stays safe

- Live reads need explicit `--live`.
- Write-capable actions start as dry-run plans first.
- Provider writes, DM sends, and token or PKCE state writes need `--ack-no-snapshot` when no saved before-state exists.
- Deletes and other irreversible actions also need `--ack-irreversible`.
- Bulk DM sends require intent evidence, an opt-out line, and a clean local opt-out ledger.
- The pinned X API snapshot, docs, tests, proof files, and coverage ledger all live in this repo so you can inspect what the agent is using.

## What it covers today

This skill covers:

- local onboarding, auth checks, token status, token set, and PKCE helpers
- explicit pinned `api <operationId>` commands for supported X API v2 reads and writes
- user helpers like `users resolve`
- DM helpers for can-send checks, single sends, bulk sends, and local opt-out protection
- batch jobs, demo safety examples, and local run history for review

## What happens before live changes

- The agent should show the dry-run plan first.
- You review the auth mode, target account, endpoint, and payload before apply.
- Read-only calls can run live with `--live`.
- Write-capable actions need `--apply --yes --ack-no-snapshot` when no saved before-state exists.
- DELETE actions also need `--ack-irreversible`.
- Demo writes and `jobs write.ping` stay template-only and refuse instead of pretending to write.

## What proof it leaves behind

- Dry-run plans can be saved with `--plan-out`.
- Approved applies can save receipts with `--receipt-out`.
- Local run history can be reviewed with `runs list` and `runs show`.
- The proof pack includes redacted example outputs for version, auth checks, explicit API planning, and DM planning.
- The docs, tests, examples, and API coverage ledger are all in this repo.

## Limits

- Most current writes do not have built-in rollback support.
- DM reachability still depends on recipient settings and your sender-account status.
- Some endpoints still depend on the right scopes, app review state, or X product access.
- Demo write flows and `jobs write.ping` are template-only safety examples, not real provider writes.

## Helpful docs

- [Browse all X docs](docs/README.md)
- [Quickstart](docs/quickstart.md)
- [Command guide](docs/command_reference.md)
- [Authentication details](docs/authentication.md)
- [Jobs and batch work](docs/jobs_and_batches.md)
- [Proof and verification](docs/proof.md)
- [API coverage](docs/api_coverage.md)

# Reddit

**Capability:** Reads + careful changes

Reddit is where account, subreddit, post, comment, message, wiki, moderation, and community work can become public very quickly.

This skill helps an agent inspect Reddit account and community data, list the official pinned API operations, and prepare write plans before anything posts, moderates, edits, messages, or changes account state.

Use it for questions like: "Is my Reddit API access ready?", "What subreddit or moderation data can we read?", "Which official operations are available?", "Can you preview this moderation action?", or "Can you plan this post-related change before applying it?"

Reddit now requires approval before Data API access, and live calls need a proper Reddit-style `User-Agent`. Reads need `--live`; writes are dry-run by default and need extra safety approval before provider changes.

A good first ask is: "Check the Reddit setup, list the account and subreddit operations available, run one safe live read if access is ready, and stop before any writes."

## Start here first

- Want ideas for real Reddit work? [What you can do with Reddit](docs/use_cases.md)
- Need setup? [Connect your Reddit account](docs/onboarding.md)
- Want the safety story first? [How this skill stays safe](docs/safety_model.md)

If you already want exact commands, jump straight to [Quickstart](docs/quickstart.md) and the [Command guide](docs/command_reference.md).

## What this skill helps with

- Check Reddit OAuth setup and token readiness.
- Review the pinned official Reddit API operation inventory.
- Read account, subreddit, user, moderation, wiki, widget, message, and multi endpoints from the pinned docs set.
- Prepare reviewed plans for Reddit writes before live apply.
- Save local plans, receipts, and run history for audit.

## What access this skill needs

- Reddit Data API approval.
- Reddit OAuth app values and scopes.
- A proper Reddit-style `User-Agent`.
- `--live` before any real Reddit network call.

## Install and first run

Install slug: `reddit`

Ask your agent to install the `reddit` skill from `Qwayk/safe-agent-skills`.

If new skills do not appear automatically, reopen the app or attach the skill to the current workspace if your host needs that.

If your host does not let the agent install skills directly, run:

```bash
npx skills add Qwayk/safe-agent-skills@reddit -g -y
```

Then try a safe first ask like:

```text
Check the Reddit setup, list the account and subreddit operations available, run one safe live read if access is ready, and stop before any writes.
```

## How this skill stays safe

- No live Reddit API call happens unless you pass `--live`.
- Reads need `--live`.
- Pinned API writes stay dry-run by default.
- API write apply needs `--live --apply`.
- Risky writes also need `--plan-in --yes`.
- Irreversible writes also need `--ack-irreversible`.
- When real before-state cannot be saved, approved writes need explicit no-snapshot approval and receipts must record the recovery limit.

## What it covers today

This skill covers the pinned official Reddit OAuth REST docs inventory from `https://www.reddit.com/dev/api/`, exposed as explicit CLI subcommands under `api`.

It includes account, subreddit, user, moderation, wiki, widget, message, and multi endpoints that are present in the pinned docs set.

## What happens before live changes

- The agent should show the dry-run plan first.
- You review the endpoint, account context, target community or record, and recovery limit.
- Risky writes reuse a reviewed plan through `--plan-in`.
- Irreversible writes need an explicit irreversible acknowledgement.
- If setup or before-state checks do not match, the tool refuses instead of sending a risky request.

## What proof it leaves behind

- Dry-run plans can be saved for review.
- Write-capable commands save local run folders under `.state/runs/`.
- Plans, receipts, and audit logs can be reviewed later.
- The docs, tests, pinned inventory, proof pack, and API coverage ledger live in this repo.

## Limits

- Reddit Data API access must be approved by Reddit.
- Live calls require a proper User-Agent and valid OAuth setup.
- The pinned API inventory can age, so refresh work should keep the local docs and coverage aligned.
- The tool does not create provider restore flows, rollback helpers, or before-state snapshots for current Reddit write families.

## Helpful docs

- [Browse all Reddit docs](docs/README.md)
- [Quickstart](docs/quickstart.md)
- [Command guide](docs/command_reference.md)
- [Authentication details](docs/authentication.md)
- [Proof and verification](docs/proof.md)
- [API coverage](docs/api_coverage.md)

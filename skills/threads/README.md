# Threads

**Capability:** Reads + careful changes

Threads is where profile identity, posts, replies, mentions, insights, search, locations, and publishing choices shape how an Instagram-connected public conversation appears.

This skill helps an agent check Threads account readiness, review owned and public posts, inspect replies and mentions, pull insights, research keywords or topic tags, and prepare publishing or moderation plans before anything changes.

Use it for questions like: "Which Threads profile does this token reach?", "What recent posts and replies need review?", "What insights are available?", "Can you search this topic tag?", or "Can you preview a post plan before publishing?"

Threads reads can run live after valid access is available. Write-capable commands start as dry-run plans, high-risk deletes need stronger approval, and token writes or Threads provider writes need explicit no-snapshot approval when no saved snapshot exists.

A good first ask is: "Check the Threads connection, show my profile, list my recent posts and replies, and stop before any writes."

## Start here first

- Want ideas for real Threads work? [What you can do with Threads](docs/use_cases.md)
- Need setup? [Connect your Threads account](docs/onboarding.md)
- Want the safety story first? [How this skill stays safe](docs/safety_model.md)

If you already want exact commands, jump straight to [Quickstart](docs/quickstart.md) and the [Command guide](docs/command_reference.md).

## What this skill helps with

- Check Threads auth, profile identity, and account readiness.
- Review owned posts, public posts, replies, mentions, and publishing limits.
- Pull user or media insights when the app already has the needed Threads permissions.
- Use keyword, topic-tag, location, and oEmbed lookups for content research and review.
- Plan careful post creation, repost, reply moderation, or delete actions before anything goes live.

## What access this skill needs

- Threads app settings in your local `.env`.
- A valid Threads access token.
- Your Threads user ID for many owned-account actions.
- Extra Threads permissions when you need discovery, mentions, insights, replies, keyword search, location tagging, or delete actions.

## Install and first run

Install slug: `threads`

Ask your agent to install the `threads` skill from `Qwayk/safe-agent-skills`.

If new skills do not appear automatically, reopen the app or attach the skill to the current workspace if your host needs that.

If your host does not let the agent install skills directly, run:

```bash
npx skills add Qwayk/safe-agent-skills@threads -g -y
```

Then try a safe first ask like:

```text
Check the Threads connection, show my profile, list my recent posts and replies, and stop before any writes.
```

## How this skill stays safe

- Read commands can run live right away.
- Write-capable commands start as dry-run plans first.
- Token exchange, token refresh, local token writes, and Threads provider writes need explicit no-snapshot approval when no saved snapshot exists.
- Irreversible deletes need stronger approval like `--yes --ack-irreversible`.
- Local run history can be reviewed with `runs list` and `runs show`.
- Docs, tests, proof files, and the API coverage ledger all live in this repo.

## What it covers today

This skill covers:

- auth checks, profile reads, owned and public post reads, replies, mentions, insights, search, locations, and oEmbed
- write planning for post creation, publish, repost, delete, reply moderation, and token-management flows
- local proof files and run history for review

## What happens before live changes

- The agent should show the dry-run plan first.
- You review the user ID, media ID, payload, and permission scope before apply.
- Reads can run live immediately.
- Normal write actions need `--apply`.
- Token management and Threads writes also need explicit no-snapshot approval when no saved snapshot exists.
- Irreversible delete actions also need `--yes --ack-irreversible`.

## What proof it leaves behind

- Dry-run plans can be saved with `--plan-out`.
- Local run history can be reviewed with `runs list` and `runs show`.
- The proof pack includes redacted example outputs and verified command shapes.
- The docs, tests, and API coverage ledger are all in this repo.

## Limits

- This runtime does not save provider-side before-state or restore points for Threads writes.
- Live Threads access still depends on the right app review state and permissions.
- Web Intents and webhook dashboard setup stay docs-only, not CLI commands.
- Some supported Threads surfaces are still live-unverified in this repo because no approved production account is stored here.

## Helpful docs

- [Browse all Threads docs](docs/README.md)
- [Quickstart](docs/quickstart.md)
- [Command guide](docs/command_reference.md)
- [Authentication details](docs/authentication.md)
- [Jobs and batch work](docs/jobs_and_batches.md)
- [Proof and verification](docs/proof.md)
- [API coverage](docs/api_coverage.md)

# Instagram

**Capability:** Reads + careful changes

Instagram is where professional-account media, comments, mentions, messages, stories, live media, and insights become public content and customer conversations.

This skill helps an agent confirm which Instagram account a token reaches, review media and comments, check insights and publishing limits, and prepare publish, moderation, mention, or message plans before anything goes live.

Use it for questions like: "Which account is connected?", "What recent media and comments need review?", "Are we near the publish quota?", "Can you prepare a Reel or carousel plan?", or "Can you draft this reply before sending it?"

Instagram reads can run live after valid access is available. Publish, moderation, mention, message, and token actions start as dry-run plans, and live applies need explicit no-snapshot approval when the tool cannot save useful before-state first.

A good first ask is: "Check the Instagram skill is connected, show which account this token reaches, and list my recent media, comments, and safe review options."

## Start here first

- Want ideas for real Instagram work? [What you can do with Instagram](docs/use_cases.md)
- Need setup? [Connect your Instagram access](docs/onboarding.md)
- Want the safety story first? [How this skill stays safe](docs/safety_model.md)

If you already want exact commands, jump straight to [Quickstart](docs/quickstart.md) and the [Command guide](docs/command_reference.md).

## What this skill helps with

- Check which Instagram professional account the current token reaches.
- Review media, stories, live media, tags, comments, mentions, and messages.
- Pull account and media insights.
- Plan careful publish flows for images, reels, and carousels.
- Plan comment, mention, and message actions before anything goes live.
- Check publish quota limits and container status during content work.

## What access this skill needs

- Local Instagram app settings in `.env`.
- A valid Instagram access token or the Instagram Login auth flow.
- An Instagram professional account that works with the Instagram Login product.
- Your Instagram user ID for many account, media, publish, and message requests.
- Extra scopes for publish, comments, messages, or insights when you need those families.

## Install and first run

Install slug: `instagram`

Ask your agent to install the `instagram` skill from `Qwayk/safe-agent-skills`.

If new skills do not appear automatically, reopen the app or attach the skill to the current workspace if your host needs that.

If your host does not let the agent install skills directly, run:

```bash
npx skills add Qwayk/safe-agent-skills@instagram -g -y
```

Then try a safe first ask like:

```text
Check the Instagram connection, show which account this token reaches, list my recent media and comments, and stop before any live changes.
```

## How this skill stays safe

- Read commands can run live right away.
- Write-capable actions start as dry-run plans first.
- Higher-risk actions can require extra confirmation flags like `--yes` or `--ack-irreversible`.
- When no saved before-state exists, live applies also need `--ack-no-snapshot`.
- Token writes, plans, receipts, and logs stay redacted and local.
- Local run history can show what changed after the work runs.
- The docs, tests, coverage notes, and source code are all here in one place.

## What it covers today

This skill covers:

- Instagram Login account lookup and token-state helpers
- users, media, comments, mentions, insights, messages, tags, stories, and live media
- publish-container creation, publish, and publish-limit review
- local run history and proof files for review

## What happens before live changes

- The agent should show the dry-run plan first.
- You review the account, media, comment, message, or publish target.
- Safe reads can run immediately.
- Write-capable actions need `--apply`.
- Higher-risk actions can also require `--yes`.
- Irreversible actions like comment delete also need `--ack-irreversible`.
- Writes without saved before-state also need `--ack-no-snapshot`.

## What proof it leaves behind

- Dry-run plans can be saved with `--plan-out`.
- Approved applies can save receipts with `--receipt-out`.
- Local run history can be reviewed with `runs list` and `runs show`.
- Plans, refusals, logs, and summaries stay under local run history when artifacts are enabled.
- The docs, tests, examples, and API coverage ledger are all in this repo.

## Limits

- This skill is for Instagram professional accounts with Instagram Login, not every Meta or Facebook-login-only Instagram surface.
- Business Discovery, Hashtag Search, and Threads account edges stay outside this tool by product choice.
- Many live writes still do not have saved before-state or a built-in undo path.
- You still need valid Instagram app setup, scopes, and token access for real account work.

## Helpful docs

- [Browse all Instagram docs](docs/README.md)
- [Quickstart](docs/quickstart.md)
- [Command guide](docs/command_reference.md)
- [Proof and verification](docs/proof.md)
- [API coverage](docs/api_coverage.md)

# Hacker News

**Capability:** Read-only

Use this skill when you want an agent to read public Hacker News data safely: check story lists, fetch one story or comment item by ID, inspect a public user profile, and see which items or profiles changed recently.

You can hand your agent jobs like trend scouting, "what is being discussed now" summaries, story research for a topic, public user lookups, job-story checks, and repeatable snapshots for a handoff or report.

This skill is safe by design. It uses the public Hacker News API, needs no account, and cannot post, vote, comment, hide, delete, or change anything. The main risk is reading too much into story IDs alone, so ask the agent to fetch the actual items before it summarizes patterns or makes decisions.

A good first ask is: "Check the Hacker News skill is connected, show me the current top stories, fetch the first story item, and stop after the read-only results."

## Start here first

- Want ideas for real Hacker News work? [What you can do with Hacker News](docs/use_cases.md)
- Need the shortest setup path? [Use Hacker News with no account](docs/onboarding.md)
- Want the safety story first? [How this skill stays safe](docs/safety_model.md)

If you already want exact commands, jump straight to [Quickstart](docs/quickstart.md) and the [Command guide](docs/command_reference.md).

## What this skill helps with

- Check the current top, new, best, Ask HN, Show HN, or job story IDs.
- Fetch one public item by ID so an agent can explain its title, URL, score, author, time, text, or comment IDs.
- Fetch one public user profile by username to review karma, account age, and submitted item IDs.
- Watch the latest changed item and profile IDs from the public updates feed.
- Build a repeatable public snapshot without scraping the Hacker News website.

## What access this skill needs

- Internet access to the public Hacker News API.
- No Hacker News account.
- No API key, bearer token, OAuth login, or browser session.
- Optional local `.env` setup only if you want to pin the public API root or timeout.

## Install and first run

Install slug: `hacker-news`

Ask your agent to install the `hacker-news` skill from `Qwayk/safe-agent-skills`.

If new skills do not appear automatically, reopen the app or attach the skill to the current workspace if your host needs that.

If your host does not let the agent install skills directly, run:

```bash
npx skills add Qwayk/safe-agent-skills@hacker-news -g -y
```

Then try a safe first ask like:

```text
Check the Hacker News skill is connected, show me the current top stories, fetch the first story item, and stop after the read-only results.
```

## How this skill stays safe

- It is read-only to Hacker News by design.
- It only uses public Hacker News API reads.
- It does not sign in, ask for secrets, or store account credentials.
- It has no command that can post, vote, comment, edit, delete, or hide anything.
- In JSON mode, each command returns one clear result object that an agent can parse.
- The docs, tests, proof pack, and API coverage ledger all live in this repo so you can inspect what the agent is using.

## What it covers today

This skill covers the full documented Hacker News v0 public HTTP read surface:

- one item by ID
- one public user by username
- top, new, best, Ask HN, Show HN, and job story ID lists
- the current max item ID
- recently changed item and profile IDs

## What happens before live changes

This skill does not make live changes in Hacker News. There is no write or account-action path.

Before a live read, the agent should run the connection check, use one of the named read commands, and summarize only what the public API returned. The only local change this skill can make is creating a placeholder `.env` file during onboarding.

## What proof it leaves behind

- Commands return machine-readable JSON you can save or review.
- Read results include the public API endpoint used.
- Optional audit logs record command events without secrets.
- The proof pack includes smoke commands and committed examples for the main result shapes.
- The API coverage page maps every supported Hacker News endpoint to the matching command and test.

## Limits

- Public Hacker News data only.
- No posting, voting, commenting, hiding, deleting, moderation, or account actions.
- No full-text search endpoint.
- Story-list commands return item IDs first; fetch item details before summarizing a story.
- Comment trees are returned as child item IDs, not automatically expanded into a full discussion.
- Public data can change quickly, so saved snapshots may age fast.

## Helpful docs

- [Browse all Hacker News docs](docs/README.md)
- [Quickstart](docs/quickstart.md)
- [Command guide](docs/command_reference.md)
- [Authentication details](docs/authentication.md)
- [Configuration](docs/configuration.md)
- [Troubleshooting](docs/troubleshooting.md)
- [Proof and verification](docs/proof.md)
- [API coverage](docs/api_coverage.md)

# Hacker News

**Capability:** Read-only

Hacker News is useful when you want a quick read on what people in tech are talking about right now. This skill lets an agent pull the public story lists, open the real story or comment items behind those lists, check public user profiles, and watch recent item or profile changes without scraping the website.

Use it for questions like: "What is getting attention today?", "Which Show HN posts look relevant to developer tools?", "What jobs are showing up?", or "What does this Hacker News thread actually include?"

No account is needed. The tool cannot post, vote, comment, hide, delete, or change anything. The useful limit to remember is that Hacker News story lists start as IDs, so ask the agent to fetch the actual items before it explains trends.

A good first ask is: "Show me the current top Hacker News stories, fetch the first five items, and tell me the main topics people are discussing. Do not summarize from IDs alone."

## Start here first

- Want ideas for real Hacker News work? [What you can do with Hacker News](docs/use_cases.md)
- Need the shortest setup path? [Use Hacker News with no account](docs/onboarding.md)
- Want the safety story first? [How this skill stays safe](docs/safety_model.md)

If you already want exact commands, jump straight to [Quickstart](docs/quickstart.md) and the [Command guide](docs/command_reference.md).

## What this skill helps with

- See what is currently on top, new, best, Ask HN, Show HN, or jobs.
- Open a story, comment, poll, or job item and get the title, link, score, author, text, time, and comment IDs.
- Check a public user profile by username.
- Watch which public items and profiles changed recently.
- Save a small snapshot for research, reporting, or a handoff.

## What access this skill needs

- A normal internet connection.
- No Hacker News account.
- No API key, login, browser session, or private access.
- Optional local settings only if you want to change the public API root or timeout.

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
Show me the current top Hacker News stories, fetch the first five items, and tell me the main topics people are discussing. Do not summarize from IDs alone.
```

## How this skill stays safe

Most of the safety story is simple: this tool has nothing that can change Hacker News. It reads the official public API in a predictable way, so an agent does not need to scrape pages or invent hidden URLs.

- It does not sign in or ask for secrets.
- It cannot post, vote, comment, edit, delete, or hide anything.
- It uses named read commands for the public Hacker News API.
- In JSON mode, each command returns one clear result object.
- The docs, tests, proof pack, and API coverage page all live in this repo so you can inspect what the agent is using.

## What it covers today

This skill covers the full documented Hacker News v0 public HTTP read surface:

- one item by ID
- one public user by username
- top, new, best, Ask HN, Show HN, and job story ID lists
- the current max item ID
- recently changed item and profile IDs

## What happens before live changes

There are no live changes to approve. This skill has no write or account-action path.

Before a read, the agent can run the connection check, use one of the named read commands, and summarize only what the public API returned. The only local change this skill can make is creating a placeholder `.env` file during onboarding.

## What proof it leaves behind

- Commands return JSON you can save or review.
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

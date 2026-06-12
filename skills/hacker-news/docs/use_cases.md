# What you can do with Hacker News

Hacker News work usually starts with a simple question: what is getting attention right now, what does one thread actually include, or which public user or item changed recently?
If you need setup first, start with [Use Hacker News with no account](onboarding.md). If you need exact commands, use [Quickstart](quickstart.md) and [Command reference](command_reference.md).

The useful part is that the agent can pull the official public API data instead of scraping the website or summarizing from story IDs alone.

## Good jobs to give the agent

- Check the current top, new, best, Ask HN, Show HN, or job story IDs.
- Fetch one story, comment, poll, or job item by ID and explain what the public fields mean.
- Fetch one public user profile to review karma, account age, and submitted item IDs.
- Watch the latest changed items and profiles.
- Create a small public snapshot for a report, trend note, or handoff.

## What the agent should remember

- The tool is read-only.
- It returns stable JSON that agents can parse.
- It should fetch item details before it explains trends.
- A list of IDs alone is not enough to understand the discussion.

## Real example

You can ask:

"Show me the top story IDs, fetch the first five items, and tell me which ones look relevant to AI tooling."

The useful part is the second step. Fetching the items gives the agent the titles, URLs, authors, scores, and comment IDs it needs before it summarizes anything.

## Honest limits

- This skill reads public Hacker News data only.
- It does not search all Hacker News text.
- It does not expand a full comment tree automatically.
- It cannot post, vote, comment, hide, delete, moderate, or change an account.

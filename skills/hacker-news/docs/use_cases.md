# What you can do with Hacker News

Use this page when you want ideas for real Hacker News jobs to hand to your agent.
If you need setup first, start with [Use Hacker News with no account](onboarding.md). If you need exact commands, use [Quickstart](quickstart.md) and [Command reference](command_reference.md).

This skill helps when you want public Hacker News data in a clean, repeatable form instead of asking an agent to scrape pages or guess URLs.

## Common jobs

- Check the current top, new, best, Ask HN, Show HN, or job story IDs.
- Fetch one story, comment, poll, or job item by ID and explain what the public fields mean.
- Fetch one public user profile to review karma, account age, and submitted item IDs.
- Watch the latest changed items and profiles.
- Create a small public snapshot for a report, trend note, or handoff.

## Where this skill is especially useful

Typical no-code automation is fine when you already have a simple page to watch.

This skill is better when you want an agent to work from the official public API:

- it avoids fragile page scraping
- it returns stable JSON that agents can parse
- it keeps the work read-only
- it reminds the agent to fetch item details before summarizing story lists

## Real example

You can ask:

"Show me the top story IDs, fetch the first five items, and tell me which ones look relevant to AI tooling."

The useful part is the second step. A list of IDs alone is not enough to understand the discussion. Fetching the items gives the agent the titles, URLs, authors, scores, and comment IDs it needs before it summarizes anything.

## Honest limits

- This skill reads public Hacker News data only.
- It does not search all Hacker News text.
- It does not expand a full comment tree automatically.
- It cannot post, vote, comment, hide, delete, moderate, or change an account.

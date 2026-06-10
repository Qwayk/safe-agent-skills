# Use cases

Use this page when you want ideas for real Hacker News jobs to hand to your agent.
If you need setup first, start with [Connect your account](onboarding.md). If you need exact commands, use [Quickstart](quickstart.md) and [Command reference](command_reference.md).

- Check the current top, new, best, Ask HN, Show HN, or job story ids without scraping the website.
- Fetch one item by id so an AI agent can explain the fields, title, score, url, or comment tree ids.
- Fetch one public user profile by id to review karma, created date, and submitted ids.
- Poll the latest `updates` feed to see which item ids and user ids changed recently.

Why this beats scraping:
- It uses the official public API instead of page HTML.
- The output is deterministic JSON.
- It is read-only and safe for automation.
- The command surface is explicit, so an agent does not need to guess hidden URLs.

Why this beats typical no-code automation:
- No-code tools often start from fragile page scraping or generic webhooks.
- This tool starts from the official API with fixed JSON shapes and named commands.
- An agent can move from “find ids” to “inspect exact items” without guessing hidden request details.

Discovery example:
- “Show me the top story ids, then fetch the first five items and tell me which ones look relevant to AI tooling.”

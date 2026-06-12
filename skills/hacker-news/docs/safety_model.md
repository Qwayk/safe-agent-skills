# Safety model

Use this page when you want to know why this Hacker News skill is safe for public read-only work.

This tool is intentionally read-only. It can fetch public Hacker News data, but it cannot change Hacker News.

## What keeps it safe

- No authentication secrets are required.
- No `--apply`, `--yes`, or write workflow exists.
- The tool only performs `GET` requests to the public Hacker News API.
- In `--output json` mode, every command prints exactly one JSON object.
- Missing items or users come back as clear JSON errors instead of silent `null` payloads.

## What this means in plain English

- The tool can fetch public Hacker News data.
- The tool cannot post, vote, comment, edit, hide, delete, or moderate anything.
- The tool cannot leak an API key because there is no API key in this workflow.
- The main user mistake is making a big conclusion from a story-list result before fetching the actual items.

## Safe first check

Ask:

"Check the Hacker News skill is connected, show me the current top stories, fetch the first story item, and stop after the read-only results."

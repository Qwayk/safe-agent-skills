# Use Hacker News with no account

Hacker News uses a public API. You do not need an account, API key, OAuth file, or token to fetch story lists, items, users, or updates.

No secrets are needed for the first run. If the tool creates a local `.env` file, treat it as local setup only; it should not contain a private service token.

Start by fetching real items, not only story IDs, so the agent summarizes the actual discussion.

## First setup

1. Install the tool in a local virtual environment.
2. Run `hacker-news-api-tool --output json onboarding` once.
3. Run `hacker-news-api-tool --output json auth check` to confirm the public API is reachable.

## What the onboarding command does

- If `.env` is missing, it can create one from `.env.example`.
- It uses the official public API root by default.
- It never asks for secrets because none are needed.

## What to ask your AI agent

- "Check that the Hacker News API is reachable."
- "Show me the top story IDs, fetch the first story item, and summarize it."
- "Get item 8863 and explain the fields."
- "Show me the latest changed items and profiles."

## What to avoid

- Do not ask it to post, vote, comment, delete, hide, or change anything. The skill cannot do that.
- Do not treat story IDs alone as a full trend summary. Ask the agent to fetch item details first.
- Do not paste account secrets into chat. This skill does not need any.

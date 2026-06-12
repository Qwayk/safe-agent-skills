# Use Hacker News with no account

This tool uses the public Hacker News API and does not need an account or API key.

You do not need to be technical to use it through an agent. The important thing to know is simple: the skill can read public Hacker News data, but it cannot change anything on Hacker News.

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

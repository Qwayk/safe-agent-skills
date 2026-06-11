# Onboarding

This tool uses the public Hacker News API and does not need an account or API key.

## Setup

1. Install the tool in a local virtual environment.
2. Run `hacker-news-api-tool --output json onboarding` once.
3. Run `hacker-news-api-tool --output json auth check` to confirm the public API is reachable.

## What the onboarding command does

- If `.env` is missing, it can create one from `.env.example`.
- It uses the official public API root by default.
- It never asks for secrets because none are needed.

## What to ask your AI agent

- “Check that the Hacker News API is reachable.”
- “Get item 8863 and summarize it.”
- “Show me the top story ids.”
- “Show me the latest changed items and profiles.”

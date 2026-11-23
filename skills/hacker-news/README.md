# Hacker News

Read public Hacker News stories, comments and profiles with Codex. You can open an item by ID, look up a user, or see what is on the top, new, best, Ask HN, Show HN and jobs lists. You need an internet connection. The reads use the public API and work without an account or API key.

## Install the skill

Run this in your terminal.

```bash
npx skills add Qwayk/safe-agent-skills@hacker-news-api-safe-cli -g -y
```

If the skill does not appear right away, reopen Codex. [Install the CLI and fetch your first story](docs/quickstart.md).

A good first request is “Fetch the first five top Hacker News stories and tell me what they’re about.” The list gives you IDs. The agent opens the items to get the titles, links and other details.

## More help

- [Example requests](docs/use_cases.md)
- [Commands, settings and fixes](docs/command_reference.md)
- [What the tool can read](docs/safety_model.md)
- [All docs](docs/README.md)

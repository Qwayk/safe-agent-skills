---
name: hacker-news-api-safe-cli
description: Use the Qwayk CLI to read public Hacker News stories, comments, profiles and recent updates.
---

Use `hacker-news-api-tool --output json` with the named commands in the [command guide](docs/command_reference.md). If the CLI is missing, follow the [quickstart](docs/quickstart.md).

- Read public data with the documented CLI. Use the default API address unless the user asks for a different compatible address.
- Start with the requested read. For one story, run `hacker-news-api-tool --output json items get --id 8863` with the ID you need. Use `auth check` if you need to check the connection.
- If you get a list of IDs, fetch the relevant items before you explain what the stories say. Base your answer on the items you opened.
- For a request to post, vote, comment or change an account, explain that this tool reads public data. Reads need no login or secrets.

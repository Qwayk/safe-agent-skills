---
name: amazon-creators
description: "Find Amazon products, compare variations, and look up categories with amazon-creators-api-tool."
---

# Amazon Creators

Use this skill to search Amazon, look up item details and variations, or describe categories. Start with [setup](docs/onboarding.md) when the account is new. Follow [the command guide](docs/command_reference.md) and keep the selected settings file on each command.

Preview any catalog request before contacting Amazon. Show the marketplace, tracking tag, search terms or item IDs, and requested fields. Wait for approval, then send the read with `--apply`. Use `--plan-in` to check that a saved preview still matches. Report products and links, the total when Amazon returns one, and any errors.

Use `onboarding` to show the settings. Create a new settings file and fetch a token only with explicit approval. Keep credentials and tokens out of chat and logs. A saved token can pass the local check even when Amazon denies catalog access. Say which step worked.

Use the returned product information to compare formats. Check Amazon or Audible separately before claiming that a title has no audiobook.

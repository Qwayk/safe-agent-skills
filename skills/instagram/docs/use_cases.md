# Use cases

Use this page when you want ideas for real Instagram jobs to hand to your agent.
If you need setup first, start with [Connect your account](onboarding.md). If you need exact commands, use [Quickstart](quickstart.md) and [Command reference](command_reference.md).

## Common read tasks

- check which Instagram account the current token reaches
- list recent media, stories, tags, live media, and comments
- pull account or media insights
- inspect mentions before replying
- check the remaining publishing quota

## Common write tasks

- preview creating a publish container for an image, reel, or carousel
- preview publishing a prepared container after review
- preview turning comments on or off for a media item
- preview replies to comments or mentions
- preview hiding or deleting a bad comment
- preview sending a message or private reply

## Good requests to give your agent

- "Check the Instagram account and list my latest media."
- "Prepare a dry run for publishing this image with this caption."
- "Show recent comments and suggest which ones to hide."
- "Pull media insights for these post IDs."
- "Reply to this mention, but show me the plan first."

## What makes it safe

- reads and writes use explicit named commands
- writes create dry-run plans first; when no saved snapshot is available, apply needs explicit no-snapshot approval and a receipt that records the recovery limit
- risky writes need extra approval flags
- write runs save local plans and receipts under `.state/runs/`

# What you can do with YouTube

YouTube work usually starts with a channel, video, playlist, caption, or upload question that needs official API data before anyone changes the channel.
If you need setup first, start with [Connect your YouTube account](onboarding.md). If you need exact commands, use [Quickstart](quickstart.md) and [Command reference](command_reference.md).

## Good jobs to give the agent

### Channel research and reporting

- “Resolve this channel from the handle, then show the latest uploads and total public video count.”
- “Search this channel for videos about a topic and summarize what needs updating.”
- “Export the public videos returned by this channel's uploads playlist into a local dataset I can review.”

### Publishing and metadata work

- “Plan a private video upload with this title, description, and file path, then stop for approval.”
- “Preview title, tag, or description updates from a spreadsheet before anything changes.”
- “Check which videos are missing a clear call to action or a needed link.”

### Playlists and organization

- “Plan a new playlist and the first set of videos to add.”
- “Audit playlists for duplicates, missing videos, or weak ordering.”
- “Compare channel sections or playlist naming so we can clean them up later.”

### Captions and localization

- “Download caption tracks I have access to into local files for translation.”
- “Plan caption uploads or replacements, then show me the exact approval gate before any write.”
- “Find videos that are missing captions or language coverage.”

### Comments and moderation

- “Pull the recent comment threads for these videos and flag likely moderation issues.”
- “Plan a reply or moderation action, but stop before posting anything.”

## What you should expect from the agent

When you ask for a change, the agent should:

1. Start with a safe read or a dry-run plan.
2. Tell you clearly whether the action is just a local export, a live read, or a real YouTube write.
3. Ask for explicit approval before uploads, non-GET writes, or other higher-risk changes.
4. Finish with a receipt, a refusal that proves nothing changed, or saved local export files.

If the agent cannot safely identify the channel, video, playlist, file path, or permission it needs, it should stop and ask you for the missing detail instead of guessing.

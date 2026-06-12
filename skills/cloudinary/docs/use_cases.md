# Use cases

Use this page when you want practical Cloudinary jobs to hand to your agent.
If you need setup first, start with [Connect your account](onboarding.md). If you need exact commands, use [Quickstart](quickstart.md) and [Command reference](command_reference.md).

Cloudinary work usually touches media people actually see, so the safest path is to inspect assets, folders, metadata, and account settings before applying changes.

## Good jobs to give the agent

- "Check whether my product and account credentials are ready."
- "Look up this asset and explain its tags, metadata, and delivery details."
- "List folders, upload presets, metadata fields, streaming profiles, or player profiles."
- "Prepare a plan to upload, rename, tag, restore, or update structured metadata."
- "Run this Analyze API job and save the result."
- "Check product environments, users, user groups, roles, and policies if my plan allows it."
- "Save sensitive or binary results to a local file instead of printing them in chat."

## What the agent should show you

When a change is requested, the agent should:

1. Show the dry-run plan first.
2. Name the asset, folder, product environment, account resource, or output file involved.
3. Keep sensitive or binary output in files.
4. Ask for stronger approval before deletes, access-key changes, or other risky work.
5. Say plainly when a write has no saved snapshot and needs no-snapshot approval.

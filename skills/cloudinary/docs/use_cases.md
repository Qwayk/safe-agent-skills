# Use cases

Use this page when you want ideas for real Cloudinary jobs to hand to your agent.
If you need setup first, start with [Connect your account](onboarding.md). If you need exact commands, use [Quickstart](quickstart.md) and [Command reference](command_reference.md).

## Common jobs

- Check whether product and account credentials are ready before a bigger task.
- Look up asset details, folders, tags, metadata fields, upload presets, streaming profiles, or player profiles.
- Prepare plans to upload files, rename assets, change tags, change context, or update structured metadata.
- Run Analyze API jobs that are exposed as read-like REST calls.
- Inspect backed-up assets through `upload download-backup`; restore writes currently plan and then require explicit no-snapshot approval before Cloudinary HTTP when no saved snapshot is available.
- Manage account-level product environments, users, user groups, roles, and custom policies when your Cloudinary plan allows it.
- Export sensitive or binary results to local files instead of printing them to the screen.

## Why it is safer than ad-hoc API calls

- Every shipped operation is allowlisted in the local inventory.
- Writes are preview-first by default.
- Current write apply attempts require explicit no-snapshot approval before Cloudinary HTTP when no saved snapshot is available.
- Deletes and access-key changes need extra confirmation.
- Sensitive results are forced to files.
- Each run can leave a local proof trail under `.state/runs/`.

## Good prompts for an agent

- "Check my Cloudinary product and account setup and tell me what is still missing."
- "Show me the shipped Upload API commands and explain which one uploads a signed file."
- "Get asset details for public ID sample in my image/upload library."
- "Plan a restore for this sample asset and confirm the apply attempt will require explicit no-snapshot approval before Cloudinary HTTP."
- "Plan a new product environment in Cloudinary provisioning, but do not apply it."
- "Run the public Cedar policy validator with this JSON body and save the result."

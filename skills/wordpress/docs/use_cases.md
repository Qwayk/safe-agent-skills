# Use cases

Use this page when you want ideas for real WordPress jobs to hand to your agent.
If you need setup first, start with [Connect your account](onboarding.md). If you need exact commands, use [Quickstart](quickstart.md) and [Command reference](command_reference.md).

## Why this is powerful (vs typical no‑code automation)

Most no‑code tools are great for *single events* (“when X happens, do Y”). This tool is built for safe, repeatable work on **large existing content libraries**, including:

- Bulk changes with a preview-first workflow (dry-run → explicit apply → verification)
- Deterministic transformations (the same input produces the same output)
- Clear audit artifacts (plans/receipts/JSON logs) so you can review what happened

## Common use cases (examples)

### Content discovery and reporting

- “Find all posts/pages mentioning a keyword and give me a report with links, status, and last modified date.”
- “Search the site for a keyword and show me what WordPress thinks matches (useful when you don’t know the post type).”
- “Tell me what post types, post statuses, and taxonomies exist on this site (so I can plan a migration safely).”
- “List the categories and tags on the site, and help me find the right one by name or slug.”
- “List comments for a specific post so I can audit what needs to be migrated.”
- “Show me which posts have featured images missing.”
- “List all images used in a post (and the matching Media Library items when possible).”
- “Find media items by keyword so I can audit alt text/captions.”

### Content hygiene (media metadata)

- “Update the Media Library caption/alt text/title for these 200 images from a spreadsheet.”
- “Standardize image captions to include a consistent license/credit format.”
- “Plan a bulk download of media files from a spreadsheet/list (including filenames/paths), then download only after I approve.”
- “Set the categories and tags on a specific post/page, but show me the preview first and only apply after I approve.”

### Safe edits inside post content

- “Update visible image captions inside posts (only where it’s safe and deterministic).”
- “Give me a preview diff for the caption changes before applying them.”

### Publishing and workflow controls (careful)

- “Change a post from draft to publish only if it’s currently draft, and verify the result.”

### Migration support

- “Generate a migration tracking CSV from WordPress export XML, so I can track progress across hundreds of posts.”

## What you’ll see from the agent (trust + safety)

When you ask for a change, the agent should:

1) Show a dry-run preview of what would change.
2) Apply only after explicit confirmation.
3) Verify after apply (read-back or idempotence).
4) Provide a short receipt: what changed, what was verified, and where proof artifacts were saved.

## What’s intentionally out of scope

This tool is not meant to manage core site administration (plugins/themes, templates/global styles, menus/navigation, and other high-risk operational controls).

See `docs/api_coverage.md` for the definitive endpoint coverage and the “gaps” list.

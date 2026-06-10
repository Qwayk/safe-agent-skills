# Use cases

Use this page when you want ideas for real Unsplash jobs to hand to your agent.
If you need setup first, start with [Connect your account](onboarding.md). If you need exact commands, use [Quickstart](quickstart.md) and [Command reference](command_reference.md).

## Why this is powerful (vs typical no‑code automation)

No‑code tools are great for “when X happens, do Y”. This tool is built for safe image research and repeatable workflows:

- High-volume discovery (search, topics, collections)
- Consistent selection (shortlists with rationale)
- Compliance-friendly download planning (tracking requires explicit no-snapshot approval when no saved snapshot is available)
- Refusal proof you can keep for auditing what did and did not happen

## Common use cases (examples)

### Image discovery

- “Find 50 photos for ‘X’ and shortlist the best 10 with links and notes.”
- “Find a consistent set: one hero image plus 3 supporting images (same style).”
- “Explore a topic/collection and propose a shortlist.”

### Downloads (explicit approval)

- “Plan downloading these approved photo IDs into a local folder (no download until I approve).”
- “Try apply only after I approve, then show the explicit no-snapshot approval.”

## What you’ll see from the agent (trust + safety)

For downloads, the agent should:

1) Show a dry-run plan (what would be downloaded and where).
2) Try apply only after explicit confirmation.
3) Confirm `refused=true`, `before_state.status=no_snapshot_available`, and no tracking endpoint or local file write happened.

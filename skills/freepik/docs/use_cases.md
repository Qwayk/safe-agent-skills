# Use cases

Use this page when you want ideas for real Freepik jobs to hand to your agent.
If you need setup first, start with [Connect your account](onboarding.md). If you need exact commands, use [Quickstart](quickstart.md) and [Command reference](command_reference.md).

## Why this is powerful (vs typical no‑code automation)

No‑code tools are great for one-off triggers. This tool is built for safe, repeatable work when you need:

- High-volume asset discovery (hundreds/thousands of search results)
- Preview-first selection (you approve IDs before any paid download/license)
- A future durable license ledger (inventory CSV) with proof URLs and checksums once licensed apply is safely enabled

## Common use cases (examples)

### Asset discovery (read-only)

- “Search for recipe photos for ‘X’ and give me 50 options with preview links.”
- “Use `search photos --shortlist` to give me a compact list of candidates, then write a jobs CSV for the finalists.”
- “Filter to photos only, exclude AI (best-effort), and summarize what you found.”
- “Find visually similar assets to this approved image ID (to keep a consistent style).”

### Preview before licensing

- “Download low-risk previews for a shortlist so I can choose final IDs.”
- “Create a plan for downloading these 20 approved IDs, and show me the expected filenames and where they will be saved.”
- “Given an approved image ID, export a ‘same shoot’ pack (`resource shoot-pack`) and generate a jobs CSV for later batch downloads.”

### Licensed download planning + refusal proof (explicit approval)

- “Prepare download plans only for the IDs I approved, then report the explicit no-snapshot approval.”
- “Refuse downloads unless the resource detail clearly indicates non‑AI (fail closed).”
- “Generate a ledger export so I can audit what was licensed and when.”

## What you’ll see from the agent (trust + safety)

When you ask for downloads, the agent should:

1) Show a dry-run preview (what would be downloaded and where).
2) Try apply only after explicit confirmation (and extra confirmation for batch jobs).
3) Report `refused=true` and `before_state.status=no_snapshot_available`.
4) Confirm no file or inventory row was written.

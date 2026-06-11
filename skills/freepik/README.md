# Freepik

**Capability:** Reads + careful changes

Use this skill when you want your agent to search Freepik, build shortlists, check resource details, and handle licensed downloads without guessing from raw docs.

You can hand it jobs like finding non-AI food photos, previewing finalists, checking same-shoot alternatives, preparing a careful download plan, or finishing approved downloads into a local folder and inventory CSV.

Read work stays simple. Licensed downloads slow down on purpose: the tool should preview first, show the dry-run plan, and ask for explicit no-snapshot approval before a live download because Freepik can create a download or license record and this tool does not save a reliable before-state snapshot for that write.

A good first ask is: "Find 20 non-AI pasta photos, show me the best previews, and prepare a careful download plan for the two I choose."

## Start here first

- Want ideas for real Freepik work? [What you can do with Freepik](docs/use_cases.md)
- Need setup? [Connect your Freepik account](docs/onboarding.md)
- Want the safety story first? [How this skill stays safe](docs/safety_model.md)

If you already want exact commands, jump straight to [Quickstart](docs/quickstart.md) and the [Command guide](docs/command_reference.md).

## What this skill helps with

- Search images or photos and build shortlists before you buy anything.
- Preview selected assets before any licensed download.
- Check resource details, related assets, and same-shoot candidates.
- Generate local jobs CSV files for later batch download work.
- Plan licensed downloads into your chosen downloads folder and inventory CSV.
- Complete approved single or batch downloads after review.

## What access this skill needs

- A Freepik API key.
- A local downloads folder and inventory CSV path if you want saved files and a license ledger.
- Enough Freepik account access for the search or download volume you want to run.

## Install and first run

Install slug: `freepik`

Ask your agent to install the `freepik` skill from `Qwayk/safe-agent-skills`.

If new skills do not appear automatically, reopen the app or attach the skill to the current workspace if your host needs that.

If your host does not let the agent install skills directly, run:

```bash
npx skills add Qwayk/safe-agent-skills@freepik -g -y
```

Then try a safe first ask like:

```text
Connect the Freepik skill to my account, find 15 non-AI food photos for mushroom pasta, and show me the best previews before any download.
```

## How this skill stays safe

- Search, resource checks, and preview work do not create licensed download records.
- Licensed downloads start as dry-run plans.
- Apply needs explicit no-snapshot approval with `--ack-no-snapshot` because this tool does not save a reliable before-state snapshot for Freepik licensed downloads.
- Downloads fail closed if the detail response does not clearly show `is_ai_generated=false` and `has_prompt=false`.
- Dedupe and overwrite guards refuse re-downloading the same asset or overwriting an existing file unless you force it.
- Approved applies record the saved file, file hash, inventory row, and recovery contract so you can review what happened after the run.

## What it covers today

This skill covers:

- search images and photos
- resource get, related, and shoot-pack
- preview
- download dry-runs
- approved single downloads and batch download rows with explicit no-snapshot approval
- local jobs CSV generation for later batch work

## What happens before live changes

- The agent should search and preview first.
- You approve the exact resource ID, destination, and format.
- The tool shows the dry-run plan before any licensed download.
- Single live download needs `--apply`.
- Batch live download needs `--apply --yes`.
- Licensed download apply also needs `--ack-no-snapshot`.

## What proof it leaves behind

- Dry-run output includes the download plan, the no-snapshot before-state contract, and the after-apply verification plan.
- Approved apply output includes the downloaded row, the no-snapshot approval record, verification details, and the irreversible recovery contract.
- The inventory CSV records the file path, hash, license URL, and other saved metadata for approved downloads.
- The docs, tests, and example outputs all live in this repo.

## Limits

- Licensed downloads do not have an automatic rollback path in this CLI.
- Freepik AI flags are fail-closed for downloads, so missing or unclear flags cause refusal.
- Preview saves and jobs CSV files are local-only helper writes and must be cleaned up manually if you no longer need them.
- You still need valid Freepik API access for real account work.

## Helpful docs

- [Browse all Freepik docs](docs/README.md)
- [Quickstart](docs/quickstart.md)
- [Command guide](docs/command_reference.md)
- [Proof pack](docs/proof.md)
- [API coverage](docs/api_coverage.md)
- [Recipe workflow](docs/recipe_workflow_recipes.md)

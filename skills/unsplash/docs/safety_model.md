# How this skill stays safe

This skill is careful by default.

Most Unsplash work here is read-only research. The riskier path is `photos download`, because a real apply can trigger Unsplash download tracking and can also write a file to your machine.

## What stays simple

- photo, collection, topic, user, search, and stats reads
- export planning
- dry-run download plans

Those steps do not trigger download tracking or write a local file unless you move into apply.

## What needs extra care

This tool has two kinds of writes:

- tracked write flows like `photos download`, `jobs run` with write rows, and `demo write`
- local immediate writes like `export ... --out ...`, `auth key set`, and `onboarding`

That means:

- tracked write flows start with a dry-run plan
- apply needs explicit approval first
- overwrite needs extra confirmation when a local file already exists
- writes without useful saved before-state also need explicit no-snapshot approval before tracking or local file writes

## What this skill does not promise

- no OAuth-only endpoint support
- no hidden download tracking in dry-run mode
- no automatic undo for download tracking or local file writes
- no saved before-state for the current tracked download path

The tool should say those limits plainly before any real tracked download is allowed.

## Local proof and run history

This skill can save:

- dry-run plans with `--plan-out`
- local run history under `.state/runs`
- refusal output that proves download tracking or local file writes stopped before apply

Those artifacts are meant to help review what happened later. They must not contain secrets.

## Recommended workflow with an AI agent

1. Run `auth check` first.
2. Do the photo research or shortlist work before you plan downloads.
3. Build the dry-run download plan first.
4. Review the photo IDs, destination path, and overwrite risk.
5. Attempt tracked downloads only after explicit approval and no-snapshot acceptance when needed.

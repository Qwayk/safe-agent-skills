# How this skill stays safe

This skill is careful by default.

The safest first step is an auth check plus one reviewed read plan before you try anything broader.

## What stays simple

- onboarding and local config
- `api ops list`
- `api ops show --op ...`
- dry-run plans

Those steps do not change TikTok data.

## What needs extra care

Current write-like operations are still plan-first because broad saved before-state support is not there yet.

That means:

- the broad `api` surface needs `--live` for real provider reads
- write-like operations start with a dry-run plan
- apply attempts need the normal write gates
- writes without real saved before-state also need explicit no-snapshot approval before provider HTTP

## One important exception

`auth check` is a real live helper even without `--live`.

It validates your current credentials against `oauth2-advertiser-get`, so it is the safest first live proof that the setup works.

## What this skill does not promise

- no raw request bridge
- no hidden live calls through the broad `api` surface
- no generic rollback
- no broad saved before-state support for current write-like operations

The tool should say those limits plainly before any live write is allowed.

## Local proof and run history

This skill can save:

- dry-run plans with `--plan-out`
- local run history under `.state/runs`
- refusal output that proves a write stopped before provider HTTP

Those artifacts are meant to help review what happened later. They must not contain secrets.

## Recommended workflow with an AI agent

1. Run `auth check` first.
2. Inspect the pinned operation surface before choosing a real API call.
3. Build the dry-run plan first.
4. Use live provider reads only when the target and request are clear.
5. Attempt writes only after explicit approval and no-snapshot acceptance when needed.

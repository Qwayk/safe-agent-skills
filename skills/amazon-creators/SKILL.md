# Amazon Creators API CLI (codex skill)

This page is the agent-facing rule sheet for the public Amazon Creators skill.
If you just want to use the skill, start with the README plus the use-cases and onboarding docs.

This skill wraps `amazon-creators-api-tool` for safe, deterministic catalog planning and guarded local write-helper flows.

## Command surface

- Remote read-only catalog commands: `browse-nodes describe`, `items get`, `variations get`, `search`.
- Local write helpers that currently plan/need required approval before writes: `onboarding`, `auth token set`, `auth token fetch`.

## Safety alignment

- Keep catalog calls review-driven: `--output json`, dry-run first, then `--apply`, then receipt.
- Local write helpers must not be treated as file-write paths yet; confirmed apply needs `--ack-no-snapshot` before env/token writes when no before-state can be saved.
- Keep `--plan-in`, `--yes`, and `--ack-irreversible` out of shipped command assumptions; they are present in the parser but not active for current flows.

## Typical call pattern

- For catalog reads, generate a plan first and only run once verified.
- For local write helpers, generate a plan first, then if apply is requested, confirm the refusal and that no file changed.

Call patterns should include `--output json` so the result is predictable.

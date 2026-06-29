# Skill wrapper guidance

Use this skill for explicit Make API tasks that match the official inventory. Avoid wrapping it as a free-form HTTP bridge.

## Core wrapper contracts

- `make-com-safe onboarding`
  - setup and local env guidance
  - no API mutation
- `make-com-safe auth check`
  - connection health check
- `make-com-safe auth token set --file`
  - stores OAuth token JSON at local state path
- `make-com-safe api list`
  - enumerates all explicit families and operation names
- `make-com-safe api schema <family> <operation>`
  - shows one operation contract for pre-review
- `make-com-safe api <family> <operation> ...`
  - executes read or write with required parameter mapping
- `make-com-safe runs list|show`
  - inspect command history and local artifacts

## Safety-first wrapper mapping

For write paths, wrapper prompts should instruct for:

1. plan output review,
2. explicit `--plan-in --apply --yes`,
3. `--ack-no-snapshot` where required by operation safety data.

## Publish status

This repo copy does not include a public skill publish slice. Use local source or internal process.

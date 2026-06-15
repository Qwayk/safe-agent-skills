# Safety model

Figma can touch files, nodes, comments, branches, webhooks, and team resources, so the safe path is to look first, plan second, and change last. Reads and dry-run plans are where the agent should do most of its thinking. Real changes should only happen after the plan is reviewed and the required approval flags are present.

That matters because the risky part is usually not the command syntax. It is choosing the wrong account, changing the wrong live resource, exposing sensitive output, or approving a change that cannot be cleanly undone.

A good safety ask is: "Read the file or node first, then require no-snapshot approval before comments, file edits, webhook changes, or team writes."

## Core rules

- Read operations can run immediately.
- Write operations build a dry-run plan unless `--apply` is passed.
- Reviewed writes need `--yes`, and some actions also need `--ack-irreversible`.
- `--plan-in` checks request drift before apply.
- Current write applies need explicit `--ack-no-snapshot` approval when no useful before-state can be saved.
- Secrets are redacted from stdout, files, and logs.

## What that means in practice

- File, project, component, analytics, and other read operations are straightforward reads.
- Comment, webhook, variable, and dev-resource writes preview first.
- `--plan-out` lets you save the exact reviewed plan.
- `--receipt-out` stores the result of a reviewed apply.
- `runs list` and `runs show` let you inspect earlier attempts.

## Verification reality

Read operations use the provider response as the verification signal.
Write verification is the provider response plus best-effort read-back when the operation supports it.
This is not a broad rollback or restore system.

## Why the tool refuses

The tool blocks with `ok: false` when:

- required auth is missing
- the live `/v1/me` probe fails
- `--plan-in` does not match the request being rebuilt
- required path or query input is malformed

The tool refuses safely with `ok: true` and `refused: true` when:

- a write tries to apply without the required approval flags
- a reviewed plan does not match the current request

## For safe agent use

An agent should always:

1. run read-only checks first
2. show the dry-run plan
3. wait for explicit approval
4. apply only with the required safety flags
5. report the no-snapshot requirement or saved receipt clearly after the run

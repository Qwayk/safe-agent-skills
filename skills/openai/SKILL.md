# Skill: OpenAI

Use this skill when the user wants an agent to inspect or prepare work against the OpenAI API: models, files, vector stores, assistants, threads, usage, projects, organization access, batches, fine-tunes, responses, realtime calls, uploads, or other documented OpenAI operations.

This wrapper keeps the agent inside `openai-api-tool` instead of letting it improvise raw API calls. That matters because OpenAI work can cost money, change account state, delete resources, or expose sensitive data if the agent guesses.

## Start safely

- Start with `openai-api-tool api ops list`, `openai-api-tool auth check`, or another small read.
- Add `--live` only when the user asks for a real OpenAI network check.
- Use only explicit shipped commands. Do not call raw OpenAI endpoints directly.
- Never print API keys, Authorization headers, OAuth tokens, cookies, or secrets.

A good first ask is: "Check the OpenAI skill is configured, list the available operations, and show me the safest live read or review steps before we plan any changes."

## Write rules

- Always create a dry-run plan first for write-capable operations.
- Only add `--live --apply --plan-in <plan.json>` after the user reviews and approves the saved plan.
- Spend-money operations also require `--yes` and `--ack-spend-money`.
- Deletes and revocations require `--ack-irreversible`.
- Current writes need `--ack-no-snapshot` before OpenAI API key use or HTTP when no before-state can be saved.
- The tool does not support automatic rollback or restore. Keep `before_state` and `recovery` explicit: `automatic_rollback:false`, `backups:[]`, `snapshots:[]`, `rollback_plan:null`.

## Artifact expectations
- Save plans (`--plan-out plan.json`) under `.state/runs/` or the path returned by the tool. After review, supported write attempts need `--ack-no-snapshot` when no before-state can be saved, and any remaining executor limit should be reported exactly.
- Use `openai-api-tool runs show --run-id <id>` to inspect proof data.

## Refuse when

- Refuse if the target command is ambiguous.
- Refuse if required config or auth is missing.
- Refuse live writes without a reviewed plan.
- Refuse spend-money, irreversible, or no-snapshot writes when the matching approval flag is missing.
- Refuse if the plan hash changed or the current inputs do not match the reviewed plan.

## Proof notes
- Mention the plan path, approval gate, and any receipt or exact limitation in your human summary.
- If you publish a proof artifact, link it under `docs/examples/`.

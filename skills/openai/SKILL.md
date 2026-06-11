# Skill: openai-api-skill

This page is the agent-facing rule sheet for the public OpenAI skill.
If you just want to use the skill, start with the README plus the use-cases and onboarding docs.

This skill wraps `openai-api-tool` and enforces the plan → review → no-snapshot approval → receipt or exact refusal loop for writes.

## Invocation guidelines
- Always call `openai-api-tool` in plan-only mode first (no `--apply`, no `--live`).
- Only add `--live --apply --yes` when you have a saved plan and the user explicitly approves the write attempt.
- Spend-money operations must also include `--plan-in <plan.json>` and `--ack-spend-money`.
- Deletes/revocations require `--ack-irreversible` in addition to the above.
- Current writes need `--ack-no-snapshot` before OpenAI API key use or HTTP when no before-state can be saved.
- The tool does not support automatic rollback or restore; keep plans explicit with blocked `before_state` and `recovery` (`automatic_rollback:false`, `backups:[]`, `snapshots:[]`, `rollback_plan:null`).

## Artifact expectations
- Save plans (`--plan-out plan.json`) under `.state/runs/` or the path returned by the tool. After review, supported write attempts need `--ack-no-snapshot` when no before-state can be saved, and any remaining executor limit should be reported exactly.
- Use `openai-api-tool runs show --run-id <id>` to inspect proof data.

## Safety checks (skill responsibility)
- Refuse if the target command is ambiguous.
- Do not run any API calls unless the plan hash matches and gating flags are satisfied.
- Never emit API keys or Authorization headers.

## Proof notes
- Mention the plan path, approval gate, and any receipt or exact limitation in your human summary.
- If you publish a proof artifact, link it under `docs/examples/`.

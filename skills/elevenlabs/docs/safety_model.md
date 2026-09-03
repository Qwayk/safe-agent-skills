# Safety model

ElevenLabs combines creative generation with account data and, through ElevenAgents and telephony, actions that can affect real people. The CLI separates looking, planning, and applying.

## Defaults

- No provider call happens without `--live`.
- Writes are plan-only unless `--live --apply` is present. Reads contact ElevenLabs only when `--live` is present.
- Reads need `--live`; sensitive or binary reads use `--out <path>` and report a file fingerprint instead of emitting the payload.
- The agent refuses an ambiguous voice, agent, file, destination, language, or workspace target rather than guessing.

## Before a live change

The agent shows the exact request, target, output path, spend or external-action risk, preconditions, and verification. You review and save that plan, mark `reviewed: true`, then apply only with matching `--plan-in` and mandatory `--receipt-out`; the plan binding covers resolved path inputs, request body, parameters, and file paths/content hashes when available. Writes currently require `--ack-no-snapshot` when provider state cannot be captured first; the plan must say `before_state.status: no_snapshot_available` and explain the recovery limit.

Spend-sensitive generation, transcription, music, voice design/changing, audio isolation, forced alignment, and similar media work also require `--ack-spend-money`. Deletes, calls, batch work, and other irreversible actions may require `--yes`, `--ack-irreversible`, or a saved `--plan-in`, as shown by the command and coverage docs.

## Sensitive and real-world results

Audio, transcripts, phone numbers, conversation content, webhook data, and similar sensitive responses stay file-only with `--out`. Do not print them, paste them into chat, or include secrets in plans, prompts, logs, or receipts. Calls and Twilio assignment need a clearly approved destination and agent because they can contact real people or incur charges.

## Plan → review → apply → verify

1. Run the explicit command without `--live` and inspect the plan.
2. Confirm the target, content, cost risk, file path, and recovery limit.
3. Apply only with required `--live --apply` and extra approval flags.
4. A durable pending receipt is written before provider I/O. Apply verifies output files locally when written, and performs a status-only exact-path GET readback for declared PUT/PATCH counterparts, reported as `readback_completed`/reachable rather than value equality.

There is no automatic rollback promise. When no snapshot or inverse operation exists, the plan and receipt must say so plainly. Account roles, paid features, provider fixtures, and endpoint availability can still block a correctly gated request; a plan is not proof of live success.

See [API coverage](api_coverage.md) for command-specific gates and [proof](proof.md) for what has actually been exercised.

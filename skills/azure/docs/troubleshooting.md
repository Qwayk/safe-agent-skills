# Troubleshooting

Start with the exact JSON error output because it usually names the missing token, endpoint, plan, acknowledgement, or allowlist rule. A good first troubleshooting ask is: show the exact JSON error, explain the safest next check, and stop before retrying anything that could change Azure. Do not ask the agent to guess missing subscription, resource group, or token values.

## Error output

Most errors include a machine-readable reason and a short human message. Keep the secret values private, but share the error name, refusal reason, command name, and whether the run was a read, plan, or apply attempt.

## Common issues

- `Missing AZURE_API_TOKEN`: set a token before reads and writes.
- `Missing AZURE_DATA_PLANE_ENDPOINT for data-plane command`: add `AZURE_DATA_PLANE_ENDPOINT` in `.env`.
- `Refused: live writes require --plan-in`: create and pass a plan file first.
- `Refused: live writes require --apply` or `--yes`: missing confirmation flags.
- `Refused: high-risk Azure writes require --ack-no-snapshot`: risk category includes no-snapshot class.
- `Refused: irreversible Azure writes require --ack-irreversible`: irreversible operation class.
- `Refused: plan file changed` or drift errors: regenerate plan and review again.

## What to ask the agent to check

- “Show the full refusal reason and what exact flag is missing.”
- “Verify whether this is a management-plane or data-plane command.”
- “Confirm if the command is blocked by allowlist scope.”

## Debug workflow

1. Start with `qwayk-azure-safe-agent-cli auth check`.
2. Confirm `.env` values and endpoint variables without printing secrets.
3. Re-run the read or plan command only after the target looks right.
4. If needed, re-create the plan and review every required flag before apply.

## Warning

Any verbose output is still expected to stay secret-safe; do not share token values.

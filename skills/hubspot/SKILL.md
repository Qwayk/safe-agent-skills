# hubspot-safe-cli

This page is the agent-facing rule sheet for the public HubSpot skill.
If you just want to use the skill, start with the README plus the use-cases and onboarding docs.

Use this skill to run `qwayk-hubspot-safe-agent-cli` safely.

## Safe first use

- If setup may be missing, run:
  - `qwayk-hubspot-safe-agent-cli onboarding`
  - `qwayk-hubspot-safe-agent-cli auth check`
- If auth check fails, stop and ask for corrected HubSpot setup.

## Reads

- Read commands can run directly under:
  - `hubspot object-library`
  - `hubspot objects`
  - `hubspot associations`
  - `hubspot association-labels`
  - `hubspot association-limits`
  - `hubspot properties`
  - `hubspot property-groups`
  - `hubspot owners`
  - `hubspot pipelines`
  - `hubspot pipeline-stages`
  - `hubspot schemas`
  - `hubspot imports`
  - `hubspot exports`
- Return results and do not infer secrets from outputs.

## Writes

- Always run write commands first without `--apply` and review the `plan`.
- Do not run live HubSpot writes without a reviewed plan and the required no-snapshot approval. Without that approval, the tool stops before HubSpot HTTP.
- If you test the gate path, include the required flags and expect a receipt or exact refusal reason:
  - `--apply`
  - `--yes` when required by command family (batch or high risk)
  - `--ack-irreversible` for irreversible actions
  - `--plan-in` when the command requires a saved reviewed plan
- Capture the refusal output and call out that no HubSpot write was sent.
- This tool does not support provider snapshots, provider backups, or automatic rollback.
- Never ask the user to paste token values or OAuth JSON in chat.

## Proof locations

- Proof files are local only:
  - `.state/runs/index.jsonl`
  - `.state/runs/<run-id>/plan.json`
  - `.state/runs/<run-id>/summary.md`
  - `.state/runs/<run-id>/audit.jsonl`

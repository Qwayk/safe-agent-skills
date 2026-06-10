# Pipedrive

This page is the agent-facing rule sheet for the public Pipedrive skill.
If you just want to use the skill, start with the README plus the use-cases and onboarding docs.

Use this tool to run read-only Pipedrive lookups.

## Use command names
- `qwayk-pipedrive-safe-agent-cli onboarding`
- `qwayk-pipedrive-safe-agent-cli auth check`
- `qwayk-pipedrive-safe-agent-cli <group> <action>`
- Example: `qwayk-pipedrive-safe-agent-cli users get-current`

## Rules
- Keep `--output json`.
- No write, apply, plan, or job commands.
- No token values in shared output.
- If no shipped read command matches the request, say that there is no matching shipped read command in `docs/api_coverage.md`.
- If a request is documented as excluded by read-only policy, return:
  - `excluded by choice: read-only tool`

# reddit-safe-cli

This page is the agent-facing rule sheet for the public Reddit skill.
If you just want to use the skill, start with the README plus the use-cases and onboarding docs.

Use this skill to work with the official Reddit Data API through `qwayk-reddit-safe-agent-cli`.

## First steps

- If setup is unknown, run `qwayk-reddit-safe-agent-cli onboarding`.
- To inspect setup, run `qwayk-reddit-safe-agent-cli auth check`.
- To see available endpoint commands, run `qwayk-reddit-safe-agent-cli api ops list`.

## Safe usage

- Use `--live` for reads and for any command that checks live data.
- Writes stay dry-run by default.
- To apply a write, use `--live --apply`.
- `--live auth exchange-code` and `--live auth refresh` are required before live token checks/writes.
- Risky writes also need `--plan-in --yes`.
- Irreversible writes also need `--ack-irreversible`.
- Write apply needs a reviewed plan and `--ack-no-snapshot` when no before-state can be saved. Expect `before_state.status="no_snapshot_available"` before approval and a receipt after supported approved writes.
- Never ask the user to paste secrets into chat.

## Common commands

- `qwayk-reddit-safe-agent-cli --live api get-api-v1-me`
- `qwayk-reddit-safe-agent-cli --live api get-top --path subreddit=python --query limit=10`
- `qwayk-reddit-safe-agent-cli api post-api-vote --body id=t3_abc123 --body dir=1 --plan-out vote-plan.json`

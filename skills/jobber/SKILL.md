---
name: jobber
description: Run Jobber read/write operations safely using qwayk-jobber-safe-agent-cli.
---

This is the agent-facing rule sheet for the Jobber safe skill.
If you want the CLI, use `qwayk-jobber-safe-agent-cli`.

Core rules:
- Always use `--output json` for parseable results.
- Never ask for or print secrets.
- Start with `auth check` and `schema summary` before read/write work.
- Use registry-generated read/write commands only.
- Never call raw GraphQL.
- Writes are plan-first by default.
- Apply writes only with `--apply --yes --plan-in <reviewed-plan.json>`.
- High-risk writes with no snapshot need `--ack-no-snapshot`.
- Clearly irreversible writes need `--ack-irreversible`.
- For token refresh and batch writes, keep explicit approval flow.

Workflow:
1. Confirm connectivity:
   - `qwayk-jobber-safe-agent-cli --output json auth check`
2. Confirm command exists in coverage:
   - `qwayk-jobber-safe-agent-cli --output json schema summary`
3. Run a safe first read if needed:
   - `qwayk-jobber-safe-agent-cli --output json read clients --selection "nodes { id name } totalCount" --limit 10`
4. Build a safe write plan:
  - `qwayk-jobber-safe-agent-cli --output json --plan-out plan.json write clientCreate --args-json '{"input":{"firstName":"Sample","lastName":"Client"}}' --selection 'client { id name } userErrors { message path }'`
5. Apply only after review:
  - `qwayk-jobber-safe-agent-cli --output json --apply --yes --plan-in plan.json write clientCreate --args-json '{"input":{"firstName":"Sample","lastName":"Client"}}' --selection 'client { id name } userErrors { message path }'`
6. For high-risk no-snapshot writes and irreversible writes, include the extra ack flags:
   - `qwayk-jobber-safe-agent-cli --output json --apply --yes --ack-no-snapshot --ack-irreversible --plan-in plan.json write clientDelete --selection 'client { id }'`
7. Check run proof when needed:
  - `qwayk-jobber-safe-agent-cli --output json runs list`
  - `qwayk-jobber-safe-agent-cli --output json runs show --run-id <run-id>`

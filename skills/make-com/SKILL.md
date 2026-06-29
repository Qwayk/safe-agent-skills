---
name: make-com
description: Use Make.com safely through explicit official Make API commands. Helps agents inspect scenarios, teams, hooks, connections, data stores, API tokens, SDK apps, templates, users, audit logs, and other Make API resources before preparing reviewed write plans.
---

# Make.com

Use this skill when the user wants an agent to inspect or manage Make.com through the official Make API.

This skill is for Make account and automation control-plane work: scenarios, scenario folders, hooks, connections, data stores, data structures, organizations, teams, users, SDK apps, AI agents, audit logs, notifications, keys, devices, templates, custom properties, remote procedures, and the other operations in the pinned Make API inventory.

Do not use this skill as a generic HTTP bridge, Make MCP setup wrapper, Make CLI wrapper, Custom Apps authoring tool, or White Label tool.

## Start Safely

1. Run `make-com-safe onboarding` when setup is unclear.
2. Run `make-com-safe auth check` before live reads.
3. Run reads first, such as:
   - `make-com-safe api list`
   - `make-com-safe api schema scenarios list-scenarios`
   - `make-com-safe api scenarios list-scenarios --query teamId=<team_id>`
4. Explain what the read results mean before preparing any change.

## Write Rules

Reads may run directly.

Writes must be reviewed first:

1. Create a dry-run plan with the exact command, target IDs, query values, and redacted body.
2. Ask the user to review the plan.
3. Apply only from the saved plan with `--plan-in --apply --yes`.
4. Add `--ack-no-snapshot` when the plan says Make does not provide a safe before-state snapshot.
5. Add `--ack-irreversible` for destructive operations.
6. Save or show the receipt after apply.

Never print Make API tokens, OAuth secrets, cookies, webhook secrets, scenario blueprint secrets, connection secrets, or private customer data.

## Useful First Ask

Ask the agent:

`Show me active Make scenarios, hooks, and team users for team <team_id>, then explain anything risky before preparing any change.`

## Source Docs

- `README.md`
- `docs/quickstart.md`
- `docs/command_reference.md`
- `docs/safety_model.md`
- `docs/api_coverage.md`
- `docs/proof.md`

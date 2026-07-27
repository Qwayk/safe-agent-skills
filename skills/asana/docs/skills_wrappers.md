# Asana skill wrapper

The source wrapper is at `skills/asana/SKILL.md`. In the published `asana` skill, the same wrapper is installed as the top-level `SKILL.md`. Both layouts use the same complete contract checks, and a copy with neither location is invalid.

Use the wrapper for official Asana REST work: project and task reviews, goals, portfolios, teams, memberships, custom fields, collaboration, time tracking, attachments, webhooks, exports, audit logs, rules, agents, and other families listed in the coverage ledger.

Do not use it for App Components, SCIM, OAuth app setup or token lifecycle, browser automation, private endpoints, or arbitrary requests.

The wrapper directs the agent to:

1. run onboarding only when setup is missing
2. confirm the connection with `auth check`
3. start with a fixed read against the user's exact target
4. inspect command metadata when inputs or access are unclear
5. save and explain a write plan before asking for approval
6. use the exact plan ID and any acknowledgements named by the plan; never edit or repair a refused plan
7. report the receipt, verification, asynchronous state, and remaining limits

The wrapper is an instruction layer. `asana-safe` performs every API call and enforces the runtime gates. Source changes begin in `skills/asana/SKILL.md`; public mirroring moves that file to top-level `SKILL.md` without changing its meaning.

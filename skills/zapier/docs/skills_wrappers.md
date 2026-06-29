# Skills wrappers

The Zapier skill wrapper lets an agent use the shipped `qwayk-zapier-safe-agent-cli` commands without guessing raw API calls. That matters because Zapier work can create Zaps, execute actions, acknowledge inbox messages, and touch connected apps outside the Zapier account itself.

## Where the skill lives

- Source wrapper: `skills/zapier/SKILL.md`
- Public mirror wrapper: `SKILL.md`
- Public install slug: `zapier`

The wrapper should run the CLI with JSON output and only pass through the explicit command groups below:

- `onboarding`
- `auth check`
- `runs list`
- `runs show`
- `partner <named-operation>`
- `trigger-inbox <named-operation>`
- `promotions <named-operation>`
- `ai-actions <named-operation>`

Safety messages to expose to agents:

- Reads are direct.
- Writes create plans by default.
- High-risk writes require:
  - `--apply`
  - `--plan-in`
  - explicit extra acknowledgement (`--yes`, `--ack-irreversible`, or `--ack-no-snapshot`).

Never suggest raw API path/method inputs.

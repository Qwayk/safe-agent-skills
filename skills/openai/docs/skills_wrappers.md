# Skills wrappers (Agent Skills)

The OpenAI skill wrapper lets an agent use the shipped `openai-api-tool` commands without guessing raw API calls. That matters because OpenAI work can touch live files, vector stores, assistants, organization access, usage, batches, fine-tunes, responses, and other actions that may cost money or change account state.

The wrapper should guide the agent to start with reads and operation discovery, then prepare write-like work as a saved plan for human review. The CLI enforces the hard gates, but the skill instructions should still make the safe path obvious before any command runs.

## Where the skill lives

- Canonical location: `skills/openai/SKILL.md`.
- Public install slug: `openai`.
- Source docs for users: `README.md`, `docs/use_cases.md`, `docs/onboarding.md`, and `docs/safety_model.md`.

## What the skill must make clear

- Use explicit shipped commands only; do not invent direct OpenAI API calls.
- No OpenAI network call runs without `--live`, even for reads.
- Start with `openai-api-tool api ops list`, `auth check`, or another small read before planning changes.
- Write-capable operations start as dry-run plans and require `--plan-in` before apply.
- Spend-money actions need the stronger spend gate.
- Delete-like actions need the irreversible gate.
- If no useful before-state can be saved, live writes also need explicit no-snapshot approval.
- Plans, receipts, refusals, and summaries must not expose API keys, tokens, or Authorization headers.
- Do not promise rollback, restore, or backup unless the exact action provides it.

## Good first skill ask

Ask: "Check the OpenAI skill is configured, list the available operations, and show me the safest live read or review steps before we plan any changes."

That first ask proves the agent is using the pinned operation catalog and gives the user a safe next step before any account-changing work.

## When to refuse

- The target OpenAI resource or operation is ambiguous.
- Required config or auth is missing.
- The user asks for a live write without a reviewed plan.
- A spend-money, delete-like, or no-snapshot write is missing its required approval.
- The runtime cannot enforce the plan, approval, and receipt loop.

# Jobber Safe CLI

A good first ask is: Connect this skill, show me what it can safely review first, and suggest the clearest next action.

You can ask for things like account summaries, report checks, risk review, and a safe change plan before any live write.

## Start here first

- What this skill can help with? [What this skill can help you do](docs/use_cases.md)
- Need setup? [Set up your account step by step](docs/onboarding.md)
- Want the safety story first? [See how this skill keeps changes safe](docs/safety_model.md)
- If you are ready for commands, go to [Quickstart](docs/quickstart.md) and the [Command guide](docs/command_reference.md).

## What this skill helps with

- Review Jobber account data using explicit, generated read commands.
- Prepare deterministic change plans for write operations from the same command registry.
- Keep a local audit path with plans, receipts, and optional run logs.
- Verify token status and OAuth app connectivity before any action.

## What access this skill needs

- OAuth app credentials from Jobber Developer Center: `JOBBER_CLIENT_ID`, `JOBBER_CLIENT_SECRET`, and `JOBBER_REDIRECT_URI`.
- A Jobber access token via `JOBBER_API_TOKEN` or `auth token set`.
- Local `.env` values for base URL and optional timeout settings.
- Secrets never leave local files or command output.

## Install and first run

Install slug: `jobber`.

Ask your agent to install the skill from `Qwayk/safe-agent-skills`.

If auto-install is not available, run:

```bash
npx skills add Qwayk/safe-agent-skills@jobber -g -y
```

Then open [Onboarding](docs/onboarding.md), then [Quickstart](docs/quickstart.md).

## How this skill stays safe

- Read commands are safe to start with and do not require apply flags.
- Write commands are dry-run by default.
- Live write execution requires `--apply --yes --plan-in <reviewed-plan.json>`.
- Job batches that include write rows also require `--apply --yes --plan-in <reviewed-plan.json>` before live execution.
- High-risk write operations that cannot capture a before-state snapshot require `--ack-no-snapshot` before live execution.
- Clearly irreversible operations also require `--ack-irreversible`.
- The tool can emit plans and receipts, then run history for later review.
- Tokens and secrets are never printed.

## What happens before live changes

1. Connect and check auth first with `auth check` and `schema summary`.
2. Run read commands and confirm scope.
3. Build a write plan with the same command plus write args.
4. Save the plan with `--plan-out`.
5. Apply only with explicit approval flags and the reviewed plan file.
6. For high-risk no-snapshot operations, include `--ack-no-snapshot` and only then apply.

## What proof it leaves behind

- Plan JSON from dry-run writes.
- Receipts from apply writes.
- Optional run artifacts and index in `.state/runs/`.
- `runs list` and `runs show` for quick audit checks.

## Limits

- OAuth scopes and account permissions still control what each command can do.
- Draft custom integrations are capped at 5 paying accounts unless approved.
- Jobber may require marketplace review for additional access.
- Jobber rate limits and query-cost behavior still apply.
- Webhook delivery is at-least-once, so consumers should be idempotent.
- Live commands are registry-backed and safety-gated; account-specific scope behavior and full business impact remain unverified until connected to live accounts.

## Helpful docs

- [Browse all docs](docs/README.md)
- [Quickstart](docs/quickstart.md)
- [Command guide](docs/command_reference.md)
- [Proof and verification](docs/proof.md)

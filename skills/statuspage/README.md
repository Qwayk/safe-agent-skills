# Statuspage

**Capability:** Read-only

See if a public status page looks healthy without giving your agent account access.

Use this skill when you want your agent to check a public Statuspage site, point out open incidents, and tell you about planned maintenance. This skill stays simple on purpose: public pages only, no sign-in, and no account changes.

## What this skill helps with

- Check this status page and tell me if anything looks down.
- Show me open incidents on this status page.
- Tell me if there is planned maintenance.
- Summarize the current component status for this page.

## What access this skill needs

You only need the public status page URL.
For the normal public-page flow, this skill does not need an API key.

## Install and first run

Ask your agent to install the `statuspage` skill from `Qwayk/safe-agent-skills`.

If new skills do not appear automatically, reopen the app or attach the skill to the current workspace if your host needs that.

If your host does not let the agent install skills directly, run:

```bash
npx skills add Qwayk/safe-agent-skills@statuspage -g -y
```

Then try a safe first ask like:

```text
Check https://status.atlassian.com and tell me if anything is down.
```

## How this skill stays safe

- It checks public Statuspage pages only.
- It does not sign in or change anything in an account.
- Most public pages do not need an API key.
- The answer includes the source page URL so you can check it yourself.
- This skill keeps the instructions, the full safe API CLI code the agent uses, and the docs and tests in one place, so you can inspect what your agent is really using.

## What it covers today

This skill covers read-only public status checks:

- overall status
- open incidents
- planned maintenance
- listed components when the page provides them

It does not sign in, ask for private account access, or change anything in an account.

## What happens before a real change

This skill does not change anything. It reads a public page and reports what it found.

## What proof it leaves behind

The proof is simple on purpose. A good answer shows:

- the page name
- the overall status
- open incidents
- planned maintenance
- affected components when the page lists them
- the source page URL

You can compare that answer with the public page in a few seconds.

## Example requests

- Check this status page and tell me if anything looks down.
- Show me open incidents on this status page.
- Tell me if there is planned maintenance.
- Summarize the current component status for this page.

## Limits

- Statuspage pages only.
- Public-page checks only.
- No private-account access.
- No writes.

## Helpful docs

- `examples/first-run.md`
- `docs/onboarding.md`
- `docs/command_reference.md`
- `docs/api_coverage.md`
- `docs/safety_model.md`
- `docs/proof.md`

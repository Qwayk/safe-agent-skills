# Statuspage

**Capability:** Read-only

Statuspage is useful when you need a quick answer about whether a service looks healthy before you deploy, reply to a customer, or decide if an outage is yours or the vendor's.

This skill lets an agent check a public Statuspage site, summarize open incidents and maintenance, and turn the page's public data into a clear status note. It works well for vendor checks, daily health summaries, component reviews, and comparing several public pages the same way.

No account is needed for normal checks. The tool only reads public Statuspage API data. The useful limit is that a public page may not show every private outage, so the first thing to check is that the agent is looking at the right page.

A good first ask is: "Check https://status.atlassian.com and tell me if anything looks down, what incidents are open, and whether any maintenance is scheduled."

## Start here first

- Want ideas for real Statuspage work? [What you can do with Statuspage](docs/use_cases.md)
- Need the shortest setup path? [Use a public Statuspage URL](docs/onboarding.md)
- Want the safety story first? [How this skill stays safe](docs/safety_model.md)

If you already want exact commands, jump straight to [Quickstart](docs/quickstart.md) and the [Command guide](docs/command_reference.md).

## What this skill helps with

- Check whether a vendor's public status page looks healthy before a deploy, launch, or support response.
- Summarize overall status, open incidents, and scheduled maintenance in plain English.
- Check whether specific components are marked operational, degraded, or down when the page exposes them.
- Capture a fast public status snapshot for a report or handoff.
- Compare several public status pages by running the same read-only checks on each one.

## What access this skill needs

- A public Statuspage URL such as `https://status.atlassian.com`.
- No API key for normal public-page checks.
- Optional local `.env` setup only if you want a default page so you do not repeat `--base-url`.

## Install and first run

Install slug: `statuspage`

Ask your agent to install the `statuspage` skill from `Qwayk/safe-agent-skills`.

If new skills do not appear automatically, reopen the app or attach the skill to the current workspace if your host needs that.

If your host does not let the agent install skills directly, run:

```bash
npx skills add Qwayk/safe-agent-skills@statuspage -g -y
```

Then try a safe first ask like:

```text
Check https://status.atlassian.com and tell me if anything looks down, what incidents are open, and whether any maintenance is scheduled.
```

## How this skill stays safe

- It is read-only to Statuspage by design.
- It only calls public Statuspage endpoints.
- It does not sign in, use private account APIs, or change anything.
- Normal checks need only a public page URL.
- Results include the source page URL so you can compare them quickly with the public page.
- The docs, tests, examples, and API coverage notes all live in this repo.

## What it covers today

This skill covers:

- current overall status
- summary snapshots
- open incidents
- scheduled maintenance
- listed components when the page publishes them in the summary response

## What happens before live changes

There are no live changes in this skill. It reads public data and returns structured output you can review, save, or compare.

## What proof it leaves behind

- Normal reads return machine-readable JSON you can review or save.
- The answer includes the source page URL.
- The proof pack includes live smoke notes plus committed examples for the main result shapes.
- The docs, tests, and API coverage ledger are all in this repo.

## Limits

- Public Statuspage sites only.
- No private account access or authenticated admin actions.
- If a company hides a problem from its public page, this skill cannot see it.
- Some pages expose fewer components or incident details than others.

## Helpful docs

- [Browse all Statuspage docs](docs/README.md)
- [Quickstart](docs/quickstart.md)
- [Command guide](docs/command_reference.md)
- [First-run example](examples/first-run.md)
- [Troubleshooting](docs/troubleshooting.md)
- [Proof and verification](docs/proof.md)
- [API coverage](docs/api_coverage.md)

# Cloudflare

**Capability:** Reads + careful changes

Cloudflare is where a small mistake can affect DNS, security rules, Workers, Pages, access policies, or production traffic. This skill helps an agent look through the account carefully before anyone changes something important.

Use it for jobs like "What zones and DNS records do we have?", "Is this Worker route pointing where we think?", "What Zero Trust policies are active?", or "Can we plan this DNS change and show the risk before it goes live?"

Read work can run as normal account review. Riskier work starts as a dry-run plan, sensitive results go to local files instead of chat, destructive actions need extra approval, and some write families need explicit no-snapshot approval when the tool cannot save useful before-state first.

A good first ask is: "Check the Cloudflare skill is connected, list my accounts and zones, and run zone-create-check before we plan any onboarding."

## Start here first

- Want ideas for real Cloudflare work? [What you can do with Cloudflare](docs/use_cases.md)
- Need setup? [Connect your Cloudflare account](docs/onboarding.md)
- Want the safety story first? [How this skill stays safe](docs/safety_model.md)

If you already want exact commands, jump straight to [Quickstart](docs/quickstart.md) and the [Command guide](docs/command_reference.md).

## What this skill helps with

- Review accounts, zones, DNS records, DNSSEC, and zone settings.
- Plan careful DNS, Workers route, Pages, and other Cloudflare changes before they go live.
- Check Workers scripts, routes, KV metadata, deployments, builds, pipelines, and Browser Run results.
- Review Zero Trust, Gateway, Access, and DLP configuration.
- Review organization members, API tokens, and account access settings.
- Use named helpers for common jobs and the broader allowlisted operations surface when a documented Cloudflare task does not have the best named front door yet.

## What access this skill needs

- A Cloudflare API token.
- Your account ID or zone ID for many jobs.
- Extra token scopes only for the surfaces you actually want to use.
- Browser Run, D1, and other special surfaces may need extra Cloudflare permissions.

For most people, a read-only inventory token is the safest place to start.

## Install and first run

Install slug: `cloudflare`

Ask your agent to install the `cloudflare` skill from `Qwayk/safe-agent-skills`.

If new skills do not appear automatically, reopen the app or attach the skill to the current workspace if your host needs that.

If your host does not let the agent install skills directly, run:

```bash
npx skills add Qwayk/safe-agent-skills@cloudflare -g -y
```

Then try a safe first ask like:

```text
Check the Cloudflare skill is connected, list my accounts and zones, and run zone-create-check before we plan any onboarding.
```

## How this skill stays safe

- It does not expose a generic raw-call bridge.
- Writes are dry-run first and need `--apply --yes`.
- Sensitive reads and secret-bearing results are file-only and never printed to stdout.
- Destructive or one-time secret actions need extra acknowledgement and output files.
- Some write families can save before-state first; where that is not practical, live apply requires explicit no-snapshot approval.
- `auth zone-create-check` is a safe preflight before bulk zone onboarding or zone-creation work.

## What it covers today

This skill covers:

- onboarding, auth, accounts, zones, DNS, Workers, Pages, observability, storage, and Browser Run
- Zero Trust, Gateway, Access, and DLP review
- organization members, API tokens, and account access review
- named helper commands for common Cloudflare jobs
- broader official Cloudflare coverage through explicit allowlisted `operations` commands when a named helper is not the best fit

## What happens before live changes

- The agent should show the dry-run plan first.
- You review the account, zone, script, or policy target before apply.
- Safe reads can run immediately.
- Writes need `--apply --yes`.
- Destructive or one-time secret actions may also need `--ack-irreversible` and file output.
- Some live writes also need explicit no-snapshot approval when the tool cannot save useful before-state first.

## What proof it leaves behind

- Dry-run plans can be saved with `--plan-out`.
- Apply receipts can be saved with `--receipt-out`.
- Before-state is captured when the write family can safely read it first.
- Sensitive reads write to local files instead of stdout.
- The docs, tests, and coverage ledgers are all in this repo, including the live official coverage ledger.

## Limits

- Broad `operations` coverage does not mean every write has a built-in undo path.
- Some Cloudflare surfaces still need extra permissions beyond a basic read-only token.
- Sensitive reads like script content and KV values stay file-only.
- When Cloudflare does not expose a clean prior state, the skill can still work, but only after explicit no-snapshot approval.

## Helpful docs

- [Browse all Cloudflare docs](docs/README.md)
- [Quickstart](docs/quickstart.md)
- [Command guide](docs/command_reference.md)
- [Proof and verification](docs/proof.md)
- [API coverage](docs/api_coverage.md)
- [Live official coverage ledger](docs/api_coverage_live_official.md)

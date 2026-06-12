# Pinterest

**Capability:** Reads + careful changes

Pinterest work often starts with a messy question: what boards, pins, sections, ads, catalogs, or feeds are actually in the account, and what looks worth fixing? This skill helps an agent export snapshots, review account structure, check analytics or catalog diagnostics, and prepare changes as plans before anything goes live.

It is useful for questions like "What changed in my boards and pins?", "Which pins or ads are performing?", "Are there catalog feed issues?", or "What would this pin-link cleanup change before we approve it?"

Snapshots and audits can run from read-only Pinterest calls plus local JSON output. Write families start as dry-run plans, and confirmed apply still needs explicit no-snapshot approval before live Pinterest writes because saved before-state support is not there yet.

A good first ask is: "Check the Pinterest skill is configured, export a snapshot of my boards and pins, and tell me what looks unusual before we plan any updates."

## Start here first

- Want ideas for real Pinterest work? [What you can do with Pinterest](docs/use_cases.md)
- Need setup? [Connect your Pinterest account](docs/onboarding.md)
- Want the safety story first? [How this skill stays safe](docs/safety_model.md)

If you already want exact commands, jump straight to [Quickstart](docs/quickstart.md) and the [Command guide](docs/command_reference.md).

## What this skill helps with

- Export board, section, and pin inventory snapshots for review or audits.
- Check account analytics, top pins, ads structure, and aggregated ads performance when your account has access.
- Review catalogs, feeds, processing results, product groups, and item issues before anyone tries to fix them live.
- Preview pin-link cleanup or other write plans before anything changes live.
- Save plans, refusals, receipts, and audit snapshots for later review.

## What access this skill needs

- A Pinterest access token, or the app ID, app secret, and refresh token for longer-lived access.
- The Pinterest scopes needed for the endpoints you want to use.
- An ad account ID for ads or catalogs work.
- A business ID for Business Access inventory.
- A local output folder when you want audit snapshots or exports saved to your machine.

For most people, a simple access token plus a read-only snapshot is the safest place to start.

## Install and first run

Install slug: `pinterest`

Ask your agent to install the `pinterest` skill from `Qwayk/safe-agent-skills`.

If new skills do not appear automatically, reopen the app or attach the skill to the current workspace if your host needs that.

If your host does not let the agent install skills directly, run:

```bash
npx skills add Qwayk/safe-agent-skills@pinterest -g -y
```

Then try a safe first ask like:

```text
Check the Pinterest skill is configured, export a snapshot of my boards and pins, and tell me if anything looks unusual before we plan any changes.
```

## How this skill stays safe

- Inventory, analytics, ads reads, and catalog reads can stay read-only to Pinterest.
- `audit snapshot` writes JSON files locally from read-only Pinterest calls.
- Remote write families start as dry-run plans first.
- Confirmed apply still needs `--apply --yes`, plus any extra acknowledgement flags for irreversible, spend-sensitive, or high-volume work.
- When no saved before-state exists, apply also needs explicit no-snapshot approval before Pinterest writes, local token writes, report outputs, or successful write receipts.
- The tool does not claim rollback or provider backup support for those live write paths today.
- Docs, tests, examples, and API coverage all live in this repo so you can inspect what the agent is using.

## What it covers today

This skill covers:

- boards, board sections, pins, board pins, and inventory snapshots
- user account, business access, and lookup resources
- ads account reads, ads structure reads, and aggregated ads analytics
- catalog reads, feed diagnostics, and catalog reporting
- plan-first write families for boards, sections, pins, ads, catalogs, reports, and jobs
- pin-link hygiene planning and apply with explicit no-snapshot approval

## What happens before live changes

- The agent should show the dry-run plan first.
- You review the target account, object IDs, payload, and risk level.
- Read-only snapshots and inventory reads can run without a Pinterest write.
- Remote write families need `--apply --yes`.
- Riskier operations can also need flags like `--ack-irreversible`, `--ack-spend`, or `--ack-volume`.
- Writes without saved before-state also need `--ack-no-snapshot` before live Pinterest HTTP.

## What proof it leaves behind

- Audit snapshots save structured JSON files locally.
- Dry-run plans can be saved and reviewed before apply.
- Refusals make it clear when missing approval stopped the write before Pinterest HTTP.
- Apply receipts can be saved when a write path is actually allowed.
- The docs, tests, proof pack, committed examples, and API coverage ledger all stay in this repo so you can inspect what the agent relied on.

## Limits

- Many Pinterest analytics, ads, and catalogs endpoints need extra scopes, account roles, or account tier.
- Live write families still do not have saved before-state, rollback, or provider backup support today.
- Auth helper writes and some job/report outputs also need explicit no-snapshot approval before local token or output writes.
- This skill is safest when you start with one snapshot or one reviewed write plan before larger work.

## Helpful docs

- [Browse all Pinterest docs](docs/README.md)
- [Quickstart](docs/quickstart.md)
- [Command guide](docs/command_reference.md)
- [Authentication details](docs/authentication.md)
- [Configuration](docs/configuration.md)
- [Troubleshooting](docs/troubleshooting.md)
- [Proof and verification](docs/proof.md)
- [API coverage](docs/api_coverage.md)

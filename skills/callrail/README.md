# CallRail

**Capability:** Reads + careful changes

CallRail is where calls, texts, forms, trackers, companies, integrations, and webhooks turn marketing traffic into real lead and support records.

This skill helps an agent review CallRail activity, check tracking setup, inspect conversations and forms, and prepare careful changes before anything affects outbound calls, messages, routing, or integrations.

Use it for questions like: "Which calls came in this week?", "What text conversations need review?", "Which trackers or integrations are active?", "Can you preview an outbound call request?", or "Can you draft this MMS reply before sending it?"

CallRail reads can run after valid account access is available. Writes are dry-run first, and live writes need explicit no-snapshot approval until command-specific snapshots exist.

A good first ask is: "Check the CallRail connection, show recent calls for one company, list integrations, and stop before any outbound calls, texts, or setting changes."

## Start here first

- Want ideas for real CallRail work? [What you can do with CallRail](docs/use_cases.md)
- Need setup? [Connect your CallRail account](docs/onboarding.md)
- Want the safety story first? [How this skill stays safe](docs/safety_model.md)

If you already want exact commands, jump straight to [Quickstart](docs/quickstart.md) and the [Command guide](docs/command_reference.md).

## What this skill helps with

- Review calls, text messages, forms, companies, trackers, integrations, webhooks, users, and notifications.
- Pull call activity, summaries, time-series results, and conversation details for reporting.
- Search recent text conversations or form submissions.
- Prepare tracker, company, tag, integration, webhook, notification, call, or text-message changes as review plans.
- Keep local proof for plans, receipts, run history, and best-effort verification.

## What access this skill needs

- A CallRail API key stored locally.
- The account ID, and often a company ID, for the records you want to inspect.
- Write-enabled CallRail access before any live write can succeed.
- Optional `Request-From` only when you are acting as a third-party integrator.

## Install and first run

Install slug: `callrail`

Ask your agent to install the `callrail` skill from `Qwayk/safe-agent-skills`.

If new skills do not appear automatically, reopen the app or attach the skill to the current workspace if your host needs that.

If your host does not let the agent install skills directly, run:

```bash
npx skills add Qwayk/safe-agent-skills@callrail -g -y
```

Then try a safe first ask like:

```text
Check the CallRail connection, show recent calls for one company, list integrations, and stop before any outbound calls, texts, or setting changes.
```

## How this skill stays safe

- Reads run without apply flags.
- Writes start as dry-run plans.
- Normal live writes need `--apply --yes --ack-no-snapshot` while command-specific snapshots are not available.
- Reviewed writes should use `--plan-out` before review and `--plan-in` for live apply.
- `calls create-outbound` and `text-messages send` also need `--ack-irreversible`.
- The tool has no raw request bridge.

## What it covers today

This skill covers explicit CallRail REST command families for:

- calls, text messages, form submissions, companies, accounts, tags, trackers, users, notifications, integrations, and webhooks
- MMS send shapes through either JSON `media_url` or multipart `--media-file`
- plan, receipt, run-history, and coverage proof for CallRail work

## What happens before live changes

- The agent should show the dry-run plan first.
- You review the account, company, target record, message or call risk, and recovery limit.
- Live writes need the required approval gates.
- Outbound calls and text messages need irreversible acknowledgement.
- If the reviewed plan does not match the live request, the tool refuses and asks for a fresh plan.

## What proof it leaves behind

- Dry-run plans can be saved with `--plan-out`.
- Reviewed applies can use `--plan-in`.
- Receipts can be saved with `--receipt-out`.
- Local run history can include `plan.json`, `receipt.json`, `audit.jsonl`, and `summary.md`.
- The docs, tests, proof pack, and API coverage ledger live in this repo.

## Limits

- Live CallRail reads and writes are locally tested with mocked provider responses in this repo, not a write-enabled CallRail test account.
- Write access must be enabled intentionally in CallRail.
- Some verification is response-based when a command cannot read back final state.
- Outbound calls and text messages can affect real people, so they use stronger approval.

## Helpful docs

- [Browse all CallRail docs](docs/README.md)
- [Quickstart](docs/quickstart.md)
- [Command guide](docs/command_reference.md)
- [Authentication details](docs/authentication.md)
- [Proof and verification](docs/proof.md)
- [API coverage](docs/api_coverage.md)

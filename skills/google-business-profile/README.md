# Google Business Profile

**Capability:** Reads + careful changes

Google Business Profile is where local customers see your hours, address, phone number, reviews, photos, services, and verification status.

This skill helps an agent review accounts and locations, check categories, attributes, reviews, media, verifications, lodging, calls, place actions, and performance, and prepare profile changes before anything affects a live listing.

Use it for questions like: "Which locations have missing basics?", "What Google-updated fields need review?", "Can you prepare a review reply?", "Is this location verified?", or "Can you preview this hours or attribute change?"

Business Profile reads can run live after access is connected. Write-capable actions start as dry-run plans, many apply paths require a reviewed plan file, and live writes need explicit no-snapshot approval when the tool cannot save useful before-state first.

A good first ask is: "Check the Google Business Profile connection, list my accounts and locations, and show me what looks incomplete before we plan any changes."

## Start here first

- Want ideas for real Google Business Profile work? [What you can do with Google Business Profile](docs/use_cases.md)
- Need setup? [Connect your Google Business Profile access](docs/onboarding.md)
- Want the safety story first? [How this skill stays safe](docs/safety_model.md)

If you already want exact commands, jump straight to [Quickstart](docs/quickstart.md) and the [Command guide](docs/command_reference.md).

## What this skill helps with

- Review accounts, locations, categories, attributes, and Google-updated location details.
- Plan careful location edits, attribute updates, account changes, and notification setting changes.
- Review or manage admins, invitations, transfers, and account structure updates.
- Review reviews, media, verification status, place action links, lodging details, and business call settings.
- Pull location performance metrics and keyword impression data.

## What access this skill needs

- Google OAuth client credentials stored locally in `.env` and local state files.
- A Google account with the Business Profile permissions needed for the locations you want to review or change.
- Account IDs, location IDs, or full resource names for many read and write requests.
- Extra approval for high-risk location transfers, deletes, review reply deletes, and similar actions.

## Install and first run

Install slug: `google-business-profile`

Ask your agent to install the `google-business-profile` skill from `Qwayk/safe-agent-skills`.

If new skills do not appear automatically, reopen the app or attach the skill to the current workspace if your host needs that.

If your host does not let the agent install skills directly, run:

```bash
npx skills add Qwayk/safe-agent-skills@google-business-profile -g -y
```

Then try a safe first ask like:

```text
Check the Google Business Profile connection, list my accounts and locations, and show me what is safe to review before we plan any live changes.
```

## How this skill stays safe

- Read commands can run live right away.
- Write-capable actions start as dry-run plans first.
- Many apply paths require `--plan-in`, and some also require `--yes` or `--ack-irreversible`.
- When no saved before-state exists, live writes also need `--ack-no-snapshot`.
- PINs, verification tokens, and other secret-like inputs stay file-based where that is safer.
- Many write flows verify success by reading the new state back after the change.
- The docs, tests, coverage notes, and source code are all here in one place.

## What it covers today

This skill covers:

- account-management, business-info, notifications, business-calls, place-actions, performance, lodging, and verifications
- media upload and media follow-up flows
- legacy v4.9 review, verification, transfer, and media commands that still matter in real GBP work
- local run history and proof files for review

## What happens before live changes

- The agent should show the dry-run plan first.
- You review the account, location, payload, permissions, and recovery limits.
- Safe reads can run immediately.
- Many writes need `--apply --plan-in`.
- Higher-risk or destructive actions can also require `--yes` and `--ack-irreversible`.
- Writes without saved before-state also need `--ack-no-snapshot`.

## What proof it leaves behind

- Dry-run plans can be saved with `--plan-out`.
- Approved applies can save receipts with `--receipt-out`.
- Many write flows verify success by reading the new state back after apply.
- Local run history can be reviewed with `runs list` and `runs show`.
- The docs, tests, examples, and API coverage ledger are all in this repo.

## Limits

- Many live writes still do not have saved before-state or a built-in undo path.
- You still need valid OAuth setup and Google Business Profile permissions for real account work.
- Some older Google Business Profile flows still live under legacy `v4.9` commands because Google still requires them.
- The shipped surface is broad, but it still follows the command set documented in this repo instead of every possible Google Business Profile action.

## Helpful docs

- [Browse all Google Business Profile docs](docs/README.md)
- [Quickstart](docs/quickstart.md)
- [Command guide](docs/command_reference.md)
- [Proof and verification](docs/proof.md)
- [API coverage](docs/api_coverage.md)

# Bluesky

**Capability:** Reads + careful changes

Bluesky is where profiles, posts, feeds, follows, lists, chat, moderation, and repo records shape a public social account and its network.

This skill helps an agent check Bluesky identity and account state, review posts or feeds, inspect lists and follows, and prepare record, post, moderation, or admin work before anything changes the account.

Use it for questions like: "What does this Bluesky profile show?", "Which recent posts should we review?", "What lists or follows are attached to this account?", "Can you preview a repo-record change?", or "Which moderation operation is available to this account?"

Live Bluesky work is deliberate. The tool previews API operations first, live reads need `--live`, and writes need explicit apply approval plus extra confirmation when the action is risky, irreversible, or missing a saved before-state.

A good first ask is: "Check the Bluesky connection, show my profile and recent posts, list the safest read options, and stop before any account changes."

## Start here first

- Want ideas for real Bluesky work? [What you can do with Bluesky](docs/use_cases.md)
- Need setup? [Connect your Bluesky account](docs/onboarding.md)
- Want the safety story first? [How this skill stays safe](docs/safety_model.md)

If you already want exact commands, jump straight to [Quickstart](docs/quickstart.md) and the [Command guide](docs/command_reference.md).

## What this skill helps with

- Check a profile, repo, or account state safely before deeper work.
- Read posts, feeds, lists, follows, chat, or moderation-related endpoints when your account has access.
- Inspect the documented Bluesky operation inventory before choosing an endpoint.
- Preview a post, record, or account write before anything goes live.
- Save plans, refusals, receipts, and run history for review.

## What access this skill needs

- A Bluesky handle or DID.
- A Bluesky app password for the main account path.
- Optional service URL overrides or admin tokens for non-default or moderation-only surfaces.
- The real Bluesky permissions required for the endpoint you want to use.

## Install and first run

Install slug: `bluesky`

Ask your agent to install the `bluesky` skill from `Qwayk/safe-agent-skills`.

If new skills do not appear automatically, reopen the app or attach the skill to the current workspace if your host needs that.

If your host does not let the agent install skills directly, run:

```bash
npx skills add Qwayk/safe-agent-skills@bluesky -g -y
```

Then try a safe first ask like:

```text
Check the Bluesky connection, show my profile and recent posts, list the safest read options, and stop before any account changes.
```

## How this skill stays safe

- API operations preview as dry-run plans first.
- Live reads need `--live`.
- Writes need `--live --apply`.
- Riskier or irreversible writes can also need `--yes` and `--ack-irreversible`.
- Writes without a saved before-state need `--ack-no-snapshot` before provider HTTP.
- Plans, refusals, receipts, run history, docs, and tests all stay together so you can inspect what happened.

## What it covers today

This skill covers:

- `onboarding` plus auth login, check, refresh, logout, and token helpers
- operation inventory through `api ops list`
- explicit query, procedure, and subscription calls across `app.bsky`, `com.atproto`, `chat.bsky`, and `tools.ozone` surfaces
- plan, refusal, receipt, and run-history support for write-capable flows
- raw subscription frame capture for stream-style inspection

## What happens before live changes

- The agent should show the dry-run plan first.
- You review the endpoint, body, target account, and risk level.
- Live reads use `--live`.
- Writes use `--live --apply`.
- Riskier or irreversible writes can also need `--yes` and `--ack-irreversible`.
- No-snapshot writes also need `--ack-no-snapshot`.

## What proof it leaves behind

- Dry-run plans can be saved with `--plan-out`.
- Apply receipts can be saved with `--receipt-out`.
- Run history can be reviewed with `runs list` and `runs show`.
- Refusal output makes it clear when missing approval stopped the write before provider HTTP.
- The docs, tests, proof pack, and API coverage ledger are all in this repo.

## Limits

- Many Bluesky write families still do not have rollback or saved before-state.
- Subscription output is raw websocket frame data, not a polished decoded event view.
- Real work still needs valid Bluesky credentials and the right endpoint permissions.
- This tool is safest when you start with one small read or one reviewed write plan before larger work.

## Helpful docs

- [Browse all Bluesky docs](docs/README.md)
- [Quickstart](docs/quickstart.md)
- [Command guide](docs/command_reference.md)
- [Authentication details](docs/authentication.md)
- [Troubleshooting](docs/troubleshooting.md)
- [Proof and verification](docs/proof.md)
- [API coverage](docs/api_coverage.md)

# YouTube

**Capability:** Reads + careful changes

Use this skill when you want your agent to research channels, run careful YouTube Data API checks, export clean channel datasets, download captions, and plan higher-risk YouTube changes without guessing from raw docs.

You can hand your agent jobs like channel lookups from a handle or URL, recent upload audits, search and playlist reporting, full public video inventory exports, caption downloads, and careful upload or metadata plans.

Read work stays simple. Riskier work slows down on purpose: live GET reads need explicit `--live`, write-capable actions start as dry-run plans, and higher-risk changes need explicit no-snapshot approval when the tool cannot save useful before-state first.

A good first ask is: "Check the YouTube skill is connected, resolve this channel, show the latest uploads, and stop before any changes."

## Start here first

- Want ideas for real YouTube work? [What you can do with YouTube](docs/use_cases.md)
- Need setup? [Connect your YouTube account](docs/onboarding.md)
- Want the safety story first? [How this skill stays safe](docs/safety_model.md)

If you already want exact commands, jump straight to [Quickstart](docs/quickstart.md) and the [Command guide](docs/command_reference.md).

## What this skill helps with

- Resolve a channel from a handle, URL, username, channel ID, or search query.
- Search videos, playlists, and other pinned YouTube Data API methods before making live calls.
- Export all public videos for a channel into a local analysis-ready dataset.
- Download captions or other supported media responses safely to local files.
- Plan uploads, metadata edits, playlist changes, moderation actions, and batch jobs before anything changes.
- Check auth readiness, token status, and whether you have the right access for the action you want.

## What access this skill needs

- An API key for many public read endpoints.
- An OAuth client secrets file for private reads, uploads, and most write-capable actions.
- Today, a working local token file if you want private reads or write-capable OAuth work right away, because the built-in login and token-set helpers still stop at the planning gate.
- The right YouTube scopes and channel permissions for the target action.

## Install and first run

Install slug: `youtube`

Ask your agent to install the `youtube` skill from `Qwayk/safe-agent-skills`.

If new skills do not appear automatically, reopen the app or attach the skill to the current workspace if your host needs that.

If your host does not let the agent install skills directly, run:

```bash
npx skills add Qwayk/safe-agent-skills@youtube -g -y
```

Then try a safe first ask like:

```text
Connect the YouTube skill, resolve this channel, show the recent uploads, and stop before any changes or uploads.
```

## How this skill stays safe

- Offline plans are the default.
- Live provider GET reads need explicit `--live`.
- `channels export --live` writes only local dataset files under `--out-dir`; it does not change YouTube state, and it protects non-empty folders unless you choose `--overwrite`, `--yes`, or `--resume`.
- Non-GET API calls, uploads, demo writes, write jobs, and local token writes need explicit approval. When there is no saved before-state, they also need `--ack-no-snapshot`.
- Delete methods also need `--ack-irreversible`.
- `auth login` and `auth token set` still stop at the plan/refusal step today instead of writing token state automatically.
- The pinned discovery snapshot, docs, tests, proof files, and coverage ledger all live in this repo so you can inspect what the agent is using.

## What it covers today

This skill covers:

- local auth checks, token status, and safe token inspection
- explicit `api <resource.method>` planning for the pinned YouTube Data API v3 surface
- live GET reads when you add `--live`
- media upload planning and supported media downloads
- channel resolve and full public channel export workflows
- batch jobs, demo safety flows, and local run history

## What happens before live changes

- The agent should show the dry-run plan first.
- You review the channel, target resource, payload, permissions, and risk before apply.
- Read-only GET calls can run live with `--live`.
- Local dataset exports use `--live` and may also need `--overwrite` or `--resume` for the output folder.
- Non-GET methods and uploads need `--apply --yes --ack-no-snapshot` when no saved before-state exists.
- Delete methods also need `--ack-irreversible`.
- `auth login` and `auth token set` remain planning-only today, so they stop before writing local token state.

## What proof it leaves behind

- Dry-run plans can be saved with `--plan-out`.
- Commands that really apply can save receipts with `--receipt-out` when the command supports it.
- Blocked apply attempts return an explicit refusal that proves nothing changed.
- Local run history can be reviewed under `.state/runs/`.
- The proof pack includes redacted version, auth, channel, search, upload-plan, and download-plan examples.

## Limits

- An API key is not enough for many private, upload, or write-capable endpoints.
- The built-in OAuth login and token-set helpers do not write `.state/token.json` automatically yet.
- Most write-capable actions do not have automatic rollback support.
- Exports and downloads write local files, so you still need to choose the destination folder carefully.

## Helpful docs

- [Browse all YouTube docs](docs/README.md)
- [Quickstart](docs/quickstart.md)
- [Command guide](docs/command_reference.md)
- [Authentication details](docs/authentication.md)
- [Jobs and batch work](docs/jobs_and_batches.md)
- [Proof and verification](docs/proof.md)
- [API coverage](docs/api_coverage.md)

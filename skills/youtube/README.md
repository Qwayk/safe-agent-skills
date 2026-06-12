# YouTube

**Capability:** Reads + careful changes

Use this skill when you want an AI agent to work with YouTube safely: research channels, check official YouTube Data API results, export channel video lists, download caption tracks you have access to, and prepare careful plans for uploads or metadata changes.

You can hand your agent jobs like channel lookups from a handle or URL, recent upload audits, search and playlist reporting, exporting public video lists, caption downloads when the API allows them, and careful upload or metadata plans.

It is best for work where you want the agent to check first and change later. Real YouTube reads run only when you ask for them clearly, and changes such as uploads, playlist edits, metadata updates, and deletes need clear approval before the tool can try them.

A good first ask is: "Check the YouTube skill is connected, resolve this channel, show the latest uploads, and stop before any changes."

## Start here first

- Want ideas for real YouTube work? [What you can do with YouTube](docs/use_cases.md)
- Need setup? [Connect your YouTube account](docs/onboarding.md)
- Want the safety story first? [How this skill stays safe](docs/safety_model.md)

If you already want exact commands, jump straight to [Quickstart](docs/quickstart.md) and the [Command guide](docs/command_reference.md).

## What this skill helps with

- Resolve a channel from a handle, URL, username, channel ID, or search query.
- Search videos, playlists, and other pinned YouTube Data API methods before making live calls.
- Export public videos returned by a channel's uploads playlist into a local analysis-ready dataset, subject to YouTube API access, quota, and paging limits.
- Download caption tracks or other supported media responses safely to local files when you have the right access.
- Plan uploads, metadata edits, playlist changes, moderation actions, and batch jobs before anything changes.
- Check auth readiness, token status, and whether you have the right access for the action you want.

## What access this skill needs

- An API key for many public read endpoints.
- An OAuth client secrets file for private reads, uploads, and most write-capable actions.
- Today, a working local token file if you want private reads or OAuth actions that can change YouTube right away, because the built-in login and token-set helpers still stop at the plan/refusal step.
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

- Most commands start as a plan, so you can review the target and action first.
- Live YouTube GET reads only run when you add `--live`.
- `channels export --live` writes local dataset files under `--out-dir`; it does not change anything on YouTube, and it protects non-empty folders unless you choose `--overwrite`, `--yes`, or `--resume`.
- Captions and other media downloads must use `--download-to`, so files are saved only to the path you choose.
- YouTube writes and uploads need `--apply --yes --ack-no-snapshot` when the tool has no saved state to restore from.
- Delete methods also need `--ack-irreversible`.
- `auth login`, `auth token set`, demo writes, and write jobs are planning-only flows today; they do not write local token state or perform real YouTube job writes.
- The pinned discovery snapshot, docs, tests, saved examples, and API method list all live in this repo so you can inspect what the agent is using.

## What it covers today

This skill covers:

- local auth checks, token status, and safe token inspection
- explicit `api <resource.method>` planning for the pinned YouTube Data API v3 methods
- live GET reads when you add `--live`
- media upload planning and supported media downloads
- channel resolve and public channel export workflows
- batch jobs, demo safety flows, and local run history

## What happens before live changes

Read-only work is simple: the agent can show a plan first, then run the real YouTube GET read with `--live`.

A channel export is different from a YouTube change. `channels export --live` creates local files in `--out-dir`; it does not edit your channel. If the output folder already has files, the tool refuses unless you choose `--resume`, `--overwrite`, or global `--yes`.

For real YouTube changes, the agent should show the dry-run plan first. If the plan is right, non-GET methods and uploads need `--apply --yes --ack-no-snapshot`. Delete methods also need `--ack-irreversible`.

`auth login` and `auth token set` still stop at the plan/refusal step today, so they do not write `.state/token.json` automatically.

## What proof it leaves behind

- Dry-run plans can be saved with `--plan-out`.
- Commands that really apply can save receipts with `--receipt-out` when the command supports it.
- Blocked apply attempts return an explicit refusal that proves nothing changed.
- Local run history can be reviewed under `.state/runs/`.
- The saved examples include redacted version, auth, channel, search, upload-plan, and download-plan output.

## Limits

- An API key is not enough for many private, upload, or write-capable endpoints.
- The built-in OAuth login and token-set helpers do not write `.state/token.json` automatically yet.
- Most write-capable actions do not have a built-in undo path.
- Caption downloads need a valid caption track ID and the right YouTube access; the official API does not let this tool download captions for every public video.
- Exports and downloads write local files, so you still need to choose the destination folder carefully.

## Helpful docs

- [Browse all YouTube docs](docs/README.md)
- [Quickstart](docs/quickstart.md)
- [Command guide](docs/command_reference.md)
- [Authentication details](docs/authentication.md)
- [Jobs and batch work](docs/jobs_and_batches.md)
- [Proof and verification](docs/proof.md)
- [API coverage](docs/api_coverage.md)

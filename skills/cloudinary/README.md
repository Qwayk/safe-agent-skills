# Cloudinary

**Capability:** Reads + careful changes

Cloudinary is where image, video, folder, upload, delivery, streaming, and account settings meet the media files people actually see in products, campaigns, and sites.

This skill helps an agent inspect assets and account setup, check folders, tags, metadata, upload presets, streaming or player settings, and prepare Cloudinary changes before they touch live media or account resources.

Use it for questions like: "What do we know about this asset?", "Which upload presets or metadata fields exist?", "Can you check the folders and tags?", "Can you plan a restore?", or "Can you preview this product environment change first?"

Cloudinary has product-level and account-level credentials. Reads can run directly after the right credentials are available; writes start as plans and need stronger approval before Cloudinary receives a live change.

A good first ask is: "Check my Cloudinary product and account setup, show one asset detail example, list the relevant upload operations, and stop before any writes."

## Start here first

- Want ideas for real Cloudinary work? [What you can do with Cloudinary](docs/use_cases.md)
- Need setup? [Connect your Cloudinary account](docs/onboarding.md)
- Want the safety story first? [How this skill stays safe](docs/safety_model.md)

If you already want exact commands, jump straight to [Quickstart](docs/quickstart.md) and the [Command guide](docs/command_reference.md).

## What this skill helps with

- Review asset details, folders, tags, metadata fields, upload presets, streaming profiles, and player profiles.
- Prepare plans for uploads, renames, tag changes, context changes, structured metadata updates, restores, and account-level work.
- Run exposed Analyze API jobs and review the results.
- Manage product environments, users, user groups, roles, and custom policies when your Cloudinary plan allows it.
- Keep sensitive or binary results in local files instead of printing them into chat.

## What access this skill needs

- Product credentials for Upload, Admin, Analyze, Video Live Streaming, Player Profiles, and Video Config:
  - `CLOUDINARY_CLOUD_NAME`
  - `CLOUDINARY_API_KEY`
  - `CLOUDINARY_API_SECRET`
- Account credentials for Provisioning and most Permissions commands:
  - `CLOUDINARY_ACCOUNT_ID`
  - `CLOUDINARY_ACCOUNT_API_KEY`
  - `CLOUDINARY_ACCOUNT_API_SECRET`
- Regional hosts only if Cloudinary gave you a different host.

## Install and first run

Install slug: `cloudinary`

Ask your agent to install the `cloudinary` skill from `Qwayk/safe-agent-skills`.

If new skills do not appear automatically, reopen the app or attach the skill to the current workspace if your host needs that.

If your host does not let the agent install skills directly, run:

```bash
npx skills add Qwayk/safe-agent-skills@cloudinary -g -y
```

Then try a safe first ask like:

```text
Check my Cloudinary product and account setup, show one asset detail example, list the relevant upload operations, and stop before any writes.
```

## How this skill stays safe

- Reads can run after valid Cloudinary access is available.
- Writes return a dry-run plan unless you add apply approval.
- Approved writes need `--apply --yes`.
- Delete-like commands and access-key commands also need `--ack-irreversible`.
- When no saved snapshot is available, write apply requires explicit no-snapshot approval before Cloudinary credentials are used for the write or Cloudinary HTTP.
- Sensitive or binary results must go to `--out` inside `--project-dir`.

## What it covers today

This skill ships explicit Cloudinary REST operations across:

- Upload
- Admin
- Provisioning
- Permissions
- Analyze
- Live Streaming
- Player Profiles
- Video Config

The non-REST Transformation URL API is intentionally out of scope.

## What happens before live changes

- The agent should show the dry-run plan first.
- You review the operation, target path, body, account scope, output path, and recovery limit.
- Live apply needs the required approval gates.
- Restore and backup-delete operations are explicit commands, not a blanket rollback system.
- If no saved snapshot exists, live apply also needs explicit no-snapshot approval.

## What proof it leaves behind

- Dry-run plans can be saved.
- Approved supported writes can leave receipts.
- Local run history can include `plan.json`, `receipt.json`, `audit.jsonl`, and `summary.md`.
- The docs, tests, proof pack, and API coverage ledger live in this repo.

## Limits

- Cloudinary plan and account permissions decide which areas are available.
- Sensitive and binary output is file-only by design.
- Backup download is a read; restore and backup-delete are separate write operations with their own approval gates.
- The tool does not provide a generic rollback command or snapshot for every Cloudinary write.

## Helpful docs

- [Browse all Cloudinary docs](docs/README.md)
- [Quickstart](docs/quickstart.md)
- [Command guide](docs/command_reference.md)
- [Authentication details](docs/authentication.md)
- [Proof and verification](docs/proof.md)
- [API coverage](docs/api_coverage.md)

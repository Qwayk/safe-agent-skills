# Quickstart

## Install

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e .
```

## Create `.env`

```bash
cloudinary-safe-agent-cli onboarding
```

That command copies `.env.example` to `.env` when `.env` does not exist.
Then fill your Cloudinary values in `.env`.

## Check access

```bash
cloudinary-safe-agent-cli --output json auth check
```

`auth check` does three things:
- calls product `GET /ping` when product credentials are set
- calls account provisioning `GET /sub_accounts` when account credentials are set
- marks public permissions schema and validate endpoints as ready without credentials

## Discover what is shipped

```bash
cloudinary-safe-agent-cli --output json operations list --area upload --limit 10
cloudinary-safe-agent-cli --output json operations show --area upload --op upload-signed
```

`operations list` hides deprecated and sensitive commands unless you opt in with `--include-deprecated` or `--include-sensitive`.

## Run a read

```bash
cloudinary-safe-agent-cli --output json operations admin \
  resources-get-details-of-a-single-resource-by-public-id \
  --path-param resource_type=image \
  --path-param type=upload \
  --path-param public_id=sample
```

## Recover from backup (explicit commands only)

There is no generic rollback command in this tool.
Use the restore commands directly:

```bash
cloudinary-safe-agent-cli --output json \
  --plan-out plans/restore-sample.json \
  operations admin resources-restore-resources-by-public-id \
  --path-param resource_type=image \
  --path-param type=upload \
  --path-param public_id=sample-public-id \
  --body-json-file examples/resources-restore-by-public-id.sample.json
```

Attempt the restore plan:

```bash
cloudinary-safe-agent-cli --output json \
  --apply --yes --ack-no-snapshot \
  --plan-in plans/restore-sample.json \
  operations admin resources-restore-resources-by-public-id \
  --path-param resource_type=image \
  --path-param type=upload \
  --path-param public_id=sample-public-id
```

If the reviewed plan still matches, `--ack-no-snapshot` allows the restore to reach Cloudinary and record a receipt even though this write path does not save a snapshot first.

Download a specific backed-up version to inspect it locally:

```bash
cloudinary-safe-agent-cli --output json \
  operations upload download-backup \
  --query public_id=sample-public-id \
  --query version_id=123 \
  --query resource_type=image \
  --query type=upload \
  --out artifacts/sample-backup.bin \
  --overwrite
```

## Plan a write

```bash
cloudinary-safe-agent-cli --output json \
  --plan-out plans/create-sub-account.json \
  operations provisioning createproductenvironment \
  --body-json-file examples/create-sub-account.sample.json
```

Without `--apply`, write commands return a dry-run plan.

## Attempt a write after review

```bash
cloudinary-safe-agent-cli --output json \
  --apply --yes --ack-no-snapshot \
  --plan-in plans/create-sub-account.json \
  operations provisioning createproductenvironment \
  --body-json-file examples/create-sub-account.sample.json
```

When no saved snapshot exists, add `--ack-no-snapshot` after review so the write can reach Cloudinary and record a receipt. Delete-like actions and access-key actions also need `--ack-irreversible`.

## Save sensitive or binary results

```bash
cloudinary-safe-agent-cli --output json \
  --project-dir . \
  operations provisioning getaccesskeys \
  --path-param sub_account_id=sub123 \
  --out artifacts/access-keys.json
```

`--out` must stay inside `--project-dir`.

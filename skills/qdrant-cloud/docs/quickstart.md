# Quickstart

Want the short non-technical path first? Start with [What you can do with Qdrant Cloud](use_cases.md), [Connect your Qdrant Cloud account](onboarding.md), and [How this skill stays safe](safety_model.md).

This page is for the exact commands.

Because this tool is safety-first, remember one important rule: nothing reaches the real Qdrant Cloud API unless you add `--live`.

## 1) Install

```bash
python3 --version
python3 -m venv .venv
.venv/bin/python -m pip install -e .
```

Optional (developer tooling):

```bash
.venv/bin/python -m pip install -e '.[dev]'
```

## 2) Configure

Copy `.env.example` to `.env`, then fill your values from [Configuration](configuration.md).

If `QDRANT_CLOUD_API_KEY` contains shell-special characters such as `|`, quote it:

```env
QDRANT_CLOUD_API_KEY='your_real_key_here'
```

## 3) First safe checks

```bash
qdrant-cloud-api-tool --output json --version
qdrant-cloud-api-tool --env-file .env --output json auth check
qdrant-cloud-api-tool --env-file .env --output json --live auth check
qdrant-cloud-api-tool --env-file .env --output json --live account-v1 list-accounts
```

## 4) Common inventory commands

```bash
qdrant-cloud-api-tool --env-file .env --output json --live account-v1 list-accounts
qdrant-cloud-api-tool --env-file .env --output json --live cluster-v1 list-clusters --account-id ACCOUNT_ID
qdrant-cloud-api-tool --env-file .env --output json --live cluster-backup-v1 list-backups --account-id ACCOUNT_ID
qdrant-cloud-api-tool --env-file .env --output json --live cluster-backup-v1 list-backup-schedules --account-id ACCOUNT_ID
```

## 5) Billing, access, and monitoring reads

```bash
qdrant-cloud-api-tool --env-file .env --output json --live billing-v1 list-invoices --account-id ACCOUNT_ID
qdrant-cloud-api-tool --env-file .env --output json --live auth-v1 list-management-keys --account-id ACCOUNT_ID
qdrant-cloud-api-tool --env-file .env --output json --live iam-v1 list-roles --account-id ACCOUNT_ID
qdrant-cloud-api-tool --env-file .env --output json --live monitoring-v1 get-cluster-summary-metrics --account-id ACCOUNT_ID --cluster-id CLUSTER_ID
```

## 6) Write planning rules

If you move from reads into live Qdrant Cloud changes:

- start with the dry-run plan first
- use `--live --apply` for confirmed write attempts
- add `--yes` when the command requires it
- add `--ack-irreversible` for destructive work
- add `--ack-spend-money` for billing or payment actions
- expect explicit no-snapshot approval too when the write has no saved before-state or provider backup

## 7) Provider backup or restore examples

These are the narrow live workflows that already map to explicit provider recovery commands:

```bash
qdrant-cloud-api-tool --env-file .env --output json cluster-backup-v1 restore-backup --account-id ACCOUNT_ID --backup-id BACKUP_ID --request-json request.json --plan-out restore.plan.json
qdrant-cloud-api-tool --env-file .env --output json --live --apply cluster-backup-v1 restore-backup --account-id ACCOUNT_ID --backup-id BACKUP_ID --request-json request.json --receipt-out restore.receipt.json
```

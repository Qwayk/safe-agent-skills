# Quickstart

This page helps you get one useful Qdrant Cloud result quickly, without turning the quickstart into a full command manual.

If you are still deciding what to ask, start with [What you can do with Qdrant Cloud](use_cases.md). If setup is not done yet, read [Connect your Qdrant Cloud account](onboarding.md).

A good first ask is:

> Which accounts, clusters, and releases exist right now?

## What you will do first

1. Make sure the local tool can run.
2. Check setup or connection status.
3. Run one safe read that proves the agent can get useful data.
4. Stop before any write, spend, upload, delete, message, or public change unless you have reviewed the plan.

## 1. Install or open the tool

Use this when you are running the tool from a local checkout. If your agent host already installed the skill, you can skip this part.

```bash
python3 --version
python3 -m venv .venv
.venv/bin/python -m pip install -e .
```

```bash
.venv/bin/python -m pip install -e '.[dev]'
```

## 2. Check setup

If you do not have credentials yet, run onboarding first and fill only the values the tool asks for. Never paste secrets into chat.

```env
QDRANT_CLOUD_API_KEY='your_real_key_here'
```

```bash
qdrant-cloud-api-tool --output json --version
qdrant-cloud-api-tool --env-file .env --output json auth check
qdrant-cloud-api-tool --env-file .env --output json --live auth check
qdrant-cloud-api-tool --env-file .env --output json --live account-v1 list-accounts
```

## 3. Run one safe first read

This should be a small read-only request. The goal is to prove the connection and get one result you can understand.

```bash
qdrant-cloud-api-tool --env-file .env --output json --live account-v1 list-accounts
qdrant-cloud-api-tool --env-file .env --output json --live cluster-v1 list-clusters --account-id ACCOUNT_ID
qdrant-cloud-api-tool --env-file .env --output json --live cluster-backup-v1 list-backups --account-id ACCOUNT_ID
qdrant-cloud-api-tool --env-file .env --output json --live cluster-backup-v1 list-backup-schedules --account-id ACCOUNT_ID
```

```bash
qdrant-cloud-api-tool --env-file .env --output json --live billing-v1 list-invoices --account-id ACCOUNT_ID
qdrant-cloud-api-tool --env-file .env --output json --live auth-v1 list-management-keys --account-id ACCOUNT_ID
qdrant-cloud-api-tool --env-file .env --output json --live iam-v1 list-roles --account-id ACCOUNT_ID
qdrant-cloud-api-tool --env-file .env --output json --live monitoring-v1 get-cluster-summary-metrics --account-id ACCOUNT_ID --cluster-id CLUSTER_ID
```

After this, ask the agent to summarize what came back in plain English and name anything missing, empty, or blocked.

## 4. Stop before changes

For anything that could change an account, spend money, upload files, send messages, publish content, delete data, or update settings, ask for a dry-run plan first.

Only apply a change after the plan names the exact target, the risk, the approval flags, and the expected proof.

## What good output looks like

A useful first result should tell you:

- what account, workspace, project, page, item, or public data was checked
- whether the tool connected successfully
- what the first read returned
- what the result means in normal language
- what is safe to do next
- where the plan, receipt, export, or saved file lives if the command created one

## Where to go next

- For real examples, read [What you can do](use_cases.md).
- For setup details, read [Connect your Qdrant Cloud account](onboarding.md).
- For exact command options, read [Command reference](command_reference.md).
- For approval rules and limits, read [How this skill stays safe](safety_model.md).

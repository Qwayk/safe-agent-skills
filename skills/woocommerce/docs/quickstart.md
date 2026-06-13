# Quickstart

This page helps you get one useful WooCommerce result quickly, without turning the quickstart into a full command manual.

If you are still deciding what to ask, start with [What you can do with WooCommerce](use_cases.md). If setup is not done yet, read [onboarding.md](onboarding.md).

A good first ask is:

> Check the WooCommerce connection, then show the store settings that matter for this review.

## What you will do first

1. Make sure the local tool can run.
2. Check setup or connection status.
3. Run one safe read that proves the agent can get useful data.
4. Stop before any write, spend, upload, delete, message, or public change unless you have reviewed the plan.

## 1. Open the tool

If the skill is already installed in your agent host, start there. If you are working from source, follow the install notes in the repository before running commands.

## 2. Check setup

If you do not have credentials yet, run onboarding first and fill only the values the tool asks for. Never paste secrets into chat.

```bash
qwayk-woocommerce-safe-agent-cli --output json --version
qwayk-woocommerce-safe-agent-cli --output json onboarding
qwayk-woocommerce-safe-agent-cli --output json auth check
qwayk-woocommerce-safe-agent-cli --output json operations list
```

## 3. Run one safe first read

This should be a small read-only request. The goal is to prove the connection and get one result you can understand.

```bash
qwayk-woocommerce-safe-agent-cli --output json products list --all --per-page 100
qwayk-woocommerce-safe-agent-cli --output json orders get --id 123
qwayk-woocommerce-safe-agent-cli --output json payment-gateways list
```

After this, ask the agent to summarize what came back in plain English and name anything missing, empty, or blocked.

## 4. Stop before changes

For anything that could change an account, spend money, upload files, send messages, publish content, delete data, or update settings, ask for a dry-run plan first.

Only apply a change after the plan names the exact target, the risk, the approval flags, and the expected proof.

A first change should stay as a preview or dry run until you approve it:

```bash
qwayk-woocommerce-safe-agent-cli --output json coupons create \
  --body-json '{"code":"SAVE10","discount_type":"percent","amount":"10"}' \
  --plan-out plan.json
```

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
- For setup details, read [onboarding.md](onboarding.md).
- For exact command options, read [Command reference](command_reference.md).
- For approval rules and limits, read [How this skill stays safe](safety_model.md).

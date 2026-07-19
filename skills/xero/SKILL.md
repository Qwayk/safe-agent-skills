---
name: xero
description: Use when the user asks to inspect, explain, export, create, update, or safely manage Xero accounting, payroll, projects, files, assets, bank feeds, finance, eInvoicing, or Xero App Store data.
---

# Xero

Use `qwayk-xero-safe-agent-cli` for the provider work. It exposes fixed commands only and enforces the target, privacy, and write-review checks locally.

## Start

1. Run `qwayk-xero-safe-agent-cli --version` if availability is unknown. If it is missing, explain that installing the skill did not install the Python CLI. From the bundled or cloned `qwayk-xero-safe-agent-cli` folder, guide the user through `python3.12 -m venv .venv`, `.venv/bin/python -m pip install -e .`, and `.venv/bin/qwayk-xero-safe-agent-cli onboarding` before auth.
2. Map the request to a fixed command. Run `inventory list --spec <family>` or `inventory show --command <name>` when the exact input, scope, region, or access gate is unclear.
3. Refuse raw requests, arbitrary endpoints, SDK pass-through, or browser automation. If no fixed command exists, explain the coverage limit.

## Connect the exact target

Use PKCE by default. Check `auth status --profile pkce` and `tenant show --profile pkce`. If setup is missing, guide the user through `onboarding`, minimum-scope `auth start`, `auth exchange`, `tenant list`, and exact `tenant select`.

Never request a token, client secret, authorization code, PKCE verifier, or `.env` contents in chat.

Use global `--auth-profile custom` only for an already configured paid single-organisation Custom Connection. App Store fixed commands use their separate non-tenanted token automatically. Never substitute one auth profile for another after an access failure.

Treat the four App Store billing commands as legacy XASS transition access. Xero deprecated XASS in March 2026 and required existing customers to migrate by 1 July 2026; the documented endpoints do not prove live entitlement or behavior.

## Reads

Run the smallest fixed read that answers the question. For financial, bank, payroll, tax, contact, file, or billing details, use global `--protected-output <private-path>` and summarize the safe stdout result. Do not paste full sensitive provider data into chat.

## Writes

Every non-GET command must create a saved plan first:

```bash
qwayk-xero-safe-agent-cli --plan-out <private-plan.json> <fixed-command> --input <private-input.json>
```

Explain the exact tenant, target, input, risk flags, before-state, no-snapshot warning, and verification. Wait for the user to approve that plan.

Apply only the same saved plan. Use the flags the plan requires: `--approve`, `--approve-high-risk`, and `--ack-no-snapshot` are separate decisions. Save a receipt with `--receipt-out`.

After apply, report what Xero accepted and what verification proved. Do not turn `accepted_not_stronger_state` into a claim that something is posted, paid, sent, completed, reconciled, delivered, or compliant.

## Limits

Treat regional, partner-only, paid, certification-only, superseded, callback-only, and unavailable areas exactly as `inventory show` and `docs/api_coverage.md` classify them. This skill does not host webhooks, expose guessed Practice Manager, Xero HQ, or Xero Tax commands, or promise generic rollback.

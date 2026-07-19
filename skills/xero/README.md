# Xero

The Xero API tool for agents helps you understand and manage the work behind your books: invoices, bills, payments, contacts, bank transactions, reports, payroll, projects, files, and account settings.

You can ask your agent to check unpaid invoices, explain a balance sheet, find a contact, review bank transactions, prepare an invoice update, inspect a pay run, or collect project time entries. It can also help with regional payroll and partner-only Xero services when your organisation and app have the required access.

For example: "Show me overdue customer invoices," "Explain what changed in this month's profit and loss," "Check this employee's leave balance," or "Prepare a correction to this draft invoice and show me the full effect first."

The agent begins by finding your connected Xero organisations and asking you to select the exact one. It can read the selected organisation and explain what it found. Before it changes financial, payroll, bank, file, billing, tax, or employment data, it saves the available before-state, shows you a plan, and waits for approval. When Xero offers no safe before-state, the plan says so clearly and needs explicit no-snapshot approval.

## Start here first

- Want a useful first check? Ask: "List my connected Xero organisations, let me choose one, then show the organisation summary and unpaid invoices without changing anything."
- Need setup? [Connect a Xero organisation](docs/onboarding.md)
- Want more ideas? [See what you can ask your agent](docs/use_cases.md)
- Want to understand approvals? [See what happens before Xero changes](docs/safety_model.md)

If you already want exact commands, use [Quickstart](docs/quickstart.md) and the [Command guide](docs/command_reference.md).

## What your agent can do

- Check invoices, credit notes, payments, bank activity, contacts, budgets, journals, and financial reports.
- Review payroll employees, leave, timesheets, pay runs, payslips, and settings for Australia, New Zealand, or the United Kingdom.
- Read projects, tasks, time entries, fixed assets, and files connected to a Xero organisation.
- Prepare a fixed Xero API change, show the exact tenant and target, and apply only an approved saved plan.
- Keep a local plan and receipt that explain what was proposed, what Xero accepted, and what was verified.

## What happens before live changes

Reads can run after you select the tenant and choose where sensitive details should go. Normal summaries hide bank details, tax numbers, employee details, contact details, and other sensitive values. You can send the full result to a protected local file when you need it.

Writes never run from a new command alone. The agent first creates a saved plan bound to the command, tenant, target, input hash, and before-state. Apply uses that exact plan. Financial, payroll, bank-feed, destructive, bulk, file, auth, billing, legal, tax, and employment changes need an extra acknowledgement. A receipt records Xero's response and the follow-up check without claiming that an accepted request is already posted, paid, sent, completed, or reconciled.

## What access this tool needs

- The normal local flow needs a Xero app client ID and an exact localhost redirect URI. It uses OAuth 2.0 authorization code with PKCE, so the default flow does not need a client secret.
- The authorisation asks for `offline_access` plus only the scopes needed for the commands you chose. New accounting connections use Xero's granular scopes.
- You must discover and select the tenant before any tenanted call. The tool never chooses the first organisation for you.
- Custom Connections are optional, paid, and limited to one organisation. App Store billing uses a separate non-tenanted client-credentials token. Xero deprecated Xero App Store Subscriptions (XASS) in March 2026, stopped accepting new apps into XASS after 4 December 2025, and required existing customers to migrate by 1 July 2026. The four pinned commands remain only for legacy transition needs; live entitlement and behavior are unverified.
- Bank Feeds, Finance, Payment Services, eInvoicing, journals, and Practice Manager can require certification, partner approval, a paid product, or commercial terms.

Never paste access tokens, refresh tokens, client secrets, authorisation codes, or PKCE verifiers into chat.

## Install and first run

Install slug: `xero`

Ask your agent to install the `xero` skill from `Qwayk/safe-agent-skills`.

If your host does not let the agent install skills directly, run:

```bash
npx skills add Qwayk/safe-agent-skills@xero -g -y
```

The skill tells the agent how to use the tool; it does not install the Python CLI by itself. From the bundled or cloned `qwayk-xero-safe-agent-cli` folder, install the CLI with Python 3.12:

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -e .
.venv/bin/qwayk-xero-safe-agent-cli --version
.venv/bin/qwayk-xero-safe-agent-cli onboarding
```

Then try a first ask like:

```text
Connect my Xero app with the minimum scopes, list the organisations I connected, and let me choose one before reading anything else.
```

## What it covers today

The tool covers the official Xero Accounting, Assets, Bank Feeds, Files, Finance, Identity, Payroll AU, Payroll AU Timesheets 2.0, Payroll NZ, Payroll UK, Projects, and App Store specifications pinned at release 16.1.0. It also adds the two documented eInvoicing registration commands.

The complete ledger has 474 fixed commands. Five older AU Payroll compatibility operations point to their current replacements instead of becoming duplicate commands. [See the complete API coverage and classifications](docs/api_coverage.md).

## Limits

- Live Xero account behavior has not been tested in this source build. Local generation, safety, examples, packaging, and installed behavior are tested without credentials or provider requests.
- Practice Manager 3.1, Xero HQ, and Xero Tax are documented but not exposed as guessed command families because they are access-controlled and the pinned OpenAPI release has no machine-readable contracts for them.
- Webhooks are callback-only. This tool documents signature verification but does not host callbacks or pretend they are CLI commands.
- Some commands are regional, paid, partner-only, certification-only, scheduled for retirement, or dependent on a Xero product and user role.
- The current Xero API reference still documents four XASS endpoints, but that does not make XASS normally available again or prove that a particular legacy app can call them.
- Xero's current Developer Terms prohibit API data from being used to train or contribute to AI or machine-learning models. This tool is for user-directed operational work and does not provide a training-data workflow. Review the [official Xero policy FAQ](https://developer.xero.com/faq) for the governing terms.
- There is no generic rollback. The tool uses exact before-state and follow-up reads when the API supports them; otherwise it gives a no-snapshot warning before apply.

## Helpful docs

- [Browse all docs](docs/README.md)
- [Quickstart](docs/quickstart.md)
- [Command guide](docs/command_reference.md)
- [Proof and verification](docs/proof.md)
- [API coverage](docs/api_coverage.md)

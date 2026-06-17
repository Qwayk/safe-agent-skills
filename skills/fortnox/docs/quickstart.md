# Quickstart

Start with a small Fortnox read: company details first, then a short customer or invoice list you can recognize by eye. That gives the agent a safe first result before it plans invoice, supplier bill, bookkeeping, payroll, or stock changes.

Need more ideas? See [What you can ask the Fortnox skill to do](use_cases.md). Need setup help? See [Set up your Fortnox connection step by step](onboarding.md).

A good first ask is:

> Check that Fortnox is connected, show our company details, list a few customers and invoices, and stop before any change that would affect live records.

## What you will do first

1. Make sure the local tool can run.
2. Connect Fortnox without pasting secrets into chat.
3. Run one small read and confirm it is the right tenant.
4. Stop before creating, updating, booking, sending, deleting, or uploading anything.

## 1. Install or open the tool

Use this when you are running the tool from a local checkout. If your agent host already installed the skill, you can skip this part.

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
```

## 2. Check setup

If you do not have Fortnox credentials yet, run onboarding first and fill only the local values the tool asks for. Keep Fortnox client secrets, access tokens, refresh tokens, and `.env` contents out of chat.

```bash
fortnox-api-tool onboarding
```

Fill these fields in `.env`:

- `FORTNOX_CLIENT_ID`
- `FORTNOX_CLIENT_SECRET`
- `FORTNOX_REDIRECT_URI`

Then ask Fortnox for the login URL:

```bash
fortnox-api-tool auth login
```

Open the returned `authorize_url`, approve the app, then run:

```bash
fortnox-api-tool auth exchange-code --code <authorization_code> --state <state>
fortnox-api-tool auth check
```

## 3. Run one small first read

Start with a read you can verify by eye. You want to see the right company or tenant before asking the agent to inspect invoices, supplier invoices, accounting records, payroll, or stock.

```bash
fortnox-api-tool company-information get
```

After this, ask the agent to summarize what came back in normal words and say whether the account looks like the right Fortnox tenant.

Useful next reads after the first company check:

```bash
fortnox-api-tool customers list --filter active --sort-by name
fortnox-api-tool suppliers list --last-modified 2026-06-01
fortnox-api-tool invoices list
```

## 4. Stop before anything risky

Ask for a reviewed plan before invoice accruals, supplier bill work, bookkeeping actions, customer or supplier updates, payroll/time changes, stock changes, file uploads, sends, bookings, deletes, or irreversible actions.

When you want to prepare a change, generate a dry-run plan and stop:

```bash
fortnox-api-tool --plan-out invoice-accrual.plan.json invoice-accruals create --json-file docs/examples/payloads/invoice_accrual.create.json
```

`jobs run` is not part of the first run yet. It stays unsupported until real registry-backed rows exist.

## What a useful first result includes

A good first Fortnox result should make these things clear:

- which company or tenant was checked
- whether the connection worked
- what records came back from Fortnox
- whether the result looks empty, blocked, or unexpected
- what is safe to inspect next
- whether any plan, receipt, or saved output was written

## Where to go next

- For real examples, read [What you can ask this skill to do](use_cases.md).
- For setup details, read [Set up your Fortnox connection step by step](onboarding.md).
- For exact command options, read [Command reference](command_reference.md).
- For approval rules and limits, read [How this skill stays safe](safety_model.md).

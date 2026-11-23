# Quickstart

Install the skill and [connect your account](onboarding.md). For a local checkout, use Python 3.12 or newer:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
```

From the tool folder, check the connection and get the first page of domains:

```bash
namebright-safe-cli --output json --version
namebright-safe-cli --output json auth check
namebright-safe-cli --output json domains list --domains-per-page 5
```

To see domains waiting to move into your account:

```bash
namebright-safe-cli --output json inbound-push list-pending
```

## Prepare a change

Ask the agent to show the exact domain and setting before it applies a change. For example, to lock a domain:

```bash
namebright-safe-cli --output json --plan-out plan.json domains update --domain example.com --opt-out-of-lock false --locked true
```

After approval, use the same NameBright settings and command values:

```bash
namebright-safe-cli --output json --apply --yes --plan-in plan.json --receipt-out plan.receipt.json --ack-high-risk domains update --domain example.com --opt-out-of-lock false --locked true
```

Use a new filename for the receipt. See the [command guide](command_reference.md) for purchases, order checks, and other commands. The [approval guide](safety_model.md) explains what to do when NameBright's reply leaves the result open.

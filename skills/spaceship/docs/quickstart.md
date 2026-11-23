# Quickstart

[Connect your Spaceship account](onboarding.md) before using a command that reads or changes the account. For a local checkout, install the command with Python 3.12 or newer:

```bash
python3.12 -m venv .venv
. .venv/bin/activate
python -m pip install .
qwayk-spaceship-safe-agent-cli --output json --version
```

Use your own `--env-file` on each command if you chose a file other than `.env`.

```bash
qwayk-spaceship-safe-agent-cli --output json auth check
qwayk-spaceship-safe-agent-cli --output json domains list --take 10
qwayk-spaceship-safe-agent-cli --output json domains price example.com
```

## Prepare a renewal

Get the current expiration date with `domains get example.com`. Save the date as `currentExpirationDate` and the number of years as `years` in a private `renewal.json`. Create a plan:

```bash
qwayk-spaceship-safe-agent-cli --output json --plan-out renewal-plan.json \
  domains renew example.com --body-file renewal.json
```

Review the domain, years, and price. After approval, apply from the same settings folder with the same account and file:

```bash
qwayk-spaceship-safe-agent-cli --output json --apply --yes --plan-in renewal-plan.json \
  --ack-spend --ack-ownership domains renew example.com --body-file renewal.json
```

Include any additional approval flags listed in your plan. When Spaceship returns an operation ID, check it with `async-operations status`. The [approval guide](safety_model.md) explains pending and unclear results.

For sold-domain reports, `--take` defaults to 100 and cannot exceed 100. Use the returned `cursor` to continue, keeping the same sale dates.
